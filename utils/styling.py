import streamlit as st

# ============================================================
# STYLING
# ============================================================

def apply_custom_styles():
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
