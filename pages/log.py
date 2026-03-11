import pathfix  # noqa
import streamlit as st

from config.constants import CATEGORIES, ROUTING_MAP, CATEGORY_COLORS, PRIORITY_CONFIG
from utils.log_manager import (
    load_log, filter_log, sort_log, delete_log_entry,
    clear_log, export_to_csv, get_log_summary,
)


def render_log():
    st.markdown("## 📋 Email Log")
    st.caption("View, filter, search and export all classified emails")

    entries = load_log()

    if not entries:
        _render_empty_state()
        return

    _render_summary_row(entries)
    st.divider()
    filtered = _render_filters(entries)
    st.divider()
    _render_toolbar(filtered)
    st.markdown("<br>", unsafe_allow_html=True)
    _render_log_table(filtered)
    st.divider()
    _render_danger_zone()


def _render_empty_state():
    st.info("📭 No emails classified yet. Go to **Classify Email** to get started.")
    if st.button("Go to Classifier →", type="primary", key="log_goto_classify"):
        st.session_state.page = "classify"
        st.rerun()


def _render_summary_row(entries):
    summary = get_log_summary(entries)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total",       summary['total'])
    with c2: st.metric("Today",       summary['today'])
    with c3: st.metric("Urgent",      summary['urgent'])
    with c4: st.metric("Overridden",  summary['overridden'])
    with c5: st.metric("Avg Conf.",   f"{summary['avg_confidence']}%")


def _render_filters(entries):
    st.caption("FILTER & SEARCH")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

    with c1:
        search = st.text_input("Search", placeholder="Subject, body, category…", key="log_search")
    with c2:
        category = st.selectbox("Category", ["All"] + CATEGORIES, key="log_filter_category")
    with c3:
        priority = st.selectbox("Priority", ["All", "urgent", "high", "normal", "low"], key="log_filter_priority")
    with c4:
        sort_options = {
            "Newest First":  ("timestamp",  False),
            "Oldest First":  ("timestamp",  True),
            "Highest Conf.": ("confidence", False),
            "Lowest Conf.":  ("confidence", True),
            "Category A–Z":  ("category",   True),
        }
        sort_choice = st.selectbox("Sort By", list(sort_options.keys()), key="log_sort")

    c_d1, c_d2, c_d3 = st.columns([1, 1, 2])
    with c_d1:
        date_from = st.date_input("From Date", value=None, key="log_date_from")
    with c_d2:
        date_to = st.date_input("To Date", value=None, key="log_date_to")
    with c_d3:
        overrides_only = st.checkbox("Show overrides only", key="log_overrides_only")

    filtered = filter_log(
        entries,
        category=category,
        priority=priority,
        date_from=str(date_from) if date_from else None,
        date_to=str(date_to)     if date_to   else None,
        search_query=search,
        overrides_only=overrides_only,
    )
    sort_field, ascending = sort_options[sort_choice]
    filtered = sort_log(filtered, sort_by=sort_field, ascending=ascending)

    st.caption(f"Showing **{len(filtered)}** of **{len(entries)}** emails")
    return filtered


def _render_toolbar(filtered):
    c1, c2 = st.columns([1, 4])
    with c1:
        if filtered:
            st.download_button(
                "⬇ Export CSV",
                data=export_to_csv(filtered),
                file_name="email_log.csv",
                mime="text/csv",
                key="log_export_csv"
            )
    with c2:
        if st.button("🔄 Refresh", key="log_refresh"):
            st.rerun()


def _render_log_table(entries):
    if not entries:
        st.info("🔍 No results found. Try adjusting your filters.")
        return

    for entry in entries:
        _render_log_entry(entry)


def _render_log_entry(entry):
    routing   = ROUTING_MAP.get(entry.get('category', ''), {})
    priority  = PRIORITY_CONFIG.get(entry.get('priority', 'normal'), PRIORITY_CONFIG['normal'])
    conf      = float(entry.get('confidence', 0))
    override  = " · ✏️ Overridden" if entry.get('was_overridden') else ""

    label = (
        f"{priority['badge']} {routing.get('icon','📧')} "
        f"**{entry.get('category','—')}** · "
        f"{entry.get('subject','(no subject)')} · "
        f"`{entry.get('timestamp','—')}`{override}"
    )

    with st.expander(label):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Subject:** {entry.get('subject', '—')}")
            st.markdown(f"**Category:** {entry.get('category', '—')}")
            st.markdown(f"**Department:** {routing.get('dept', '—')}")
            st.markdown(f"**Priority:** {priority['badge']} {priority['label']}")
            st.markdown(f"**Timestamp:** {entry.get('timestamp', '—')}")
            st.markdown(f"**Inference:** {entry.get('elapsed_ms', '—')} ms")
            st.markdown(f"**Log ID:** `{entry.get('id', '—')}`")
            st.divider()
            st.caption("BODY PREVIEW")
            st.text(entry.get('body_preview', '—'))

            if entry.get('was_overridden') and entry.get('original_category'):
                st.warning(
                    f"✏️ Overridden from **{entry['original_category']}** "
                    f"→ **{entry.get('category','—')}**"
                )

        with col2:
            st.metric("Confidence", f"{conf:.1f}%")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑 Delete", key=f"del_{entry.get('id','')}", use_container_width=True):
                if delete_log_entry(entry.get('id', '')):
                    st.success("Deleted.")
                    st.rerun()
                else:
                    st.error("Could not delete.")


def _render_danger_zone():
    with st.expander("⚠️ Danger Zone — Clear All Logs"):
        st.warning("This will permanently delete **all** log entries and cannot be undone.")
        c1, c2 = st.columns([1, 3])
        with c1:
            if st.button("🗑 Clear All Logs", key="log_clear_all"):
                st.session_state['confirm_clear'] = True

        if st.session_state.get('confirm_clear'):
            st.error("Are you sure? This cannot be undone.")
            if st.button("Yes, delete everything", type="primary", key="log_confirm_clear"):
                clear_log()
                st.session_state['confirm_clear'] = False
                st.success("All logs deleted.")