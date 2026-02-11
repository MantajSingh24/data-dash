"""
Business metrics calculations for Data Dash.
Uses standardized column names (prefixed with _).
"""

import pandas as pd


def calculate_summary(df: pd.DataFrame, numeric_cols: list) -> dict:
    """Calculate basic summary stats for numeric columns."""
    if df is None or not numeric_cols:
        return {}
    
    summary = {}
    for col in numeric_cols:
        summary[col] = {
            'sum': df[col].sum(),
            'mean': df[col].mean(),
            'min': df[col].min(),
            'max': df[col].max(),
            'count': df[col].count()
        }
    return summary


def get_top_values(df, group_col, value_col, n=10):
    """Get top N values grouped by a column."""
    if df is None:
        return pd.DataFrame()
    grouped = df.groupby(group_col)[value_col].sum().reset_index()
    return grouped.sort_values(value_col, ascending=False).head(n)


def get_grouped_breakdown(df, group_col, value_cols):
    """Get breakdown of values by a grouping column."""
    if df is None or group_col not in df.columns:
        return pd.DataFrame()
    valid_cols = [c for c in value_cols if c in df.columns]
    if not valid_cols:
        return pd.DataFrame()
    breakdown = df.groupby(group_col)[valid_cols].sum().reset_index()
    return breakdown.sort_values(valid_cols[0], ascending=False)


def calculate_kpis(df: pd.DataFrame, options: dict) -> dict:
    """
    Calculate key performance indicators.
    
    Args:
        df: Prepared dataframe with standardized columns
        options: Filter options dict with has_* flags
    
    Returns:
        dict of KPI values
    """
    kpis = {
        'total_sales': 0, 'total_profit': 0,
        'total_orders': 0, 'total_customers': 0,
        'total_quantity': 0, 'avg_order_value': 0,
        'profit_margin': 0, 'avg_discount': 0,
        'row_count': len(df)
    }
    
    if '_sales' in df.columns:
        kpis['total_sales'] = df['_sales'].sum()
    
    if '_profit' in df.columns:
        kpis['total_profit'] = df['_profit'].sum()
        if kpis['total_sales'] > 0:
            kpis['profit_margin'] = (kpis['total_profit'] / kpis['total_sales'] * 100)
    
    if '_order_id' in df.columns:
        kpis['total_orders'] = df['_order_id'].nunique()
    else:
        kpis['total_orders'] = len(df)
    
    if '_customer' in df.columns:
        kpis['total_customers'] = df['_customer'].nunique()
    
    if '_quantity' in df.columns:
        kpis['total_quantity'] = df['_quantity'].sum()
    
    if kpis['total_orders'] > 0:
        kpis['avg_order_value'] = kpis['total_sales'] / kpis['total_orders']
    
    if '_discount' in df.columns:
        kpis['avg_discount'] = df['_discount'].mean() * 100
    
    return kpis


def calculate_monthly_metrics(df: pd.DataFrame):
    """Calculate monthly aggregated metrics."""
    if '_year_month' not in df.columns or '_sales' not in df.columns:
        return None
    
    agg_dict = {'_sales': 'sum'}
    if '_profit' in df.columns:
        agg_dict['_profit'] = 'sum'
    if '_order_id' in df.columns:
        agg_dict['_order_id'] = 'nunique'
    if '_quantity' in df.columns:
        agg_dict['_quantity'] = 'sum'
    
    monthly = df.groupby('_year_month').agg(agg_dict).reset_index()
    monthly.columns = ['Month'] + [c.replace('_', '').title() for c in monthly.columns[1:]]
    
    if 'Order Id' in monthly.columns:
        monthly = monthly.rename(columns={'Order Id': 'Orders'})
    
    monthly = monthly.sort_values('Month')
    
    if 'Sales' in monthly.columns:
        monthly['Sales Change'] = monthly['Sales'].pct_change() * 100
    
    return monthly


def get_top_items(df, group_col, n=10, by='Sales'):
    """Get top N items by a given metric."""
    if group_col not in df.columns or '_sales' not in df.columns:
        return None
    
    agg_dict = {'_sales': 'sum'}
    if '_profit' in df.columns:
        agg_dict['_profit'] = 'sum'
    if '_quantity' in df.columns:
        agg_dict['_quantity'] = 'sum'
    if '_order_id' in df.columns:
        agg_dict['_order_id'] = 'nunique'
    
    items = df.groupby(group_col).agg(agg_dict).reset_index()
    col_map = {group_col: 'Name', '_sales': 'Sales', '_profit': 'Profit',
               '_quantity': 'Quantity', '_order_id': 'Orders'}
    items = items.rename(columns=col_map)
    
    sort_col = by if by in items.columns else 'Sales'
    return items.sort_values(sort_col, ascending=False).head(n)


def _get_breakdown(df, col, col_name):
    """Get sales/profit breakdown by a dimension."""
    if col not in df.columns or '_sales' not in df.columns:
        return None
    
    agg_dict = {'_sales': 'sum'}
    if '_profit' in df.columns:
        agg_dict['_profit'] = 'sum'
    if '_quantity' in df.columns:
        agg_dict['_quantity'] = 'sum'
    if '_order_id' in df.columns:
        agg_dict['_order_id'] = 'nunique'
    if '_customer' in df.columns:
        agg_dict['_customer'] = 'nunique'
    
    breakdown = df.groupby(col).agg(agg_dict).reset_index()
    col_map = {col: col_name, '_sales': 'Sales', '_profit': 'Profit',
               '_quantity': 'Quantity', '_order_id': 'Orders', '_customer': 'Customers'}
    breakdown = breakdown.rename(columns=col_map)
    
    if 'Sales' in breakdown.columns and 'Profit' in breakdown.columns:
        breakdown['Profit Margin'] = (breakdown['Profit'] / breakdown['Sales'] * 100).round(2)
    
    return breakdown.sort_values('Sales', ascending=False)


def get_category_breakdown(df):
    """Get breakdown by category."""
    return _get_breakdown(df, '_category', 'Category')


def get_region_breakdown(df):
    """Get breakdown by region."""
    return _get_breakdown(df, '_region', 'Region')


def get_segment_breakdown(df):
    """Get breakdown by segment."""
    return _get_breakdown(df, '_segment', 'Segment')
