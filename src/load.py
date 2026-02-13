"""
Data loading and preprocessing for Data Dash.
Handles dynamic column mapping for any dataset.
"""

import pandas as pd
import streamlit as st
from pathlib import Path


def get_data_and_mapping():
    """
    Get data and column mapping from session state.
    
    Returns:
        tuple: (DataFrame, column_mapping dict) or (None, None) if not available
    """
    if 'data' not in st.session_state or st.session_state.data is None:
        return None, None
    
    if 'column_mapping' not in st.session_state:
        return None, None
    
    return st.session_state.data.copy(), st.session_state.column_mapping


def prepare_data(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Prepare data based on column mapping.
    Standardizes column names for internal use.
    
    Args:
        df: Raw dataframe
        mapping: Column mapping dictionary
    
    Returns:
        pd.DataFrame: Prepared dataframe with standardized columns
    """
    prepared = df.copy()
    
    # Parse date column if specified
    if mapping.get('date'):
        try:
            prepared['_date'] = pd.to_datetime(prepared[mapping['date']], errors='coerce')
            prepared['_year'] = prepared['_date'].dt.year
            prepared['_month'] = prepared['_date'].dt.month
            prepared['_year_month'] = prepared['_date'].dt.to_period('M').astype(str)
            prepared['_quarter'] = prepared['_date'].dt.quarter
        except Exception:
            pass
    
    # Standardize numeric columns
    if mapping.get('sales'):
        prepared['_sales'] = pd.to_numeric(prepared[mapping['sales']], errors='coerce').fillna(0)
    
    if mapping.get('profit'):
        prepared['_profit'] = pd.to_numeric(prepared[mapping['profit']], errors='coerce').fillna(0)
    
    if mapping.get('quantity'):
        prepared['_quantity'] = pd.to_numeric(prepared[mapping['quantity']], errors='coerce').fillna(0)
    
    if mapping.get('discount'):
        prepared['_discount'] = pd.to_numeric(prepared[mapping['discount']], errors='coerce').fillna(0)
    
    # Standardize category columns
    if mapping.get('category'):
        prepared['_category'] = prepared[mapping['category']].astype(str)
    
    if mapping.get('customer'):
        prepared['_customer'] = prepared[mapping['customer']].astype(str)
    
    if mapping.get('order_id'):
        prepared['_order_id'] = prepared[mapping['order_id']].astype(str)
    
    if mapping.get('region'):
        prepared['_region'] = prepared[mapping['region']].astype(str)
    
    if mapping.get('segment'):
        prepared['_segment'] = prepared[mapping['segment']].astype(str)
    
    if mapping.get('product'):
        prepared['_product'] = prepared[mapping['product']].astype(str)
    
    # Handle returned/status column
    if mapping.get('returned'):
        col = mapping['returned']
        prepared['_returned'] = prepared[col].astype(str).str.lower().isin(['yes', 'true', '1', 'returned'])
    
    return prepared


def filter_data(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    categories: list = None,
    regions: list = None,
    segments: list = None
) -> pd.DataFrame:
    """
    Filter the dataframe based on user selections.
    Uses standardized column names (prefixed with _).
    """
    filtered = df.copy()
    
    # Date filtering
    if start_date is not None and '_date' in filtered.columns:
        start_dt = pd.to_datetime(start_date)
        filtered = filtered[filtered['_date'] >= start_dt]
    
    if end_date is not None and '_date' in filtered.columns:
        end_dt = pd.to_datetime(end_date)
        filtered = filtered[filtered['_date'] <= end_dt]
    
    # Category filtering
    if categories and len(categories) > 0 and '_category' in filtered.columns:
        filtered = filtered[filtered['_category'].isin(categories)]
    
    if regions and len(regions) > 0 and '_region' in filtered.columns:
        filtered = filtered[filtered['_region'].isin(regions)]
    
    if segments and len(segments) > 0 and '_segment' in filtered.columns:
        filtered = filtered[filtered['_segment'].isin(segments)]
    
    return filtered


def get_filter_options(df: pd.DataFrame) -> dict:
    """
    Get unique values for filter dropdowns.
    Uses standardized column names.
    """
    options = {
        'min_date': None,
        'max_date': None,
        'categories': [],
        'regions': [],
        'segments': [],
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
