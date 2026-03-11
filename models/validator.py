# model/validator.py
# Confidence threshold checks and alert logic
# Depends on: config/constants.py

from config.constants import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    ROUTING_MAP,
    PRIORITY_CONFIG,
)


# ─── Confidence Level ─────────────────────────────────────────────────────────

def get_confidence_level(confidence: float) -> dict:
    """
    Determine confidence level from a 0.0–1.0 score.

    Args:
        confidence: Float between 0.0 and 1.0

    Returns:
        dict with keys:
            - level   (str)   'high' | 'medium' | 'low'
            - label   (str)   human-readable label
            - color   (str)   hex color
            - icon    (str)   emoji indicator
            - pct     (float) confidence as percentage 0–100
    """
    pct = confidence * 100

    if pct >= CONFIDENCE_HIGH:
        return {
            'level': 'high',
            'label': 'High Confidence',
            'color': '#6495ed',
            'icon':  '🟢',
            'pct':   pct,
        }
    elif pct >= CONFIDENCE_MEDIUM:
        return {
            'level': 'medium',
            'label': 'Medium Confidence — Review Recommended',
            'color': '#F59E0B',
            'icon':  '🟡',
            'pct':   pct,
        }
    else:
        return {
            'level': 'low',
            'label': 'Low Confidence — Manual Review Required',
            'color': '#EF4444',
            'icon':  '🔴',
            'pct':   pct,
        }


# ─── Alert Logic ──────────────────────────────────────────────────────────────

def should_alert(confidence: float) -> bool:
    """
    Return True if confidence is below the HIGH threshold,
    meaning the email should be flagged for human review.

    Args:
        confidence: Float between 0.0 and 1.0

    Returns:
        bool
    """
    return (confidence * 100) < CONFIDENCE_HIGH


def get_alert_message(confidence: float, category: str) -> dict | None:
    """
    Build an alert message dict if confidence is below threshold.
    Returns None if confidence is high (no alert needed).

    Args:
        confidence: Float between 0.0 and 1.0
        category:   Predicted category string

    Returns:
        dict with keys: type, title, message
        or None if no alert
    """
    level = get_confidence_level(confidence)

    if level['level'] == 'high':
        return None

    if level['level'] == 'medium':
        return {
            'type':    'warning',
            'title':   '⚠️ Medium Confidence',
            'message': (
                f"The model predicted **{category}** with "
                f"**{level['pct']:.1f}%** confidence. "
                f"Consider reviewing the classification before routing."
            ),
        }

    # low
    return {
        'type':    'error',
        'title':   '🔴 Low Confidence — Manual Review Required',
        'message': (
            f"The model predicted **{category}** with only "
            f"**{level['pct']:.1f}%** confidence. "
            f"Please manually verify the category before routing this email."
        ),
    }


# ─── Priority Logic ───────────────────────────────────────────────────────────

def get_priority(category: str) -> dict:
    """
    Get priority level for a given category from ROUTING_MAP.

    Args:
        category: Email category string

    Returns:
        dict from PRIORITY_CONFIG with keys: label, color, badge
    """
    routing  = ROUTING_MAP.get(category, {})
    priority = routing.get('priority', 'normal')
    return {
        'key':   priority,
        **PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG['normal']),
    }


def is_urgent(category: str) -> bool:
    """Return True if the category is marked as urgent priority."""
    return get_priority(category)['key'] == 'urgent'


def is_high_priority(category: str) -> bool:
    """Return True if the category is urgent or high priority."""
    return get_priority(category)['key'] in ('urgent', 'high')


# ─── Validation Summary ───────────────────────────────────────────────────────

def validate_result(result: dict) -> dict:
    """
    Run all validation checks on a prediction result and return
    a single validation summary dict used by the classify page.

    Args:
        result: Dict returned by predict_email()

    Returns:
        dict with keys:
            - confidence_info  (dict)  from get_confidence_level()
            - alert            (dict | None) from get_alert_message()
            - priority         (dict)  from get_priority()
            - needs_review     (bool)  True if confidence < HIGH threshold
            - is_urgent        (bool)  True if category is urgent
    """
    category   = result['category']
    confidence = result['confidence']

    confidence_info = get_confidence_level(confidence)
    alert           = get_alert_message(confidence, category)
    priority        = get_priority(category)

    return {
        'confidence_info': confidence_info,
        'alert':           alert,
        'priority':        priority,
        'needs_review':    should_alert(confidence),
        'is_urgent':       is_urgent(category),
    }