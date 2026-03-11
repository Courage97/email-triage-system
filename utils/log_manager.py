# utils/log_manager.py
# Handles all email log operations — save, load, filter, export
# Log is stored as a JSON file at data/email_log.json
# Depends on: config/constants.py

import json
import os
import uuid
from datetime import datetime

import pandas as pd

from config.constants import LOG_FILE_PATH, CATEGORIES


# ─── Ensure data directory exists ─────────────────────────────────────────────

def _ensure_data_dir():
    """Create the data/ directory if it does not exist."""
    try:
        data_dir = os.path.dirname(LOG_FILE_PATH)
        os.makedirs(data_dir, exist_ok=True)
        print(f"[log_manager] _ensure_data_dir → {data_dir} exists: {os.path.exists(data_dir)}")
    except Exception as e:
        print(f"[log_manager] _ensure_data_dir → FAILED: {e}")


# ─── Load & Save ──────────────────────────────────────────────────────────────

def load_log() -> list[dict]:
    """
    Load all email log entries from the JSON file.

    Returns:
        List of log entry dicts, newest first.
        Empty list if file does not exist or is corrupt.
    """
    _ensure_data_dir()
    print(f"[log_manager] LOG_FILE_PATH = {LOG_FILE_PATH}")
    print(f"[log_manager] file exists   = {os.path.exists(LOG_FILE_PATH)}")
    if not os.path.exists(LOG_FILE_PATH):
        return []
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_log(entries: list[dict]) -> bool:
    """
    Save the full log list back to the JSON file.
    """
    try:
        _ensure_data_dir()
        print(f"[log_manager] save_log → writing {len(entries)} entries to {LOG_FILE_PATH}")
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        print(f"[log_manager] save_log → SUCCESS, file exists: {os.path.exists(LOG_FILE_PATH)}")
        return True
    except Exception as e:
        print(f"[log_manager] save_log → FAILED: {e}")
        return False


# ─── Add Entry ────────────────────────────────────────────────────────────────

def add_log_entry(
    subject:        str,
    body:           str,
    category:       str,
    confidence:     float,
    department:     str,
    priority:       str,
    elapsed_ms:     str,
    was_overridden: bool  = False,
    original_category: str | None = None,
) -> dict:
    """
    Create a new log entry and prepend it to the log file.

    Args:
        subject:           Email subject line
        body:              Email body text
        category:          Final category (after any override)
        confidence:        Model confidence 0.0–1.0
        department:        Routed department name
        priority:          Priority level string
        elapsed_ms:        Inference time string
        was_overridden:    True if user manually changed the category
        original_category: The AI's original prediction before override

    Returns:
        The new log entry dict
    """
    entry = {
        'id':                str(uuid.uuid4())[:8].upper(),
        'timestamp':         datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date':              datetime.now().strftime('%Y-%m-%d'),
        'time':              datetime.now().strftime('%H:%M:%S'),
        'subject':           subject.strip() or '(no subject)',
        'body_preview':      body.strip()[:120] + '...' if len(body.strip()) > 120 else body.strip(),
        'category':          category,
        'confidence':        round(confidence * 100, 2),
        'department':        department,
        'priority':          priority,
        'elapsed_ms':        elapsed_ms,
        'was_overridden':    was_overridden,
        'original_category': original_category,
        'status':            'routed',
    }

    entries = load_log()
    entries.insert(0, entry)   # newest first
    save_log(entries)

    return entry


# ─── Delete Entry ─────────────────────────────────────────────────────────────

def delete_log_entry(entry_id: str) -> bool:
    """
    Remove a single log entry by its ID.

    Args:
        entry_id: The 8-character ID string

    Returns:
        True if found and deleted, False otherwise
    """
    entries = load_log()
    original_len = len(entries)
    entries = [e for e in entries if e.get('id') != entry_id]

    if len(entries) == original_len:
        return False

    return save_log(entries)


def clear_log() -> bool:
    """Delete all log entries."""
    return save_log([])


# ─── Filter & Search ──────────────────────────────────────────────────────────

def filter_log(
    entries:      list[dict],
    category:     str  = "All",
    priority:     str  = "All",
    date_from:    str  = None,
    date_to:      str  = None,
    search_query: str  = "",
    overrides_only: bool = False,
) -> list[dict]:
    """
    Filter log entries by multiple criteria.

    Args:
        entries:       Full list of log entries
        category:      Category name or "All"
        priority:      Priority level or "All"
        date_from:     Start date string YYYY-MM-DD or None
        date_to:       End date string YYYY-MM-DD or None
        search_query:  Keyword to match against subject/body preview
        overrides_only: If True, only return manually overridden entries

    Returns:
        Filtered list of log entry dicts
    """
    filtered = entries

    if category != "All":
        filtered = [e for e in filtered if e.get('category') == category]

    if priority != "All":
        filtered = [e for e in filtered if e.get('priority') == priority]

    if date_from:
        filtered = [e for e in filtered if e.get('date', '') >= date_from]

    if date_to:
        filtered = [e for e in filtered if e.get('date', '') <= date_to]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [
            e for e in filtered
            if q in e.get('subject', '').lower()
            or q in e.get('body_preview', '').lower()
            or q in e.get('category', '').lower()
            or q in e.get('department', '').lower()
        ]

    if overrides_only:
        filtered = [e for e in filtered if e.get('was_overridden')]

    return filtered


# ─── Sort ─────────────────────────────────────────────────────────────────────

def sort_log(
    entries:    list[dict],
    sort_by:    str = 'timestamp',
    ascending:  bool = False,
) -> list[dict]:
    """
    Sort log entries by a given field.

    Args:
        entries:   List of log entry dicts
        sort_by:   Field name to sort by
                   Options: 'timestamp' | 'confidence' | 'category' |
                            'priority' | 'department'
        ascending: Sort direction

    Returns:
        Sorted list
    """
    priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}

    if sort_by == 'priority':
        return sorted(
            entries,
            key=lambda e: priority_order.get(e.get('priority', 'normal'), 2),
            reverse=not ascending
        )

    return sorted(
        entries,
        key=lambda e: e.get(sort_by, ''),
        reverse=not ascending
    )


# ─── Export ───────────────────────────────────────────────────────────────────

def export_to_csv(entries: list[dict]) -> bytes:
    """
    Convert log entries to a CSV byte string for download.

    Args:
        entries: List of log entry dicts

    Returns:
        UTF-8 encoded CSV bytes
    """
    if not entries:
        return b""

    df = pd.DataFrame(entries)

    # Reorder and rename columns for clean export
    export_cols = {
        'id':                'ID',
        'timestamp':         'Timestamp',
        'subject':           'Subject',
        'category':          'Category',
        'confidence':        'Confidence (%)',
        'department':        'Department',
        'priority':          'Priority',
        'elapsed_ms':        'Inference (ms)',
        'was_overridden':    'Manually Overridden',
        'original_category': 'Original AI Category',
        'status':            'Status',
        'body_preview':      'Body Preview',
    }

    # Only include columns that exist
    available = [c for c in export_cols if c in df.columns]
    df = df[available].rename(columns={c: export_cols[c] for c in available})

    return df.to_csv(index=False).encode('utf-8')


# ─── Statistics Helpers ───────────────────────────────────────────────────────

def get_log_summary(entries: list[dict]) -> dict:
    """
    Compute quick summary counts from the log for the dashboard.

    Args:
        entries: Full list of log entries

    Returns:
        dict with keys:
            - total         (int)
            - today         (int)
            - overridden    (int)
            - urgent        (int)
            - avg_confidence (float) average confidence percentage
            - by_category   (dict)  { category: count }
            - by_priority   (dict)  { priority: count }
    """
    if not entries:
        return {
            'total':          0,
            'today':          0,
            'overridden':     0,
            'urgent':         0,
            'avg_confidence': 0.0,
            'by_category':    {cat: 0 for cat in CATEGORIES},
            'by_priority':    {'urgent': 0, 'high': 0, 'normal': 0, 'low': 0},
        }

    today = datetime.now().strftime('%Y-%m-%d')

    by_category = {cat: 0 for cat in CATEGORIES}
    by_priority = {'urgent': 0, 'high': 0, 'normal': 0, 'low': 0}
    total_conf  = 0.0

    for e in entries:
        cat = e.get('category', '')
        pri = e.get('priority', 'normal')
        if cat in by_category:
            by_category[cat] += 1
        if pri in by_priority:
            by_priority[pri] += 1
        total_conf += float(e.get('confidence', 0))

    return {
        'total':          len(entries),
        'today':          sum(1 for e in entries if e.get('date') == today),
        'overridden':     sum(1 for e in entries if e.get('was_overridden')),
        'urgent':         by_priority['urgent'],
        'avg_confidence': round(total_conf / len(entries), 1) if entries else 0.0,
        'by_category':    by_category,
        'by_priority':    by_priority,
    }