"""
Data Dash - Premium Analytics Dashboard
"""

import io
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

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

st.set_page_config(page_title="Data Dash", page_icon="â—†", layout="wide", initial_sidebar_state="collapsed")

# Premium Apple/Samsung-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    :root {
        --bg: #000000;
        --surface: rgba(255,255,255,0.04);
        --glass: rgba(255,255,255,0.06);
        --border: rgba(255,255,255,0.08);
        --text: #f5f5f7;
        --text-sec: #86868b;
        --accent: #2997ff;
        --accent2: #bf5af2;
        --green: #30d158;
        --red: #ff453a;
        --orange: #ff9f0a;
        --radius: 16px;
    }
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    .stApp { background: var(--bg); }
    [data-testid="stSidebar"] {
        background: rgba(28,28,30,0.95);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * { color: var(--text-sec) !important; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p { color: var(--text) !important; font-weight: 500; }
    #MainMenu, footer, header { visibility: hidden; }
    .hero { text-align: center; padding: 60px 20px 40px 20px; }
    .hero-badge {
        display: inline-block; padding: 6px 16px; border-radius: 100px;
        background: rgba(41,151,255,0.12); color: var(--accent);
        font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px;
        text-transform: uppercase; margin-bottom: 20px;
    }
    .hero h1 {
        font-size: 3.4rem; font-weight: 800; letter-spacing: -1.5px; line-height: 1.1;
        background: linear-gradient(135deg, #f5f5f7 0%, #86868b 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0 0 16px 0;
    }
    .hero p { color: var(--text-sec); font-size: 1.15rem; font-weight: 400; max-width: 520px; margin: 0 auto; line-height: 1.6; }
    .sep { height: 1px; background: var(--border); margin: 40px 0; }
    .sec-label { font-size: 0.75rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--accent); margin: 0 0 8px 0; }
    .sec-title { font-size: 1.6rem; font-weight: 700; color: var(--text); letter-spacing: -0.5px; margin: 0 0 24px 0; }
    .glass-card {
        background: var(--glass); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border); border-radius: var(--radius); padding: 28px;
        transition: all 0.35s cubic-bezier(.25,.8,.25,1);
    }
    .glass-card:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.14); transform: translateY(-2px); }
    .step-num {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1;
    }
    .step-label { font-size: 1rem; font-weight: 600; color: var(--text); margin: 12px 0 6px 0; }
    .step-sub { font-size: 0.85rem; color: var(--text-sec); }
    .ready-banner {
        background: linear-gradient(135deg, rgba(48,209,88,0.08), rgba(41,151,255,0.08));
        border: 1px solid rgba(48,209,88,0.15); border-radius: var(--radius); padding: 20px 28px; margin-bottom: 32px;
    }
    .ready-banner strong { color: var(--green); }
    .ready-banner span { color: var(--text-sec); font-size: 0.9rem; }
    .info-banner {
        background: rgba(41,151,255,0.06); border: 1px solid rgba(41,151,255,0.12);
        border-radius: var(--radius); padding: 20px 28px; color: var(--text-sec); font-size: 0.9rem; line-height: 1.7;
    }
    .info-banner strong { color: var(--text); }
    .info-banner ol { margin: 12px 0 0 20px; padding: 0; }
    .info-banner li { margin: 6px 0; }
    .stMetric {
        background: var(--glass) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important; padding: 20px !important;
    }
    [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { color: var(--text-sec) !important; font-weight: 500 !important; text-transform: uppercase !important; font-size: 0.7rem !important; letter-spacing: 0.8px !important; }
    [data-testid="stMetricDelta"] { font-weight: 600 !important; }
    .stButton > button {
        background: var(--accent) !important; color: #fff !important; border: none !important;
        border-radius: 100px !important; padding: 10px 28px !important; font-weight: 600 !important;
        font-size: 0.9rem !important; transition: all 0.3s !important;
    }
    .stButton > button:hover { background: #0a84ff !important; box-shadow: 0 4px 20px rgba(41,151,255,0.35) !important; transform: scale(1.02) !important; }
    [data-testid="stFileUploader"] {
        background: var(--glass); border: 2px dashed rgba(255,255,255,0.1);
        border-radius: var(--radius); padding: 20px; transition: all 0.3s;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--accent); background: rgba(41,151,255,0.04); }
    [data-testid="stSelectbox"] > div > div { background: var(--surface) !important; border-color: var(--border) !important; border-radius: 10px !important; color: var(--text) !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; background: var(--surface); border-radius: 10px; padding: 3px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 20px; color: var(--text-sec); font-weight: 500; }
    .stTabs [aria-selected="true"] { background: var(--glass) !important; color: var(--text) !important; }
    .streamlit-expanderHeader { background: var(--surface) !important; border-radius: 12px !important; font-weight: 500 !important; color: var(--text-sec) !important; }
    .stRadio > div { gap: 0 !important; }
    .stRadio [role="radiogroup"] { background: var(--surface); border-radius: 10px; padding: 3px; }
    [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: var(--radius); }
    .site-footer { text-align: center; padding: 60px 0 30px 0; color: var(--text-sec); font-size: 0.8rem; }
    .site-footer span { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600; }
    .file-badge { display: inline-flex; align-items: center; gap: 10px; background: var(--glass); border: 1px solid var(--border); border-radius: 12px; padding: 14px 20px; margin: 8px 0 20px 0; }
    .file-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); }
    .file-badge .fname { color: var(--text); font-weight: 600; font-size: 0.95rem; }
    .file-badge .fmeta { color: var(--text-sec); font-size: 0.8rem; }

    /* Animated background canvas */
    #bg-canvas {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: 0;
        pointer-events: none;
    }

    /* Floating gradient orbs */
    .orb {
        position: fixed;
        border-radius: 50%;
        filter: blur(80px);
        z-index: 0;
        pointer-events: none;
        animation: orbFloat linear infinite;
    }
    .orb-1 {
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(41,151,255,0.12) 0%, transparent 70%);
        top: -100px; left: -100px;
        animation-duration: 20s;
        animation-delay: 0s;
    }
    .orb-2 {
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(191,90,242,0.10) 0%, transparent 70%);
        top: 30vh; right: -150px;
        animation-duration: 25s;
        animation-delay: -8s;
    }
    .orb-3 {
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(48,209,88,0.07) 0%, transparent 70%);
        bottom: 10vh; left: 20vw;
        animation-duration: 18s;
        animation-delay: -12s;
    }
    @keyframes orbFloat {
        0%   { transform: translate(0px, 0px) scale(1); }
        25%  { transform: translate(40px, -30px) scale(1.05); }
        50%  { transform: translate(20px, 50px) scale(0.97); }
        75%  { transform: translate(-30px, 20px) scale(1.03); }
        100% { transform: translate(0px, 0px) scale(1); }
    }

    /* Ensure Streamlit content sits above the canvas */
    .stApp > div { position: relative; z-index: 1; }
    [data-testid="stAppViewContainer"] { position: relative; z-index: 1; }
</style>
""", unsafe_allow_html=True)

# Animated background: canvas particles + floating orbs
st.markdown("""
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<canvas id="bg-canvas"></canvas>
<script>
(function() {
    var canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    var NUM = 70;
    var particles = [];
    var mouse = { x: null, y: null };

    window.addEventListener('mousemove', function(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    function rand(min, max) { return Math.random() * (max - min) + min; }

    var PALETTE = [
        'rgba(41,151,255,',
        'rgba(191,90,242,',
        'rgba(100,210,255,',
        'rgba(48,209,88,',
    ];

    for (var i = 0; i < NUM; i++) {
        particles.push({
            x: rand(0, window.innerWidth),
            y: rand(0, window.innerHeight),
            vx: rand(-0.35, 0.35),
            vy: rand(-0.35, 0.35),
            r: rand(1.5, 3.5),
            color: PALETTE[Math.floor(Math.random() * PALETTE.length)],
            alpha: rand(0.4, 0.9),
        });
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Connect nearby particles
        for (var i = 0; i < particles.length; i++) {
            for (var j = i + 1; j < particles.length; j++) {
                var dx = particles[i].x - particles[j].x;
                var dy = particles[i].y - particles[j].y;
                var dist = Math.sqrt(dx*dx + dy*dy);
                var MAX_DIST = 140;
                if (dist < MAX_DIST) {
                    var opacity = (1 - dist / MAX_DIST) * 0.18;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = particles[i].color + opacity + ')';
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }

            // Mouse attraction
            if (mouse.x !== null) {
                var mdx = mouse.x - particles[i].x;
                var mdy = mouse.y - particles[i].y;
                var mdist = Math.sqrt(mdx*mdx + mdy*mdy);
                if (mdist < 160) {
                    var mOpacity = (1 - mdist / 160) * 0.35;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = particles[i].color + mOpacity + ')';
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }

            // Draw particle
            ctx.beginPath();
            ctx.arc(particles[i].x, particles[i].y, particles[i].r, 0, Math.PI * 2);
            ctx.fillStyle = particles[i].color + particles[i].alpha + ')';
            ctx.fill();

            // Move
            particles[i].x += particles[i].vx;
            particles[i].y += particles[i].vy;

            // Bounce
            if (particles[i].x < 0 || particles[i].x > canvas.width)  particles[i].vx *= -1;
            if (particles[i].y < 0 || particles[i].y > canvas.height) particles[i].vy *= -1;
        }

        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
""", unsafe_allow_html=True)


def detect_column_types(df):
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
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">Analytics Dashboard</div>
        <h1>Data Dash</h1>
        <p>Upload your data. Map your columns. Get instant insights.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-label">Step 1</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">Upload your data</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Drag and drop CSV or Excel", type=['csv', 'xlsx', 'xls'], help="Supports .csv, .xlsx, and .xls files")

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                raw = uploaded_file.read()
                uploaded_file.seek(0)
                for enc in ('utf-8', 'latin-1', 'cp1252', 'iso-8859-1'):
                    try:
                        df = pd.read_csv(io.BytesIO(raw), encoding=enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode CSV. Try saving as UTF-8.")
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.data = df
            st.session_state.file_name = uploaded_file.name
        except Exception as e:
            st.error(f"Couldn't read file: {str(e)}")

    if uploaded_file is None and st.session_state.data is not None:
        name = st.session_state.get('file_name', 'Dataset')
        rows = len(st.session_state.data)
        cols_count = len(st.session_state.data.columns)
        st.markdown(f'<div class="file-badge"><div class="dot"></div><div><div class="fname">{name}</div><div class="fmeta">{rows:,} rows &middot; {cols_count} columns</div></div></div>', unsafe_allow_html=True)
        if st.button("Clear & upload new"):
            st.session_state.data = None
            st.session_state.column_mapping = {}
            st.session_state.file_name = None
            st.rerun()

    if st.session_state.data is None:
        st.markdown('<div class="info-banner"><strong>How it works</strong><ol><li><strong>Upload</strong> a CSV or Excel file</li><li><strong>Map</strong> your columns (revenue, date, etc.)</li><li><strong>Analyze</strong> overview, customers & returns instantly</li></ol></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        for col, num, label, desc in [(c1, "01", "Upload", "Drop any CSV or Excel file"), (c2, "02", "Map", "Pick your columns"), (c3, "03", "Analyze", "Insights appear instantly")]:
            with col:
                st.markdown(f'<div class="glass-card" style="text-align:center;"><div class="step-num">{num}</div><div class="step-label">{label}</div><div class="step-sub">{desc}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="site-footer">Designed with precision. Powered by <span>Data Dash</span>.</div>', unsafe_allow_html=True)
        return

    df = st.session_state.data
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-label">Step 2</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">Map your columns</p>', unsafe_allow_html=True)
    st.caption("At least **Revenue** is required. Selections are saved.")

    date_cols, numeric_cols, category_cols = detect_column_types(df)
    all_cols = df.columns.tolist()

    def idx(col_name, opts):
        v = st.session_state.column_mapping.get(col_name)
        if v and v in opts:
            return 1 + opts.index(v)
        return 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Date**")
        date_col = st.selectbox("Date", ["None"] + all_cols, index=idx('date', all_cols) or ((1 + all_cols.index(date_cols[0])) if date_cols and date_cols[0] in all_cols else 0), label_visibility="collapsed", key="date_col")
        st.markdown("**Revenue** *(required)*")
        sales_col = st.selectbox("Sales", ["None"] + numeric_cols, index=idx('sales', numeric_cols), label_visibility="collapsed", key="sales_col")
    with col2:
        st.markdown("**Profit**")
        profit_col = st.selectbox("Profit", ["None"] + numeric_cols, index=idx('profit', numeric_cols), label_visibility="collapsed", key="profit_col")
        st.markdown("**Quantity**")
        quantity_col = st.selectbox("Quantity", ["None"] + numeric_cols, index=idx('quantity', numeric_cols), label_visibility="collapsed", key="qty_col")
    with col3:
        st.markdown("**Category**")
        category_col = st.selectbox("Category", ["None"] + all_cols, index=idx('category', all_cols), label_visibility="collapsed", key="cat_col")
        st.markdown("**Customer**")
        customer_col = st.selectbox("Customer", ["None"] + all_cols, index=idx('customer', all_cols), label_visibility="collapsed", key="cust_col")

    with st.expander("More options"):
        c1, c2, c3 = st.columns(3)
        with c1:
            order_col = st.selectbox("Order ID", ["None"] + all_cols, index=idx('order_id', all_cols), key="order_col")
            product_col = st.selectbox("Product", ["None"] + all_cols, index=idx('product', all_cols), key="product_col")
        with c2:
            region_col = st.selectbox("Region", ["None"] + all_cols, index=idx('region', all_cols), key="region_col")
            segment_col = st.selectbox("Segment", ["None"] + all_cols, index=idx('segment', all_cols), key="segment_col")
        with c3:
            discount_col = st.selectbox("Discount", ["None"] + numeric_cols, index=idx('discount', numeric_cols), key="discount_col")
            returned_col = st.selectbox("Returned", ["None"] + all_cols, index=idx('returned', all_cols), key="returned_col", help="Yes/No or True/False column")

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

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    if st.session_state.column_mapping['sales'] is None:
        st.warning("Select at least a **Revenue** column to continue.")
        st.dataframe(df.head(8), use_container_width=True)
        st.markdown('<div class="site-footer">Designed with precision. Powered by <span>Data Dash</span>.</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="ready-banner"><strong>Ready.</strong> <span>Scroll down for Overview, Customers & Returns.</span></div>', unsafe_allow_html=True)

    prepared_df = prepare_data(df, st.session_state.column_mapping)
    filter_opts = get_filter_options(prepared_df)

    st.sidebar.markdown("### Filters")
    if filter_opts['has_date'] and filter_opts['min_date'] is not None:
        date_range = st.sidebar.date_input("Date Range", value=(filter_opts['min_date'], filter_opts['max_date']), min_value=filter_opts['min_date'], max_value=filter_opts['max_date'])
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

    filtered_df = filter_data(prepared_df, start_date=start_date, end_date=end_date, categories=selected_categories, regions=selected_regions, segments=selected_segments)

    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return

    kpis = calculate_kpis(filtered_df, filter_opts)

    # OVERVIEW
    st.markdown('<p class="sec-label">Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">Key Metrics</p>', unsafe_allow_html=True)
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
            st.metric("Orders", f"{kpis['total_orders']:,}")
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

    if filter_opts['has_date']:
        monthly_data = calculate_monthly_metrics(filtered_df)
        if monthly_data is not None and len(monthly_data) > 1:
            available_metrics = [c for c in ['Sales', 'Profit', 'Quantity'] if c in monthly_data.columns]
            if available_metrics:
                st.markdown("#### Trends")
                tabs = st.tabs(available_metrics)
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
        st.markdown("#### Breakdown")
        cols = st.columns(len(breakdown_cols))
        for i, (name, data) in enumerate(breakdown_cols):
            with cols[i]:
                if data is not None and len(data) > 0:
                    view = st.radio(f"{name}", ["Bar", "Pie"], horizontal=True, key=f"{name}_view")
                    fig = create_category_chart(data, 'pie' if view == "Pie" else 'bar')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

    if filter_opts['has_product']:
        st.markdown("#### Top Products")
        col1, col2 = st.columns([2, 1])
        with col1:
            top_n = st.slider("Show top", 5, 20, 10, key="top_prod_slider")
            metrics_avail = ['Sales'] + (['Profit'] if filter_opts['has_profit'] else []) + (['Quantity'] if filter_opts['has_quantity'] else [])
            metric_choice = st.radio("Rank by", metrics_avail, horizontal=True, key="product_metric")
            top_products = get_top_items(filtered_df, '_product', n=top_n, by=metric_choice)
            if top_products is not None:
                fig = create_top_items_chart(top_products, metric_choice)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        with col2:
            if top_products is not None:
                dcols = [c for c in ['Name', 'Sales', 'Profit', 'Quantity'] if c in top_products.columns]
                fmt = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Quantity': '{:,.0f}'}
                st.dataframe(top_products[dcols].style.format({k: v for k, v in fmt.items() if k in dcols}), use_container_width=True, height=400)

    # CUSTOMERS
    if filter_opts['has_customer']:
        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-label">Customers</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-title">Buyers & Loyalty</p>', unsafe_allow_html=True)
        total_customers, repeat_customers, repeat_rate = calculate_repeat_customers(filtered_df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Customers", f"{total_customers:,}")
        with col2:
            st.metric("Repeat Customers", f"{repeat_customers:,}", delta=f"{repeat_rate:.1f}%")
        with col3:
            st.metric("Avg Revenue / Customer", f"${kpis['total_sales']/max(total_customers,1):,.0f}")
        with col4:
            if filter_opts['has_order_id']:
                st.metric("Avg Orders / Customer", f"{kpis['total_orders']/max(total_customers,1):.1f}")
            else:
                st.metric("Total Revenue", f"${kpis['total_sales']:,.0f}")
        st.markdown("#### Top Customers")
        col1, col2 = st.columns([2, 1])
        with col1:
            top_n_c = st.slider("Show top", 5, 20, 10, key="top_cust_slider")
            top_customers = get_top_customers(filtered_df, n=top_n_c)
            if top_customers is not None and len(top_customers) > 0:
                fig = create_customers_chart(top_customers)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        with col2:
            if top_customers is not None and len(top_customers) > 0:
                dcols = [c for c in ['Customer', 'Sales', 'Profit', 'Orders'] if c in top_customers.columns]
                fmt = {'Sales': '${:,.0f}', 'Profit': '${:,.0f}', 'Orders': '{:,}'}
                st.dataframe(top_customers[dcols].style.format({k: v for k, v in fmt.items() if k in dcols}), use_container_width=True, height=400)

    # RETURNS
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sec-label">Returns</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-title">Return Rate & Issues</p>', unsafe_allow_html=True)
    has_returns = filter_opts['has_returned']
    if has_returns:
        rm = get_return_metrics(filtered_df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders", f"{rm['total_orders']:,}")
        with col2:
            st.metric("Returned", f"{rm['returned_orders']:,}", delta=f"-{rm['return_rate']:.1f}%", delta_color="inverse")
        with col3:
            st.metric("Return Rate", f"{rm['return_rate']:.1f}%")
        with col4:
            if filter_opts['has_profit']:
                st.metric("Lost Profit", f"${abs(rm['returned_profit_loss']):,.0f}", delta="from returns", delta_color="off")
            else:
                st.metric("Returned Sales", f"${rm['returned_sales']:,.0f}")
        if filter_opts['has_product']:
            st.markdown("#### Problem Products")
            col1, col2 = st.columns([2, 1])
            with col1:
                top_n_r = st.slider("Show top", 5, 15, 10, key="problem_prod_slider")
                prod_ret = get_items_by_return_rate(filtered_df, '_product', 'Product', n=top_n_r)
                if prod_ret is not None and len(prod_ret) > 0:
                    fig = create_return_rate_chart(prod_ret)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            with col2:
                if prod_ret is not None and len(prod_ret) > 0:
                    dcols = [c for c in ['Product', 'Total Orders', 'Returns', 'Return Rate'] if c in prod_ret.columns]
                    fmt = {'Total Orders': '{:,}', 'Returns': '{:,}', 'Return Rate': '{:.1f}%'}
                    st.dataframe(prod_ret[dcols].style.format({k: v for k, v in fmt.items() if k in dcols}), use_container_width=True, height=400)
    else:
        st.markdown('<div class="info-banner"><strong>No return column in dataset.</strong><br>To see return analytics, scroll up and map a <strong>Returned</strong> column in <strong>More options</strong>. It should contain Yes/No or True/False values.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown("#### Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    st.markdown('<div class="site-footer">Designed with precision. Powered by <span>Data Dash</span>.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()