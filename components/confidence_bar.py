import pathfix  # noqa
import streamlit as st
from models.validator import get_confidence_level
from config.constants import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


def render_confidence_block(confidence: float):
    info = get_confidence_level(confidence)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption("CONFIDENCE SCORE")
        st.progress(int(info['pct']))
        st.caption(f"{info['icon']} {info['label']}")
    with col2:
        st.metric("", f"{info['pct']:.1f}%")


def render_confidence_pill(confidence: float):
    pct  = confidence if confidence > 1 else confidence * 100
    info = get_confidence_level(pct / 100)
    st.caption(f"{info['icon']} {pct:.1f}% · {info['label']}")


def render_confidence_meter(confidence: float, show_label: bool = True):
    info = get_confidence_level(confidence)
    if show_label:
        st.caption("CONFIDENCE")
    st.progress(int(info['pct']))
    st.caption(f"{info['icon']} {info['label']} · {info['pct']:.1f}%")


def render_avg_confidence_card(avg_confidence: float):
    st.metric("Avg Confidence", f"{avg_confidence:.1f}%")


def render_threshold_legend():
    st.caption(
        f"Thresholds: 🟢 High ≥ {CONFIDENCE_HIGH}% · "
        f"🟡 Medium ≥ {CONFIDENCE_MEDIUM}% · "
        f"🔴 Low < {CONFIDENCE_MEDIUM}%"
    )