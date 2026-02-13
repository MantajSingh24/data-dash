"""
Data Dash - Simple Analytics for Your Data
"""

import io
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.load import prepare_data, filter_data, get_filter_options
from src.metrics import (
    calculate_kpis, calculate_monthly_metrics, get_top_items, 
    get_category_breakdown, get_region_breakdown, get_top_customers,
    calculate_repeat_customers, get_segment_breakdown, get_return_metrics,
    get_items_by_return_rate
)
from src.charts import (
    create_monthly_trend_chart, create_top_items_chart, create_category_chart,
    create_bar_chart, create_customers_chart, create_pie_chart,
    create_return_rate_chart, create_monthly_change_chart
)

# Page configuration
st.set_page_config(
    page_title="Data Dash",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        padding-top: 0;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0;
    }
    
    /* Section title */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ffffff;
        margin: 30px 0 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Logo area */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .dd-logo {
        width: 55px;
        height: 55px;
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 800;
        color: #1a1a2e;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .tagline {
        color: #8892b0;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    
    .success-box {
        background: rgba(46, 213, 115, 0.15);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #2ed573;
        margin: 15px 0;
    }
    
    .step-card {
        background: rgba(255,255,255,0.03);
        border-radius: 15px;
        padding: 30px 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
        transition: all 0.3s;
    }
    
    .step-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 107, 107, 0.3);
        background: rgba(255,255,255,0.05);
    }
    
    .step-number {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ff6b6b, #feca57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .step-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #ffffff;
        margin: 12px 0 8px 0;
    }
    
    .step-desc {
        color: #8892b0;
        font-size: 0.9rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4);
    }
    
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .divider {
        height: 2px;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
        border-radius: 2px;
        margin: 30px 0;
        opacity: 0.7;
    }
    
    .footer {
        text-align: center;
        padding: 40px;
        color: #505050;
        font-size: 0.85rem;
        margin-top: 60px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
    }
    
    .how-to-box {
        background: rgba(72, 219, 251, 0.08);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #48dbfb;
        margin: 20px 0;
    }
    .how-to-box ol { margin: 10px 0 0 20px; color: #c0c0c0; }
    .how-to-box li { margin: 6px 0; }
    
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


def detect_column_types(df):
    """Detect and categorize column types."""
    date_cols = []
    numeric_cols = []
    category_cols = []
    
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            date_cols.append(col)
        elif df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col].head(100), errors='raise')
                date_cols.append(col)
            except:
                category_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
    
    return date_cols, numeric_cols, category_cols


def main():
    # Header with DD logo
    st.markdown("""
        <div class="logo-container">
            <div class="dd-logo">DD</div>
            <h1 class="app-title">Data Dash</h1>
        </div>
        <p class="tagline">Drop your spreadsheet, pick your columns, see all insights on one page.</p>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    
    # ---- Step 1: Upload ----
    st.markdown('<p class="section-title">📁 Step 1 — Upload your data</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop your CSV or Excel file here",
        type=['csv', 'xlsx', 'xls'],
        help="Supports CSV and Excel. For returns analysis, include a column with Yes/No or True/False for returned items."
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                raw = uploaded_file.read()
                uploaded_file.seek(0)
                for encoding in ('utf-8', 'latin-1', 'cp1252', 'iso-8859-1'):
                    try:
                        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode CSV. Try saving the file as UTF-8.")
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.data = df
            st.session_state.file_name = uploaded_file.name
            st.success(f"✓ Loaded **{uploaded_file.name}** — {len(df):,} rows × {len(df.columns)} columns")
        except Exception as e:
            st.error(f"Couldn't read file: {str(e)}")
    
    # Show currently loaded data
    if uploaded_file is None and st.session_state.data is not None:
        st.info(f"""
        ✓ **Currently loaded:** {st.session_state.get('file_name', 'Your dataset')}  
        ({len(st.session_state.data):,} rows × {len(st.session_state.data.columns)} columns)
        """)
        if st.button("🗑️ Clear data and upload new file"):
            st.session_state.data = None
            st.session_state.column_mapping = {}
            st.session_state.file_name = None
            st.rerun()
    
    # ---- No data: how it works ----
    if st.session_state.data is None:
        st.markdown("""
        <div class="how-to-box">
            <strong>How to use Data Dash</strong>
            <ol>
                <li><strong>Upload</strong> a CSV or Excel file above.</li>
                <li><strong>Map columns</strong> — choose which column is Date, Revenue, etc. (at least Revenue is required).</li>
                <li><strong>See analytics</strong> — Overview, Customers, and Returns appear below automatically.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<p class="section-title">🚀 Upload → Map → Analyze</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-title">Upload</div>
                <div class="step-desc">Drop CSV or Excel</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-title">Map</div>
                <div class="step-desc">Pick columns</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-title">Analyze</div>
                <div class="step-desc">All insights on one page</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('<div class="footer">Made with Streamlit</div>', unsafe_allow_html=True)
        return
    
    # ---- Step 2: Map columns ----
    df = st.session_state.data
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🔧 Step 2 — Map your columns</p>', unsafe_allow_html=True)
    st.caption("Your selections stay saved. At least **Revenue** is required. Use **More options** for Returns, Region, Product, etc.")
    
    date_cols, numeric_cols, category_cols = detect_column_types(df)
    all_cols = df.columns.tolist()
    
    # Helper to get the index for selectbox from session state
    def get_select_index(col_name, options_list):
        """Get index for selectbox based on session state value."""
        mapped_val = st.session_state.column_mapping.get(col_name)
        if mapped_val and mapped_val in options_list:
            return 1 + options_list.index(mapped_val)
        return 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📅 Date**")
        date_col = st.selectbox("Date", ["None"] + all_cols,
            index=get_select_index('date', all_cols) or ((1 + all_cols.index(date_cols[0])) if date_cols and date_cols[0] in all_cols else 0),
            label_visibility="collapsed", key="date_col")
        st.markdown("**💵 Revenue** *(required)*")
        sales_col = st.selectbox("Sales", ["None"] + numeric_cols,
            index=get_select_index('sales', numeric_cols),
            label_visibility="collapsed", key="sales_col")
    with col2:
        st.markdown("**📈 Profit**")
        profit_col = st.selectbox("Profit", ["None"] + numeric_cols,
            index=get_select_index('profit', numeric_cols),
            label_visibility="collapsed", key="profit_col")
        st.markdown("**🔢 Quantity**")
        quantity_col = st.selectbox("Quantity", ["None"] + numeric_cols,
            index=get_select_index('quantity', numeric_cols),
            label_visibility="collapsed", key="qty_col")
    with col3:
        st.markdown("**📦 Category**")
        category_col = st.selectbox("Category", ["None"] + all_cols,
            index=get_select_index('category', all_cols),
            label_visibility="collapsed", key="cat_col")
        st.markdown("**👤 Customer**")
        customer_col = st.selectbox("Customer", ["None"] + all_cols,
            index=get_select_index('customer', all_cols),
            label_visibility="collapsed", key="cust_col")
    
    with st.expander("⚙️ More options (Order ID, Product, Region, Segment, Discount, Returned)"):
        c1, c2, c3 = st.columns(3)
        with c1:
            order_col = st.selectbox("Order ID", ["None"] + all_cols,
                index=get_select_index('order_id', all_cols), key="order_col")
            product_col = st.selectbox("Product", ["None"] + all_cols,
                index=get_select_index('product', all_cols), key="product_col")
        with c2:
            region_col = st.selectbox("Region", ["None"] + all_cols,
                index=get_select_index('region', all_cols), key="region_col")
            segment_col = st.selectbox("Segment", ["None"] + all_cols,
                index=get_select_index('segment', all_cols), key="segment_col")
        with c3:
            discount_col = st.selectbox("Discount", ["None"] + numeric_cols,
                index=get_select_index('discount', numeric_cols), key="discount_col")
            returned_col = st.selectbox("Returned (Yes/No column)", ["None"] + all_cols,
                index=get_select_index('returned', all_cols), key="returned_col",
                help="Column with Yes/No, True/False, or 'Returned'")
    
    st.session_state.column_mapping = {
        'date': None if date_col == "None" else date_col,
        'sales': None if sales_col == "None" else sales_col,
        'profit': None if profit_col == "None" else profit_col,
        'quantity': None if quantity_col == "None" else quantity_col,
        'category': None if category_col == "None" else category_col,
        'customer': None if customer_col == "None" else customer_col,
        'order_id': None if order_col == "None" else order_col,
        'region': None if region_col == "None" else region_col,
        'segment': None if segment_col == "None" else segment_col,
        'product': None if product_col == "None" else product_col,
        'discount': None if discount_col == "None" else discount_col,
        'returned': None if returned_col == "None" else returned_col,
    }
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if st.session_state.column_mapping['sales'] is None:
        st.warning("👆 Select at least a **Revenue** column to see analytics.")
        st.markdown('<p class="section-title">👀 Preview</p>', unsafe_allow_html=True)
        st.dataframe(df.head(8), use_container_width=True)
        st.markdown('<div class="footer">Made with Streamlit</div>', unsafe_allow_html=True)
        return
    
    # ===== ANALYTICS (all on one page) =====
    st.markdown("""
    <div class="success-box">
        <strong>✓ All set!</strong> Your analytics are below. Selections stay saved. Scroll down to see Overview, Customers, and Returns.
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare data
    prepared_df = prepare_data(df, st.session_state.column_mapping)
    filter_opts = get_filter_options(prepared_df)
    
    # Sidebar filters
    st.sidebar.markdown("## 🔍 Filters")
    if filter_opts['has_date'] and filter_opts['min_date'] is not None:
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(filter_opts['min_date'], filter_opts['max_date']),
            min_value=filter_opts['min_date'],
            max_value=filter_opts['max_date']
        )
        start_date, end_date = (date_range if len(date_range) == 2 else (date_range[0], date_range[0]))
    else:
        start_date = end_date = None
    
    if filter_opts['has_category'] and filter_opts['categories']:
        selected_categories = st.sidebar.multiselect("Categories", options=filter_opts['categories'], default=filter_opts['categories'])
    else:
        selected_categories = None
    
    if filter_opts['has_region'] and filter_opts['regions']:
        selected_regions = st.sidebar.multiselect("Regions", options=filter_opts['regions'], default=filter_opts['regions'])
    else:
        selected_regions = None
    
    if filter_opts['has_segment'] and filter_opts['segments']:
        selected_segments = st.sidebar.multiselect("Segments", options=filter_opts['segments'], default=filter_opts['segments'])
    else:
        selected_segments = None
    
    filtered_df = filter_data(prepared_df, start_date=start_date, end_date=end_date,
                               categories=selected_categories, regions=selected_regions, segments=selected_segments)
    
    if filtered_df.empty:
        st.warning("No data matches filters. Adjust in sidebar.")
        st.markdown('<div class="footer">Made with Streamlit</div>', unsafe_allow_html=True)
        return
    
    kpis = calculate_kpis(filtered_df, filter_opts)
    
    # ===== OVERVIEW =====
    st.markdown('<p class="section-title">📈 Overview — Key Metrics</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Revenue", value=f"${kpis['total_sales']:,.0f}")
    with col2:
        if filter_opts['has_profit']:
            st.metric(label="Total Profit", value=f"${kpis['total_profit']:,.0f}", delta=f"{kpis['profit_margin']:.1f}% margin")
        else:
            st.metric(label="Records", value=f"{kpis['row_count']:,}")
    with col3:
        if filter_opts['has_order_id']:
            st.metric(label="Total Orders", value=f"{kpis['total_orders']:,}")
        elif filter_opts['has_customer']:
            st.metric(label="Customers", value=f"{kpis['total_customers']:,}")
        else:
            st.metric(label="Avg Value", value=f"${kpis['total_sales']/kpis['row_count']:,.2f}" if kpis['row_count'] > 0 else "$0")
    with col4:
        if kpis['total_orders'] > 0:
            st.metric(label="Avg Order Value", value=f"${kpis['avg_order_value']:,.2f}")
        elif filter_opts['has_quantity']:
            st.metric(label="Total Quantity", value=f"{kpis['total_quantity']:,.0f}")
        else:
            st.metric(label="Data Points", value=f"{kpis['row_count']:,}")
    
    if filter_opts['has_date']:
        st.markdown("#### 📊 Trends Over Time")
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
    
    breakdown_cols = []
    if filter_opts['has_category']:
        breakdown_cols.append(('Category', get_category_breakdown(filtered_df)))
    if filter_opts['has_region']:
        breakdown_cols.append(('Region', get_region_breakdown(filtered_df)))
    if breakdown_cols:
        st.markdown("#### 📦 Performance Breakdown")
        cols = st.columns(len(breakdown_cols))
        for i, (name, data) in enumerate(breakdown_cols):
            with cols[i]:
                if data is not None and len(data) > 0:
                    chart_type = st.radio(f"{name} View", ["Bar", "Pie"], horizontal=True, key=f"{name}_view")
                    fig = create_category_chart(data, 'pie' if chart_type == "Pie" else 'bar')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
    
    if filter_opts['has_product']:
        st.markdown("#### 🏆 Top Products")
        col1, col2 = st.columns([2, 1])
        with col1:
            top_n = st.slider("Number of products", 5, 20, 10, key="top_prod_slider")
            available_metrics = ['Sales'] + (['Profit'] if filter_opts['has_profit'] else []) + (['Quantity'] if filter_opts['has_quantity'] else [])
            metric_choice = st.radio("Rank by", available_metrics, horizontal=True, key="product_metric")
            top_products = get_top_items(filtered_df, '_product', n=top_n, by=metric_choice)
            if top_products is not None:
                fig = create_top_items_chart(top_products, metric_choice)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        with col2:
            if top_products is not None:
                display_cols = [c for c in ['Name', 'Sales', 'Profit', 'Quantity'] if c in top_products.columns]
                format_dict = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Quantity': '{:,.0f}'}
                st.dataframe(top_products[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}), use_container_width=True, height=400)
    
    # ===== CUSTOMERS =====
    if filter_opts['has_customer']:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-title">👥 Customers — Top Buyers & Loyalty</p>', unsafe_allow_html=True)
        total_customers, repeat_customers, repeat_rate = calculate_repeat_customers(filtered_df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Customers", value=f"{total_customers:,}")
        with col2:
            st.metric(label="Repeat Customers", value=f"{repeat_customers:,}", delta=f"{repeat_rate:.1f}% of total")
        with col3:
            avg_per_customer = kpis['total_sales'] / total_customers if total_customers > 0 else 0
            st.metric(label="Avg Revenue/Customer", value=f"${avg_per_customer:,.0f}")
        with col4:
            if filter_opts['has_order_id']:
                avg_orders = kpis['total_orders'] / total_customers if total_customers > 0 else 0
                st.metric(label="Avg Orders/Customer", value=f"{avg_orders:.2f}")
            else:
                st.metric(label="Total Revenue", value=f"${kpis['total_sales']:,.0f}")
        
        st.markdown("#### 🏆 Top Customers")
        col1, col2 = st.columns([2, 1])
        with col1:
            top_n_cust = st.slider("Number of customers", 5, 20, 10, key="top_cust_slider")
            top_customers = get_top_customers(filtered_df, n=top_n_cust)
            if top_customers is not None and len(top_customers) > 0:
                fig = create_customers_chart(top_customers)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        with col2:
            if top_customers is not None and len(top_customers) > 0:
                display_cols = [c for c in ['Customer', 'Sales', 'Profit', 'Orders'] if c in top_customers.columns]
                format_dict = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Orders': '{:,}'}
                st.dataframe(top_customers[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}), use_container_width=True, height=400)
    
    # ===== RETURNS =====
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🔄 Returns — Return Rate & Problem Products</p>', unsafe_allow_html=True)
    has_returns = filter_opts['has_returned']
    if has_returns:
        return_metrics = get_return_metrics(filtered_df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Orders", value=f"{return_metrics['total_orders']:,}")
        with col2:
            st.metric(label="Returned Orders", value=f"{return_metrics['returned_orders']:,}", delta=f"-{return_metrics['return_rate']:.1f}%", delta_color="inverse")
        with col3:
            st.metric(label="Return Rate", value=f"{return_metrics['return_rate']:.1f}%")
        with col4:
            if filter_opts['has_profit']:
                st.metric(label="Lost Profit", value=f"${abs(return_metrics['returned_profit_loss']):,.0f}", delta="from returns", delta_color="off")
            else:
                st.metric(label="Returned Sales", value=f"${return_metrics['returned_sales']:,.0f}")
        
        if filter_opts['has_product']:
            st.markdown("#### ⚠️ Problem Products")
            col1, col2 = st.columns([2, 1])
            with col1:
                top_n_ret = st.slider("Number of products", 5, 15, 10, key="problem_prod_slider")
                prod_returns = get_items_by_return_rate(filtered_df, '_product', 'Product', n=top_n_ret)
                if prod_returns is not None and len(prod_returns) > 0:
                    fig = create_return_rate_chart(prod_returns)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            with col2:
                if prod_returns is not None and len(prod_returns) > 0:
                    display_cols = [c for c in ['Product', 'Total Orders', 'Returns', 'Return Rate'] if c in prod_returns.columns]
                    format_dict = {'Total Orders': '{:,}', 'Returns': '{:,}', 'Return Rate': '{:.1f}%'}
                    st.dataframe(prod_returns[display_cols].style.format({k: v for k, v in format_dict.items() if k in display_cols}), use_container_width=True, height=400)
    else:
        st.info("""
        ℹ️ **No return column in dataset.**  
        To see return analytics, scroll up and map a 'Returned' column (in **More options**).  
        The column should contain Yes/No, True/False, or similar values.
        """)
    
    st.markdown('<p class="section-title">👀 Data Preview</p>', unsafe_allow_html=True)
    st.dataframe(df.head(8), use_container_width=True)
    st.markdown('<div class="footer">Made with Streamlit</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
