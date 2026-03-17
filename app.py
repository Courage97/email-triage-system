import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from config.page_config import setup_page
from components.sidebar import render_sidebar
from pages.landing import render_landing
from pages.classify import render_classify
from pages.inbox import render_inbox
from pages.log import render_log
from pages.dashboard import render_dashboard


def main():
    setup_page()

    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'show_override' not in st.session_state:
        st.session_state.show_override = False
    if 'confirm_clear' not in st.session_state:
        st.session_state.confirm_clear = False
    if 'imap_connected' not in st.session_state:
        st.session_state.imap_connected = False

    # Load model only for pages that need it
    models = None
    if st.session_state.page in ('classify', 'inbox'):
        from models.loader import load_models
        with st.spinner('Loading MobileBERT…'):
            models = load_models()

    render_sidebar(models=models)

    page = st.session_state.page

    if page == 'landing':
        render_landing()
    elif page == 'classify':
        if models is None:
            from models.loader import load_models
            models = load_models()
        render_classify(models)
    elif page == 'inbox':
        if models is None:
            from models.loader import load_models
            models = load_models()
        render_inbox(models)
    elif page == 'log':
        render_log()
    elif page == 'dashboard':
        render_dashboard()
    else:
        st.session_state.page = 'landing'
        st.rerun()


if __name__ == '__main__':
    main()