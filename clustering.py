# clustering.py
# MODULE 6: Issue Clustering & Ward-Level Heat Map
# Patent feature #5 — groups individual reports into zone-level
# civic health data. Turns CivicFix from a complaint box into
# an urban planning intelligence tool.

import math

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate distance in metres between two GPS coordinates.
    Uses the Haversine formula — standard for GPS distance.
    """
    R = 6371000  # Earth's radius in metres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def cluster_reports(reports, radius_metres=500):
    """
    Group nearby reports into clusters.
    Any reports within radius_metres of each other form a cluster.
    Returns a list of clusters, each with a centre point and count.
    This powers the heat map on the Live Issues page.
    """
    clusters = []
    used = set()

    for i, report in enumerate(reports):
        if i in used:
            continue
        if not report.get('lat') or not report.get('lng'):
            continue

        cluster = {
            'centre_lat':   report['lat'],
            'centre_lng':   report['lng'],
            'reports':      [report],
            'count':        1,
            'high_count':   1 if report.get('priority') == 'HIGH' else 0,
            'ward':         report.get('ward', 'Unknown'),
            'issue_types':  [report.get('issue_type', '')]
        }
        used.add(i)

        for j, other in enumerate(reports):
            if j in used or j == i:
                continue
            if not other.get('lat') or not other.get('lng'):
                continue
            dist = calculate_distance(
                report['lat'], report['lng'],
                other['lat'],  other['lng']
            )
            if dist <= radius_metres:
                cluster['reports'].append(other)
                cluster['count'] += 1
                cluster['high_count'] += 1 if other.get('priority') == 'HIGH' else 0
                cluster['issue_types'].append(other.get('issue_type', ''))
                used.add(j)

        clusters.append(cluster)

    return clusters

def get_ward_health_report(ward_data):
    """
    Generate a civic health score for each ward (0–100).
    Lower score = more problems = needs more attention.
    This is the urban planning intelligence feature.
    """
    health_reports = []
    for ward in ward_data:
        total = ward.get('count', 0)
        high  = ward.get('high_count', 0)

        # Score formula: start at 100, deduct for each issue
        # High priority issues deduct more
        score = 100 - (total * 3) - (high * 7)
        score = max(0, min(100, score))  # clamp 0–100

        if score >= 75:
            status = 'Healthy'
        elif score >= 50:
            status = 'Needs Attention'
        elif score >= 25:
            status = 'Critical'
        else:
            status = 'Emergency'

        health_reports.append({
            'ward':         ward.get('ward', 'Unknown'),
            'total_issues': total,
            'high_issues':  high,
            'health_score': score,
            'status':       status
        })

    return sorted(health_reports, key=lambda x: x['health_score'])