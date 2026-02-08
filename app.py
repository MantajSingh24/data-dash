"""
Data Dash - Day 3: Added Basic Metrics
"""

import streamlit as st
from src.load import load_file, get_column_info, get_data_preview
from src.metrics import calculate_summary, get_top_values, get_grouped_breakdown

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
        st.success(f"Loaded {len(df)} rows and {len(df.columns)} columns!")
        
        # Show column info
        info = get_column_info(df)
        
        # Data preview
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(get_data_preview(df, 10), use_container_width=True)
        
        st.markdown("---")
        
        # --- Metrics Section ---
        st.subheader("📊 Quick Stats")
        
        numeric_cols = info['numeric_cols']
        text_cols = info['text_cols']
        
        if numeric_cols:
            # Show summary metrics as cards
            summary = calculate_summary(df, numeric_cols)
            
            # Display up to 4 numeric columns as metric cards
            display_cols = numeric_cols[:4]
            cols = st.columns(len(display_cols))
            
            for i, col_name in enumerate(display_cols):
                with cols[i]:
                    st.metric(
                        label=f"Total {col_name}",
                        value=f"{summary[col_name]['sum']:,.2f}"
                    )
            
            # Let user pick columns for breakdown
            st.markdown("---")
            st.subheader("🔍 Explore Your Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                group_by = st.selectbox(
                    "Group by",
                    options=text_cols if text_cols else ['No text columns found'],
                    help="Pick a column to group your data by"
                )
            
            with col2:
                value_col = st.selectbox(
                    "Measure",
                    options=numeric_cols,
                    help="Pick a numeric column to analyze"
                )
            
            if group_by and group_by != 'No text columns found' and value_col:
                # Top values
                st.subheader(f"Top {group_by} by {value_col}")
                top = get_top_values(df, group_by, value_col, n=10)
                st.dataframe(top, use_container_width=True, hide_index=True)
                
                # Full breakdown
                with st.expander("Full Breakdown"):
                    breakdown = get_grouped_breakdown(df, group_by, numeric_cols)
                    st.dataframe(breakdown, use_container_width=True, hide_index=True)
        else:
            st.warning("No numeric columns found in your data.")
else:
    st.info("👆 Upload a file to get started")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>Built with Streamlit</p>", unsafe_allow_html=True)
