"""
Data Dash - Home Page
Upload data and map columns here. Analytics pages appear in the sidebar.
"""

import io
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Data Dash",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    
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
    }
    
    .tagline {
        color: #8892b0;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #ffffff;
        margin: 30px 0 15px 0;
    }
    
    .divider {
        height: 2px;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
        border-radius: 2px;
        margin: 30px 0;
        opacity: 0.7;
    }
    
    .step-card {
        background: rgba(255,255,255,0.03);
        border-radius: 15px;
        padding: 30px 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    .step-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ff6b6b, #feca57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .step-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 10px 0 5px 0;
    }
    
    .step-desc { color: #8892b0; font-size: 0.9rem; }
    
    .success-box {
        background: rgba(46, 213, 115, 0.15);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #2ed573;
        margin: 15px 0;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stMetricValue"] { color: #ff6b6b; }
    
    .footer {
        text-align: center;
        padding: 40px;
        color: #505050;
        font-size: 0.85rem;
        margin-top: 60px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def detect_column_types(df):
    """Detect date, numeric, and category columns."""
    date_cols, numeric_cols, category_cols = [], [], []
    
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
    # Header
    st.markdown("""
        <div class="logo-container">
            <div class="dd-logo">DD</div>
            <h1 class="app-title">Data Dash</h1>
        </div>
        <p class="tagline">Upload your data, map columns, explore insights in the sidebar pages.</p>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Session state init
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    
    # --- Step 1: Upload ---
    st.markdown('<p class="section-title">📁 Step 1 — Upload your data</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop your CSV or Excel file here",
        type=['csv', 'xlsx', 'xls'],
        help="Supports CSV and Excel files"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                raw = uploaded_file.read()
                uploaded_file.seek(0)
                for encoding in ('utf-8', 'latin-1', 'cp1252'):
                    try:
                        df = pd.read_csv(io.BytesIO(raw), encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode CSV. Try saving as UTF-8.")
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.data = df
            st.session_state.file_name = uploaded_file.name
            st.success(f"Loaded **{uploaded_file.name}** — {len(df):,} rows x {len(df.columns)} columns")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    # Show loaded data info
    if uploaded_file is None and st.session_state.data is not None:
        st.info(f"Currently loaded: **{st.session_state.file_name}** ({len(st.session_state.data):,} rows)")
        if st.button("Clear data"):
            st.session_state.data = None
            st.session_state.column_mapping = {}
            st.session_state.file_name = None
            st.rerun()
    
    # --- No data: show instructions ---
    if st.session_state.data is None:
        st.markdown("---")
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
                <div class="step-desc">Pick your columns</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-title">Explore</div>
                <div class="step-desc">Open pages in sidebar</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('<div class="footer">Made with Streamlit</div>', unsafe_allow_html=True)
        return
    
    # --- Step 2: Map columns ---
    df = st.session_state.data
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🔧 Step 2 — Map your columns</p>', unsafe_allow_html=True)
    st.caption("Tell the app which columns are what. At minimum, pick a **Revenue** column.")
    
    date_cols, numeric_cols, category_cols = detect_column_types(df)
    all_cols = df.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📅 Date**")
        date_col = st.selectbox("Date", ["None"] + all_cols, key="date_col",
            index=(1 + all_cols.index(date_cols[0])) if date_cols else 0,
            label_visibility="collapsed")
        
        st.markdown("**💵 Revenue** *(required)*")
        sales_col = st.selectbox("Sales", ["None"] + numeric_cols, key="sales_col",
            label_visibility="collapsed")
    
    with col2:
        st.markdown("**📈 Profit**")
        profit_col = st.selectbox("Profit", ["None"] + numeric_cols, key="profit_col",
            label_visibility="collapsed")
        
        st.markdown("**🔢 Quantity**")
        quantity_col = st.selectbox("Quantity", ["None"] + numeric_cols, key="qty_col",
            label_visibility="collapsed")
    
    with col3:
        st.markdown("**📦 Category**")
        category_col = st.selectbox("Category", ["None"] + all_cols, key="cat_col",
            label_visibility="collapsed")
        
        st.markdown("**👤 Customer**")
        customer_col = st.selectbox("Customer", ["None"] + all_cols, key="cust_col",
            label_visibility="collapsed")
    
    with st.expander("More options"):
        c1, c2, c3 = st.columns(3)
        with c1:
            order_col = st.selectbox("Order ID", ["None"] + all_cols, key="order_col")
            product_col = st.selectbox("Product", ["None"] + all_cols, key="product_col")
        with c2:
            region_col = st.selectbox("Region", ["None"] + all_cols, key="region_col")
            segment_col = st.selectbox("Segment", ["None"] + all_cols, key="segment_col")
        with c3:
            discount_col = st.selectbox("Discount", ["None"] + numeric_cols, key="discount_col")
            returned_col = st.selectbox("Returned (Yes/No)", ["None"] + all_cols, key="returned_col")
    
    # Save mapping
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
    
    if st.session_state.column_mapping.get('sales') is None:
        st.warning("Select at least a **Revenue** column to unlock analytics pages.")
    else:
        st.markdown("""
        <div class="success-box">
            <strong>All set!</strong> Use the sidebar to navigate to analytics pages: Overview, Customers, Returns.
        </div>
        """, unsafe_allow_html=True)
    
    # Data preview
    st.markdown('<p class="section-title">👀 Data Preview</p>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True)
    
    st.markdown('<div class="footer">Made with Streamlit</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
