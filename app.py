"""
China-Russia Supply Chain Risk Dashboard

Streamlit application for analyzing supply chain risk indices,
historical trends, monthly indicators, and future forecasts.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="China-Russia Supply Chain Risk Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_PATH = Path("overall_data_with_predictions.csv")

FORECAST_START = pd.Timestamp("2026-06-01")
FORECAST_END = pd.Timestamp("2026-11-30")

RISK_INDEX_COLUMNS = {
    "Overall": {
        "actual": "overall_actual_future",
        "predicted": "overall_predicted_future",
        "color": "#2563eb"
    },
    "Russia": {
        "actual": "russia_actual_future",
        "predicted": "russia_predicted_future",
        "color": "#dc2626"
    },
    "China": {
        "actual": "china_actual_future",
        "predicted": "china_predicted_future",
        "color": "#16a34a"
    }
}

FORECAST_COLOR = "#0d9488"
PREDICTION_COLOR = "#f59e0b"

# Explicit indicator descriptions and categories based on the dataset documentation.
# Only columns that actually exist in the CSV are displayed.
INDICATOR_INFO = {
    # Trade Risk
    "CHN_IMP": ("Trade Risk", "China Global Imports (CIF)"),
    "CHN_EXP": ("Trade Risk", "China Global Exports (FOB)"),
    "CHN_TB": ("Trade Risk", "China Global Trade Balance"),
    "RUS_IMP": ("Trade Risk", "Russia Global Imports (CIF)"),
    "RUS_EXP": ("Trade Risk", "Russia Global Exports (FOB)"),
    "RUS_TB": ("Trade Risk", "Russia Global Trade Balance"),
    "RUS_IMP_CHN": ("Trade Risk", "Russia Imports from China (CIF)"),
    "RUS_EXP_CHN": ("Trade Risk", "Russia Exports to China (FOB)"),
    "RUS_TB_CHN": ("Trade Risk", "Russia's Trade Balance with China"),
    "CHN_IMP_RUS": ("Trade Risk", "China Imports from Russia (CIF)"),
    "CHN_EXP_RUS": ("Trade Risk", "China Exports to Russia (FOB)"),
    "CHN_TB_RUS": ("Trade Risk", "China's Trade Balance with Russia"),
    "G_IMP": ("Trade Risk", "Global Imports (CIF)"),
    "G_EXP": ("Trade Risk", "Global Exports (FOB)"),
    "RUS_CHN_TII": ("Trade Risk", "Russia–China Trade Intensity Index"),
    "CHN_RUS_TII": ("Trade Risk", "China–Russia Trade Intensity Index"),

    # Dependency Risk
    "RUS_IMP_DEP": ("Dependency Risk", "Russia Import Dependency on China"),
    "RUS_EXP_DEP": ("Dependency Risk", "Russia Export Dependency on China"),
    "CHN_IMP_DEP": ("Dependency Risk", "China Import Dependency on Russia"),
    "CHN_EXP_DEP": ("Dependency Risk", "China Export Dependency on Russia"),

    # Transportation Risk
    "CHN_TRANS_FROM_RUS": ("Transportation Risk", "China Transport Costs from Russia"),
    "RUS_TRANS_FROM_CHN": ("Transportation Risk", "Russia Transport Costs from China"),
    "LSCI_CHN": ("Transportation Risk", "China Liner Shipping Connectivity Index"),
    "LSCI_RUS": ("Transportation Risk", "Russia Liner Shipping Connectivity Index"),
    "LSBCI": ("Transportation Risk", "Liner Shipping Connectivity Index (LSBCI)"),

    # Economic Risk
    "CHN_CPI_MoM": ("Economic Risk", "China Month-over-Month CPI (%)"),
    "CHN_CPI_YoY": ("Economic Risk", "China Year-over-Year CPI (%)"),
    "RUS_CPI_MoM": ("Economic Risk", "Russia Month-over-Month CPI (%)"),
    "RUS_CPI_YoY": ("Economic Risk", "Russia Year-over-Year CPI (%)"),
    "USD_RUB": ("Economic Risk", "USD to RUB Exchange Rate"),
    "USD_CNY": ("Economic Risk", "USD to CNY Exchange Rate"),
    "RUS_PRICE_INDEX": ("Economic Risk", "Russia Commodity Net Export Price Index"),
    "CHN_PRICE_INDEX": ("Economic Risk", "China Commodity Net Export Price Index"),

    # Geopolitical Risk
    "GPR": ("Geopolitical Risk", "Global Geopolitical Risk Index (GPR)"),
    "GPR_RUS": ("Geopolitical Risk", "Russia-specific Geopolitical Risk (%)"),
    "GPR_CHN": ("Geopolitical Risk", "China-specific Geopolitical Risk (%)"),

    # Sanctions Risk
    "CHN_SANC_START": ("Sanctions Risk", "New Sanctions Cases Targeting China"),
    "CHN_SANC": ("Sanctions Risk", "Active Sanctions Cases Targeting China"),
    "RUS_SANC": ("Sanctions Risk", "Active Sanctions Cases Targeting Russia"),
    "CHN_RUS_SANC": ("Sanctions Risk", "Active China–Russia Bilateral Sanctions Cases"),
}

# Each pair is plotted on one chart so the two countries can be compared.
# The source documentation does not identify a RUS_SANC_START column, so it is
# intentionally not assumed or added here.
INDICATOR_PAIRS = [
    ("CHN_IMP", "RUS_IMP"),
    ("CHN_EXP", "RUS_EXP"),
    ("CHN_TB", "RUS_TB"),
    ("RUS_IMP_CHN", "CHN_IMP_RUS"),
    ("RUS_EXP_CHN", "CHN_EXP_RUS"),
    ("RUS_TB_CHN", "CHN_TB_RUS"),
    ("RUS_CHN_TII", "CHN_RUS_TII"),
    ("RUS_IMP_DEP", "CHN_IMP_DEP"),
    ("RUS_EXP_DEP", "CHN_EXP_DEP"),
    ("CHN_TRANS_FROM_RUS", "RUS_TRANS_FROM_CHN"),
    ("LSCI_CHN", "LSCI_RUS"),
    ("CHN_CPI_MoM", "RUS_CPI_MoM"),
    ("CHN_CPI_YoY", "RUS_CPI_YoY"),
    ("CHN_PRICE_INDEX", "RUS_PRICE_INDEX"),
    ("GPR_CHN", "GPR_RUS"),
    ("CHN_SANC", "RUS_SANC"),
]

INDICATOR_COLORS = {
    "CHN": "#2563eb",
    "RUS": "#dc2626",
    "OTHER": "#0d9488",
}



# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.4rem;
            font-weight: 750;
            color: #1e3a5f;
            margin-bottom: 0.2rem;
        }

        .sub-header {
            font-size: 1.35rem;
            font-weight: 650;
            color: #334155;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }

        .description {
            color: #64748b;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .kpi-card {
            background: linear-gradient(135deg, #1e3a8a, #4338ca);
            padding: 1.3rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            min-height: 145px;
        }

        .kpi-label {
            font-size: 0.95rem;
            opacity: 0.9;
        }

        .kpi-value {
            font-size: 2.2rem;
            font-weight: 750;
            margin: 0.5rem 0;
        }

        .kpi-month {
            font-size: 0.85rem;
            opacity: 0.8;
        }

        .section-divider {
            border-top: 1px solid #e2e8f0;
            margin: 1.8rem 0;
        }

        .forecast-info {
            background-color: #fef3c7;
            color: #78350f;
            padding: 0.9rem 1rem;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            margin: 1rem 0;
        }

        .small-note {
            color: #64748b;
            font-size: 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    """Load and prepare the dashboard dataset."""

    if not CSV_PATH.exists():
        return None, f"CSV file not found: {CSV_PATH.resolve()}"

    try:
        df = pd.read_csv(CSV_PATH)

        if "Month" not in df.columns:
            return None, "The dataset does not contain a Month column."

        df["Month"] = pd.to_datetime(
            df["Month"],
            errors="coerce"
        )

        df = df.dropna(subset=["Month"])
        df = df.sort_values("Month").reset_index(drop=True)

        # Convert indicator columns to numeric where possible.
        for col in df.columns:
            if col != "Month":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Check for duplicate monthly observations.
        if df["Month"].duplicated().any():
            return None, (
                "The dataset contains duplicate Month values. "
                "Please resolve these before using the dashboard."
            )

        return df, None

    except Exception as e:
        return None, f"Error loading dataset: {str(e)}"


# ============================================================
# GENERAL HELPERS
# ============================================================

def format_value(value):
    """Format a numerical value for display."""

    if pd.isna(value):
        return "N/A"

    return f"{value:.2f}"


def get_latest_actual(df, index_type):
    """Get the latest historical actual index value."""

    actual_col = RISK_INDEX_COLUMNS[index_type]["actual"]

    if actual_col not in df.columns:
        return None, None

    historical = df[
        (df["Month"] < FORECAST_START) &
        (df[actual_col].notna())
    ]

    if historical.empty:
        return None, None

    row = historical.iloc[-1]

    return row[actual_col], row["Month"]


def get_forecast_data(df, index_type):
    """
    Return the historical and forecast data for an index.

    The actual column contains historical observations and
    future forecasts. The predicted column contains historical
    model predictions.
    """

    actual_col = RISK_INDEX_COLUMNS[index_type]["actual"]
    predicted_col = RISK_INDEX_COLUMNS[index_type]["predicted"]

    if actual_col not in df.columns:
        return None, None

    historical = df[df["Month"] < FORECAST_START].copy()

    future = df[
        (df["Month"] >= FORECAST_START) &
        (df["Month"] <= FORECAST_END)
    ].copy()

    historical = historical.dropna(subset=[actual_col])
    future = future.dropna(subset=[actual_col])

    return historical, future


def filter_data_by_date(df, start_date, end_date):
    """Filter dataset by date range."""

    return df[
        (df["Month"] >= pd.Timestamp(start_date)) &
        (df["Month"] <= pd.Timestamp(end_date))
    ].copy()


def create_download_button(df, filename, label="Download CSV"):
    """Create a CSV download button."""

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


def add_forecast_boundary(fig):
    """Add a vertical line marking the forecast period."""

    fig.add_vline(
        x=FORECAST_START,
        line_dash="dash",
        line_color="#64748b",
        line_width=1.5,
        annotation_text="Forecast Begins",
        annotation_position="top"
    )


def style_chart(fig, title=None, yaxis_title="Risk Index"):
    """Apply consistent Plotly styling."""

    fig.update_layout(
        title=title,
        template="plotly_white",
        height=440,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=65, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        xaxis_title="Month",
        yaxis_title=yaxis_title
    )

    return fig


# ============================================================
# RISK INDEX CHARTS
# ============================================================

def create_risk_index_chart(
    df,
    index_type,
    show_predictions=True,
    show_forecast=True
):
    """Create an actual-versus-forecast risk index chart."""

    actual_col = RISK_INDEX_COLUMNS[index_type]["actual"]
    predicted_col = RISK_INDEX_COLUMNS[index_type]["predicted"]
    historical_color = RISK_INDEX_COLUMNS[index_type]["color"]

    if actual_col not in df.columns:
        return None

    fig = go.Figure()

    historical = df[
        (df["Month"] < FORECAST_START) &
        (df[actual_col].notna())
    ].copy()

    future = df[
        (df["Month"] >= FORECAST_START) &
        (df["Month"] <= FORECAST_END) &
        (df[actual_col].notna())
    ].copy()

    # Historical actual values.
    if not historical.empty:
        fig.add_trace(
            go.Scatter(
                x=historical["Month"],
                y=historical[actual_col],
                mode="lines",
                name="Historical Actual",
                line=dict(
                    color=historical_color,
                    width=3
                ),
                hovertemplate=(
                    "%{x|%b %Y}<br>"
                    "Actual: %{y:.2f}"
                    "<extra></extra>"
                )
            )
        )

    # Future forecast values.
    # Include the last historical point so the forecast connects
    # visually to the historical line.
    if show_forecast and not future.empty:

        if not historical.empty:
            connecting_point = historical.iloc[-1]

            forecast_x = pd.concat(
                [
                    pd.Series([connecting_point["Month"]]),
                    future["Month"]
                ],
                ignore_index=True
            )

            forecast_y = pd.concat(
                [
                    pd.Series([connecting_point[actual_col]]),
                    future[actual_col]
                ],
                ignore_index=True
            )

        else:
            forecast_x = future["Month"]
            forecast_y = future[actual_col]

        fig.add_trace(
            go.Scatter(
                x=forecast_x,
                y=forecast_y,
                mode="lines",
                name="Future Forecast",
                line=dict(
                    color=historical_color,
                    width=3
                ),
                opacity=0.6,
                hovertemplate=(
                    "%{x|%b %Y}<br>"
                    "Forecast: %{y:.2f}"
                    "<extra></extra>"
                )
            )
        )

    # Historical model predictions.
    if show_predictions and predicted_col in df.columns:

        prediction_data = df[
            (df["Month"] < FORECAST_START) &
            (df[predicted_col].notna())
        ].copy()

        if not prediction_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=prediction_data["Month"],
                    y=prediction_data[predicted_col],
                    mode="lines",
                    name="Historical Model Predictions",
                    line=dict(
                        color=PREDICTION_COLOR,
                        width=2,
                        dash="dot"
                    ),
                    hovertemplate=(
                        "%{x|%b %Y}<br>"
                        "Model Prediction: %{y:.2f}"
                        "<extra></extra>"
                    )
                )
            )

    add_forecast_boundary(fig)

    fig.update_yaxes(
        range=[0, 100],
        fixedrange=False
    )

    return style_chart(
        fig,
        title=f"{index_type} Risk Index",
        yaxis_title="Risk Index (0–100)"
    )


def create_comparison_chart(df, show_predictions=False):
    """Compare the three risk indices."""

    fig = go.Figure()

    for index_type, settings in RISK_INDEX_COLUMNS.items():

        actual_col = settings["actual"]
        predicted_col = settings["predicted"]

        if actual_col not in df.columns:
            continue

        historical = df[
            (df["Month"] < FORECAST_START) &
            (df[actual_col].notna())
        ]

        future = df[
            (df["Month"] >= FORECAST_START) &
            (df["Month"] <= FORECAST_END) &
            (df[actual_col].notna())
        ]

        if not historical.empty:
            fig.add_trace(
                go.Scatter(
                    x=historical["Month"],
                    y=historical[actual_col],
                    mode="lines",
                    name=f"{index_type} Historical",
                    line=dict(
                        color=settings["color"],
                        width=2.5
                    )
                )
            )

        if not future.empty:
            if not historical.empty:
                forecast_x = pd.concat(
                    [
                        pd.Series([historical["Month"].iloc[-1]]),
                        future["Month"]
                    ],
                    ignore_index=True
                )

                forecast_y = pd.concat(
                    [
                        pd.Series([historical[actual_col].iloc[-1]]),
                        future[actual_col]
                    ],
                    ignore_index=True
                )
            else:
                forecast_x = future["Month"]
                forecast_y = future[actual_col]

            fig.add_trace(
                go.Scatter(
                    x=forecast_x,
                    y=forecast_y,
                    mode="lines",
                    name=f"{index_type} Forecast",
                    line=dict(
                        color=settings["color"],
                        width=2.5
                    ),
                    opacity=0.6
                )
            )

        if show_predictions and predicted_col in df.columns:
            prediction_data = df[
                (df["Month"] < FORECAST_START) &
                df[predicted_col].notna()
            ]

            if not prediction_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=prediction_data["Month"],
                        y=prediction_data[predicted_col],
                        mode="lines",
                        name=f"{index_type} Model Predictions",
                        line=dict(
                            color=settings["color"],
                            width=1.5,
                            dash="dot"
                        ),
                        opacity=0.65
                    )
                )

    add_forecast_boundary(fig)

    fig.update_yaxes(range=[0, 100])

    return style_chart(
        fig,
        title="China-Russia Risk Index Comparison",
        yaxis_title="Risk Index (0–100)"
    )


# ============================================================
# KPI CARDS
# ============================================================

def render_kpi_card(label, value, month, color):
    month_text = (
        month.strftime("%B %Y")
        if month is not None
        else "No historical data"
    )

    value_text = format_value(value)

    st.html(
        f"""
        <div class="kpi-card"
             style="background: linear-gradient(135deg, {color}, #334155);">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value_text}</div>
            <div class="kpi-month">
                Latest observed value · {month_text}
            </div>
        </div>
        """
    )


# ============================================================
# PAGE 1: RISK INDEX OVERVIEW
# ============================================================

def render_overview_page(df):

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
        '<div class="sub-header">Latest Observed Risk Indices</div>',
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
        st.plotly_chart(fig, use_container_width=True)
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
        use_container_width=True
    )


# ============================================================
# PAGE 2: INDIVIDUAL RISK INDEX ANALYSIS
# ============================================================

def render_individual_analysis_page(df):

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
        st.plotly_chart(fig, use_container_width=True)
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
            use_container_width=True,
            hide_index=True
        )

        create_download_button(
            forecast_table,
            f"{index_type.lower()}_risk_forecast.csv"
        )

    else:
        st.info("No forecast observations are available.")


# ============================================================
# PAGE 3: MONTHLY INDICATORS EXPLORER
# ============================================================

def get_indicator_columns(df):
    """Return documented monthly indicator columns present in the dataset."""

    excluded_columns = {
        "Month",
        *[
            settings["actual"]
            for settings in RISK_INDEX_COLUMNS.values()
        ],
        *[
            settings["predicted"]
            for settings in RISK_INDEX_COLUMNS.values()
        ],
    }

    return [
        col for col in INDICATOR_INFO
        if col in df.columns and col not in excluded_columns
    ]


def categorize_indicators(df):
    """Group documented indicators into the six dashboard baskets."""

    categories = {
        "Trade Risk": [],
        "Dependency Risk": [],
        "Transportation Risk": [],
        "Economic Risk": [],
        "Geopolitical Risk": [],
        "Sanctions Risk": [],
    }

    for column in get_indicator_columns(df):
        category, _ = INDICATOR_INFO[column]
        categories[category].append(column)

    return categories


def get_indicator_color(column):
    """Return a consistent country color for an indicator."""

    # For bilateral columns, the leading country identifies the reporter.
    # For LSCI columns, the country is represented by the suffix.
    if column.startswith("CHN_") or column == "LSCI_CHN":
        return INDICATOR_COLORS["CHN"]

    if column.startswith("RUS_") or column == "LSCI_RUS":
        return INDICATOR_COLORS["RUS"]

    return INDICATOR_COLORS["OTHER"]


def get_indicator_chart_groups(selected_indicators):
    """Group selected indicators into pairs or individual chart series."""

    selected = set(selected_indicators)
    groups = []
    handled = set()

    for first, second in INDICATOR_PAIRS:
        if first in selected or second in selected:
            pair = [column for column in (first, second) if column in selected]
            if len(pair) == 2:
                groups.append(pair)
                handled.update(pair)
            elif len(pair) == 1:
                groups.append(pair)
                handled.update(pair)

    for column in selected_indicators:
        if column not in handled:
            groups.append([column])
            handled.add(column)

    return groups


def render_indicators_page(df):

    st.markdown(
        '<div class="main-header">Monthly Indicators Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="description">'
        'Explore the monthly indicators used to examine China–Russia '
        'supply chain vulnerabilities. Select a variable to view its '
        'trend; comparable China and Russia indicators are shown together.'
        '</div>',
        unsafe_allow_html=True
    )

    categories = categorize_indicators(df)
    available_columns = set(get_indicator_columns(df))

    # Date filtering.
    min_date = df["Month"].min().date()
    max_date = df["Month"].max().date()

    date_range = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="indicator_date_range"
    )

    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        st.info("Select both a start date and an end date.")
        return

    start_date, end_date = date_range
    filtered_df = filter_data_by_date(df, start_date, end_date)

    search = st.text_input(
        "Search indicators",
        placeholder="Search by descriptive indicator name...",
        key="indicator_search"
    ).strip().casefold()

    st.markdown(
        '<div class="sub-header">Indicator Categories</div>',
        unsafe_allow_html=True
    )

    selected_indicators = []

    for category, indicators in categories.items():
        matching_indicators = [
            column for column in indicators
            if search in INDICATOR_INFO[column][1].casefold()
            or search in column.casefold()
        ]

        if not matching_indicators:
            continue

        with st.expander(
            f"{category} ({len(matching_indicators)} indicators)",
            expanded=(category == "Trade Risk")
        ):
            selected = st.multiselect(
                f"Select {category} indicators",
                options=matching_indicators,
                default=[],
                format_func=lambda column: INDICATOR_INFO[column][1],
                key=f"indicator_select_{category}"
            )
            selected_indicators.extend(selected)

    if not selected_indicators:
        st.info("Select one or more indicators above to display their trends.")
        return

    # If one member of a documented pair is selected, automatically include
    # its counterpart when that counterpart exists in the loaded CSV.
    expanded_selection = set(selected_indicators)
    for first, second in INDICATOR_PAIRS:
        if first in expanded_selection and second in available_columns:
            expanded_selection.add(second)
        elif second in expanded_selection and first in available_columns:
            expanded_selection.add(first)

    selected_indicators = [
        column for column in get_indicator_columns(df)
        if column in expanded_selection
    ]

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Indicator Trends</div>',
        unsafe_allow_html=True
    )

    chart_groups = get_indicator_chart_groups(selected_indicators)

    for group in chart_groups:
        fig = go.Figure()
        plotted_any = False

        for indicator in group:
            chart_data = filtered_df[["Month", indicator]].dropna()
            if chart_data.empty:
                continue

            label = INDICATOR_INFO.get(indicator, (None, indicator))[1]
            fig.add_trace(
                go.Scatter(
                    x=chart_data["Month"],
                    y=chart_data[indicator],
                    mode="lines",
                    name=label,
                    line=dict(color=get_indicator_color(indicator), width=2.5),
                    connectgaps=False,
                    hovertemplate=(
                        "%{x|%b %Y}<br>"
                        + label
                        + ": %{y:,.3f}<extra></extra>"
                    )
                )
            )
            plotted_any = True

        if not plotted_any:
            st.warning(
                "No observations available for "
                + ", ".join(INDICATOR_INFO[column][1] for column in group)
                + "."
            )
            continue

        title = " / ".join(INDICATOR_INFO[column][1] for column in group)
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=360,
            hovermode="x unified",
            xaxis_title="Month",
            yaxis_title="Value",
            margin=dict(l=20, r=20, t=65, b=30),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    # Selected data table uses descriptive labels rather than raw column codes.
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Selected Indicator Data</div>',
        unsafe_allow_html=True
    )

    selected_data = filtered_df[["Month"] + selected_indicators].copy()
    selected_data = selected_data.rename(
        columns={column: INDICATOR_INFO[column][1] for column in selected_indicators}
    )

    st.dataframe(
        selected_data,
        use_container_width=True,
        hide_index=True
    )

    create_download_button(
        selected_data,
        "selected_monthly_indicators.csv",
        "Download Selected Indicators"
    )



# ============================================================
# PAGE 4: DATA EXPLORER
# ============================================================

def render_data_explorer_page(df):

    st.markdown(
        '<div class="main-header">Data Explorer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="description">'
        'Inspect the underlying dataset, filter observations, '
        'and export selected variables.'
        '</div>',
        unsafe_allow_html=True
    )

    # Dataset information.
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Observations", f"{len(df):,}")
    col2.metric("Total Columns", f"{len(df.columns):,}")
    col3.metric(
        "Missing Values",
        f"{df.isna().sum().sum():,}"
    )

    st.markdown('<div class="section-divider"></div>',
                unsafe_allow_html=True)

    # Date filter.
    min_date = df["Month"].min().date()
    max_date = df["Month"].max().date()

    date_range = st.date_input(
        "Filter by date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="explorer_date_range"
    )

    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        st.info("Select both a start date and an end date.")
        return

    start_date, end_date = date_range

    filtered_df = filter_data_by_date(
        df,
        start_date,
        end_date
    )

    # Column selection.
    selected_columns = st.multiselect(
        "Select columns to display",
        options=list(df.columns),
        default=list(df.columns),
        key="explorer_columns"
    )

    if not selected_columns:
        st.warning("Select at least one column.")
        return

    display_df = filtered_df[selected_columns].copy()

    # Search.
    search = st.text_input(
        "Search displayed data",
        placeholder="Search for a value..."
    ).strip()

    if search:
        searchable = display_df.astype(str).apply(
            lambda col: col.str.contains(
                search,
                case=False,
                na=False,
                regex=False
            )
        )

        display_df = display_df[searchable.any(axis=1)]

    st.markdown(
        f"Displaying **{len(display_df):,}** observations."
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    create_download_button(
        display_df,
        "filtered_supply_chain_dataset.csv",
        "Download Filtered Dataset"
    )

    # Missing-value report.
    with st.expander("Missing Value Summary"):

        missing = pd.DataFrame({
            "Column": df.columns,
            "Missing Values": df.isna().sum().values,
            "Missing Percentage": (
                df.isna().mean().values * 100
            ).round(2)
        })

        missing = missing[
            missing["Missing Values"] > 0
        ].sort_values(
            "Missing Percentage",
            ascending=False
        )

        if missing.empty:
            st.success("No missing values found.")
        else:
            st.dataframe(
                missing,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# PAGE 5: ABOUT AND METHODOLOGY
# ============================================================

def render_about_page():

    st.markdown(
        '<div class="main-header">About the Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        This dashboard provides an interactive view of supply chain
        risks associated with China-Russia trade relationships.

        It combines historical monthly indicators, composite risk
        indices, and machine-learning forecasts to help examine
        potential vulnerabilities and changes in bilateral trade.
        """
    )

    st.markdown(
        '<div class="sub-header">Risk Index Framework</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        The risk index framework is organized around five baskets:

        1. **Dependency Risk:** Measures reliance on trade partners
           and exposure to concentrated trade relationships.

        2. **Transportation Risk:** Examines transportation,
           shipping, and logistics-related vulnerabilities.

        3. **Economic Risk:** Captures economic conditions and
           potential economic instability.

        4. **Geopolitical Risk:** Reflects geopolitical tensions
           and political instability.

        5. **Sanctions Risk:** Captures sanctions-related exposure
           and restrictions affecting trade relationships.
        """
    )

    st.markdown(
        '<div class="sub-header">Risk Index Interpretation</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        All composite risk indices are scaled from 0 to 100.

        - Lower values indicate relatively lower measured risk.
        - Higher values indicate relatively higher measured risk.

        The indices are comparative analytical measures and should
        not be interpreted as probabilities of disruption.
        """
    )

    st.markdown(
        '<div class="sub-header">Forecasting</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        The dashboard displays forecasts for June through November
        2026.

        Historical actual values, historical model predictions,
        and future forecasts are displayed separately.

        Historical model predictions are provided for comparison
        with observed values. Future forecasts represent model
        estimates and are not observed outcomes.
        """
    )

    st.markdown(
        '<div class="sub-header">Data Limitations</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        Results depend on the coverage, quality, and consistency
        of the underlying data sources.

        Differences in source methodology, reporting delays,
        proxy variables, and estimated values may affect
        comparisons across time.

        Forecasts are subject to model uncertainty and should
        be interpreted alongside the underlying indicators.
        """
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    df, error = load_data()

    if error:
        st.error(error)
        st.info(
            "Place overall_data_with_predictions.csv "
            "in the same directory as app.py."
        )
        st.stop()

    if df is None or df.empty:
        st.error("The dataset is empty.")
        st.stop()

    # Check required risk index columns.
    missing_columns = []

    for settings in RISK_INDEX_COLUMNS.values():
        actual_col = settings["actual"]

        if actual_col not in df.columns:
            missing_columns.append(actual_col)

    if missing_columns:
        st.error(
            "Required risk index columns are missing: "
            + ", ".join(missing_columns)
        )
        st.stop()

    # Sidebar.
    st.sidebar.title("📊 Risk Dashboard")

    st.sidebar.markdown(
        "China-Russia Supply Chain Risk Analysis"
    )

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Risk Index Overview",
            "Individual Risk Index Analysis",
            "Monthly Indicators Explorer",
            "Data Explorer",
            "About & Methodology"
        ]
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown("### Dataset Information")

    st.sidebar.caption(
        f"Data range: {df['Month'].min():%b %Y} "
        f"– {df['Month'].max():%b %Y}"
    )

    st.sidebar.caption(
        f"Observations: {len(df):,}"
    )

    st.sidebar.caption(
        f"Indicators: {len(get_indicator_columns(df)):,}"
    )

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "Forecast period: June – November 2026"
    )

    # Page routing.
    if page == "Risk Index Overview":
        render_overview_page(df)

    elif page == "Individual Risk Index Analysis":
        render_individual_analysis_page(df)

    elif page == "Monthly Indicators Explorer":
        render_indicators_page(df)

    elif page == "Data Explorer":
        render_data_explorer_page(df)

    elif page == "About & Methodology":
        render_about_page()

    # Footer.
    st.markdown("---")

    st.caption(
        "China-Russia Supply Chain Risk Dashboard | "
        "Historical analysis and model-based forecasts"
    )


if __name__ == "__main__":
    main()
