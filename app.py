"""
AI Email Triage System - Professional Multi-Page App
Automated Classification System for School Registry
Using MobileBERT Model

Run with: streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import re
import time
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="AI Email Triage System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Professional Dark Theme CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: #191970;
    background-image:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(100, 149, 237, 0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 90% 100%, rgba(27, 0, 63, 0.7) 0%, transparent 60%),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 79px,
            rgba(100, 149, 237, 0.03) 79px,
            rgba(100, 149, 237, 0.03) 80px
        ),
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 79px,
            rgba(100, 149, 237, 0.03) 79px,
            rgba(100, 149, 237, 0.03) 80px
        );
    font-family: 'DM Sans', sans-serif;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b003f 0%, #0d0028 100%);
    border-right: 1px solid rgba(100, 149, 237, 0.2);
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #9EB8F0 !important;
    border: 1px solid rgba(100, 149, 237, 0.25) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.2rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(100, 149, 237, 0.15) !important;
    border-color: #6495ed !important;
    color: #E6E6FA !important;
    transform: none !important;
}

/* ── Global Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: #E6E6FA !important;
}
p, li, span, label, div {
    font-family: 'DM Sans', sans-serif;
    color: #B8C4E8;
}

/* ── Sidebar labels ── */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #B8C4E8 !important;
}

/* ── Hero Section ── */
.hero-wrap {
    padding: 4rem 3rem 3.5rem;
    background: linear-gradient(135deg, rgba(27,0,63,0.9) 0%, rgba(25,25,112,0.8) 100%);
    border: 1px solid rgba(100,149,237,0.25);
    border-radius: 20px;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 60% 80% at 80% 20%, rgba(100,149,237,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-block;
    background: rgba(100,149,237,0.15);
    border: 1px solid rgba(100,149,237,0.35);
    color: #e6e6fa !important;
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3.2rem, 4vw, 4.6rem);
    font-weight: 900;
    color: #ffffff !important;
    line-height: 1.2;
    line-spacing: 0.02em;
    margin-bottom: 1rem;
}
.hero-title span {
    color: #e6e6fa !important;
}
.hero-sub {
    font-size: 1.05rem;
    color: #8EA8D8 !important;
    max-width: 520px;
    line-height: 1.7;
}
.hero-badge-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 2rem;
}
.hero-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(100,149,237,0.1);
    border: 1px solid rgba(100,149,237,0.2);
    border-radius: 8px;
    padding: 0.45rem 0.85rem;
    font-size: 0.82rem;
    color: #9EB8F0 !important;
    font-weight: 500;
}
.hero-badge strong { color: #E6E6FA !important; font-weight: 700; }

/* ── Section Headers ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #6495ed !important;
    margin-bottom: 1.2rem;
}

/* ── Stat Cards ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2.5rem;
}
.stat-card {
    background: linear-gradient(135deg, rgba(27,0,63,0.7) 0%, rgba(25,25,112,0.5) 100%);
    border: 1px solid rgba(100,149,237,0.2);
    border-radius: 14px;
    padding: 1.5rem 1.25rem;
    text-align: center;
    transition: border-color 0.25s, transform 0.25s;
}
.stat-card:hover {
    border-color: rgba(100,149,237,0.5);
    transform: translateY(-3px);
}
.stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #6495ed !important;
    display: block;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.stat-lbl {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7A92C0 !important;
}

/* ── Feature Cards ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-bottom: 2.5rem;
}
.feat-card {
    background: linear-gradient(145deg, rgba(27,0,63,0.6) 0%, rgba(25,25,112,0.4) 100%);
    border: 1px solid rgba(100,149,237,0.18);
    border-radius: 16px;
    padding: 1.75rem 1.5rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.feat-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6495ed, #1b003f);
    opacity: 0;
    transition: opacity 0.25s;
}
.feat-card:hover { border-color: rgba(100,149,237,0.45); transform: translateY(-4px); }
.feat-card:hover::after { opacity: 1; }
.feat-icon {
    width: 44px; height: 44px;
    background: rgba(100,149,237,0.12);
    border: 1px solid rgba(100,149,237,0.25);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 1rem;
}
.feat-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #E6E6FA !important;
    margin-bottom: 0.5rem;
}
.feat-desc { font-size: 0.85rem; color: #8EA8D8 !important; line-height: 1.6; }

/* ── Category Cards ── */
.cat-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
    margin-bottom: 2rem;
}
.cat-item {
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    background: rgba(27,0,63,0.45);
    border: 1px solid rgba(100,149,237,0.15);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    transition: border-color 0.2s;
}
.cat-item:hover { border-color: rgba(100,149,237,0.4); }
.cat-emoji { font-size: 1.2rem; flex-shrink: 0; margin-top: 0.1rem; }
.cat-name { font-family: 'Syne', sans-serif; font-size: 0.88rem; font-weight: 700; color: #CDD6F4 !important; }
.cat-desc { font-size: 0.78rem; color: #7A92C0 !important; margin-top: 0.15rem; }

/* ── CTA Banner ── */
.cta-banner {
    background: linear-gradient(135deg, #1b003f 0%, rgba(100,149,237,0.15) 100%);
    border: 1px solid rgba(100,149,237,0.3);
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.cta-title { font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; color:#E6E6FA !important; margin-bottom:0.5rem; }
.cta-sub { font-size:0.9rem; color:#8EA8D8 !important; }

/* ── Page Classify Header ── */
.page-hdr {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid rgba(100,149,237,0.18);
}
.page-hdr-icon {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #1b003f, #6495ed22);
    border: 1px solid rgba(100,149,237,0.35);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
}
.page-hdr-title { font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:800; color:#E6E6FA !important; }
.page-hdr-sub { font-size:0.85rem; color:#7A92C0 !important; margin-top:0.1rem; }

/* ── Input Panel ── */
.input-panel {
    background: linear-gradient(145deg, rgba(27,0,63,0.55), rgba(25,25,112,0.35));
    border: 1px solid rgba(100,149,237,0.2);
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
}

/* ── Streamlit Input Overrides ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(27,0,63,0.7) !important;
    border: 1px solid rgba(100,149,237,0.3) !important;
    border-radius: 10px !important;
    color: #E6E6FA !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6495ed !important;
    box-shadow: 0 0 0 3px rgba(100,149,237,0.12) !important;
    outline: none !important;
}
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label {
    color: #9EB8F0 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

/* ── Primary Button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1b003f 0%, #6495ed 100%) !important;
    color: #E6E6FA !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    transition: opacity 0.2s, transform 0.2s !important;
    box-shadow: 0 4px 20px rgba(100,149,237,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-2px) !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: rgba(100,149,237,0.08) !important;
    color: #9EB8F0 !important;
    border: 1px solid rgba(100,149,237,0.3) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
    text-transform: none !important;
}
.stButton > button:not([kind]):hover {
    background: rgba(100,149,237,0.16) !important;
    border-color: rgba(100,149,237,0.6) !important;
    color: #E6E6FA !important;
    transform: translateY(-1px) !important;
}

/* ── Result Card ── */
.result-card {
    background: linear-gradient(145deg, rgba(27,0,63,0.8) 0%, rgba(25,25,112,0.5) 100%);
    border: 1px solid rgba(100,149,237,0.3);
    border-radius: 18px;
    padding: 2.25rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    animation: slideUp 0.4s ease-out;
}
.result-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 50% 60% at 90% 0%, rgba(100,149,237,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.result-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(100,149,237,0.12);
    border: 1px solid rgba(100,149,237,0.3);
    border-radius: 8px;
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6495ed !important;
    margin-bottom: 1rem;
}
.result-category {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #E6E6FA !important;
    margin-bottom: 0.35rem;
    line-height: 1.15;
}
.result-meta { font-size: 0.85rem; color: #7A92C0 !important; margin-bottom: 1.75rem; }

/* Confidence bar */
.conf-wrap { margin: 1.25rem 0; }
.conf-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 0.5rem;
}
.conf-label { font-size: 0.8rem; font-weight: 600; color: #9EB8F0 !important; letter-spacing: 0.05em; text-transform: uppercase; }
.conf-value { font-family:'Syne',sans-serif; font-size:1.35rem; font-weight:800; }
.conf-track {
    height: 8px;
    background: rgba(100,149,237,0.1);
    border-radius: 100px;
    overflow: hidden;
}
.conf-fill {
    height: 100%;
    border-radius: 100px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}
.conf-status {
    font-size: 0.75rem;
    color: #7A92C0 !important;
    margin-top: 0.4rem;
    text-align: right;
}

/* ── Routing Card ── */
.routing-card {
    background: rgba(27,0,63,0.6);
    border: 1px solid rgba(100,149,237,0.25);
    border-left: 3px solid #6495ed;
    border-radius: 14px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
}
.routing-label { font-size:0.72rem; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:#6495ed !important; margin-bottom:0.6rem; }
.routing-dept { font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:700; color:#E6E6FA !important; margin-bottom:0.4rem; }
.routing-desc { font-size:0.88rem; color:#8EA8D8 !important; line-height:1.6; margin-bottom:1.1rem; }
.routing-meta {
    display: flex; gap: 1.5rem; flex-wrap: wrap;
    padding-top: 1rem;
    border-top: 1px solid rgba(100,149,237,0.15);
}
.routing-meta-item { font-size:0.78rem; color:#7A92C0 !important; }
.routing-meta-item strong { color:#9EB8F0 !important; }

/* ── Dividers ── */
hr, .stDivider { border-color: rgba(100,149,237,0.15) !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(27,0,63,0.5) !important;
    border: 1px solid rgba(100,149,237,0.2) !important;
    border-radius: 10px !important;
    color: #9EB8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.streamlit-expanderContent {
    background: rgba(25,25,112,0.25) !important;
    border: 1px solid rgba(100,149,237,0.15) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Alerts ── */
.stSuccess > div { background: rgba(16,185,129,0.1) !important; border-color: rgba(16,185,129,0.4) !important; color: #6EE7B7 !important; border-radius: 10px !important; }
.stError > div { background: rgba(239,68,68,0.1) !important; border-color: rgba(239,68,68,0.4) !important; color: #FCA5A5 !important; border-radius: 10px !important; }
.stInfo > div { background: rgba(100,149,237,0.1) !important; border-color: rgba(100,149,237,0.3) !important; color: #93C5FD !important; border-radius: 10px !important; }
.stWarning > div { background: rgba(245,158,11,0.1) !important; border-color: rgba(245,158,11,0.3) !important; color: #FCD34D !important; border-radius: 10px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6495ed !important; }

/* ── Footer ── */
.footer-bar {
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid rgba(100,149,237,0.15);
    margin-top: 3rem;
}
.footer-bar p { font-size: 0.78rem; color: #556080 !important; }

/* ── Animations ── */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)


# ─── Model Loading ────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    """Load MobileBERT model"""
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    with open('preprocessed_data/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    num_labels = len(label_encoder.classes_)

    model = AutoModelForSequenceClassification.from_pretrained(
        'models/mobilebert',
        num_labels=num_labels,
        ignore_mismatched_sizes=True
    )
    tokenizer = AutoTokenizer.from_pretrained('models/mobilebert')

    model.to(device)
    model.eval()

    return {
        'label_encoder': label_encoder,
        'model': model,
        'tokenizer': tokenizer,
        'device': device
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────
def clean_text(text):
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_email(text, models):
    import torch
    cleaned = clean_text(text)
    enc = models['tokenizer'](
        cleaned,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_token_type_ids=True,
        return_tensors='pt'
    )
    input_ids       = enc['input_ids'].to(models['device'])
    attention_mask  = enc['attention_mask'].to(models['device'])
    token_type_ids  = enc['token_type_ids'].to(models['device'])

    with torch.no_grad():
        outputs = models['model'](
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        probs       = torch.softmax(outputs.logits, dim=1)
        pred        = torch.argmax(probs, dim=1).item()
        confidence  = probs[0][pred].item()
        all_probs   = probs[0].cpu().numpy()

    label = models['label_encoder'].inverse_transform([pred])[0]
    return {
        'category':      label,
        'confidence':    confidence,
        'probabilities': all_probs,
        'class_id':      pred
    }


def get_department_routing(category):
    routing = {
        'Admission Inquiry':    {'dept': 'Admissions Office',        'desc': 'Handles all admission-related inquiries, applications, and requirements.', 'icon': '🎓'},
        'Fees & Payment':       {'dept': 'Bursary Department',        'desc': 'Manages tuition fees, payment plans, and financial transactions.',          'icon': '💰'},
        'Course Registration':  {'dept': 'Academic Affairs Office',   'desc': 'Oversees course enrollment, scheduling, and academic programs.',            'icon': '📚'},
        'Result / Grade Issues':{'dept': 'Examination Unit',          'desc': 'Addresses grade concerns, result queries, and academic records.',            'icon': '📊'},
        'Hostel / Accommodation':{'dept': 'Student Affairs Office',   'desc': 'Manages student housing, hostel allocation, and accommodation services.',    'icon': '🏠'},
        'Meeting Requests':     {'dept': 'Administrative Office',     'desc': 'Schedules meetings, appointments, and administrative consultations.',        'icon': '📅'},
        'Transcript Requests':  {'dept': 'Records Office',            'desc': 'Processes transcript requests, certificates, and official documents.',       'icon': '📄'},
        'Complaints':           {'dept': 'Complaints & Support Desk', 'desc': 'Handles grievances, complaints, and student or staff concerns.',             'icon': '⚠️'},
        'General Inquiry':      {'dept': 'Information Center',        'desc': 'Provides general information and directs queries to the right department.',  'icon': '❓'},
        'Staff Matters':        {'dept': 'Human Resources',           'desc': 'Manages staff employment, contracts, and HR-related matters.',               'icon': '👥'},
    }
    return routing.get(category, {'dept': 'Registry', 'desc': 'General registry services.', 'icon': '📧'})


# ─── Pages ────────────────────────────────────────────────────────────────────
def landing_page():
    # Hero
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-eyebrow"> &nbsp;AI-Powered Classification System</div>
        <h1 class="hero-title">EMAIL TRIAGE<br><span>FOR SCHOOL REGISTRY</span></h1>
        <p class="hero-sub">
            Automatically classify and route incoming emails with
            MobileBERT — a compact yet powerful transformer model
            trained specifically for academic registry workflows.
        </p>
        <div class="hero-badge-row">
            <div class="hero-badge"><strong>92.54%</strong> Test Accuracy</div>
            <div class="hero-badge"><strong>&lt; 50 ms</strong> Inference</div>
            <div class="hero-badge"><strong>10</strong> Categories</div>
            <div class="hero-badge"><strong>MobileBERT</strong> Architecture</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    st.markdown("""
    <div class="stats-row">
        <div class="stat-card">
            <span class="stat-val">92.54%</span>
            <span class="stat-lbl">Accuracy</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">89.29%</span>
            <span class="stat-lbl">Avg Confidence</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">&lt;50 ms</span>
            <span class="stat-lbl">Processing Speed</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">10</span>
            <span class="stat-lbl">Categories</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Features
    st.markdown('<p class="section-label">Why it works</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feat-card">
            <div class="feat-icon">⚡</div>
            <div class="feat-title">Lightning Fast</div>
            <div class="feat-desc">Under 50 ms inference via GPU-accelerated MobileBERT — email responses routed before staff read the subject line.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">🎯</div>
            <div class="feat-title">High Accuracy</div>
            <div class="feat-desc">92.54% classification accuracy with a 89% average confidence score across all 10 academic categories.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">🔄</div>
            <div class="feat-title">Smart Routing</div>
            <div class="feat-desc">Automatically maps each email to the correct department, reducing manual triage time and human error.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Categories
    st.markdown('<p class="section-label">Supported Categories</p>', unsafe_allow_html=True)
    categories_info = [
        ("🎓", "Admission Inquiry",      "Applications, requirements, deadlines"),
        ("💰", "Fees & Payment",          "Tuition payments, financial aid"),
        ("📚", "Course Registration",     "Enrollment, course selection"),
        ("📊", "Result / Grade Issues",   "Grade queries, result verification"),
        ("🏠", "Hostel / Accommodation",  "Housing requests, hostel allocation"),
        ("📅", "Meeting Requests",        "Appointments, consultations"),
        ("📄", "Transcript Requests",     "Official documents, certificates"),
        ("⚠️", "Complaints",              "Grievances, service issues"),
        ("❓", "General Inquiry",         "Information requests"),
        ("👥", "Staff Matters",           "Employment, HR-related issues"),
    ]
    items_html = ""
    for emoji, name, desc in categories_info:
        items_html += f"""
        <div class="cat-item">
            <span class="cat-emoji">{emoji}</span>
            <div>
                <div class="cat-name">{name}</div>
                <div class="cat-desc">{desc}</div>
            </div>
        </div>"""
    st.markdown(f'<div class="cat-grid">{items_html}</div>', unsafe_allow_html=True)

    # CTA
    st.markdown("""
    <div class="cta-banner">
        <div class="cta-title">Ready to classify your emails?</div>
        <div class="cta-sub">Paste any email and get an instant AI-powered classification with department routing.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Open Classifier →", type="primary", use_container_width=True):
            st.session_state.page = "classify"
            st.rerun()


def classification_page(models):
    # Header
    st.markdown("""
    <div class="page-hdr">
        <div class="page-hdr-icon">📧</div>
        <div>
            <div class="page-hdr-title">Email Classifier</div>
            <div class="page-hdr-sub">Paste an email below and the AI will classify it in real-time</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sample_emails = {
        "— Select a sample email —": {"subject": "", "body": ""},
        "🎓 Admission Inquiry": {
            "subject": "Application for Computer Science Program",
            "body": "Hello, I would like to know the admission requirements for the Computer Science program. What are the deadlines for the next semester? I have completed my A-levels and would like to apply. Thank you."
        },
        "💰 Fees Payment Issue": {
            "subject": "Payment Not Reflecting",
            "body": "I need urgent help with my school fees payment. I made a payment yesterday through the online portal but it's not reflecting in my account. My student ID is 2024001. Please assist as soon as possible."
        },
        "📊 Grade Issue": {
            "subject": "Error in Semester Results",
            "body": "There seems to be an error in my semester results. My grade for Mathematics doesn't match what I expected based on my continuous assessment scores. Can you please review this? My registration number is ENG/2023/456."
        },
        "🏠 Hostel Accommodation": {
            "subject": "Hostel Allocation Request",
            "body": "I would like to request accommodation in the school hostel for next semester. What is the application process and what documents do I need to submit? Also, what are the accommodation fees?"
        },
        "📄 Transcript Request": {
            "subject": "Urgent Transcript Request",
            "body": "I need my official transcript for a job application. The deadline is in two weeks. How long does it take to process and what are the fees? Please let me know the fastest way to get this done."
        }
    }

    selected = st.selectbox(
        "Quick-test with a sample",
        options=list(sample_emails.keys()),
        help="Select a pre-written email to test the classifier"
    )

    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        email_subject = st.text_input(
            "Subject Line",
            value=sample_emails[selected]["subject"] if selected != "— Select a sample email —" else "",
            placeholder="Enter email subject…"
        )
    with col2:
        email_body = st.text_area(
            "Email Body",
            value=sample_emails[selected]["body"] if selected != "— Select a sample email —" else "",
            height=180,
            placeholder="Paste or type the email content here…"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        run = st.button("Classify →", type="primary", use_container_width=True)

    if run:
        if not email_subject.strip() and not email_body.strip():
            st.error("Please enter a subject or email body before classifying.")
            return

        full_email = f"{email_subject} {email_body}".strip()

        with st.spinner("Analysing with MobileBERT…"):
            t0 = time.time()
            result = predict_email(full_email, models)
            elapsed = time.time() - t0

        routing     = get_department_routing(result['category'])
        conf        = result['confidence'] * 100
        elapsed_ms  = f"{elapsed * 1000:.0f}"
        timestamp   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if conf >= 80:
            conf_color, conf_status = "#6495ed", "High Confidence"
        elif conf >= 60:
            conf_color, conf_status = "#F59E0B", "Medium Confidence"
        else:
            conf_color, conf_status = "#EF4444", "Low Confidence — review manually"

        # Result card — split into separate markdown calls to avoid Streamlit
        # sanitising inline style attributes that contain dynamic Python values.
        st.markdown(f"""
        <div class="result-card">
            <div class="result-badge">✦ Classification Result</div>
            <div class="result-category">{routing['icon']} {result['category']}</div>
            <div class="result-meta">Classified and ready for automatic routing</div>
        </div>
        """, unsafe_allow_html=True)

        # Confidence — rendered with native Streamlit widgets so values always display
        conf_col1, conf_col2 = st.columns([3, 1])
        with conf_col1:
            st.markdown(
                f'<p style="font-size:0.75rem;font-weight:700;letter-spacing:0.1em;'
                f'text-transform:uppercase;color:#9EB8F0;margin-bottom:0.4rem;">'
                f'Confidence Score</p>',
                unsafe_allow_html=True
            )
            st.progress(int(conf))
            st.markdown(
                f'<p style="font-size:0.75rem;color:#7A92C0;margin-top:0.2rem;">'
                f'{conf_status}</p>',
                unsafe_allow_html=True
            )
        with conf_col2:
            st.markdown(
                f'<p style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;'
                f'color:{conf_color};text-align:right;margin-top:1.4rem;">'
                f'{conf:.1f}%</p>',
                unsafe_allow_html=True
            )

        # Routing card
        st.markdown(f"""
        <div class="routing-card">
            <div class="routing-label">Automatic Routing</div>
            <div class="routing-dept">{routing['icon']} {routing['dept']}</div>
            <div class="routing-desc">{routing['desc']}</div>
            <div class="routing-meta">
                <span class="routing-meta-item">⚡ <strong>Processing:</strong> {elapsed_ms} ms</span>
                <span class="routing-meta-item">🤖 <strong>Model:</strong> MobileBERT (25M params)</span>
                <span class="routing-meta-item">📅 <strong>Timestamp:</strong> {timestamp}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Probability chart
        with st.expander("📊 Full Probability Distribution"):
            prob_data = [
                {'Category': cat, 'Probability': float(result['probabilities'][i])}
                for i, cat in enumerate(models['label_encoder'].classes_)
            ]
            prob_df = pd.DataFrame(prob_data).sort_values('Probability', ascending=True)

            import plotly.graph_objects as go
            colors = ['rgba(100,149,237,0.35)'] * len(prob_df)
            colors[-1] = '#6495ed'  # highlight top

            fig = go.Figure(go.Bar(
                y=prob_df['Category'],
                x=prob_df['Probability'],
                orientation='h',
                marker=dict(color=colors, line=dict(color='rgba(100,149,237,0.6)', width=1)),
                text=[f"{v*100:.1f}%" for v in prob_df['Probability']],
                textposition='outside',
                textfont=dict(color='#9EB8F0', size=11),
            ))
            fig.update_layout(
                plot_bgcolor='rgba(27,0,63,0.0)',
                paper_bgcolor='rgba(27,0,63,0.0)',
                font=dict(color='#9EB8F0', family='DM Sans'),
                height=420,
                margin=dict(l=10, r=60, t=20, b=20),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(100,149,237,0.08)',
                    tickformat='.0%',
                    color='#556080',
                    range=[0, max(prob_df['Probability']) * 1.25]
                ),
                yaxis=dict(color='#9EB8F0', tickfont=dict(size=12)),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Action row
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅  Approve & Route", use_container_width=True):
                st.success(f"Email routed to the {routing['dept']}.")
        with c2:
            if st.button("↩  Classify Another", use_container_width=True):
                st.info("Clear the fields above and enter a new email.")
        with c3:
            if st.button("📋  Copy Result", use_container_width=True):
                st.info(f"Category: {result['category']} — Confidence: {conf:.1f}%")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "landing"

    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        if st.button("🏠  Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
        if st.button("📧  Classify Emails", use_container_width=True):
            st.session_state.page = "classify"
            st.rerun()

        st.markdown("---")
        st.markdown("**System Status**")
        st.success("🟢  Online")

        if st.session_state.page == "classify":
            with st.spinner("Loading model…"):
                models = load_models()
            st.markdown("---")
            st.markdown("**Model**")
            st.info(f"""
MobileBERT

Parameters: 25 M  
Accuracy: 92.54%  
Device: `{models['device']}`
""")

    # Route
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "classify":
        models = load_models()
        classification_page(models)

    # Footer
    st.markdown("""
    <div class="footer-bar">
        <p>AI Email Triage System &nbsp;·&nbsp; MobileBERT &nbsp;·&nbsp; Academic Research Project &nbsp;·&nbsp; 92.54% Test Accuracy</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()