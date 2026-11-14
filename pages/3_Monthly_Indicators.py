import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.styling import apply_custom_styles
from utils.config import (
    INDICATOR_COLORS,
    INDICATOR_INFO,
    INDICATOR_PAIRS,
    RISK_INDEX_COLUMNS,
    SANCTION_CHART_GROUPS,
    SANCTION_COLORS,
)
from utils.helpers import create_download_button, filter_data_by_date


# ============================================================
# PAGE INITIALIZATION
# ============================================================

apply_custom_styles()

df, err = load_data()

if err:
    st.error(err)
    st.stop()

if df is None or df.empty:
    st.error("The dataset is empty.")
    st.stop()


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
    if column.startswith("CHN_") or column.endswith("CHN"):
        return INDICATOR_COLORS["CHN"]

    if column.startswith("RUS_") or column.endswith("RUS"):
        return INDICATOR_COLORS["RUS"]

    return INDICATOR_COLORS["OTHER"]

def get_chart_color(indicator):
    """Assign distinct colors to sanctions types."""

    for sanction_type, color in SANCTION_COLORS.items():
        if indicator.endswith(sanction_type):
            return color

    return get_indicator_color(indicator)

def get_indicator_chart_groups(selected_indicators):
    """
    Group selected indicators into:
    - Country-specific sanctions charts
    - Comparable indicator pairs
    - Individual indicator charts
    """

    selected = set(selected_indicators)
    groups = []
    handled = set()

    # --------------------------------------------------------
    # Group sanctions indicators by country
    # --------------------------------------------------------

    for group_name, indicators in SANCTION_CHART_GROUPS.items():

        available_group = [
            column for column in indicators
            if column in selected
        ]

        if available_group:
            groups.append({
                "title": group_name,
                "columns": available_group
            })

            handled.update(available_group)

    # --------------------------------------------------------
    # Group other comparable indicators into pairs
    # --------------------------------------------------------

    for first, second in INDICATOR_PAIRS:

        if first in selected or second in selected:

            pair = [
                column for column in (first, second)
                if column in selected
            ]

            if pair:
                groups.append({
                    "title": " / ".join(
                        INDICATOR_INFO[column][1]
                        for column in pair
                    ),
                    "columns": pair
                })

                handled.update(pair)

    # --------------------------------------------------------
    # Display remaining indicators individually
    # --------------------------------------------------------

    for column in selected_indicators:

        if column not in handled:
            groups.append({
                "title": INDICATOR_INFO[column][1],
                "columns": [column]
            })

            handled.add(column)

    return groups


def render_indicators_page(df):

    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DATE FILTERING
    # --------------------------------------------------------

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

    filtered_df = filter_data_by_date(
        df,
        start_date,
        end_date
    )

    # --------------------------------------------------------
    # INDICATOR SEARCH
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CATEGORY SELECTION
    # --------------------------------------------------------

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
        st.info(
            "Select one or more indicators above to display their trends."
        )
        return

    # --------------------------------------------------------
    # AUTOMATICALLY INCLUDE RELATED INDICATORS
    # --------------------------------------------------------

    expanded_selection = set(selected_indicators)

    available_columns = set(get_indicator_columns(df))

    # Automatically include all available sanctions indicators
    # whenever at least one indicator from that group is selected.
    for group_name, indicators in SANCTION_CHART_GROUPS.items():

        if any(
            column in expanded_selection
            for column in indicators
        ):

            expanded_selection.update(
                column for column in indicators
                if column in available_columns
            )

    # Automatically include counterparts for other indicator pairs.
    for first, second in INDICATOR_PAIRS:

        if first in expanded_selection and second in available_columns:
            expanded_selection.add(second)

        elif second in expanded_selection and first in available_columns:
            expanded_selection.add(first)

    # Preserve the original dataset column order.
    selected_indicators = [
        column for column in get_indicator_columns(df)
        if column in expanded_selection
    ]

    # --------------------------------------------------------
    # INDICATOR TREND CHARTS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-header">Indicator Trends</div>',
        unsafe_allow_html=True
    )

    chart_groups = get_indicator_chart_groups(selected_indicators)

    for group in chart_groups:

        fig = go.Figure()
        plotted_any = False

        for indicator in group["columns"]:

            chart_data = filtered_df[
                ["Month", indicator]
            ].dropna()

            if chart_data.empty:
                continue

            label = INDICATOR_INFO[indicator][1]

            fig.add_trace(
                go.Scatter(
                    x=chart_data["Month"],
                    y=chart_data[indicator],
                    mode="lines",
                    name=label,
                    line=dict(
                        color=get_chart_color(indicator),
                        width=2.5
                    ),
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
                f"No observations available for {group['title']}."
            )
            continue

        fig.update_layout(
            title=dict(
                text=group["title"],
                x=0,
                xanchor="left",
                y=0.98
            ),
            template="plotly_white",
            height=440,
            margin=dict(l=20, r=20, t=65, b=70),
            hovermode="x unified",
            xaxis_title="Month",
            yaxis_title="Indicator Value",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.22,
                xanchor="left",
                x=0,
                title_text=""
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # SELECTED INDICATOR DATA TABLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-header">Selected Indicator Data</div>',
        unsafe_allow_html=True
    )

    selected_data = filtered_df[
        ["Month"] + selected_indicators
    ].copy()

    selected_data = selected_data.rename(
        columns={
            column: INDICATOR_INFO[column][1]
            for column in selected_indicators
        }
    )

    st.dataframe(
        selected_data,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # CSV DOWNLOAD
    # --------------------------------------------------------

    create_download_button(
        selected_data,
        "selected_monthly_indicators.csv",
        "Download Selected Indicators"
    )


# ============================================================
# RENDER PAGE
# ============================================================

render_indicators_page(df)
