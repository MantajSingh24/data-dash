"""
Customers Page - Customer Analytics and Segmentation
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.load import get_data_and_mapping, prepare_data, filter_data, get_filter_options
from src.metrics import calculate_kpis, get_top_customers, calculate_repeat_customers, get_segment_breakdown, get_region_breakdown
from src.charts import create_customers_chart, create_pie_chart, create_bar_chart

# Page config
st.set_page_config(
    page_title="Customers | Data Dash",
    page_icon="👥",
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
        border-bottom: 2px solid #48dbfb;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stMetricValue"] {
        color: #48dbfb;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("👥 Customer Insights")
st.markdown("Customer analytics, top buyers, and loyalty metrics")

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

# Check if customer data is available
if not filter_opts['has_customer']:
    st.info("💡 **Tip:** To see customer analytics, go to Home and select a Customer ID column in the configuration.")
    st.markdown("---")
    st.markdown("### What you can see with customer data:")
    st.markdown("""
    - Top customers by revenue
    - Repeat customer rate
    - Customer segmentation
    - Regional customer distribution
    """)
    st.stop()

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
    regions=selected_regions,
    segments=selected_segments
)

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# Calculate metrics
kpis = calculate_kpis(filtered_df, filter_opts)
total_customers, repeat_customers, repeat_rate = calculate_repeat_customers(filtered_df)

# Customer KPIs
st.markdown('<p class="section-header">Customer Metrics</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Customers",
        value=f"{total_customers:,}"
    )

with col2:
    st.metric(
        label="Repeat Customers",
        value=f"{repeat_customers:,}",
        delta=f"{repeat_rate:.1f}% of total"
    )

with col3:
    avg_per_customer = kpis['total_sales'] / total_customers if total_customers > 0 else 0
    st.metric(
        label="Avg Revenue/Customer",
        value=f"${avg_per_customer:,.0f}"
    )

with col4:
    if filter_opts['has_order_id']:
        avg_orders = kpis['total_orders'] / total_customers if total_customers > 0 else 0
        st.metric(
            label="Avg Orders/Customer",
            value=f"{avg_orders:.2f}"
        )
    else:
        st.metric(
            label="Total Revenue",
            value=f"${kpis['total_sales']:,.0f}"
        )

# Customer Segmentation (if available)
if filter_opts['has_segment']:
    st.markdown('<p class="section-header">📊 Customer Segmentation</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        segment_data = get_segment_breakdown(filtered_df)
        if segment_data is not None:
            fig = create_pie_chart(segment_data, 'Sales', 'Segment', 'Revenue by Segment')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Segment Performance")
        if segment_data is not None:
            display_cols = [c for c in ['Segment', 'Sales', 'Profit', 'Customers', 'Avg Order Value'] if c in segment_data.columns]
            format_dict = {
                'Sales': '${:,.0f}',
                'Profit': '${:,.0f}',
                'Customers': '{:,}',
                'Avg Order Value': '${:,.2f}'
            }
            st.dataframe(
                segment_data[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
                use_container_width=True
            )
            
            # Top segment insight
            top_seg = segment_data.iloc[0]
            st.info(f"**Top Segment:** {top_seg['Segment']} with ${top_seg['Sales']:,.0f} revenue")

# Top Customers
st.markdown('<p class="section-header">🏆 Top Customers</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    top_n = st.slider("Number of customers", 5, 20, 10)
    top_customers = get_top_customers(filtered_df, n=top_n)
    
    if top_customers is not None and len(top_customers) > 0:
        fig = create_customers_chart(top_customers)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer data available for chart.")

with col2:
    st.markdown("#### Top Customers Table")
    if top_customers is not None and len(top_customers) > 0:
        display_cols = [c for c in ['Customer', 'Sales', 'Profit', 'Orders'] if c in top_customers.columns]
        format_dict = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Orders': '{:,}'}
        st.dataframe(
            top_customers[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
            use_container_width=True,
            height=400
        )

# Regional Analysis (if available)
if filter_opts['has_region']:
    st.markdown('<p class="section-header">🌎 Customers by Region</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        region_data = get_region_breakdown(filtered_df)
        if region_data is not None:
            fig = create_bar_chart(region_data, 'Region', 'Sales', 'Revenue by Region', color_by='Profit' if 'Profit' in region_data.columns else None)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Regional Breakdown")
        if region_data is not None:
            display_cols = [c for c in ['Region', 'Sales', 'Profit', 'Customers', 'Orders'] if c in region_data.columns]
            format_dict = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Customers': '{:,}', 'Orders': '{:,}'}
            st.dataframe(
                region_data[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
                use_container_width=True
            )

# Customer Loyalty Analysis
st.markdown('<p class="section-header">🔄 Customer Loyalty</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Order frequency distribution
    if filter_opts['has_order_id']:
        customer_orders = filtered_df.groupby('_customer')['_order_id'].nunique().reset_index()
        customer_orders.columns = ['Customer', 'Order Count']
    else:
        customer_orders = filtered_df.groupby('_customer').size().reset_index()
        customer_orders.columns = ['Customer', 'Order Count']
    
    # Create frequency buckets
    order_bins = [1, 2, 3, 5, 10, float('inf')]
    order_labels = ['1 order', '2 orders', '3-4 orders', '5-9 orders', '10+ orders']
    customer_orders['Frequency'] = pd.cut(
        customer_orders['Order Count'],
        bins=order_bins,
        labels=order_labels,
        right=False
    )
    
    freq_dist = customer_orders['Frequency'].value_counts().sort_index()
    
    import plotly.express as px
    fig = px.bar(
        x=freq_dist.index.astype(str),
        y=freq_dist.values,
        title='Customer Order Frequency',
        labels={'x': 'Order Frequency', 'y': 'Number of Customers'},
        color=freq_dist.values,
        color_continuous_scale='Purples'
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Loyalty Breakdown")
    
    one_time = (customer_orders['Order Count'] == 1).sum()
    multi_order = (customer_orders['Order Count'] >= 2).sum()
    loyal = (customer_orders['Order Count'] >= 3).sum()
    
    st.metric("One-Time Customers", f"{one_time:,}", f"{one_time/total_customers*100:.1f}%" if total_customers > 0 else "0%")
    st.metric("Multi-Order Customers (2+)", f"{multi_order:,}", f"{multi_order/total_customers*100:.1f}%" if total_customers > 0 else "0%")
    st.metric("Loyal Customers (3+)", f"{loyal:,}", f"{loyal/total_customers*100:.1f}%" if total_customers > 0 else "0%")

# Key Insights
st.markdown('<p class="section-header">💡 Key Insights</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.success(f"""
    **Repeat Rate:** {repeat_rate:.1f}%  
    {repeat_customers:,} customers made 2+ purchases
    """)

with col2:
    if filter_opts['has_region'] and region_data is not None and len(region_data) > 0:
        best_region = region_data.iloc[0]
        cust_count = best_region.get('Customers', 'N/A')
        st.info(f"""
        **Top Region:** {best_region['Region']}  
        {cust_count if isinstance(cust_count, str) else f'{cust_count:,}'} customers
        """)
    else:
        st.info(f"""
        **Total Customers:** {total_customers:,}  
        Generating ${kpis['total_sales']:,.0f} revenue
        """)

with col3:
    if top_customers is not None and len(top_customers) > 0:
        top_cust = top_customers.iloc[0]
        st.warning(f"""
        **Top Customer:** {top_cust['Customer'][:20]}{'...' if len(str(top_cust['Customer'])) > 20 else ''}  
        ${top_cust['Sales']:,.0f} lifetime value
        """)
