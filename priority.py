# priority.py
# MODULE 3: AI Predictive Severity Escalation
# This is one of our 4 patent features.
# It doesn't just assign HIGH/MEDIUM/LOW —
# it also predicts how fast the issue will worsen.

import datetime

# ── Issue severity base scores ──────────────────────────────────
# Each issue type has a base score (0–10).
# Higher = more urgent by default.
SEVERITY_BASE = {
    'pothole':              8.5,
    'sewage leak':          9.0,
    'fallen tree':          9.5,
    'broken streetlight':   7.0,
    'leaking public tap':   6.0,
    'garbage overflow':     5.5,
    'damaged footpath':     5.0,
    'graffiti':             2.5,
}

# ── Worsening rate per day ──────────────────────────────────────
# How much the severity score increases every day if ignored.
# This is the "predictive decay" part of our patent feature.
WORSENING_RATE = {
    'pothole':              0.8,   # gets worse fast in rain
    'sewage leak':          1.2,   # health hazard, worsens quickly
    'fallen tree':          0.3,   # stable unless storm
    'broken streetlight':   0.2,   # stable
    'leaking public tap':   0.5,
    'garbage overflow':     0.9,   # worsens with heat/rain
    'damaged footpath':     0.3,
    'graffiti':             0.1,
}

def get_base_score(issue_type):
    """Get the base severity score for an issue type."""
    key = issue_type.lower()
    for k, v in SEVERITY_BASE.items():
        if k in key:
            return v
    return 5.0  # default medium score

def get_worsening_rate(issue_type):
    """Get how fast this issue worsens per day if ignored."""
    key = issue_type.lower()
    for k, v in WORSENING_RATE.items():
        if k in key:
            return v
    return 0.3

def predict_worsening(issue_type):
    """
    Predict how the issue will worsen over time.
    Returns a human-readable string for the report.
    This is our patent feature — no other civic app does this.
    """
    rate = get_worsening_rate(issue_type)
    if rate >= 1.0:
        return 'Critical — will worsen significantly within 24 hours'
    elif rate >= 0.7:
        return 'High — noticeable worsening within 2–3 days'
    elif rate >= 0.4:
        return 'Moderate — will worsen within a week'
    else:
        return 'Stable — low worsening rate'

def assign_priority(issue_type):
    """
    Assign priority based on base severity score.
    HIGH if score >= 7, MEDIUM if >= 4.5, else LOW.
    """
    score = get_base_score(issue_type)
    if score >= 7.0:
        return 'HIGH'
    elif score >= 4.5:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_full_severity(issue_type):
    """
    Returns everything: priority, score, and worsening prediction.
    This is what app.py calls — one function gives all severity info.
    """
    return {
        'priority':            assign_priority(issue_type),
        'severity_score':      get_base_score(issue_type),
        'predicted_worsening': predict_worsening(issue_type)
    }