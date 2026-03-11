# pages/landing.py
# Landing / home page
# Depends on: config/constants.py, utils/log_manager.py

import streamlit as st

from config.constants import (
    APP_NAME,
    APP_SUBTITLE,
    MODEL_NAME,
    MODEL_ACCURACY,
    AVG_CONFIDENCE,
    INFERENCE_SPEED,
    CATEGORIES,
    ROUTING_MAP,
    CATEGORY_COLORS,
)
from utils.log_manager import load_log, get_log_summary


def render_landing():
    """Render the full landing / home page."""
    _render_hero()
    _render_stats()
    _render_features()
    _render_categories()
    _render_cta()
    _render_footer()


# ─── Hero ─────────────────────────────────────────────────────────────────────

def _render_hero():
    # Use native Streamlit elements — no large HTML blocks
    # Styling applied via CSS classes injected in page_config.py

    st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)

    st.markdown(
        '<span class="hero-eyebrow">🤖 AI-Powered Classification System</span>',
        unsafe_allow_html=True
    )

    st.title("Intelligent Email Triage System")

    st.markdown(
        f'<p class="hero-sub">Automatically classify and route incoming registry '
        f'emails using <strong>{MODEL_NAME}</strong> — a compact transformer '
        f'fine-tuned for academic registry workflows across 10 categories.</p>',
        unsafe_allow_html=True
    )

    # Badge row — short single-line HTML, no nesting issues
    b1 = f'<span class="hero-badge"><strong>{MODEL_ACCURACY}</strong> Accuracy</span>'
    b2 = f'<span class="hero-badge"><strong>{AVG_CONFIDENCE}</strong> Confidence</span>'
    b3 = f'<span class="hero-badge"><strong>{INFERENCE_SPEED}</strong> Speed</span>'
    b4 = f'<span class="hero-badge"><strong>10</strong> Categories</span>'
    b5 = f'<span class="hero-badge"><strong>{MODEL_NAME}</strong></span>'

    st.markdown(
        f'<div class="hero-badges">{b1}{b2}{b3}{b4}{b5}</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def _badge(value: str, label: str) -> str:
    return f"""
    <div style="
        display:flex;
        flex-direction:column;
        background:rgba(100,149,237,0.08);
        border:1px solid rgba(100,149,237,0.2);
        border-radius:10px;
        padding:0.55rem 1rem;
        min-width:90px;
    ">
        <span style="
            font-family:'Space Grotesk',sans-serif;
            font-size:1rem;
            font-weight:700;
            color:#E6E6FA;
            line-height:1;
        ">{value}</span>
        <span style="
            font-family:'JetBrains Mono',monospace;
            font-size:0.6rem;
            color:#5a6a8a;
            letter-spacing:0.08em;
            text-transform:uppercase;
            margin-top:0.25rem;
        ">{label}</span>
    </div>
    """


# ─── Stats Row ────────────────────────────────────────────────────────────────

def _render_stats():
    entries = load_log()
    summary = get_log_summary(entries)

    st.markdown('<span class="section-label">Live System Stats</span>',
                unsafe_allow_html=True)

    cols = st.columns(4)
    stats = [
        (str(summary['total']),          "Emails Classified", "#6495ed"),
        (str(summary['today']),          "Classified Today",  "#10B981"),
        (str(summary['urgent']),         "Urgent Flagged",    "#EF4444"),
        (f"{summary['avg_confidence']}%","Avg Confidence",    "#F59E0B"),
    ]

    for col, (val, lbl, color) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card" style="border-color:rgba(100,149,237,0.2);">
                <span class="stat-val" style="color:{color};">{val}</span>
                <span class="stat-lbl">{lbl}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


# ─── Features ─────────────────────────────────────────────────────────────────

def _render_features():
    st.markdown('<span class="section-label">Why It Works</span>',
                unsafe_allow_html=True)

    features = [
        ("⚡", "Lightning Fast",
         f"Sub-50ms inference using {MODEL_NAME}. Emails are classified "
         "and routed before staff finish reading the subject line."),
        ("🎯", "High Accuracy",
         f"{MODEL_ACCURACY} classification accuracy with {AVG_CONFIDENCE} "
         "average confidence across all 10 academic registry categories."),
        ("🔄", "Smart Routing",
         "Each email is automatically mapped to the correct department "
         "with priority tagging — urgent emails are flagged instantly."),
        ("✏️", "Manual Override",
         "If the AI misclassifies, staff can correct and re-route manually. "
         "All overrides are logged for model improvement."),
        ("📋", "Full Audit Log",
         "Every classified email is stored with timestamp, confidence, "
         "department, and override history for full traceability."),
        ("📊", "Analytics Dashboard",
         "Live charts showing category distribution, confidence trends, "
         "volume over time, and model override rates."),
    ]

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card card-accent-top" style="margin-bottom:1rem;">
                <div style="
                    width:40px; height:40px;
                    background:rgba(100,149,237,0.1);
                    border:1px solid rgba(100,149,237,0.22);
                    border-radius:10px;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.2rem;
                    margin-bottom:0.85rem;
                ">{icon}</div>
                <div style="
                    font-family:'Space Grotesk',sans-serif;
                    font-size:0.95rem;
                    font-weight:700;
                    color:#E6E6FA;
                    margin-bottom:0.45rem;
                ">{title}</div>
                <div style="
                    font-family:'Inter',sans-serif;
                    font-size:0.82rem;
                    color:#a8b4d0;
                    line-height:1.65;
                ">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


# ─── Categories ───────────────────────────────────────────────────────────────

def _render_categories():
    st.markdown('<span class="section-label">Supported Email Categories</span>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    for i, category in enumerate(CATEGORIES):
        routing   = ROUTING_MAP[category]
        cat_color = CATEGORY_COLORS[category]
        col       = col1 if i % 2 == 0 else col2

        with col:
            st.markdown(f"""
            <div style="
                display:flex;
                align-items:center;
                gap:0.85rem;
                background:rgba(18,18,58,0.6);
                border:1px solid rgba(100,149,237,0.12);
                border-left:2px solid {cat_color};
                border-radius:10px;
                padding:0.85rem 1rem;
                margin-bottom:0.6rem;
                transition:all 0.2s;
            ">
                <div style="
                    width:36px; height:36px;
                    background:{cat_color}15;
                    border-radius:8px;
                    display:flex; align-items:center;
                    justify-content:center;
                    font-size:1.1rem;
                    flex-shrink:0;
                ">{routing['icon']}</div>
                <div>
                    <div style="
                        font-family:'Space Grotesk',sans-serif;
                        font-size:0.88rem;
                        font-weight:600;
                        color:#E6E6FA;
                        margin-bottom:0.1rem;
                    ">{category}</div>
                    <div style="
                        font-family:'Inter',sans-serif;
                        font-size:0.75rem;
                        color:#5a6a8a;
                    ">{routing['dept']}</div>
                </div>
                <div style="
                    margin-left:auto;
                    font-family:'JetBrains Mono',monospace;
                    font-size:0.62rem;
                    color:{cat_color};
                    background:{cat_color}12;
                    border:1px solid {cat_color}30;
                    border-radius:100px;
                    padding:0.15rem 0.55rem;
                    white-space:nowrap;
                ">{routing['priority'].upper()}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


# ─── CTA ──────────────────────────────────────────────────────────────────────

def _render_cta():
    st.markdown("""
    <div style="
        background:linear-gradient(
            135deg,
            rgba(27,0,63,0.9) 0%,
            rgba(100,149,237,0.1) 100%
        );
        border:1px solid rgba(100,149,237,0.25);
        border-radius:18px;
        padding:2.5rem;
        text-align:center;
        margin-bottom:1.5rem;
    ">
        <div style="
            font-family:'Space Grotesk',sans-serif;
            font-size:1.6rem;
            font-weight:700;
            color:#E6E6FA;
            margin-bottom:0.5rem;
        ">Ready to classify?</div>
        <div style="
            font-family:'Inter',sans-serif;
            font-size:0.9rem;
            color:#a8b4d0;
            margin-bottom:0;
        ">
            Paste any email and get an instant AI classification
            with automatic department routing.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Open Classifier →", type="primary",
                     use_container_width=True, key="cta_classify"):
            st.session_state.page = "classify"
            st.rerun()


# ─── Footer ───────────────────────────────────────────────────────────────────

def _render_footer():
    st.markdown(f"""
    <div class="footer">
        <p>
            {APP_NAME} &nbsp;·&nbsp; {MODEL_NAME} &nbsp;·&nbsp;
            Academic Research Project &nbsp;·&nbsp;
            {MODEL_ACCURACY} Test Accuracy
        </p>
    </div>
    """, unsafe_allow_html=True)