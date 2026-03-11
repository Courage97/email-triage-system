# utils/stats.py
# Statistics calculations for the dashboard
# Depends on: config/constants.py, utils/log_manager.py

from datetime import datetime, timedelta
from collections import defaultdict

import pandas as pd

from config.constants import CATEGORIES, CATEGORY_COLORS, PRIORITY_CONFIG


# ─── Category Distribution ────────────────────────────────────────────────────

def category_distribution(entries: list[dict]) -> pd.DataFrame:
    """
    Count emails per category for a pie / bar chart.

    Args:
        entries: List of log entry dicts

    Returns:
        DataFrame with columns: category, count, color, percentage
    """
    counts = {cat: 0 for cat in CATEGORIES}
    for e in entries:
        cat = e.get('category', '')
        if cat in counts:
            counts[cat] += 1

    total = sum(counts.values()) or 1

    rows = [
        {
            'category':   cat,
            'count':      count,
            'color':      CATEGORY_COLORS.get(cat, '#6495ed'),
            'percentage': round(count / total * 100, 1),
        }
        for cat, count in counts.items()
        if count > 0
    ]

    return pd.DataFrame(rows).sort_values('count', ascending=False)


# ─── Confidence Distribution ──────────────────────────────────────────────────

def confidence_distribution(entries: list[dict]) -> pd.DataFrame:
    """
    Bucket confidence scores into ranges for a histogram.

    Buckets: 0–20, 20–40, 40–60, 60–80, 80–100

    Args:
        entries: List of log entry dicts

    Returns:
        DataFrame with columns: range, count, color
    """
    buckets = {
        '0–20%':   0,
        '20–40%':  0,
        '40–60%':  0,
        '60–80%':  0,
        '80–100%': 0,
    }
    colors = {
        '0–20%':   '#EF4444',
        '20–40%':  '#F97316',
        '40–60%':  '#F59E0B',
        '60–80%':  '#6495ed',
        '80–100%': '#10B981',
    }

    for e in entries:
        conf = float(e.get('confidence', 0))
        if conf < 20:
            buckets['0–20%'] += 1
        elif conf < 40:
            buckets['20–40%'] += 1
        elif conf < 60:
            buckets['40–60%'] += 1
        elif conf < 80:
            buckets['60–80%'] += 1
        else:
            buckets['80–100%'] += 1

    rows = [
        {'range': k, 'count': v, 'color': colors[k]}
        for k, v in buckets.items()
    ]
    return pd.DataFrame(rows)


# ─── Volume Over Time ─────────────────────────────────────────────────────────

def volume_over_time(
    entries:     list[dict],
    period:      str = 'daily',
    last_n_days: int = 30,
) -> pd.DataFrame:
    """
    Count emails classified per time period for a line/bar chart.

    Args:
        entries:     List of log entry dicts
        period:      'daily' | 'weekly' | 'monthly'
        last_n_days: How many days back to include

    Returns:
        DataFrame with columns: period, count
    """
    if not entries:
        return pd.DataFrame(columns=['period', 'count'])

    cutoff = datetime.now() - timedelta(days=last_n_days)
    counts: dict = defaultdict(int)

    for e in entries:
        try:
            dt = datetime.strptime(e.get('date', ''), '%Y-%m-%d')
        except ValueError:
            continue

        if dt < cutoff:
            continue

        if period == 'daily':
            key = dt.strftime('%Y-%m-%d')
        elif period == 'weekly':
            key = f"W{dt.isocalendar()[1]} {dt.year}"
        else:
            key = dt.strftime('%b %Y')

        counts[key] += 1

    if not counts:
        return pd.DataFrame(columns=['period', 'count'])

    df = pd.DataFrame(
        [{'period': k, 'count': v} for k, v in sorted(counts.items())]
    )
    return df


# ─── Priority Breakdown ───────────────────────────────────────────────────────

def priority_breakdown(entries: list[dict]) -> pd.DataFrame:
    """
    Count emails per priority level.

    Args:
        entries: List of log entry dicts

    Returns:
        DataFrame with columns: priority, label, count, color, badge
    """
    counts = {'urgent': 0, 'high': 0, 'normal': 0, 'low': 0}

    for e in entries:
        pri = e.get('priority', 'normal')
        if pri in counts:
            counts[pri] += 1

    rows = [
        {
            'priority': pri,
            'label':    PRIORITY_CONFIG[pri]['label'],
            'count':    count,
            'color':    PRIORITY_CONFIG[pri]['color'],
            'badge':    PRIORITY_CONFIG[pri]['badge'],
        }
        for pri, count in counts.items()
        if count > 0
    ]

    priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
    return pd.DataFrame(rows).sort_values(
        'priority', key=lambda s: s.map(priority_order)
    )


# ─── Top Categories ───────────────────────────────────────────────────────────

def top_categories(entries: list[dict], n: int = 5) -> list[dict]:
    """
    Return the N most frequent email categories.

    Args:
        entries: List of log entry dicts
        n:       Number of top categories to return

    Returns:
        List of dicts: [{ category, count, color, percentage }]
    """
    df = category_distribution(entries)
    if df.empty:
        return []
    return df.head(n).to_dict(orient='records')


# ─── Override Rate ────────────────────────────────────────────────────────────

def override_rate(entries: list[dict]) -> dict:
    """
    Calculate the manual override rate.

    Args:
        entries: List of log entry dicts

    Returns:
        dict with keys: total, overridden, rate_pct, accuracy_pct
    """
    total      = len(entries)
    overridden = sum(1 for e in entries if e.get('was_overridden'))
    rate       = round(overridden / total * 100, 1) if total else 0.0
    accuracy   = round(100 - rate, 1)

    return {
        'total':       total,
        'overridden':  overridden,
        'rate_pct':    rate,
        'accuracy_pct': accuracy,
    }


# ─── Average Confidence Per Category ─────────────────────────────────────────

def avg_confidence_by_category(entries: list[dict]) -> pd.DataFrame:
    """
    Compute average confidence score per category.

    Args:
        entries: List of log entry dicts

    Returns:
        DataFrame with columns: category, avg_confidence, color
        Sorted by avg_confidence descending
    """
    totals: dict = defaultdict(list)

    for e in entries:
        cat  = e.get('category', '')
        conf = float(e.get('confidence', 0))
        if cat in CATEGORIES:
            totals[cat].append(conf)

    rows = [
        {
            'category':       cat,
            'avg_confidence': round(sum(vals) / len(vals), 1),
            'color':          CATEGORY_COLORS.get(cat, '#6495ed'),
        }
        for cat, vals in totals.items()
        if vals
    ]

    if not rows:
        return pd.DataFrame(columns=['category', 'avg_confidence', 'color'])

    return pd.DataFrame(rows).sort_values('avg_confidence', ascending=False)


# ─── Daily Stats Summary ──────────────────────────────────────────────────────

def daily_summary(entries: list[dict]) -> dict:
    """
    Compute stats for today only.

    Args:
        entries: Full log entry list

    Returns:
        dict with keys: count, avg_confidence, urgent_count, override_count
    """
    today = datetime.now().strftime('%Y-%m-%d')
    today_entries = [e for e in entries if e.get('date') == today]

    if not today_entries:
        return {
            'count':          0,
            'avg_confidence': 0.0,
            'urgent_count':   0,
            'override_count': 0,
        }

    confidences = [float(e.get('confidence', 0)) for e in today_entries]

    return {
        'count':          len(today_entries),
        'avg_confidence': round(sum(confidences) / len(confidences), 1),
        'urgent_count':   sum(1 for e in today_entries if e.get('priority') == 'urgent'),
        'override_count': sum(1 for e in today_entries if e.get('was_overridden')),
    }