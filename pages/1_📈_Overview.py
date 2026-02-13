"""
Overview Page - Key Performance Indicators and Trends
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.load import get_data_and_mapping, prepare_data, filter_data, get_filter_options
from src.metrics import calculate_kpis, calculate_monthly_metrics, get_top_items, get_category_breakdown, get_region_breakdown
from src.charts import create_monthly_trend_chart, create_top_items_chart, create_category_chart, create_bar_chart

# Page config
st.set_page_config(
    page_title="Overview | Data Dash",
    page_icon="📈",
    layout="wide"
)

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
    
    [data-testid="stMetricValue"] {
        color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📈 Sales Overview")
st.markdown("Key performance indicators and trends")

# Check for data
df_raw, mapping = get_data_and_mapping()

if df_raw is None or mapping is None:
    st.warning("⚠️ No data loaded. Please go to the **Home** page and upload a file first.")
    st.stop()

if mapping.get('sales') is None:
    st.warning("⚠️ No sales column configured. Please go to **Home** and select a Sales/Revenue column.")
    st.stop()

# Prepare data
df = prepare_data(df_raw, mapping)
filter_opts = get_filter_options(df)

# Sidebar filters
st.sidebar.markdown("## 🔍 Filters")

# Date filter
if filter_opts['has_date'] and filter_opts['min_date'] is not None:
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(filter_opts['min_date'], filter_opts['max_date']),
        min_value=filter_opts['min_date'],
        max_value=filter_opts['max_date']
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]
else:
    start_date = end_date = None

# Category filter
if filter_opts['has_category'] and filter_opts['categories']:
    selected_categories = st.sidebar.multiselect(
        "Categories",
        options=filter_opts['categories'],
        default=filter_opts['categories']
    )
else:
    selected_categories = None

# Region filter
if filter_opts['has_region'] and filter_opts['regions']:
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=filter_opts['regions'],
        default=filter_opts['regions']
    )
else:
    selected_regions = None

# Segment filter
if filter_opts['has_segment'] and filter_opts['segments']:
    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=filter_opts['segments'],
        default=filter_opts['segments']
    )
else:
    selected_segments = None

# Apply filters
filtered_df = filter_data(
    df,
    start_date=start_date,
    end_date=end_date,
    categories=selected_categories,
    regions=selected_regions,
    segments=selected_segments
)

if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust your selection.")
    st.stop()

# Calculate KPIs
kpis = calculate_kpis(filtered_df, filter_opts)

# KPI Cards
st.markdown('<p class="section-header">Key Metrics</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value=f"${kpis['total_sales']:,.0f}" if kpis['total_sales'] >= 1000 else f"${kpis['total_sales']:,.2f}",
        help="Sum of all sales"
    )

with col2:
    if filter_opts['has_profit']:
        st.metric(
            label="Total Profit",
            value=f"${kpis['total_profit']:,.0f}" if abs(kpis['total_profit']) >= 1000 else f"${kpis['total_profit']:,.2f}",
            delta=f"{kpis['profit_margin']:.1f}% margin"
        )
    else:
        st.metric(
            label="Records",
            value=f"{kpis['row_count']:,}",
            help="Number of records"
        )

with col3:
    if filter_opts['has_order_id']:
        st.metric(
            label="Total Orders",
            value=f"{kpis['total_orders']:,}"
        )
    elif filter_opts['has_customer']:
        st.metric(
            label="Customers",
            value=f"{kpis['total_customers']:,}"
        )
    else:
        st.metric(
            label="Avg Value",
            value=f"${kpis['total_sales']/kpis['row_count']:,.2f}" if kpis['row_count'] > 0 else "$0"
        )

with col4:
    if kpis['total_orders'] > 0:
        st.metric(
            label="Avg Order Value",
            value=f"${kpis['avg_order_value']:,.2f}"
        )
    elif filter_opts['has_quantity']:
        st.metric(
            label="Total Quantity",
            value=f"{kpis['total_quantity']:,.0f}"
        )
    else:
        st.metric(
            label="Data Points",
            value=f"{kpis['row_count']:,}"
        )

# Trends Section
if filter_opts['has_date']:
    st.markdown('<p class="section-header">📊 Trends Over Time</p>', unsafe_allow_html=True)
    
    monthly_data = calculate_monthly_metrics(filtered_df)
    
    if monthly_data is not None and len(monthly_data) > 1:
        available_metrics = [col for col in ['Sales', 'Profit', 'Quantity'] if col in monthly_data.columns]
        
        if available_metrics:
            tabs = st.tabs([f"{m} Trend" for m in available_metrics])
            
            for i, metric in enumerate(available_metrics):
                with tabs[i]:
                    fig = create_monthly_trend_chart(monthly_data, metric)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough time-based data to show trends. Need at least 2 months of data.")

# Category/Region Breakdown
breakdown_cols = []
if filter_opts['has_category']:
    breakdown_cols.append(('Category', get_category_breakdown(filtered_df)))
if filter_opts['has_region']:
    breakdown_cols.append(('Region', get_region_breakdown(filtered_df)))

if breakdown_cols:
    st.markdown('<p class="section-header">📦 Performance Breakdown</p>', unsafe_allow_html=True)
    
    cols = st.columns(len(breakdown_cols))
    
    for i, (name, data) in enumerate(breakdown_cols):
        with cols[i]:
            if data is not None and len(data) > 0:
                chart_type = st.radio(f"{name} View", ["Bar", "Pie"], horizontal=True, key=f"{name}_view")
                fig = create_category_chart(data, 'pie' if chart_type == "Pie" else 'bar')
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                with st.expander(f"View {name} Details"):
                    display_cols = [c for c in ['Sales', 'Profit', 'Orders', 'Customers', 'Profit Margin'] if c in data.columns]
                    format_dict = {
                        'Sales': '${:,.0f}',
                        'Profit': '${:,.0f}',
                        'Orders': '{:,}',
                        'Customers': '{:,}',
                        'Profit Margin': '{:.1f}%'
                    }
                    st.dataframe(
                        data[[name] + display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
                        use_container_width=True
                    )

# Top Products/Items Section
if filter_opts['has_product']:
    st.markdown('<p class="section-header">🏆 Top Products</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_n = st.slider("Number of products", 5, 20, 10)
        available_metrics = ['Sales'] + (['Profit'] if filter_opts['has_profit'] else []) + (['Quantity'] if filter_opts['has_quantity'] else [])
        metric_choice = st.radio("Rank by", available_metrics, horizontal=True)
        
        top_products = get_top_items(filtered_df, '_product', n=top_n, by=metric_choice)
        
        if top_products is not None:
            fig = create_top_items_chart(top_products, metric_choice)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top Products Table")
        if top_products is not None:
            display_cols = [c for c in ['Name', 'Sales', 'Profit', 'Quantity'] if c in top_products.columns]
            format_dict = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Quantity': '{:,.0f}'}
            st.dataframe(
                top_products[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
                use_container_width=True,
                height=400
            )

# Insights Section
st.markdown('<p class="section-header">💡 Key Insights</p>', unsafe_allow_html=True)

insights = []

# Best month insight
if filter_opts['has_date'] and monthly_data is not None and len(monthly_data) > 0:
    best_month = monthly_data.loc[monthly_data['Sales'].idxmax()]
    insights.append(f"**Best Month:** {best_month['Month']} with ${best_month['Sales']:,.0f} in revenue")

# Top category insight
if filter_opts['has_category']:
    cat_data = get_category_breakdown(filtered_df)
    if cat_data is not None and len(cat_data) > 0:
        top_cat = cat_data.iloc[0]
        insights.append(f"**Top Category:** {top_cat['Category']} (${top_cat['Sales']:,.0f})")

# Top region insight
if filter_opts['has_region']:
    reg_data = get_region_breakdown(filtered_df)
    if reg_data is not None and len(reg_data) > 0:
        top_reg = reg_data.iloc[0]
        insights.append(f"**Top Region:** {top_reg['Region']} (${top_reg['Sales']:,.0f})")

if insights:
    cols = st.columns(len(insights))
    for i, insight in enumerate(insights):
        with cols[i]:
            st.info(insight)
else:
    st.info("Add more column mappings (Date, Category, Region) to see insights.")
