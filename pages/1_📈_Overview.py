"""
Overview Page - Key Metrics & Trends
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.load import get_data_and_mapping, prepare_data, filter_data, get_filter_options
from src.metrics import calculate_kpis, calculate_monthly_metrics, get_category_breakdown, get_region_breakdown
from src.charts import create_monthly_trend_chart, create_category_chart

# Page config
st.set_page_config(page_title="Overview | Data Dash", page_icon="📈", layout="wide")

# Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ff6b6b;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stMetricValue"] { color: #ff6b6b; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Sales Overview")
st.markdown("Key performance indicators and trends")

# Check for data
df_raw, mapping = get_data_and_mapping()

if df_raw is None or mapping is None:
    st.warning("No data loaded. Go to **Home** and upload a file first.")
    st.stop()

if mapping.get('sales') is None:
    st.warning("No revenue column set. Go to **Home** and select a Revenue column.")
    st.stop()

# Prepare and filter data
df = prepare_data(df_raw, mapping)
filter_opts = get_filter_options(df)

# Sidebar filters
st.sidebar.markdown("## 🔍 Filters")

start_date = end_date = None
if filter_opts['has_date'] and filter_opts['min_date'] is not None:
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(filter_opts['min_date'], filter_opts['max_date']),
        min_value=filter_opts['min_date'],
        max_value=filter_opts['max_date']
    )
    start_date, end_date = (date_range if len(date_range) == 2 else (date_range[0], date_range[0]))

selected_categories = None
if filter_opts['has_category'] and filter_opts['categories']:
    selected_categories = st.sidebar.multiselect("Categories", filter_opts['categories'], default=filter_opts['categories'])

selected_regions = None
if filter_opts['has_region'] and filter_opts['regions']:
    selected_regions = st.sidebar.multiselect("Regions", filter_opts['regions'], default=filter_opts['regions'])

filtered_df = filter_data(df, start_date=start_date, end_date=end_date,
                          categories=selected_categories, regions=selected_regions)

if filtered_df.empty:
    st.warning("No data matches filters. Adjust in sidebar.")
    st.stop()

# KPI Cards
kpis = calculate_kpis(filtered_df, filter_opts)

st.markdown('<p class="section-header">Key Metrics</p>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", f"${kpis['total_sales']:,.0f}")
with col2:
    if filter_opts['has_profit']:
        st.metric("Total Profit", f"${kpis['total_profit']:,.0f}", delta=f"{kpis['profit_margin']:.1f}% margin")
    else:
        st.metric("Records", f"{kpis['row_count']:,}")
with col3:
    if filter_opts['has_order_id']:
        st.metric("Total Orders", f"{kpis['total_orders']:,}")
    elif filter_opts['has_customer']:
        st.metric("Customers", f"{kpis['total_customers']:,}")
    else:
        st.metric("Avg Value", f"${kpis['total_sales']/max(kpis['row_count'],1):,.2f}")
with col4:
    if kpis['total_orders'] > 0:
        st.metric("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")
    elif filter_opts['has_quantity']:
        st.metric("Total Quantity", f"{kpis['total_quantity']:,.0f}")
    else:
        st.metric("Data Points", f"{kpis['row_count']:,}")

# Monthly Trends
if filter_opts['has_date']:
    st.markdown('<p class="section-header">📊 Trends Over Time</p>', unsafe_allow_html=True)
    monthly_data = calculate_monthly_metrics(filtered_df)
    
    if monthly_data is not None and len(monthly_data) > 1:
        available = [c for c in ['Sales', 'Profit', 'Quantity'] if c in monthly_data.columns]
        if available:
            tabs = st.tabs([f"{m} Trend" for m in available])
            for i, metric in enumerate(available):
                with tabs[i]:
                    fig = create_monthly_trend_chart(monthly_data, metric)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 months of data to show trends.")

# Category / Region Breakdown
breakdowns = []
if filter_opts['has_category']:
    breakdowns.append(('Category', get_category_breakdown(filtered_df)))
if filter_opts['has_region']:
    breakdowns.append(('Region', get_region_breakdown(filtered_df)))

if breakdowns:
    st.markdown('<p class="section-header">📦 Performance Breakdown</p>', unsafe_allow_html=True)
    cols = st.columns(len(breakdowns))
    
    for i, (name, data) in enumerate(breakdowns):
        with cols[i]:
            if data is not None and len(data) > 0:
                view = st.radio(f"{name} View", ["Bar", "Pie"], horizontal=True, key=f"{name}_view")
                fig = create_category_chart(data, 'pie' if view == "Pie" else 'bar')
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                with st.expander(f"View {name} Details"):
                    st.dataframe(data, use_container_width=True)
