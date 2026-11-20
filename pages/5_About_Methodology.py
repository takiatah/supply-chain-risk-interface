from pathlib import Path

import streamlit as st

from utils.styling import apply_custom_styles

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DESCRIPTION_PATH = PROJECT_ROOT / "overall_data_description.md"

apply_custom_styles()

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
        The dashboard displays forecasts for July through November
        2026 using XGBoost decision tree models.

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

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-header">Downloadable Data Documentation</div>',
        unsafe_allow_html=True
    )

    if DATA_DESCRIPTION_PATH.exists():

        with open(DATA_DESCRIPTION_PATH, "rb") as file:
            st.download_button(
                label="Download Complete Data Documentation",
                data=file,
                file_name="overall_data_description.md",
                mime="text/markdown",
                width="stretch"
            )

    else:
        st.warning("Data documentation file not found.")

render_about_page()