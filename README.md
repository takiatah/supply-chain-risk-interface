# China–Russia Supply Chain Risk Dashboard

An interactive Streamlit dashboard for exploring China–Russia trade relationships, monitoring supply chain vulnerabilities, and analyzing historical and forecasted risk indices.

## Overview

This project examines supply chain risks associated with China–Russia trade relationships through historical trade data, economic indicators, geopolitical developments, transportation metrics, and sanctions data.

The dashboard provides interactive visualizations and analytical tools to explore risk trends, compare China and Russia, investigate individual indicators, and examine projected changes in supply chain risk.

## Features

- **Risk Index Overview:** View the latest observed risk indices for Overall, Russia, and China, alongside November 2026 forecasts.
- **Individual Risk Analysis:** Examine historical trends, model predictions, and future forecasts for each risk index.
- **Monthly Indicators Explorer:** Explore monthly indicators across six categories:
  - Trade Risk
  - Dependency Risk
  - Transportation Risk
  - Economic Risk
  - Geopolitical Risk
  - Sanctions Risk
- **Data Explorer:** Filter, inspect, and download the underlying dataset.
- **About & Methodology:** Review the risk-index framework, forecasting approach, and data limitations.
- **Interactive Visualizations:** Explore trends and compare indicators using interactive Plotly charts.

## Risk Index Framework

The project evaluates supply chain risk through five primary components:

| Risk Category | Description |
|---|---|
| Dependency Risk | Measures reliance on trade relationships and imports or exports between China and Russia. |
| Transportation Risk | Examines transportation costs and shipping connectivity. |
| Economic Risk | Captures economic conditions and exchange-rate fluctuations. |
| Geopolitical Risk | Incorporates geopolitical uncertainty and country-specific geopolitical developments. |
| Sanctions Risk | Examines sanctions activity and restrictions affecting China and Russia. |

The overall risk index is normalized to a scale of **0–100**, with higher values representing greater estimated supply chain risk.

## Forecasting

The dashboard includes historical model predictions and future risk-index forecasts generated using XGBoost regression models.

- **Historical observations:** Actual risk-index values from the available historical dataset.
- **Historical model predictions:** Model-generated estimates for historical observations.
- **Future forecasts:** Projected risk-index values for June–November 2026.

Historical model predictions and future forecasts are displayed separately to distinguish model evaluation from forward-looking projections.

## Project Structure

```text
supply-chain-risk-interface/
├── cleaned_datasets
│   ├── china_risk_index_monthly.csv
│   ├── main_data.csv
│   ├── overall_data.csv
│   ├── risk_index_monthly.csv
│   └── russia_risk_index_monthly.csv
├── pages
│   ├── 1_Risk_Index_Overview.py
│   ├── 2_Individual_Risk_Analysis.py
│   ├── 3_Monthly_Indicators.py
│   ├── 4_Data_Explorer.py
│   └── 5_About_Methodology.py
├── predictions
│   ├── graphs
│   │   ├── china_predictions.png
│   │   ├── overall_predictions.png
│   │   ├── russia_predictions.png
│   │   ├── XGBoost - China Risk Index.png
│   │   ├── XGBoost - Overall Risk Index.png
│   │   └── XGBoost - Russia Risk Index.png
│   └── make_predictions.py
├── utils
│   ├── __init__.py
│   ├── charts.py
│   ├── config.py
│   ├── data_loader.py
│   ├── helpers.py
│   └── styling.py
├── app.py
├── overall_data_with_predictions.csv
├── requirements.txt
└── .gitignore
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Navigate into the project directory:

```bash
cd supply-chain-risk-interface
```

Replace the repository URL and directory name with your actual GitHub repository details.

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit application

From the project's root directory, execute:

```bash
streamlit run app.py
```

Streamlit will start a local development server. Open the URL displayed in your terminal, typically:

```text
http://localhost:8501
```

To stop the application, press `Ctrl + C` in your terminal.

## Technologies Used

- **Python** – Core programming language
- **Streamlit** – Interactive dashboard and application framework
- **Pandas** – Data manipulation and analysis
- **NumPy** – Numerical computing
- **Plotly** – Interactive data visualizations
- **Matplotlib** – Statistical visualizations
- **Scikit-learn** – Model evaluation metrics
- **XGBoost** – Gradient boosting regression models

## Data Sources and Limitations

The project integrates trade, economic, transportation, geopolitical, and sanctions-related datasets.

Some important data considerations include:

- Historical trade data combines UN Comtrade data for 2010–2014 and General Administration of Customs of China (GACC) data for 2015–2026.
- OECD transportation data from 2024 is applied to 2025–2026 where more recent observations are unavailable.
- Some indicators are proxies or estimates rather than direct measurements of supply chain risk.
- Forecasted values represent model estimates and should not be interpreted as observed outcomes.
- Sanctions indicators distinguish between newly initiated sanctions and total active sanctions where applicable.

These limitations should be considered when interpreting the dashboard's visualizations and forecasts.

## Disclaimer

This project is intended for research, educational, and analytical purposes. The risk indices and forecasts are model-based estimates and should not be treated as definitive measurements or predictions of future geopolitical or economic conditions.