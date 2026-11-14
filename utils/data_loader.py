import pandas as pd
import streamlit as st
from utils.config import CSV_PATH

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

