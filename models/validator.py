import pathfix  # noqa
# model/validator.py
# Confidence threshold checks, alert logic, and irrelevant detection

from config.constants import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    IRRELEVANT_THRESHOLD,
    ROUTING_MAP,
    PRIORITY_CONFIG,
)


def get_confidence_level(confidence: float) -> dict:
    pct = confidence * 100
    if pct >= CONFIDENCE_HIGH:
        return {'level': 'high',   'label': 'High Confidence',
                'color': '#10B981', 'icon': '🟢', 'pct': pct}
    elif pct >= CONFIDENCE_MEDIUM:
        return {'level': 'medium', 'label': 'Medium Confidence — Review Recommended',
                'color': '#F59E0B', 'icon': '🟡', 'pct': pct}
    else:
        return {'level': 'low',    'label': 'Low Confidence — Manual Review Required',
                'color': '#EF4444', 'icon': '🔴', 'pct': pct}


def is_irrelevant(confidence: float) -> bool:
    """
    Return True if the model's top confidence is below IRRELEVANT_THRESHOLD,
    meaning the email is likely not meant for the registry.
    """
    return (confidence * 100) < IRRELEVANT_THRESHOLD


def get_irrelevant_reason(confidence: float, category: str) -> str:
    """Return a plain-English explanation of why the email is flagged irrelevant."""
    pct = confidence * 100
    return (
        f"The model's best guess was **{category}** with only **{pct:.1f}%** confidence "
        f"(threshold: {IRRELEVANT_THRESHOLD}%). This email does not appear to be "
        f"intended for the registry. It has been flagged as **Irrelevant**."
    )


def should_alert(confidence: float) -> bool:
    return (confidence * 100) < CONFIDENCE_HIGH


def get_alert_message(confidence: float, category: str) -> dict | None:
    level = get_confidence_level(confidence)
    if level['level'] == 'high':
        return None
    if level['level'] == 'medium':
        return {
            'type':    'warning',
            'title':   '⚠️ Medium Confidence',
            'message': (
                f"Predicted **{category}** with **{level['pct']:.1f}%** confidence. "
                f"Consider reviewing before routing."
            ),
        }
    return {
        'type':    'error',
        'title':   '🔴 Low Confidence',
        'message': (
            f"Predicted **{category}** with only **{level['pct']:.1f}%** confidence. "
            f"Please manually verify before routing."
        ),
    }


def get_priority(category: str) -> dict:
    routing  = ROUTING_MAP.get(category, {})
    priority = routing.get('priority', 'normal')
    return {'key': priority, **PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG['normal'])}


def is_urgent(category: str) -> bool:
    return get_priority(category)['key'] == 'urgent'


def is_high_priority(category: str) -> bool:
    return get_priority(category)['key'] in ('urgent', 'high')


def validate_result(result: dict) -> dict:
    """
    Full validation — includes irrelevant detection.
    Returns dict with: confidence_info, alert, priority,
                       needs_review, is_urgent, is_irrelevant, irrelevant_reason
    """
    category   = result['category']
    confidence = result['confidence']

    confidence_info   = get_confidence_level(confidence)
    alert             = get_alert_message(confidence, category)
    priority          = get_priority(category)
    irrelevant        = is_irrelevant(confidence)
    irrelevant_reason = get_irrelevant_reason(confidence, category) if irrelevant else None

    return {
        'confidence_info':   confidence_info,
        'alert':             alert,
        'priority':          priority,
        'needs_review':      should_alert(confidence),
        'is_urgent':         is_urgent(category),
        'is_irrelevant':     irrelevant,
        'irrelevant_reason': irrelevant_reason,
    }