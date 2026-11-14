import streamlit as st

from utils.data_loader import load_data
from utils.charts import create_risk_index_chart
from utils.styling import apply_custom_styles
from utils.config import FORECAST_END, FORECAST_START, RISK_INDEX_COLUMNS
from utils.helpers import create_download_button, format_value, get_latest_actual

apply_custom_styles()

df, err = load_data()

if df is None:
    st.stop()

# ============================================================
# PAGE 2: INDIVIDUAL RISK INDEX ANALYSIS
# ============================================================

st.markdown(
    '<div class="main-header">Individual Risk Index Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="description">'
    'Examine historical performance and future forecasts '
    'for each individual risk index.'
    '</div>',
    unsafe_allow_html=True
)

index_type = st.selectbox(
    "Select Risk Index",
    list(RISK_INDEX_COLUMNS.keys())
)

show_predictions = st.checkbox(
    "Show historical model predictions",
    value=True,
    key="individual_predictions"
)

latest_value, latest_month = get_latest_actual(
    df,
    index_type
)

actual_col = RISK_INDEX_COLUMNS[index_type]["actual"]

future = df[
    (df["Month"] >= FORECAST_START) &
    (df["Month"] <= FORECAST_END)
].dropna(subset=[actual_col])

latest_forecast = (
    future.iloc[-1][actual_col]
    if not future.empty
    else None
)

forecast_change = (
    latest_forecast - latest_value
    if latest_forecast is not None and latest_value is not None
    else None
)

# Metrics.
col1, col2, col3 = st.columns(3)

col1.metric(
    "Latest Observed Risk",
    format_value(latest_value),
    latest_month.strftime("%b %Y") if latest_month is not None else None
)

col2.metric(
    "Latest Forecast",
    format_value(latest_forecast),
    future.iloc[-1]["Month"].strftime("%b %Y")
    if not future.empty else None
)

col3.metric(
    "Forecast Change",
    format_value(forecast_change),
    delta=(
        f"{forecast_change:+.2f}"
        if forecast_change is not None else None
    )
)

st.markdown('<div class="section-divider"></div>',
            unsafe_allow_html=True)

# Chart.
fig = create_risk_index_chart(
    df,
    index_type,
    show_predictions=show_predictions
)

if fig:
    st.plotly_chart(fig, width="stretch")
else:
    st.warning(f"No data available for {index_type}.")

# Forecast table.
st.markdown(
    '<div class="sub-header">Forecast Details</div>',
    unsafe_allow_html=True
)

if not future.empty:

    forecast_table = future[["Month", actual_col]].copy()

    forecast_table.columns = [
        "Month",
        "Forecasted Risk Index"
    ]

    forecast_table["Month"] = (
        forecast_table["Month"].dt.strftime("%B %Y")
    )

    forecast_table["Forecasted Risk Index"] = (
        forecast_table["Forecasted Risk Index"].round(2)
    )

    st.dataframe(
        forecast_table,
        width="stretch",
        hide_index=True
    )

    create_download_button(
        forecast_table,
        f"{index_type.lower()}_risk_forecast.csv"
    )

else:
    st.info("No forecast observations are available.")
