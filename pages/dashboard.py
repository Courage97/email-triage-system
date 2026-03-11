import pathfix  # noqa
import streamlit as st
import plotly.graph_objects as go

from config.constants import CATEGORY_COLORS, MODEL_ACCURACY, MODEL_NAME
from utils.log_manager import load_log, get_log_summary
from utils.stats import (
    category_distribution, confidence_distribution, volume_over_time,
    priority_breakdown, top_categories, override_rate,
    avg_confidence_by_category, daily_summary,
)

PLOT_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#a8b4d0', family='Inter'),
    margin=dict(l=10, r=10, t=30, b=10),
)
AXIS_STYLE = dict(
    showgrid=True, gridcolor='rgba(100,149,237,0.07)',
    color='#5a6a8a', zeroline=False,
)


def render_dashboard():
    st.markdown("## 📊 Analytics Dashboard")
    st.caption("Live statistics, classification trends and model performance")

    entries = load_log()

    if not entries:
        st.info("📈 No data yet. Classify and approve some emails first.")
        if st.button("Go to Classifier →", type="primary", key="dash_goto_classify"):
            st.session_state.page = "classify"
            st.rerun()
        return

    summary = get_log_summary(entries)
    daily   = daily_summary(entries)

    _render_summary_stats(summary)
    st.divider()
    _render_today_strip(daily)
    st.divider()
    _render_charts_row1(entries)
    st.divider()
    _render_charts_row2(entries)
    st.divider()
    _render_model_performance(entries)


def _render_summary_stats(summary):
    st.caption("OVERALL SUMMARY")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Classified",  summary['total'])
    with c2: st.metric("Today",             summary['today'])
    with c3: st.metric("Urgent",            summary['urgent'])
    with c4: st.metric("Overrides",         summary['overridden'])
    with c5: st.metric("Avg Confidence",    f"{summary['avg_confidence']}%")


def _render_today_strip(daily):
    st.caption("TODAY AT A GLANCE")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Emails Today",    daily['count'])
    with c2: st.metric("Avg Confidence",  f"{daily['avg_confidence']}%")
    with c3: st.metric("Urgent Today",    daily['urgent_count'])
    with c4: st.metric("Overrides Today", daily['override_count'])


def _render_charts_row1(entries):
    st.caption("CLASSIFICATION OVERVIEW")
    col1, col2 = st.columns(2)
    with col1: _chart_category_pie(entries)
    with col2: _chart_volume_over_time(entries)


def _chart_category_pie(entries):
    df = category_distribution(entries)
    if df.empty:
        st.info("No category data yet.")
        return
    fig = go.Figure(go.Pie(
        labels=df['category'], values=df['count'],
        marker=dict(colors=df['color'].tolist(),
                    line=dict(color='rgba(10,10,26,0.8)', width=2)),
        textinfo='label+percent',
        textfont=dict(size=11, family='Inter', color='#E6E6FA'),
        hole=0.42,
    ))
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text='Category Distribution',
                   font=dict(size=14, family='Inter', color='#E6E6FA'), x=0),
        height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def _chart_volume_over_time(entries):
    c1, c2 = st.columns(2)
    with c1: period = st.selectbox("Period", ["daily","weekly","monthly"], key="dash_period")
    with c2: days   = st.selectbox("Lookback", [7,14,30,60,90], index=2, key="dash_days")

    df = volume_over_time(entries, period=period, last_n_days=days)
    if df.empty:
        st.info("Not enough data for this period.")
        return
    fig = go.Figure(go.Bar(
        x=df['period'], y=df['count'],
        marker=dict(color='rgba(100,149,237,0.7)',
                    line=dict(color='#6495ed', width=1)),
    ))
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text='Email Volume Over Time',
                   font=dict(size=14, family='Inter', color='#E6E6FA'), x=0),
        height=340,
        xaxis={**AXIS_STYLE, 'tickangle': -30},
        yaxis={**AXIS_STYLE, 'title': 'Count'})
    st.plotly_chart(fig, use_container_width=True)


def _render_charts_row2(entries):
    st.caption("CONFIDENCE & PRIORITY")
    col1, col2 = st.columns(2)
    with col1: _chart_confidence_distribution(entries)
    with col2: _chart_priority_breakdown(entries)


def _chart_confidence_distribution(entries):
    df = confidence_distribution(entries)
    fig = go.Figure(go.Bar(
        x=df['range'], y=df['count'],
        marker=dict(color=df['color'].tolist(),
                    line=dict(color='rgba(10,10,26,0.6)', width=1)),
        text=df['count'], textposition='outside',
        textfont=dict(color='#a8b4d0', size=11),
    ))
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text='Confidence Distribution',
                   font=dict(size=14, family='Inter', color='#E6E6FA'), x=0),
        height=340,
        xaxis={**AXIS_STYLE, 'title': 'Confidence Range'},
        yaxis={**AXIS_STYLE, 'title': 'Count'})
    st.plotly_chart(fig, use_container_width=True)


def _chart_priority_breakdown(entries):
    df = priority_breakdown(entries)
    if df.empty:
        st.info("No priority data yet.")
        return
    fig = go.Figure(go.Bar(
        y=df['label'], x=df['count'], orientation='h',
        marker=dict(color=df['color'].tolist(),
                    line=dict(color='rgba(10,10,26,0.5)', width=1)),
        text=df['count'], textposition='outside',
        textfont=dict(color='#a8b4d0', size=11),
    ))
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text='Priority Breakdown',
                   font=dict(size=14, family='Inter', color='#E6E6FA'), x=0),
        height=340,
        xaxis={**AXIS_STYLE, 'title': 'Count',
               'range': [0, df['count'].max() * 1.3]},
        yaxis={**AXIS_STYLE})
    st.plotly_chart(fig, use_container_width=True)


def _render_model_performance(entries):
    st.caption("MODEL PERFORMANCE")
    col1, col2 = st.columns(2)
    with col1: _chart_avg_confidence_by_category(entries)
    with col2:
        _render_override_stats(entries)
        _render_top_categories(entries)


def _chart_avg_confidence_by_category(entries):
    df = avg_confidence_by_category(entries)
    if df.empty:
        st.info("No data yet.")
        return
    fig = go.Figure(go.Bar(
        y=df['category'], x=df['avg_confidence'], orientation='h',
        marker=dict(color=df['color'].tolist(),
                    line=dict(color='rgba(10,10,26,0.5)', width=1)),
        text=[f"{v:.1f}%" for v in df['avg_confidence']],
        textposition='outside',
        textfont=dict(color='#a8b4d0', size=11),
    ))
    fig.update_layout(**PLOT_LAYOUT,
        title=dict(text='Avg Confidence by Category',
                   font=dict(size=14, family='Inter', color='#E6E6FA'), x=0),
        height=420,
        xaxis={**AXIS_STYLE, 'title': 'Avg Confidence (%)',
               'range': [0, df['avg_confidence'].max() * 1.25]},
        yaxis={**AXIS_STYLE, 'tickfont': dict(size=11)})
    st.plotly_chart(fig, use_container_width=True)


def _render_override_stats(entries):
    stats = override_rate(entries)
    st.caption("OVERRIDE & ACCURACY")
    c1, c2 = st.columns(2)
    with c1: st.metric("Implied Accuracy", f"{stats['accuracy_pct']}%")
    with c2: st.metric("Override Rate",    f"{stats['rate_pct']}%")
    st.info(
        f"**{stats['overridden']}** of **{stats['total']}** emails were manually corrected. "
        f"Implied accuracy: **{stats['accuracy_pct']}%** "
        f"(test accuracy: **{MODEL_ACCURACY}**)."
    )


def _render_top_categories(entries):
    top = top_categories(entries, n=5)
    if not top:
        return
    st.caption("TOP 5 CATEGORIES")
    for i, row in enumerate(top):
        st.markdown(f"**#{i+1}** {row['category']} — `{row['count']}` ({row['percentage']}%)")
        st.progress(int(row['percentage']))