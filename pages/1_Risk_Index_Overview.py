import streamlit as st
from utils.data_loader import load_data
from utils.charts import create_risk_index_chart, create_comparison_chart, render_kpi_card
from utils.styling import apply_custom_styles
from utils.config import RISK_INDEX_COLUMNS
from utils.helpers import get_latest_actual, get_latest_forecast


apply_custom_styles()

df, err = load_data()

if df is None:
    st.stop()

# ============================================================
# PAGE 1: RISK INDEX OVERVIEW
# ============================================================

st.markdown(
    '<div class="main-header">'
    'China-Russia Supply Chain Risk Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="description">
        Monitor supply chain vulnerabilities, historical risk trends,
        and projected changes in China-Russia trade relationships.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="forecast-info">
        <strong>Forecast period:</strong>
        June 2026 – November 2026.
        Historical observations and future model forecasts
        are displayed separately.
    </div>
    """,
    unsafe_allow_html=True
)

# KPI cards.
st.markdown(
    '<div class="sub-header">Latest Observed Risk Indices (June 2026)</div>',
    unsafe_allow_html=True
)

cols = st.columns(3)

for col, (index_type, settings) in zip(
    cols,
    RISK_INDEX_COLUMNS.items()
):

    value, month = get_latest_actual(df, index_type)

    with col:
        render_kpi_card(
            index_type,
            value,
            month,
            settings["color"]
        )

# Latest forecast KPI cards.
st.markdown(
    '<div class="sub-header">Latest Forecasted Risk Indices (November 2026)</div>',
    unsafe_allow_html=True
)

forecast_cols = st.columns(3)

for col, (index_type, settings) in zip(
    forecast_cols,
    RISK_INDEX_COLUMNS.items()
):

    value, month = get_latest_forecast(df, index_type)

    with col:
        render_kpi_card(
            index_type,
            value,
            month,
            settings["color"]
        )

st.markdown('<div class="section-divider"></div>',
            unsafe_allow_html=True)

# Main chart.
st.markdown(
    '<div class="sub-header">Overall Supply Chain Risk</div>',
    unsafe_allow_html=True
)

show_predictions = st.checkbox(
    "Show historical model predictions",
    value=False,
    key="overview_predictions"
)

fig = create_risk_index_chart(
    df,
    "Overall",
    show_predictions=show_predictions
)

if fig:
    st.plotly_chart(fig, width="stretch")
else:
    st.warning("Overall risk index data is unavailable.")

st.caption(
    "The solid blue line represents historical observations. "
    "The teal line represents future forecasts. "
    "The orange dotted line represents historical model predictions."
)

st.markdown('<div class="section-divider"></div>',
            unsafe_allow_html=True)

# Comparison chart.
st.markdown(
    '<div class="sub-header">Risk Index Comparison</div>',
    unsafe_allow_html=True
)

comparison_predictions = st.checkbox(
    "Include historical model predictions in comparison",
    value=False,
    key="comparison_predictions"
)

comparison_fig = create_comparison_chart(
    df,
    show_predictions=comparison_predictions
)

st.plotly_chart(
    comparison_fig,
    width="stretch"
)