"""
China-Russia Supply Chain Risk Dashboard
"""

import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="China-Russia Supply Chain Risk Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PAGE NAVIGATION
# ============================================================

pages = {
    "Risk Dashboard": [
        st.Page(
            "pages/1_Risk_Index_Overview.py",
            title="Risk Index Overview",
            default=True
        ),
        st.Page(
            "pages/2_Individual_Risk_Analysis.py",
            title="Individual Risk Analysis",
        ),
        st.Page(
            "pages/3_Monthly_Indicators.py",
            title="Monthly Indicators Explorer",
        ),
        st.Page(
            "pages/4_Data_Explorer.py",
            title="Data Explorer",
        ),
        st.Page(
            "pages/5_About_Methodology.py",
            title="About & Methodology",
        )
    ]
}


# ============================================================
# RUN APPLICATION
# ============================================================

pg = st.navigation(pages, position="sidebar")

pg.run()