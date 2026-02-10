"""
Data loading and preprocessing for Data Dash.
Handles file import and column mapping.
"""

import pandas as pd
import streamlit as st


def load_file(uploaded_file):
    """
    Load data from uploaded CSV or Excel file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        pd.DataFrame or None
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
    """Get basic info about dataframe columns."""
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
    """Get a preview of the data."""
    if df is None:
        return pd.DataFrame()
    return df.head(rows)


def get_data_and_mapping():
    """
    Get data and column mapping from session state.
    
    Returns:
        tuple: (DataFrame, column_mapping dict) or (None, None)
    """
    if 'data' not in st.session_state or st.session_state.data is None:
        return None, None
    
    if 'column_mapping' not in st.session_state:
        return None, None
    
    return st.session_state.data.copy(), st.session_state.column_mapping


def prepare_data(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Prepare data based on column mapping.
    Creates standardized internal columns (prefixed with _).
    """
    prepared = df.copy()
    
    # Parse dates
    if mapping.get('date'):
        try:
            prepared['_date'] = pd.to_datetime(prepared[mapping['date']], errors='coerce')
            prepared['_year'] = prepared['_date'].dt.year
            prepared['_month'] = prepared['_date'].dt.month
            prepared['_year_month'] = prepared['_date'].dt.to_period('M').astype(str)
        except Exception:
            pass
    
    # Numeric columns
    for key in ['sales', 'profit', 'quantity', 'discount']:
        if mapping.get(key):
            prepared[f'_{key}'] = pd.to_numeric(prepared[mapping[key]], errors='coerce').fillna(0)
    
    # Text/category columns
    for key in ['category', 'customer', 'order_id', 'region', 'segment', 'product']:
        if mapping.get(key):
            prepared[f'_{key}'] = prepared[mapping[key]].astype(str)
    
    # Returned column (boolean)
    if mapping.get('returned'):
        col = mapping['returned']
        prepared['_returned'] = prepared[col].astype(str).str.lower().isin(['yes', 'true', '1', 'returned'])
    
    return prepared


def filter_data(df, start_date=None, end_date=None, categories=None, regions=None, segments=None):
    """Filter dataframe based on user selections."""
    filtered = df.copy()
    
    if start_date and '_date' in filtered.columns:
        filtered = filtered[filtered['_date'] >= pd.to_datetime(start_date)]
    
    if end_date and '_date' in filtered.columns:
        filtered = filtered[filtered['_date'] <= pd.to_datetime(end_date)]
    
    if categories and '_category' in filtered.columns:
        filtered = filtered[filtered['_category'].isin(categories)]
    
    if regions and '_region' in filtered.columns:
        filtered = filtered[filtered['_region'].isin(regions)]
    
    if segments and '_segment' in filtered.columns:
        filtered = filtered[filtered['_segment'].isin(segments)]
    
    return filtered


def get_filter_options(df: pd.DataFrame) -> dict:
    """Get unique values for filter dropdowns."""
    options = {
        'min_date': None, 'max_date': None,
        'categories': [], 'regions': [], 'segments': [],
        'has_date': '_date' in df.columns,
        'has_category': '_category' in df.columns,
        'has_region': '_region' in df.columns,
        'has_segment': '_segment' in df.columns,
        'has_profit': '_profit' in df.columns,
        'has_quantity': '_quantity' in df.columns,
        'has_customer': '_customer' in df.columns,
        'has_order_id': '_order_id' in df.columns,
        'has_product': '_product' in df.columns,
        'has_returned': '_returned' in df.columns,
        'has_discount': '_discount' in df.columns,
    }
    
    if '_date' in df.columns:
        valid_dates = df['_date'].dropna()
        if len(valid_dates) > 0:
            options['min_date'] = valid_dates.min()
            options['max_date'] = valid_dates.max()
    
    if '_category' in df.columns:
        options['categories'] = sorted(df['_category'].dropna().unique().tolist())
    if '_region' in df.columns:
        options['regions'] = sorted(df['_region'].dropna().unique().tolist())
    if '_segment' in df.columns:
        options['segments'] = sorted(df['_segment'].dropna().unique().tolist())
    
    return options
