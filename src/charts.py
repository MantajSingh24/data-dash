"""
Chart creation functions for Data Dash.
Professional, clean visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


# Warm colorful palette for dark theme
COLORS = {
    'primary': '#ff6b6b',
    'secondary': '#feca57',
    'success': '#2ed573',
    'danger': '#ff4757',
    'warning': '#feca57',
    'info': '#48dbfb',
    'dark': '#1a1a2e',
    'light': '#a0a0a0'
}

# Vibrant color sequence
COLOR_SEQUENCE = [
    '#ff6b6b', '#feca57', '#48dbfb', '#2ed573',
    '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3'
]

# Chart template settings for dark theme
CHART_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Poppins, sans-serif', 'color': '#eaeaea'},
        'title': {'font': {'size': 16, 'color': '#ffffff'}},
        'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 30},
        'xaxis': {'gridcolor': 'rgba(255,255,255,0.1)', 'color': '#a0a0a0'},
        'yaxis': {'gridcolor': 'rgba(255,255,255,0.1)', 'color': '#a0a0a0'}
    }
}


def create_monthly_trend_chart(monthly_df: pd.DataFrame, metric: str = 'Sales') -> Optional[go.Figure]:
    """Create a monthly trend line chart."""
    if monthly_df is None or metric not in monthly_df.columns:
        return None
    
    fig = px.line(
        monthly_df,
        x='Month',
        y=metric,
        markers=True,
        title=f'Monthly {metric} Trend'
    )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title=metric,
        hovermode='x unified',
        **CHART_TEMPLATE['layout']
    )
    
    fig.update_traces(
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['primary'])
    )
    
    fig.update_xaxes(tickangle=45, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    horizontal: bool = False,
    color_by: str = None
) -> Optional[go.Figure]:
    """Create a bar chart."""
    if df is None or x not in df.columns or y not in df.columns:
        return None
    
    if horizontal:
        df = df.sort_values(y, ascending=True)
        fig = px.bar(
            df, x=y, y=x, orientation='h', title=title,
            color=color_by if color_by and color_by in df.columns else y,
            color_continuous_scale='Reds'
        )
    else:
        fig = px.bar(
            df, x=x, y=y, title=title,
            color=color_by if color_by and color_by in df.columns else y,
            color_continuous_scale='Reds'
        )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        showlegend=False,
        coloraxis_showscale=False,
        **CHART_TEMPLATE['layout']
    )
    
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.05)')
    
    return fig


def create_pie_chart(df: pd.DataFrame, values: str, names: str, title: str) -> Optional[go.Figure]:
    """Create a pie chart."""
    if df is None or values not in df.columns or names not in df.columns:
        return None
    
    fig = px.pie(
        df,
        values=values,
        names=names,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hole=0.4  # Makes it a donut chart
    )
    
    fig.update_layout(**CHART_TEMPLATE['layout'])
    
    return fig


def create_category_chart(category_df: pd.DataFrame, chart_type: str = 'bar') -> Optional[go.Figure]:
    """Create a category breakdown chart."""
    if category_df is None or 'Sales' not in category_df.columns:
        return None
    
    name_col = category_df.columns[0]  # First column is the name
    
    if chart_type == 'pie':
        return create_pie_chart(category_df, 'Sales', name_col, f'Sales by {name_col}')
    else:
        # Bar chart with optional profit
        if 'Profit' in category_df.columns:
            fig = px.bar(
                category_df,
                x=name_col,
                y=['Sales', 'Profit'],
                title=f'Sales & Profit by {name_col}',
                barmode='group',
                color_discrete_sequence=[COLORS['primary'], COLORS['success']]
            )
        else:
            fig = px.bar(
                category_df,
                x=name_col,
                y='Sales',
                title=f'Sales by {name_col}',
                color='Sales',
                color_continuous_scale='Reds'
            )
            fig.update_layout(coloraxis_showscale=False)
        
        fig.update_layout(
            xaxis_title='',
            yaxis_title='Amount',
            legend_title='Metric',
            **CHART_TEMPLATE['layout']
        )
        
        return fig


def create_top_items_chart(df: pd.DataFrame, metric: str = 'Sales') -> Optional[go.Figure]:
    """Create a horizontal bar chart for top items."""
    if df is None or 'Name' not in df.columns or metric not in df.columns:
        return None
    
    df = df.sort_values(metric, ascending=True)
    
    fig = px.bar(
        df,
        x=metric,
        y='Name',
        orientation='h',
        title=f'Top Items by {metric}',
        color=metric,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        xaxis_title=metric,
        yaxis_title='',
        showlegend=False,
        coloraxis_showscale=False,
        **CHART_TEMPLATE['layout']
    )
    
    return fig


def create_customers_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create a top customers horizontal bar chart."""
    if df is None or 'Customer' not in df.columns or 'Sales' not in df.columns:
        return None
    
    df = df.sort_values('Sales', ascending=True)
    
    color_col = 'Profit' if 'Profit' in df.columns else 'Sales'
    
    fig = px.bar(
        df,
        x='Sales',
        y='Customer',
        orientation='h',
        title='Top Customers by Revenue',
        color=color_col,
        color_continuous_scale='RdYlGn' if color_col == 'Profit' else 'Purples'
    )
    
    fig.update_layout(
        xaxis_title='Sales',
        yaxis_title='',
        **CHART_TEMPLATE['layout']
    )
    
    return fig


def create_return_rate_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create a return rate bar chart."""
    if df is None or 'Return Rate' not in df.columns:
        return None
    
    name_col = df.columns[0]
    df = df.sort_values('Return Rate', ascending=True)
    
    fig = px.bar(
        df,
        x='Return Rate',
        y=name_col,
        orientation='h',
        title='Items by Return Rate (%)',
        color='Return Rate',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        xaxis_title='Return Rate (%)',
        yaxis_title='',
        showlegend=False,
        coloraxis_showscale=False,
        **CHART_TEMPLATE['layout']
    )
    
    return fig


def create_monthly_change_chart(monthly_df: pd.DataFrame) -> Optional[go.Figure]:
    """Create a month-over-month change chart."""
    if monthly_df is None or 'Sales Change' not in monthly_df.columns:
        return None
    
    # Create color list based on positive/negative
    colors = [COLORS['success'] if x >= 0 else COLORS['danger'] 
              for x in monthly_df['Sales Change'].fillna(0)]
    
    fig = go.Figure(data=[
        go.Bar(
            x=monthly_df['Month'],
            y=monthly_df['Sales Change'],
            marker_color=colors,
            name='Sales Change %'
        )
    ])
    
    fig.update_layout(
        title='Month-over-Month Sales Change (%)',
        xaxis_title='',
        yaxis_title='Change (%)',
        **CHART_TEMPLATE['layout']
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig


def create_scatter_chart(df: pd.DataFrame, x: str, y: str, color: str = None, size: str = None) -> Optional[go.Figure]:
    """Create a scatter plot."""
    if df is None or x not in df.columns or y not in df.columns:
        return None
    
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color if color and color in df.columns else None,
        size=size if size and size in df.columns else None,
        title=f'{y} vs {x}',
        color_discrete_sequence=COLOR_SEQUENCE
    )
    
    # Add zero line if y contains negative values
    if df[y].min() < 0:
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(**CHART_TEMPLATE['layout'])
    
    return fig
