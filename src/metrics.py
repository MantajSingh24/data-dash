"""
Basic metrics calculations for Data Dash.
Computes summary stats from uploaded data.
"""

import pandas as pd


def calculate_summary(df: pd.DataFrame, numeric_cols: list) -> dict:
    """
    Calculate basic summary stats for numeric columns.
    
    Args:
        df: Input dataframe
        numeric_cols: List of numeric column names
    
    Returns:
        dict with summary statistics
    """
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


def get_top_values(df: pd.DataFrame, group_col: str, value_col: str, n: int = 10) -> pd.DataFrame:
    """
    Get top N values grouped by a column.
    
    Args:
        df: Input dataframe
        group_col: Column to group by
        value_col: Column to sum/rank by
        n: Number of top items
    
    Returns:
        DataFrame with top items
    """
    if df is None:
        return pd.DataFrame()
    
    grouped = df.groupby(group_col)[value_col].sum().reset_index()
    grouped = grouped.sort_values(value_col, ascending=False).head(n)
    
    return grouped


def get_grouped_breakdown(df: pd.DataFrame, group_col: str, value_cols: list) -> pd.DataFrame:
    """
    Get breakdown of values by a grouping column.
    
    Args:
        df: Input dataframe
        group_col: Column to group by
        value_cols: List of numeric columns to aggregate
    
    Returns:
        DataFrame with grouped totals
    """
    if df is None or group_col not in df.columns:
        return pd.DataFrame()
    
    valid_cols = [c for c in value_cols if c in df.columns]
    if not valid_cols:
        return pd.DataFrame()
    
    breakdown = df.groupby(group_col)[valid_cols].sum().reset_index()
    breakdown = breakdown.sort_values(valid_cols[0], ascending=False)
    
    return breakdown
