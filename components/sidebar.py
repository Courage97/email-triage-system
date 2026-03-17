import pathfix  # noqa — must be first, adds project root to sys.path

import streamlit as st

from config.constants import APP_NAME, APP_VERSION, MODEL_NAME, MODEL_ACCURACY, MODEL_PARAMS
from models.loader import get_device_label
from utils.log_manager import load_log, get_log_summary

PAGES = [
    {"key": "landing",   "label": "Home",          "icon": "🏠"},
    {"key": "classify",  "label": "Classify Email", "icon": "📧"},
    {"key": "inbox",     "label": "Live Inbox",      "icon": "📬"},
    {"key": "log",       "label": "Email Log",      "icon": "📋"},
    {"key": "dashboard", "label": "Dashboard",      "icon": "📊"},
]


def render_sidebar(models: dict = None) -> str:
    with st.sidebar:
        _render_brand()
        st.divider()
        _render_navigation()
        st.divider()
        _render_status(models)
        st.divider()
        _render_log_summary()
        if models:
            st.divider()
            _render_model_info(models)
        _render_sidebar_footer()

    return st.session_state.get('page', 'landing')


def _render_brand():
    st.markdown(f"### 🤖 {APP_NAME}")
    st.caption(f"v{APP_VERSION} · Academic Research Project")


def _render_navigation():
    st.caption("NAVIGATION")
    current = st.session_state.get('page', 'landing')

    for page in PAGES:
        label = f"{page['icon']}  {page['label']}"
        if current == page['key']:
            st.markdown(f"**→ {label}**")
        else:
            if st.button(label, key=f"nav_{page['key']}", use_container_width=True):
                st.session_state.page = page['key']
                st.rerun()


def _render_status(models: dict = None):
    st.caption("SYSTEM STATUS")
    if models:
        device = get_device_label(models)
        st.success(f"🟢 Online · {device}")
    else:
        st.warning("🟡 Model not loaded")


def _render_log_summary():
    st.caption("LOG SUMMARY")
    entries = load_log()
    summary = get_log_summary(entries)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total",   summary['total'])
        st.metric("Urgent",  summary['urgent'])
    with col2:
        st.metric("Today",     summary['today'])
        st.metric("Overrides", summary['overridden'])


def _render_model_info(models: dict):
    st.caption("MODEL INFO")
    st.metric("Architecture", MODEL_NAME)
    st.metric("Parameters",   MODEL_PARAMS)
    st.metric("Accuracy",     MODEL_ACCURACY)
    st.metric("Device",       get_device_label(models))


def _render_sidebar_footer():
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("AI Email Triage System · MobileBERT · 2026")