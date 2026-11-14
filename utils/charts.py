import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils.config import *
from utils.helpers import add_forecast_boundary, format_value, style_chart

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
