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


def get_top_customers(df, n=10):
    """Get top N customers by revenue."""
    if '_customer' not in df.columns or '_sales' not in df.columns:
        return None
    
    agg_dict = {'_sales': 'sum'}
    if '_profit' in df.columns:
        agg_dict['_profit'] = 'sum'
    if '_order_id' in df.columns:
        agg_dict['_order_id'] = 'nunique'
    if '_quantity' in df.columns:
        agg_dict['_quantity'] = 'sum'
    
    customers = df.groupby('_customer').agg(agg_dict).reset_index()
    col_map = {'_customer': 'Customer', '_sales': 'Sales', '_profit': 'Profit',
               '_order_id': 'Orders', '_quantity': 'Items'}
    customers = customers.rename(columns=col_map)
    
    return customers.sort_values('Sales', ascending=False).head(n)


def calculate_repeat_customers(df):
    """
    Calculate repeat customer metrics.
    
    Returns:
        tuple: (total_customers, repeat_customers, repeat_rate)
    """
    if '_customer' not in df.columns:
        return 0, 0, 0
    
    if '_order_id' in df.columns:
        customer_orders = df.groupby('_customer')['_order_id'].nunique()
    else:
        customer_orders = df.groupby('_customer').size()
    
    total_customers = len(customer_orders)
    repeat_customers = (customer_orders >= 2).sum()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    return total_customers, repeat_customers, repeat_rate


def get_return_metrics(df):
    """Calculate return-related metrics."""
    metrics = {
        'total_orders': 0, 'returned_orders': 0,
        'return_rate': 0, 'returned_sales': 0,
        'returned_profit_loss': 0
    }
    
    if '_returned' not in df.columns:
        return metrics
    
    if '_order_id' in df.columns:
        metrics['total_orders'] = df['_order_id'].nunique()
        metrics['returned_orders'] = df[df['_returned']]['_order_id'].nunique()
    else:
        metrics['total_orders'] = len(df)
        metrics['returned_orders'] = df['_returned'].sum()
    
    if metrics['total_orders'] > 0:
        metrics['return_rate'] = (metrics['returned_orders'] / metrics['total_orders'] * 100)
    
    if '_sales' in df.columns:
        metrics['returned_sales'] = df[df['_returned']]['_sales'].sum()
    
    if '_profit' in df.columns:
        metrics['returned_profit_loss'] = df[df['_returned']]['_profit'].sum()
    
    return metrics


def get_items_by_return_rate(df, group_col, col_name, n=10):
    """Get items with highest return rates."""
    if group_col not in df.columns or '_returned' not in df.columns:
        return None
    
    agg_dict = {'_returned': 'sum'}
    if '_order_id' in df.columns:
        agg_dict['_order_id'] = 'nunique'
    if '_sales' in df.columns:
        agg_dict['_sales'] = 'sum'
    if '_profit' in df.columns:
        agg_dict['_profit'] = 'sum'
    
    items = df.groupby(group_col).agg(agg_dict).reset_index()
    col_map = {group_col: col_name, '_returned': 'Returns',
               '_order_id': 'Total Orders', '_sales': 'Sales', '_profit': 'Profit'}
    items = items.rename(columns=col_map)
    
    if 'Total Orders' not in items.columns:
        items['Total Orders'] = df.groupby(group_col).size().values
    
    items['Return Rate'] = (items['Returns'] / items['Total Orders'] * 100).round(2)
    items = items[items['Returns'] > 0]
    
    return items.sort_values('Return Rate', ascending=False).head(n)
