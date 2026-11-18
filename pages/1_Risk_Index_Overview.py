import streamlit as st
import pandas as pd
from pathlib import Path

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
    fig.add_hline(
        y=75,
        line_dash="dash",
        line_color="#ef4444",
        line_width=2,
        annotation_text="Alert Threshold (75)",
        annotation_position="top left",
        annotation_font_color="#ef4444"
    )
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

comparison_fig.add_hline(
    y=75,
    line_dash="dash",
    line_color="#ef4444",
    line_width=2,
    annotation_text="Alert Threshold (75)",
    annotation_position="top left",
    annotation_font_color="#ef4444"
)

st.plotly_chart(
    comparison_fig,
    width="stretch"
)

# ============================================================
# KNOWN SHOCK ANALYSIS
# ============================================================

st.markdown(
    '<div class="sub-header">Known Shock Analysis</div>',
    unsafe_allow_html=True
)

st.caption(
    "Evaluate how each risk index responded to major geopolitical "
    "events by comparing the average risk level during the six months "
    "before an event with the maximum risk level during the six months after."
    "The alert threshold is 75: a risk index value of 75 or higher "
    "is considered an alert."
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SHOCK_FILES = {
    "Overall": PROJECT_ROOT / "cleaned_datasets" / "overall" / "check_shocks.csv",
    "Russia": PROJECT_ROOT / "cleaned_datasets" / "russia" / "check_shocks.csv",
    "China": PROJECT_ROOT / "cleaned_datasets" / "china" / "check_shocks.csv"
}

for index_type, file_path in SHOCK_FILES.items():

    st.markdown(f"**{index_type} Risk Index**")

    if not file_path.exists():
        st.warning(f"Shock analysis file not found: {file_path.name}")
        continue

    shock_df = pd.read_csv(file_path)

    # Keep only the equal-weighted risk index.
    shock_df = shock_df[
        shock_df["series"] == "index_equal"
    ].copy()

    if shock_df.empty:
        st.info(f"No equal-weighted index shock results available for {index_type}.")
        continue

    # Remove the series column since every row represents index_equal.
    shock_df = shock_df.drop(columns=["series"])

    # Rename columns for readability.
    shock_df = shock_df.rename(columns={
        "event": "Geopolitical Event",
        "avg_6m_before": "Average Risk (6M Before)",
        "max_6m_after": "Maximum Risk (6M After)",
        "rise": "Risk Increase",
        "first_month_at_or_above_alert": "First Alert Month (75+)"
    })

    # Format numerical columns.
    numeric_columns = [
        "Average Risk (6M Before)",
        "Maximum Risk (6M After)",
        "Risk Increase"
    ]

    shock_df[numeric_columns] = shock_df[numeric_columns].round(1)

    st.dataframe(
        shock_df,
        hide_index=True,
        width="stretch"
    )

    st.markdown("")