# app.py
# Main entry point — initialises the app and routes between pages
# Run with: streamlit run app.py

import sys
import os

# Ensure the project root is on the path so all packages resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config.page_config import setup_page
from components.sidebar import render_sidebar
from pages.landing import render_landing
from pages.classify import render_classify
from pages.log import render_log
from pages.dashboard import render_dashboard


def main():
    # ── Page config & CSS (must be first Streamlit call) ──────────────────
    setup_page()

    # ── Session state defaults ────────────────────────────────────────────
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

    if 'show_override' not in st.session_state:
        st.session_state.show_override = False

    if 'confirm_clear' not in st.session_state:
        st.session_state.confirm_clear = False

    # ── Load model only when needed ───────────────────────────────────────
    # Model is loaded here so the sidebar always has access to device info
    # on the classify page, but skipped on other pages to save memory.
    models = None
    if st.session_state.page == 'classify':
        from models.loader import load_models
        with st.spinner('Loading MobileBERT…'):
            models = load_models()

    # ── Sidebar (always rendered) ─────────────────────────────────────────
    render_sidebar(models=models)

    # ── Page routing ──────────────────────────────────────────────────────
    page = st.session_state.page

    if page == 'landing':
        render_landing()

    elif page == 'classify':
        if models is None:
            # Fallback — load if somehow missed above
            from models.loader import load_models
            models = load_models()
        render_classify(models)

    elif page == 'log':
        render_log()

    elif page == 'dashboard':
        render_dashboard()

    else:
        # Unknown page — reset to landing
        st.session_state.page = 'landing'
        st.rerun()


if __name__ == '__main__':
    main()