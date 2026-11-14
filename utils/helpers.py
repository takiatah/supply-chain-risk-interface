import streamlit as st
import pandas as pd
import numpy as np
from utils.config import RISK_INDEX_COLUMNS, FORECAST_START, FORECAST_END

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

def get_latest_forecast(df, index_type):
    actual_col = RISK_INDEX_COLUMNS[index_type]["actual"]

    november_data = df[
        df["Month"] == pd.Timestamp("2026-11-01")
    ]

    if november_data.empty:
        return None, None

    value = november_data[actual_col].iloc[0]

    return value, pd.Timestamp("2026-11-01")

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

