"""
Data Dash - Day 2: Added File Upload
"""

import streamlit as st
from src.load import load_file, get_column_info, get_data_preview

# Page config
st.set_page_config(
    page_title="Data Dash",
    page_icon="📊",
    layout="wide"
)

# Simple styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ff6b6b;
        text-align: center;
        margin-top: 30px;
    }
    .tagline {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">📊 Data Dash</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Simple analytics for your spreadsheets</p>', unsafe_allow_html=True)

st.markdown("---")

# File upload section
st.subheader("📁 Upload Your Data")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload your data file to get started"
)

if uploaded_file is not None:
    # Load the data
    df = load_file(uploaded_file)
    
    if df is not None:
        st.success(f"Loaded {len(df)} rows!")
        
        # Show column info
        info = get_column_info(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", info['row_count'])
        with col2:
            st.metric("Total Columns", len(info['columns']))
        
        # Data preview
        st.subheader("📋 Data Preview")
        st.dataframe(get_data_preview(df, 10), use_container_width=True)
        
        # Column info
        st.subheader("📊 Column Types")
        col_info = st.columns(2)
        with col_info[0]:
            st.write("**Numeric columns:**")
            st.write(info['numeric_cols'] if info['numeric_cols'] else "None found")
        with col_info[1]:
            st.write("**Text columns:**")
            st.write(info['text_cols'] if info['text_cols'] else "None found")
else:
    st.info("👆 Upload a file to get started")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>Built with Streamlit</p>", unsafe_allow_html=True)
