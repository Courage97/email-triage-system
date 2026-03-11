import pathfix  # noqa
# components/result_card.py
# Reusable result card — 100% native Streamlit, zero inline HTML styles

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from config.constants import ROUTING_MAP, CATEGORY_COLORS
from models.validator import validate_result


def render_result_card(result: dict):
    validation = validate_result(result)
    conf_info  = validation['confidence_info']
    priority   = validation['priority']
    routing    = ROUTING_MAP.get(result['category'], {})
    icon       = routing.get('icon', '📧')

    # Alerts
    if validation['is_urgent']:
        st.error("🔴 URGENT PRIORITY — This email requires immediate attention")

    if validation['alert']:
        alert = validation['alert']
        if alert['type'] == 'warning':
            st.warning(alert['message'])
        else:
            st.error(alert['message'])

    # Result header
    st.markdown("---")
    st.markdown(f"### {icon} {result['category']}")
    st.caption("✦ Classification Result · Classified and ready for routing")
    st.markdown("---")

    # Confidence + Priority
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.caption("CONFIDENCE SCORE")
        st.progress(int(conf_info['pct']))
        st.caption(f"{conf_info['icon']} {conf_info['label']} · {conf_info['pct']:.1f}%")

    with col2:
        st.metric("Confidence", f"{conf_info['pct']:.1f}%")

    with col3:
        st.metric("Priority", f"{priority['badge']} {priority['label']}")


def render_probability_chart(result: dict):
    prob_data = [
        {'Category': label, 'Probability': float(result['probabilities'][i])}
        for i, label in enumerate(result['all_labels'])
    ]
    df = pd.DataFrame(prob_data).sort_values('Probability', ascending=True)

    colors = [
        CATEGORY_COLORS.get(cat, 'rgba(100,149,237,0.35)')
        if cat == result['category']
        else 'rgba(100,149,237,0.22)'
        for cat in df['Category']
    ]

    fig = go.Figure(go.Bar(
        y=df['Category'],
        x=df['Probability'],
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(100,149,237,0.3)', width=1)),
        text=[f"{v * 100:.1f}%" for v in df['Probability']],
        textposition='outside',
        textfont=dict(color='#a8b4d0', size=11, family='Inter'),
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a8b4d0', family='Inter'),
        height=400,
        margin=dict(l=10, r=70, t=10, b=10),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100,149,237,0.07)',
            tickformat='.0%',
            color='#5a6a8a',
            range=[0, df['Probability'].max() * 1.3],
            zeroline=False,
        ),
        yaxis=dict(color='#a8b4d0', tickfont=dict(size=11, family='Inter')),
    )

    with st.expander("📊 Full Probability Distribution"):
        st.plotly_chart(fig, use_container_width=True)