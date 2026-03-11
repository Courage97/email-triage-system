# components/routing_card.py
# 100% native Streamlit — zero inline HTML styles

import streamlit as st
from datetime import datetime
from config.constants import ROUTING_MAP


def render_routing_card(result: dict, elapsed_ms: str = "—"):
    category  = result['category']
    routing   = ROUTING_MAP.get(category, {
        'dept': 'Registry', 'desc': 'General registry services.', 'icon': '📧'
    })
    timestamp = datetime.now().strftime('%H:%M:%S')

    st.caption("⟶ AUTOMATIC ROUTING")
    st.markdown(f"#### {routing['icon']} {routing['dept']}")
    st.markdown(routing['desc'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚡ Inference", f"{elapsed_ms} ms")
    with col2:
        st.metric("🤖 Model", "MobileBERT")
    with col3:
        st.metric("🎯 Category", category)
    with col4:
        st.metric("📅 Time", timestamp)


def render_routing_summary(category: str):
    routing = ROUTING_MAP.get(category, {'dept': 'Registry', 'icon': '📧'})
    st.caption(f"{routing['icon']} {routing['dept']}")


def render_override_routing_card(
    original_category: str,
    new_category:      str,
    elapsed_ms:        str = "—",
):
    orig_routing = ROUTING_MAP.get(original_category, {'dept': 'Registry', 'icon': '📧'})
    new_routing  = ROUTING_MAP.get(new_category,      {'dept': 'Registry', 'icon': '📧'})
    timestamp    = datetime.now().strftime('%H:%M:%S')

    st.caption("✏️ MANUAL OVERRIDE — ROUTING UPDATED")

    col_orig, col_arrow, col_new = st.columns([5, 1, 5])

    with col_orig:
        st.error(
            f"**AI Predicted**\n\n"
            f"~~{orig_routing['icon']} {original_category}~~\n\n"
            f"*{orig_routing['dept']}*"
        )

    with col_arrow:
        st.markdown("<br><br>→", unsafe_allow_html=True)

    with col_new:
        st.success(
            f"**Corrected To**\n\n"
            f"{new_routing['icon']} **{new_category}**\n\n"
            f"*{new_routing['dept']}*"
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⚡ Inference", f"{elapsed_ms} ms")
    with col2:
        st.metric("🤖 Model", "MobileBERT")
    with col3:
        st.metric("📅 Time", timestamp)