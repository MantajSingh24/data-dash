"""
Data Dash - Day 1: Basic Setup & Landing Page
"""

import streamlit as st

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
        margin-top: 50px;
    }
    .tagline {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 40px;
    }
    .coming-soon {
        text-align: center;
        padding: 60px;
        background: #f8f9fa;
        border-radius: 15px;
        margin: 20px auto;
        max-width: 600px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">📊 Data Dash</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Simple analytics for your spreadsheets</p>', unsafe_allow_html=True)

# Coming soon message
st.markdown("""
<div class="coming-soon">
    <h3>🚧 Work in Progress</h3>
    <p>Building an easy-to-use analytics dashboard.</p>
    <p><strong>Coming soon:</strong></p>
    <ul style="text-align: left; display: inline-block;">
        <li>CSV & Excel file upload</li>
        <li>Automatic chart generation</li>
        <li>Sales & customer insights</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>Built with Streamlit</p>", unsafe_allow_html=True)
