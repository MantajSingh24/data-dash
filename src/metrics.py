"""
Business metrics calculations for Data Dash.
Uses standardized column names (prefixed with _).
"""

import pandas as pd
from typing import Tuple, Optional


def calculate_kpis(df: pd.DataFrame, options: dict) -> dict:
    """
    Calculate key performance indicators.
    
    Args:
        df: Prepared dataframe with standardized columns
        options: Filter options dict with has_* flags
    
    Returns:
        dict: Dictionary of KPI values
    """
    kpis = {
        'total_sales': 0,
        'total_profit': 0,
        'total_orders': 0,
        'total_customers': 0,
        'total_quantity': 0,
        'avg_order_value': 0,
        'profit_margin': 0,
        'avg_discount': 0,
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
        kpis['total_orders'] = len(df)  # Assume each row is an order
    
    if '_customer' in df.columns:
        kpis['total_customers'] = df['_customer'].nunique()
    
    if '_quantity' in df.columns:
        kpis['total_quantity'] = df['_quantity'].sum()
    
    if kpis['total_orders'] > 0:
        kpis['avg_order_value'] = kpis['total_sales'] / kpis['total_orders']
    
    if '_discount' in df.columns:
        kpis['avg_discount'] = df['_discount'].mean() * 100
    
    return kpis


def calculate_monthly_metrics(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Calculate monthly aggregated metrics.
    
    Returns:
        pd.DataFrame or None if no date column
    """
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
    
    # Rename columns for display
    monthly.columns = ['Month'] + [c.replace('_', '').title() for c in monthly.columns[1:]]
    if 'Order Id' in monthly.columns:
        monthly = monthly.rename(columns={'Order Id': 'Orders'})
    
    monthly = monthly.sort_values('Month')
    
    # Calculate changes
    if 'Sales' in monthly.columns:
        monthly['Sales Change'] = monthly['Sales'].pct_change() * 100
    
    if 'Profit' in monthly.columns:
        monthly['Profit Change'] = monthly['Profit'].pct_change() * 100
    
    return monthly


def get_top_items(df: pd.DataFrame, group_col: str, n: int = 10, by: str = 'Sales') -> Optional[pd.DataFrame]:
    """
    Get top N items by a given metric.
    
    Args:
        df: Prepared dataframe
        group_col: Standardized column name to group by (e.g., '_product', '_category')
        n: Number of items to return
        by: Metric to rank by ('Sales', 'Profit', 'Quantity')
    """
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
    
    # Clean column names
    col_map = {
        group_col: 'Name',
        '_sales': 'Sales',
        '_profit': 'Profit',
        '_quantity': 'Quantity',
        '_order_id': 'Orders'
    }
    items = items.rename(columns=col_map)
    
    sort_col = by if by in items.columns else 'Sales'
    items = items.sort_values(sort_col, ascending=False).head(n)
    
    return items


def get_category_breakdown(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Get breakdown by category."""
    return get_breakdown(df, '_category', 'Category')


def get_region_breakdown(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Get breakdown by region."""
    return get_breakdown(df, '_region', 'Region')


def get_segment_breakdown(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Get breakdown by segment."""
    return get_breakdown(df, '_segment', 'Segment')


def get_breakdown(df: pd.DataFrame, col: str, col_name: str) -> Optional[pd.DataFrame]:
    """
    Get sales/profit breakdown by a dimension.
    """
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
    
    # Rename columns
    col_map = {
        col: col_name,
        '_sales': 'Sales',
        '_profit': 'Profit',
        '_quantity': 'Quantity',
        '_order_id': 'Orders',
        '_customer': 'Customers'
    }
    breakdown = breakdown.rename(columns=col_map)
    
    # Calculate profit margin if both columns exist
    if 'Sales' in breakdown.columns and 'Profit' in breakdown.columns:
        breakdown['Profit Margin'] = (breakdown['Profit'] / breakdown['Sales'] * 100).round(2)
    
    # Calculate avg order value if applicable
    if 'Sales' in breakdown.columns and 'Orders' in breakdown.columns:
        breakdown['Avg Order Value'] = (breakdown['Sales'] / breakdown['Orders']).round(2)
    
    return breakdown.sort_values('Sales', ascending=False)


def get_top_customers(df: pd.DataFrame, n: int = 10) -> Optional[pd.DataFrame]:
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
    
    col_map = {
        '_customer': 'Customer',
        '_sales': 'Sales',
        '_profit': 'Profit',
        '_order_id': 'Orders',
        '_quantity': 'Items'
    }
    customers = customers.rename(columns=col_map)
    
    return customers.sort_values('Sales', ascending=False).head(n)


def calculate_repeat_customers(df: pd.DataFrame) -> Tuple[int, int, float]:
    """
    Calculate repeat customer metrics.
    
    Returns:
        Tuple: (total_customers, repeat_customers, repeat_rate)
    """
    if '_customer' not in df.columns:
        return 0, 0, 0
    
    if '_order_id' in df.columns:
        customer_orders = df.groupby('_customer')['_order_id'].nunique()
    else:
        # Assume each row is an order
        customer_orders = df.groupby('_customer').size()
    
    total_customers = len(customer_orders)
    repeat_customers = (customer_orders >= 2).sum()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    return total_customers, repeat_customers, repeat_rate


def get_return_metrics(df: pd.DataFrame) -> dict:
    """Calculate return-related metrics."""
    metrics = {
        'total_orders': 0,
        'returned_orders': 0,
        'return_rate': 0,
        'returned_sales': 0,
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


def get_items_by_return_rate(df: pd.DataFrame, group_col: str, col_name: str, n: int = 10) -> Optional[pd.DataFrame]:
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
    
    col_map = {
        group_col: col_name,
        '_returned': 'Returns',
        '_order_id': 'Total Orders',
        '_sales': 'Sales',
        '_profit': 'Profit'
    }
    items = items.rename(columns=col_map)
    
    # If no order_id, use row count
    if 'Total Orders' not in items.columns:
        items['Total Orders'] = df.groupby(group_col).size().values
    
    items['Return Rate'] = (items['Returns'] / items['Total Orders'] * 100).round(2)
    
    # Filter to items with returns
    items = items[items['Returns'] > 0]
    
    return items.sort_values('Return Rate', ascending=False).head(n)
