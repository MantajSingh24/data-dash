# Data Dash 📊

A simple analytics dashboard for CSV and Excel files. Upload your spreadsheet and get instant insights.

## Status: ✅ Core Features Complete

### Features
- [x] File upload (CSV, Excel)
- [x] Auto-detect column types
- [x] Dynamic column mapping
- [x] Basic metrics & summary stats
- [x] Charts & visualizations (bar, pie, line, trend)
- [x] Dark theme with custom styling
- [x] Multi-page app structure
- [x] Overview page (KPIs, trends, breakdowns)
- [x] Customer insights (top buyers, loyalty, segmentation)
- [x] Returns analysis (return rates, problem products)
- [x] Sidebar filters (date, category, region)
- [x] Sample dataset included

### Tech Stack
- Python
- Streamlit (multi-page apps)
- Pandas
- Plotly

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run Home.py
```

## How to Use

1. Run the app and go to the **Home** page
2. Upload a CSV or Excel file
3. Map your columns (date, revenue, profit, category, etc.)
4. Navigate to **Overview**, **Customers**, or **Returns** pages in the sidebar

---
*Built step by step as a learning project.*
