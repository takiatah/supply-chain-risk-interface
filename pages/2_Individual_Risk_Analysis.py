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
    "Overall": PROJECT_ROOT / "cleaned_datasets" / "overall" / "risk_index_monthly.csv",
    "Russia": PROJECT_ROOT / "cleaned_datasets" / "russia" / "risk_index_monthly.csv",
    "China": PROJECT_ROOT / "cleaned_datasets" / "china" / "risk_index_monthly.csv"
}

SHOCK_FILES = {
    "Overall": PROJECT_ROOT / "cleaned_datasets" / "overall" / "check_shocks.csv",
    "Russia": PROJECT_ROOT / "cleaned_datasets" / "russia" / "check_shocks.csv",
    "China": PROJECT_ROOT / "cleaned_datasets" / "china" / "check_shocks.csv"
}

SPIKE_FILES = {
    "Overall": PROJECT_ROOT / "cleaned_datasets" / "overall" / "risk_change_monthly.csv",
    "Russia": PROJECT_ROOT / "cleaned_datasets" / "russia" / "risk_change_monthly.csv",
    "China": PROJECT_ROOT / "cleaned_datasets" / "china" / "risk_change_monthly.csv"
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

    numeric_columns = list(COMPONENT_COLUMNS.keys()) + ["trend_12m"]

    for column in numeric_columns:
        if column in component_df.columns:
            component_df[column] = pd.to_numeric(
                component_df[column],
                errors="coerce"
            )

    return component_df

@st.cache_data
def load_shock_data(file_path):
    shock_df = pd.read_csv(file_path)

    # Keep only the equal-weighted risk index.
    shock_df = shock_df[
        shock_df["series"] == "index_equal"
    ].copy()

    shock_df = shock_df.drop(columns=["series"])

    shock_df = shock_df.rename(columns={
        "event": "Geopolitical Event",
        "avg_6m_before": "Average Risk (6M Before)",
        "max_6m_after": "Maximum Risk (6M After)",
        "rise": "Risk Increase",
        "first_month_at_or_above_alert": "First Alert Month (75+)"
    })

    numeric_columns = [
        "Average Risk (6M Before)",
        "Maximum Risk (6M After)",
        "Risk Increase"
    ]

    for column in numeric_columns:
        shock_df[column] = pd.to_numeric(
            shock_df[column],
            errors="coerce"
        ).round(1)

    return shock_df


@st.cache_data
def load_spike_data(file_path):
    spike_df = pd.read_csv(file_path)

    spike_df["Month"] = pd.to_datetime(
        spike_df["Month"],
        errors="coerce"
    )

    numeric_columns = [
        "index",
        "gap_vs_trend",
        "change_3m"
    ]

    for column in numeric_columns:
        if column in spike_df.columns:
            spike_df[column] = pd.to_numeric(
                spike_df[column],
                errors="coerce"
            )

    spike_df = (
        spike_df
        .dropna(subset=["Month"])
        .sort_values("Month")
        .reset_index(drop=True)
    )

    return spike_df


def create_spike_summary(spike_df):

    data = spike_df.copy()

    # Identify months classified as short-term spikes.
    data["is_spike"] = (
        data["short_term"]
        .astype(str)
        .str.lower()
        .eq("spike")
    )

    # Identify consecutive monthly spike episodes.
    month_number = (
        data["Month"].dt.year * 12
        + data["Month"].dt.month
    )

    consecutive_spike = (
        data["is_spike"].shift(fill_value=False)
        & month_number.diff().eq(1)
    )

    episode_start = (
        data["is_spike"] & ~consecutive_spike
    )

    data["spike_group"] = episode_start.cumsum()

    spikes = data[data["is_spike"]].copy()

    if spikes.empty:
        return pd.DataFrame()

    summaries = []

    for _, episode in spikes.groupby("spike_group"):

        # Find the month with the highest risk index.
        peak_row = episode.loc[episode["index"].idxmax()]

        # Extract the main driver from the peak month's description.
        description = str(peak_row.get("description", ""))

        driver_match = pd.Series([description]).str.extract(
            r"Main driver over 3 months:\s*([^(]+)"
        ).iloc[0, 0]

        main_driver = (
            driver_match.strip().title()
            if pd.notna(driver_match)
            else "Not identified"
        )

        summaries.append({
            "Spike Period": (
                episode["Month"].min().strftime("%b %Y")
                if episode["Month"].min() == episode["Month"].max()
                else (
                    f"{episode['Month'].min():%b %Y} – "
                    f"{episode['Month'].max():%b %Y}"
                )
            ),
            "Peak Month": peak_row["Month"].strftime("%b %Y"),
            "Peak Risk Index": peak_row["index"],
            "Gap vs. Trend": peak_row["gap_vs_trend"],
            "3-Month Change": peak_row["change_3m"],
            "Duration (Months)": len(episode),
            "Main Driver": main_driver
        })

    summary_df = pd.DataFrame(summaries)

    summary_df = summary_df.sort_values(
        "Peak Month",
        key=lambda col: pd.to_datetime(col, format="%b %Y"),
        ascending=True
    ).reset_index(drop=True)

    # Format numeric columns.
    numeric_columns = [
        "Peak Risk Index",
        "Gap vs. Trend",
        "3-Month Change"
    ]

    summary_df[numeric_columns] = (
        summary_df[numeric_columns].round(2)
    )

    return summary_df


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

show_trend = st.checkbox(
    "Show 12-month long-term trend",
    value=False,
    key="individual_trend"
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

    # Add 12-month long-term trend if selected.
    if show_trend:

        component_path = COMPONENT_FILES[index_type]

        if component_path.exists():

            component_df = load_component_data(
                str(component_path)
            )

            if "trend_12m" in component_df.columns:

                fig.add_scatter(
                    x=component_df["Month"],
                    y=component_df["trend_12m"],
                    mode="lines",
                    name="12-Month Long-Term Trend",
                    line=dict(
                        color="#16a34a",
                        width=2.5,
                        dash="dash"
                    )
                )

            else:
                st.warning(
                    "The 12-month trend column is unavailable."
                )

    # Add alert threshold at 75.
    fig.add_hline(
        y=75,
        line_dash="dash",
        line_color="#ef4444",
        line_width=2,
        annotation_text="Alert Threshold (75)",
        annotation_position="top left",
        annotation_font_color="#ef4444"
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
            y=1.12,
            xanchor="left",
            x=0
        ),
        margin=dict(t=170)
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



# ============================================================
# HISTORICAL RISK SPIKES
# ============================================================

st.markdown(
    '<div class="section-divider"></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-header">Historical Risk Spikes</div>',
    unsafe_allow_html=True
)

st.caption(
    "Summary of periods when the short-term risk index was "
    "classified as a spike relative to its 12-month trend. "
    "Episodes are grouped by consecutive spike months."
)

spike_path = SPIKE_FILES[index_type]

if spike_path.exists():

    spike_df = load_spike_data(str(spike_path))

    spike_summary = create_spike_summary(spike_df)

    if not spike_summary.empty:

        st.dataframe(
            spike_summary,
            width="stretch",
            hide_index=True
        )

        create_download_button(
            spike_summary,
            f"{index_type.lower()}_spike_summary.csv"
        )

    else:
        st.info(
            f"No short-term risk spikes identified for {index_type}."
        )

else:
    st.warning(
        f"Risk change data file not found: {spike_path}"
    )


# ============================================================
# KNOWN SHOCK ANALYSIS
# ============================================================

st.markdown('<div class="section-divider"></div>',
            unsafe_allow_html=True)

st.markdown(
    '<div class="sub-header">Known Shock Analysis</div>',
    unsafe_allow_html=True
)

st.caption(
    "Evaluate how the risk index responded to major geopolitical "
    "events by comparing its average value during the six months "
    "before an event with its maximum value during the six months after."
)

shock_path = SHOCK_FILES[index_type]

if shock_path.exists():

    shock_df = load_shock_data(str(shock_path))

    if not shock_df.empty:

        st.dataframe(
            shock_df,
            width="stretch",
            hide_index=True
        )

        create_download_button(
            shock_df,
            f"{index_type.lower()}_known_shocks.csv"
        )

    else:
        st.info(
            f"No equal-weighted index shock results available for {index_type}."
        )

else:
    st.warning(
        f"Shock analysis file not found: {shock_path}"
    )