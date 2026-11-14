import pandas as pd
import streamlit as st

from utils.data_loader import load_data
from utils.helpers import create_download_button, filter_data_by_date
from utils.styling import apply_custom_styles


apply_custom_styles()

df, err = load_data()

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
    col1, col2= st.columns(2)

    col1.metric("Total Observations", f"{len(df):,}")
    col2.metric("Total Columns", f"{len(df.columns):,}")

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
        width="stretch",
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
                width="stretch",
                hide_index=True
            )

render_data_explorer_page(df)