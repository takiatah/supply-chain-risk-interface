from pathlib import Path
import pandas as pd
import streamlit as st

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

FORECAST_START = pd.Timestamp("2026-07-01")
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

    # Sanctions Risk — Russia
    "RUS_SANC": ("Sanctions Risk", "Russia: Total Active Sanctions"),
    "RUS_SANC_TRADE": ("Sanctions Risk", "Russia: Trade Sanctions"),
    "RUS_SANC_ARMS": ("Sanctions Risk", "Russia: Arms Sanctions"),
    "RUS_SANC_MILITARY": ("Sanctions Risk", "Russia: Military Sanctions"),
    "RUS_SANC_FINANCIAL": ("Sanctions Risk", "Russia: Financial Sanctions"),
    "RUS_SANC_TRAVEL": ("Sanctions Risk", "Russia: Travel Sanctions"),
    "RUS_SANC_OTHER": ("Sanctions Risk", "Russia: Other Sanctions"),
    "RUS_SANC_START": ("Sanctions Risk", "Russia: New Sanctions Cases"),

    # Sanctions Risk — China
    "CHN_SANC": ("Sanctions Risk", "China: Total Active Sanctions"),
    "CHN_SANC_TRADE": ("Sanctions Risk", "China: Trade Sanctions"),
    "CHN_SANC_ARMS": ("Sanctions Risk", "China: Arms Sanctions"),
    "CHN_SANC_MILITARY": ("Sanctions Risk", "China: Military Sanctions"),
    "CHN_SANC_FINANCIAL": ("Sanctions Risk", "China: Financial Sanctions"),
    "CHN_SANC_TRAVEL": ("Sanctions Risk", "China: Travel Sanctions"),
    "CHN_SANC_OTHER": ("Sanctions Risk", "China: Other Sanctions"),
    "CHN_SANC_START": ("Sanctions Risk", "China: New Sanctions Cases"),

    # Bilateral Sanctions
    "CHN_RUS_SANC": ("Sanctions Risk", "China–Russia: Total Active Bilateral Sanctions"),
    "CHN_RUS_SANC_START": ("Sanctions Risk", "China–Russia: New Bilateral Sanctions Cases"),
}

# Sanctions indicators grouped into dedicated charts.
SANCTION_CHART_GROUPS = {
    "Russia Sanctions by Category": [
        "RUS_SANC_TRADE",
        "RUS_SANC_ARMS",
        "RUS_SANC_MILITARY",
        "RUS_SANC_FINANCIAL",
        "RUS_SANC_TRAVEL",
        "RUS_SANC_OTHER",
    ],

    "China Sanctions by Category": [
        "CHN_SANC_TRADE",
        "CHN_SANC_ARMS",
        "CHN_SANC_MILITARY",
        "CHN_SANC_FINANCIAL",
        "CHN_SANC_TRAVEL",
        "CHN_SANC_OTHER",
    ],

    "China-Russia Bilateral Sanctions": [
        "CHN_RUS_SANC",
        "CHN_RUS_SANC_START",
    ],
}

SANCTION_COLORS = {
    "SANC_TRADE": "#ff7f0e",
    "SANC_ARMS": "#2ca02c",
    "SANC_MILITARY": "#d62728",
    "SANC_FINANCIAL": "#9467bd",
    "SANC_TRAVEL": "#1f77b4",
    "SANC_OTHER": "#e377c2",
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
    ("CHN_SANC_START", "RUS_SANC_START"),
]

INDICATOR_COLORS = {
    "RUS": "#2563eb",
    "CHN": "#dc2626",
    "OTHER": "#0d9488",
}

