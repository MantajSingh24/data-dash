"""
Customers Page - Customer Analytics & Top Buyers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.load import get_data_and_mapping, prepare_data, filter_data, get_filter_options
from src.metrics import calculate_kpis, get_top_customers, calculate_repeat_customers, get_segment_breakdown, get_region_breakdown
from src.charts import create_customers_chart, create_pie_chart, create_bar_chart

# Page config
st.set_page_config(page_title="Customers | Data Dash", page_icon="👥", layout="wide")

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
    
    [data-testid="stMetricValue"] { color: #48dbfb; }
</style>
""", unsafe_allow_html=True)

st.title("👥 Customer Insights")
st.markdown("Customer analytics, top buyers, and loyalty metrics")

# Check for data
df_raw, mapping = get_data_and_mapping()

if df_raw is None or mapping is None:
    st.warning("No data loaded. Go to **Home** and upload a file first.")
    st.stop()

if mapping.get('sales') is None:
    st.warning("No revenue column set. Go to **Home** and select a Revenue column.")
    st.stop()

# Prepare data
df = prepare_data(df_raw, mapping)
filter_opts = get_filter_options(df)

if not filter_opts['has_customer']:
    st.info("To see customer analytics, go to Home and map a **Customer** column.")
    st.markdown("---")
    st.markdown("### With customer data you can see:")
    st.markdown("- Top customers by revenue\n- Repeat customer rate\n- Customer segmentation\n- Loyalty analysis")
    st.stop()

# Sidebar filters
st.sidebar.markdown("## 🔍 Filters")

start_date = end_date = None
if filter_opts['has_date'] and filter_opts['min_date'] is not None:
    date_range = st.sidebar.date_input("Date Range",
        value=(filter_opts['min_date'], filter_opts['max_date']),
        min_value=filter_opts['min_date'], max_value=filter_opts['max_date'])
    start_date, end_date = (date_range if len(date_range) == 2 else (date_range[0], date_range[0]))

selected_regions = None
if filter_opts['has_region'] and filter_opts['regions']:
    selected_regions = st.sidebar.multiselect("Regions", filter_opts['regions'], default=filter_opts['regions'])

selected_segments = None
if filter_opts['has_segment'] and filter_opts['segments']:
    selected_segments = st.sidebar.multiselect("Segments", filter_opts['segments'], default=filter_opts['segments'])

filtered_df = filter_data(df, start_date=start_date, end_date=end_date,
                          regions=selected_regions, segments=selected_segments)

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# Customer KPIs
kpis = calculate_kpis(filtered_df, filter_opts)
total_customers, repeat_customers, repeat_rate = calculate_repeat_customers(filtered_df)

st.markdown('<p class="section-header">Customer Metrics</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Repeat Customers", f"{repeat_customers:,}", delta=f"{repeat_rate:.1f}% of total")
with col3:
    avg_rev = kpis['total_sales'] / total_customers if total_customers > 0 else 0
    st.metric("Avg Revenue/Customer", f"${avg_rev:,.0f}")
with col4:
    if filter_opts['has_order_id']:
        avg_orders = kpis['total_orders'] / total_customers if total_customers > 0 else 0
        st.metric("Avg Orders/Customer", f"{avg_orders:.2f}")
    else:
        st.metric("Total Revenue", f"${kpis['total_sales']:,.0f}")

# Segmentation
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
            st.dataframe(segment_data, use_container_width=True)

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

with col2:
    st.markdown("#### Top Customers Table")
    if top_customers is not None and len(top_customers) > 0:
        display_cols = [c for c in ['Customer', 'Sales', 'Profit', 'Orders'] if c in top_customers.columns]
        st.dataframe(top_customers[display_cols], use_container_width=True, height=400)

# Loyalty Analysis
st.markdown('<p class="section-header">🔄 Customer Loyalty</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if '_order_id' in filtered_df.columns:
        customer_orders = filtered_df.groupby('_customer')['_order_id'].nunique().reset_index()
    else:
        customer_orders = filtered_df.groupby('_customer').size().reset_index()
    customer_orders.columns = ['Customer', 'Order Count']
    
    order_bins = [1, 2, 3, 5, 10, float('inf')]
    order_labels = ['1 order', '2 orders', '3-4 orders', '5-9 orders', '10+ orders']
    customer_orders['Frequency'] = pd.cut(customer_orders['Order Count'],
                                          bins=order_bins, labels=order_labels, right=False)
    
    freq_dist = customer_orders['Frequency'].value_counts().sort_index()
    fig = px.bar(x=freq_dist.index.astype(str), y=freq_dist.values,
                 title='Customer Order Frequency',
                 labels={'x': 'Order Frequency', 'y': 'Number of Customers'},
                 color=freq_dist.values, color_continuous_scale='Purples')
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Loyalty Breakdown")
    one_time = (customer_orders['Order Count'] == 1).sum()
    multi = (customer_orders['Order Count'] >= 2).sum()
    loyal = (customer_orders['Order Count'] >= 3).sum()
    
    st.metric("One-Time Customers", f"{one_time:,}",
              f"{one_time/total_customers*100:.1f}%" if total_customers > 0 else "0%")
    st.metric("Multi-Order (2+)", f"{multi:,}",
              f"{multi/total_customers*100:.1f}%" if total_customers > 0 else "0%")
    st.metric("Loyal (3+)", f"{loyal:,}",
              f"{loyal/total_customers*100:.1f}%" if total_customers > 0 else "0%")

# Insights
st.markdown('<p class="section-header">💡 Key Insights</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.success(f"**Repeat Rate:** {repeat_rate:.1f}% — {repeat_customers:,} customers made 2+ purchases")

with col2:
    if top_customers is not None and len(top_customers) > 0:
        top = top_customers.iloc[0]
        st.info(f"**Top Customer:** {str(top['Customer'])[:25]} — ${top['Sales']:,.0f} revenue")
