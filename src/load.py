"""
Data loading utilities for Data Dash.
Handles CSV and Excel file imports.
"""

import pandas as pd
import streamlit as st


def load_file(uploaded_file):
    """
    Load data from uploaded CSV or Excel file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        pd.DataFrame or None if loading fails
    """
    if uploaded_file is None:
        return None
    
    try:
        filename = uploaded_file.name.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Please upload a CSV or Excel file")
            return None
        
        return df
    
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def get_column_info(df: pd.DataFrame) -> dict:
    """
    Get basic info about dataframe columns.
    
    Args:
        df: Input dataframe
    
    Returns:
        dict with column names and types
    """
    if df is None:
        return {}
    
    return {
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'row_count': len(df),
        'numeric_cols': df.select_dtypes(include=['number']).columns.tolist(),
        'text_cols': df.select_dtypes(include=['object']).columns.tolist()
    }


def get_data_preview(df: pd.DataFrame, rows: int = 5) -> pd.DataFrame:
    """
    Get a preview of the data.
    
    Args:
        df: Input dataframe
        rows: Number of rows to preview
    
    Returns:
        Preview dataframe
    """
    if df is None:
        return pd.DataFrame()
    
    return df.head(rows)
