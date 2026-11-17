import streamlit as st
from pathlib import Path
import pandas as pd

from utils.data_loader import load_data
from utils.charts import create_risk_index_chart
from utils.styling import apply_custom_styles
from utils.config import FORECAST_END, FORECAST_START, RISK_INDEX_COLUMNS
from utils.helpers import create_download_button, format_value, get_latest_actual

# ============================================================
# RISK INDEX COMPONENTS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

COMPONENT_FILES = {
    "Overall": PROJECT_ROOT / "cleaned_datasets" / "risk_index_monthly.csv",
    "Russia": PROJECT_ROOT / "cleaned_datasets" / "russia_risk_index_monthly.csv",
    "China": PROJECT_ROOT / "cleaned_datasets" / "china_risk_index_monthly.csv"
}

COMPONENT_COLUMNS = {
    "comp_dependency": "Dependency",
    "comp_transportation": "Transportation",
    "comp_economic": "Economic",
    "comp_geopolitical": "Geopolitical",
    "comp_sanctions": "Sanctions"
}

COMPONENT_COLORS = {
    "comp_dependency": "#2563eb",
    "comp_transportation": "#f59e0b",
    "comp_economic": "#16a34a",
    "comp_geopolitical": "#9333ea",
    "comp_sanctions": "#dc2626"
}


@st.cache_data
def load_component_data(file_path):
    component_df = pd.read_csv(file_path)

    component_df["Month"] = pd.to_datetime(
        component_df["Month"],
        errors="coerce"
    )

    component_df = (
        component_df
        .dropna(subset=["Month"])
        .sort_values("Month")
    )

    for column in COMPONENT_COLUMNS:
        if column in component_df.columns:
            component_df[column] = pd.to_numeric(
                component_df[column],
                errors="coerce"
            )

    return component_df

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

show_components = st.checkbox(
    "Show risk index components",
    value=False,
    key="individual_components"
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

# ============================================================
# CHART
# ============================================================

fig = create_risk_index_chart(
    df,
    index_type,
    show_predictions=show_predictions
)

if fig:

    # Save the original chart timeframe before adding components.
    original_dates = []

    for trace in fig.data:
        if trace.x is not None:
            original_dates.extend(list(trace.x))

    original_dates = pd.to_datetime(
        pd.Series(original_dates),
        errors="coerce"
    ).dropna()

    original_x_range = (
        [original_dates.min(), original_dates.max()]
        if not original_dates.empty
        else None
    )

    # Add risk index components if selected.
    if show_components:

        component_path = COMPONENT_FILES[index_type]

        if component_path.exists():

            component_df = load_component_data(
                str(component_path)
            )

            available_components = [
                column
                for column in COMPONENT_COLUMNS
                if column in component_df.columns
            ]

            missing_components = [
                column
                for column in COMPONENT_COLUMNS
                if column not in component_df.columns
            ]

            if missing_components:
                st.warning(
                    "Some components are unavailable: "
                    + ", ".join(missing_components)
                )

            for column in available_components:

                fig.add_scatter(
                    x=component_df["Month"],
                    y=component_df[column],
                    mode="lines",
                    name=COMPONENT_COLUMNS[column],
                    line=dict(
                        color=COMPONENT_COLORS[column],
                        width=1.8
                    ),
                    opacity=0.3
                )

        else:
            st.warning(
                f"Component data file not found: {component_path}"
            )

    # Restore the original timeframe.
    if original_x_range is not None:
        fig.update_xaxes(
            range=original_x_range,
            autorange=False
        )

    # Position the legend above the plot.
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        margin=dict(t=100)
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

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
