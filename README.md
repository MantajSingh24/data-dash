# Data Dash 📊

A beautiful analytics dashboard for CSV and Excel files. Upload your spreadsheet, map your columns, and get instant insights — all in one place.

## Features

- **File Upload** — Supports CSV and Excel files with auto-encoding detection
- **Dynamic Column Mapping** — Map any dataset's columns to revenue, profit, dates, etc.
- **Overview Dashboard** — KPIs, monthly trends, category & region breakdowns, top products
- **Customer Insights** — Top buyers, repeat rate, loyalty analysis, segmentation
- **Returns Analysis** — Return rates, problem products, month-over-month trends
- **Sidebar Filters** — Filter by date range, category, region, and segment
- **Dark Theme** — Professional dark UI with gradient styling
- **Sample Data** — Includes a Superstore dataset to try out immediately

## Tech Stack

- **Python** — Core language
- **Streamlit** — Multi-page web framework
- **Pandas** — Data manipulation
- **Plotly** — Interactive charts

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

## How to Use

1. Run the app and go to the **Home** page
2. Upload a CSV or Excel file (or use the included sample data)
3. Map your columns — date, revenue, profit, category, customer, etc.
4. Navigate to **Overview**, **Customers**, or **Returns** in the sidebar
5. Use sidebar filters to drill down into your data

## Project Structure

```
Data Dash/
├── Home.py                  # Main entry point — upload & column mapping
├── pages/
│   ├── 1_📈_Overview.py     # KPIs, trends, breakdowns
│   ├── 2_👥_Customers.py    # Customer analytics & loyalty
│   └── 3_🔄_Returns.py      # Return analysis & anomalies
├── src/
│   ├── __init__.py
│   ├── load.py              # Data loading & preprocessing
│   ├── metrics.py           # Business metrics calculations
│   └── charts.py            # Plotly chart components
├── data/
│   └── superstore.csv       # Sample dataset
├── .streamlit/
│   └── config.toml          # Theme & server config
├── requirements.txt
└── start.bat                # Quick launcher (Windows)
```

---
*Built as a learning project — step by step.*
