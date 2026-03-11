# config/page_config.py
# Page configuration and global CSS theme
# Call setup_page() once at the top of app.py

import streamlit as st
from config.constants import APP_NAME


def setup_page():
    """Configure Streamlit page and inject global CSS theme."""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    _inject_css()


def _inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap');

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CSS VARIABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
:root {
    --bg-base:        #0a0a1a;
    --bg-surface:     #191970;
    --bg-elevated:    #1e1e4a;
    --bg-card:        #12123a;
    --bg-deep:        #1b003f;

    --accent-primary: #6495ed;
    --accent-soft:    rgba(100, 149, 237, 0.15);
    --accent-border:  rgba(100, 149, 237, 0.25);
    --accent-glow:    rgba(100, 149, 237, 0.08);

    --text-primary:   #E6E6FA;
    --text-secondary: #a8b4d0;
    --text-muted:     #5a6a8a;
    --text-accent:    #6495ed;

    --success:        #10B981;
    --warning:        #F59E0B;
    --danger:         #EF4444;
    --urgent:         #EF4444;

    --radius-sm:      8px;
    --radius-md:      12px;
    --radius-lg:      18px;
    --radius-xl:      24px;

    --font-display:   'Space Grotesk', sans-serif;
    --font-body:      'Inter', sans-serif;
    --font-mono:      'JetBrains Mono', monospace;

    --transition:     all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   RESET & BASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background-color: var(--bg-base);
    background-image:
        radial-gradient(ellipse 100% 50% at 50% -10%,
            rgba(100, 149, 237, 0.06) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 0% 100%,
            rgba(27, 0, 63, 0.8) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 100% 0%,
            rgba(100, 149, 237, 0.04) 0%, transparent 60%);
    font-family: var(--font-body);
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 5rem;
    max-width: 1400px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TYPOGRAPHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}
p, li, span, label {
    font-family: var(--font-body);
    color: var(--text-secondary);
}
code, pre {
    font-family: var(--font-mono) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SIDEBAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d2e 0%, #0a0020 100%);
    border-right: 1px solid var(--accent-border);
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BUTTONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
/* Primary */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1b003f 0%, #6495ed 100%) !important;
    color: var(--text-primary) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.65rem 2rem !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.03em !important;
    transition: var(--transition) !important;
    box-shadow: 0 4px 20px rgba(100, 149, 237, 0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(100, 149, 237, 0.35) !important;
}

/* Secondary / default */
.stButton > button:not([kind="primary"]) {
    background: var(--accent-soft) !important;
    color: var(--text-accent) !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-body) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: var(--transition) !important;
    box-shadow: none !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(100, 149, 237, 0.22) !important;
    border-color: var(--accent-primary) !important;
    color: var(--text-primary) !important;
    transform: translateY(-1px) !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid rgba(100, 149, 237, 0.18) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 0.85rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: var(--transition) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-soft) !important;
    border-color: var(--accent-primary) !important;
    color: var(--text-primary) !important;
    transform: none !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   INPUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(18, 18, 58, 0.8) !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(100, 149, 237, 0.1) !important;
    outline: none !important;
}
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label {
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PROGRESS BAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #1b003f, #6495ed) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: rgba(100, 149, 237, 0.1) !important;
    border-radius: 100px !important;
    height: 6px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ALERTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid !important;
    font-family: var(--font-body) !important;
    font-size: 0.88rem !important;
}
.stSuccess > div {
    background: rgba(16, 185, 129, 0.08) !important;
    border-color: rgba(16, 185, 129, 0.35) !important;
    color: #6EE7B7 !important;
}
.stError > div {
    background: rgba(239, 68, 68, 0.08) !important;
    border-color: rgba(239, 68, 68, 0.35) !important;
    color: #FCA5A5 !important;
}
.stInfo > div {
    background: rgba(100, 149, 237, 0.08) !important;
    border-color: var(--accent-border) !important;
    color: #93C5FD !important;
}
.stWarning > div {
    background: rgba(245, 158, 11, 0.08) !important;
    border-color: rgba(245, 158, 11, 0.35) !important;
    color: #FCD34D !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   EXPANDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--accent-border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.88rem !important;
}
.streamlit-expanderContent {
    background: rgba(18, 18, 58, 0.5) !important;
    border: 1px solid var(--accent-border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TABS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--accent-border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    border: none !important;
    padding: 0.5rem 1.25rem !important;
    transition: var(--transition) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent-soft) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--accent-border) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DATAFRAME / TABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stDataFrame"] {
    border: 1px solid var(--accent-border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}
.dvn-scroller { background: var(--bg-card) !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SPINNER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stSpinner > div {
    border-top-color: var(--accent-primary) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DIVIDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
hr {
    border-color: var(--accent-border) !important;
    margin: 1.5rem 0 !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   REUSABLE UTILITY CLASSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/* Cards */
.card {
    background: var(--bg-card);
    border: 1px solid var(--accent-border);
    border-radius: var(--radius-lg);
    padding: 1.75rem;
    position: relative;
    overflow: hidden;
    transition: var(--transition);
}
.card:hover {
    border-color: rgba(100, 149, 237, 0.45);
    transform: translateY(-2px);
}
.card-accent-top::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-primary), transparent);
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--accent-soft);
    border: 1px solid var(--accent-border);
    border-radius: 100px;
    padding: 0.25rem 0.75rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    color: var(--text-accent) !important;
}

/* Section label */
.section-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-accent) !important;
    margin-bottom: 1rem;
    display: block;
}

/* Page header */
.page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--accent-border);
}
.page-header-icon {
    width: 48px; height: 48px;
    background: var(--accent-soft);
    border: 1px solid var(--accent-border);
    border-radius: var(--radius-md);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}
.page-header-title {
    font-family: var(--font-display);
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    line-height: 1.1;
}
.page-header-sub {
    font-size: 0.83rem;
    color: var(--text-muted) !important;
    margin-top: 0.2rem;
}

/* Stat card */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--accent-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    transition: var(--transition);
}
.stat-card:hover {
    border-color: rgba(100, 149, 237, 0.5);
    transform: translateY(-3px);
}
.stat-val {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-primary) !important;
    display: block;
    line-height: 1;
    margin-bottom: 0.35rem;
}
.stat-lbl {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-top: 1px solid var(--accent-border);
    margin-top: 4rem;
}
.footer p {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-muted) !important;
    letter-spacing: 0.04em;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ANIMATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes pulse-border {
    0%, 100% { border-color: var(--accent-border); }
    50%       { border-color: var(--accent-primary); }
}
.animate-fade-up  { animation: fadeUp 0.4s ease-out both; }
.animate-fade-in  { animation: fadeIn 0.3s ease-out both; }
.animate-pulse-border { animation: pulse-border 2s ease-in-out infinite; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HERO SECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.hero-eyebrow {
    display: inline-block;
    background: rgba(100,149,237,0.1);
    border: 1px solid rgba(100,149,237,0.3);
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6495ed !important;
    margin-bottom: 0.5rem;
}

/* ── st.metric override ── */
[data-testid="stMetric"] {
    background: rgba(18,18,58,0.7) !important;
    border: 1px solid rgba(100,149,237,0.2) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: var(--accent-primary) !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MOBILE RESPONSIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 4rem; }
    .page-header-title { font-size: 1.3rem; }
    .stat-val { font-size: 1.5rem; }
    .stats-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .feature-grid { grid-template-columns: 1fr !important; }
    .cat-grid { grid-template-columns: 1fr !important; }
    .routing-meta { flex-direction: column; gap: 0.5rem; }
}
@media (max-width: 480px) {
    .block-container { padding: 0.75rem 0.75rem 3rem; }
    .stats-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 0.6rem !important; }
}
</style>
""", unsafe_allow_html=True)