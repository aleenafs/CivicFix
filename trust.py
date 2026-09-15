# trust.py
# MODULE 5: Community Verification & Trust Scoring

BASE_TRUST_SCORE = 5.0
MAX_TRUST_SCORE  = 10.0
MIN_TRUST_SCORE  = 1.0

def calculate_new_trust_score(current_score, verified=True):
    if verified:
        gap = MAX_TRUST_SCORE - current_score
        new_score = current_score + (gap * 0.15)
    else:
        decrease = (current_score - MIN_TRUST_SCORE) * 0.25
        new_score = current_score - decrease
    return round(max(MIN_TRUST_SCORE, min(MAX_TRUST_SCORE, new_score)), 2)

def get_trust_label(score):
    if score >= 8.5:
        return 'Trusted Reporter'
    elif score >= 6.5:
        return 'Verified Citizen'
    elif score >= 4.0:
        return 'New Reporter'
    else:
        return 'Low Trust - Under Review'

def get_priority_boost(trust_score, current_priority):
    if trust_score >= 8.5 and current_priority == 'HIGH':
        return 1.5
    elif trust_score >= 6.5:
        return 1.2
    else:
        return 1.0

def process_verification(report_id, reporter_trust_score,
                         verifier_trust_score, is_confirmed):
    new_score = calculate_new_trust_score(reporter_trust_score, verified=is_confirmed)
    return {
        'new_trust_score': new_score,
        'trust_label':     get_trust_label(new_score),
        'result':          'confirmed' if is_confirmed else 'disputed'
    }