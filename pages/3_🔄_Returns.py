"""
Returns Page - Returns Analysis and Anomaly Detection
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.load import get_data_and_mapping, prepare_data, filter_data, get_filter_options
from src.metrics import get_return_metrics, get_items_by_return_rate, calculate_monthly_metrics
from src.charts import create_return_rate_chart, create_monthly_change_chart, create_bar_chart

# Page config
st.set_page_config(
    page_title="Returns & Trends | Data Dash",
    page_icon="🔄",
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
        border-bottom: 2px solid #feca57;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stMetricValue"] {
        color: #feca57;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🔄 Returns & Anomalies")
st.markdown("Return analysis, problem areas, and trend anomalies")

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

# Apply filters
filtered_df = filter_data(
    df,
    start_date=start_date,
    end_date=end_date,
    categories=selected_categories,
    regions=selected_regions
)

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# Initialize so Key Insights never hits undefined variables
monthly_data = None
drops = pd.DataFrame()
cat_returns = None
prod_returns = None
return_metrics = None

# Check if return data is available
has_returns = filter_opts['has_returned']

if has_returns:
    # Return Metrics Section
    return_metrics = get_return_metrics(filtered_df)
    
    st.markdown('<p class="section-header">Return Metrics</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Orders",
            value=f"{return_metrics['total_orders']:,}"
        )
    
    with col2:
        st.metric(
            label="Returned Orders",
            value=f"{return_metrics['returned_orders']:,}",
            delta=f"-{return_metrics['return_rate']:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Return Rate",
            value=f"{return_metrics['return_rate']:.1f}%"
        )
    
    with col4:
        if filter_opts['has_profit']:
            st.metric(
                label="Lost Profit",
                value=f"${abs(return_metrics['returned_profit_loss']):,.0f}",
                delta="from returns",
                delta_color="off"
            )
        else:
            st.metric(
                label="Returned Sales",
                value=f"${return_metrics['returned_sales']:,.0f}"
            )
    
    # Returns by Category
    if filter_opts['has_category']:
        st.markdown('<p class="section-header">📦 Returns by Category</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            cat_returns = get_items_by_return_rate(filtered_df, '_category', 'Category', n=20)
            if cat_returns is not None and len(cat_returns) > 0:
                fig = create_return_rate_chart(cat_returns)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No returns found in categories.")
        
        with col2:
            st.markdown("#### Category Return Details")
            if cat_returns is not None and len(cat_returns) > 0:
                display_cols = [c for c in ['Category', 'Total Orders', 'Returns', 'Return Rate', 'Profit'] if c in cat_returns.columns]
                format_dict = {
                    'Total Orders': '{:,}',
                    'Returns': '{:,}',
                    'Return Rate': '{:.1f}%',
                    'Profit': '${:,.0f}'
                }
                st.dataframe(
                    cat_returns[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
                    use_container_width=True
                )
                
                worst_cat = cat_returns.iloc[0]
                st.error(f"""
                **Highest Return Rate:** {worst_cat['Category']}  
                {worst_cat['Return Rate']:.1f}% return rate ({worst_cat['Returns']:,} returns)
                """)
    
    # Returns by Product
    if filter_opts['has_product']:
        st.markdown('<p class="section-header">⚠️ Problem Products</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_n = st.slider("Number of products", 5, 15, 10)
            prod_returns = get_items_by_return_rate(filtered_df, '_product', 'Product', n=top_n)
            
            if prod_returns is not None and len(prod_returns) > 0:
                fig = create_return_rate_chart(prod_returns)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No products with returns found.")
        
        with col2:
            st.markdown("#### Products by Return Rate")
            if prod_returns is not None and len(prod_returns) > 0:
                display_cols = [c for c in ['Product', 'Total Orders', 'Returns', 'Return Rate'] if c in prod_returns.columns]
                format_dict = {'Total Orders': '{:,}', 'Returns': '{:,}', 'Return Rate': '{:.1f}%'}
                st.dataframe(
                    prod_returns[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}),
                    use_container_width=True,
                    height=400
                )

else:
    st.info("""
    ℹ️ **No return column found in dataset.**  
    To see return analytics, go to the **Home** page and map a 'Returned' column (in **More options**).  
    The column should contain Yes/No, True/False, or similar values indicating returned orders.
    """)

# Month-over-Month Trends (always show if date available)
if filter_opts['has_date']:
    st.markdown('<p class="section-header">📈 Month-over-Month Trends</p>', unsafe_allow_html=True)
    
    monthly_data = calculate_monthly_metrics(filtered_df)
    
    if monthly_data is not None and len(monthly_data) > 1 and 'Sales Change' in monthly_data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_monthly_change_chart(monthly_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Monthly Performance")
            
            # Find drops
            drops = monthly_data[monthly_data['Sales Change'] < 0].sort_values('Sales Change')
            
            if len(drops) > 0:
                st.markdown("**Months with Decline:**")
                for _, row in drops.head(3).iterrows():
                    st.warning(f"""
                    **{row['Month']}:** {row['Sales Change']:.1f}% change  
                    Revenue: ${row['Sales']:,.0f}
                    """)
            else:
                st.success("No significant revenue drops detected!")
            
            # Best growth
            gains = monthly_data[monthly_data['Sales Change'] > 0].sort_values('Sales Change', ascending=False)
            if len(gains) > 0:
                best = gains.iloc[0]
                st.success(f"""
                **Best Growth:** {best['Month']}  
                +{best['Sales Change']:.1f}% increase
                """)
        
        # Monthly data table
        st.markdown("#### Monthly Breakdown")
        display_cols = [c for c in ['Month', 'Sales', 'Profit', 'Sales Change', 'Profit Change'] if c in monthly_data.columns]
        format_dict = {
            'Sales': '${:,.0f}',
            'Profit': '${:,.0f}',
            'Sales Change': '{:+.1f}%',
            'Profit Change': '{:+.1f}%'
        }
        
        # Fill NaN for display
        display_data = monthly_data[display_cols].copy()
        display_data = display_data.fillna(0)
        
        st.dataframe(
            display_data.style.format({k: v for k, v in format_dict.items() if k in display_cols})
            .background_gradient(subset=[c for c in ['Sales Change'] if c in display_cols], cmap='RdYlGn', vmin=-50, vmax=50),
            use_container_width=True
        )
    else:
        st.info("Need at least 2 months of data to show trends.")

# Key Insights
st.markdown('<p class="section-header">💡 Key Insights</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if has_returns:
        if return_metrics['return_rate'] > 10:
            st.error(f"""
            **High Return Rate Alert**  
            {return_metrics['return_rate']:.1f}% is above 10%  
            Consider investigating quality issues
            """)
        elif return_metrics['return_rate'] > 5:
            st.warning(f"""
            **Moderate Return Rate**  
            {return_metrics['return_rate']:.1f}% returns  
            Room for improvement
            """)
        else:
            st.success(f"""
            **Healthy Return Rate**  
            {return_metrics['return_rate']:.1f}% returns  
            Within acceptable range
            """)
    else:
        st.info("Add a return status column to see return insights")

with col2:
    if has_returns and filter_opts['has_category']:
        if cat_returns is not None and len(cat_returns) > 0:
            worst = cat_returns.iloc[0]
            st.warning(f"""
            **Focus Area:** {worst['Category']}  
            {worst['Return Rate']:.1f}% return rate  
            Investigate quality or expectations
            """)
    elif filter_opts['has_date'] and monthly_data is not None:
        if len(drops) > 0:
            worst_drop = drops.iloc[0]
            st.warning(f"""
            **Biggest Drop:** {worst_drop['Month']}  
            {worst_drop['Sales Change']:.1f}% decline  
            Check for seasonal/external factors
            """)
        else:
            st.success("Consistent growth trend!")

with col3:
    if filter_opts['has_date'] and monthly_data is not None and len(monthly_data) > 0:
        latest = monthly_data.iloc[-1]
        prev = monthly_data.iloc[-2] if len(monthly_data) > 1 else None
        
        if prev is not None and 'Sales Change' in latest:
            change = latest['Sales Change'] if pd.notna(latest['Sales Change']) else 0
            if change >= 0:
                st.success(f"""
                **Latest Month:** {latest['Month']}  
                ${latest['Sales']:,.0f} revenue  
                {'+' if change >= 0 else ''}{change:.1f}% vs previous
                """)
            else:
                st.warning(f"""
                **Latest Month:** {latest['Month']}  
                ${latest['Sales']:,.0f} revenue  
                {change:.1f}% vs previous
                """)
        else:
            st.info(f"""
            **Latest Month:** {latest['Month']}  
            ${latest['Sales']:,.0f} revenue
            """)
