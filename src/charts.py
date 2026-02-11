"""
Chart creation for Data Dash.
Plotly visualizations with consistent styling.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Color palette
COLORS = {
    'primary': '#ff6b6b',
    'secondary': '#feca57',
    'success': '#2ed573',
    'danger': '#ff4757',
    'info': '#48dbfb',
}

COLOR_SEQUENCE = ['#ff6b6b', '#feca57', '#48dbfb', '#2ed573', '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3']

# Chart styling
CHART_LAYOUT = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'family': 'Poppins, sans-serif', 'color': '#eaeaea'},
    'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 30},
}


def create_bar_chart(df, x, y, title, horizontal=False, color_by=None):
    """Create a bar chart."""
    if df is None or x not in df.columns or y not in df.columns:
        return None
    
    if horizontal:
        df = df.sort_values(y, ascending=True)
        fig = px.bar(df, x=y, y=x, orientation='h', title=title,
                     color=color_by if color_by and color_by in df.columns else y,
                     color_continuous_scale='Reds')
    else:
        fig = px.bar(df, x=x, y=y, title=title,
                     color=color_by if color_by and color_by in df.columns else y,
                     color_continuous_scale='Reds')
    
    fig.update_layout(xaxis_title='', yaxis_title='', showlegend=False,
                      coloraxis_showscale=False, **CHART_LAYOUT)
    return fig


def create_pie_chart(df, values, names, title):
    """Create a donut/pie chart."""
    if df is None or values not in df.columns or names not in df.columns:
        return None
    
    fig = px.pie(df, values=values, names=names, title=title,
                 color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_traces(textposition='inside', textinfo='percent+label', hole=0.4)
    fig.update_layout(**CHART_LAYOUT)
    return fig


def create_line_chart(df, x, y, title):
    """Create a line chart."""
    if df is None or x not in df.columns or y not in df.columns:
        return None
    
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    fig.update_traces(line=dict(color=COLORS['primary'], width=3), marker=dict(size=8))
    fig.update_layout(xaxis_title='', yaxis_title=y, **CHART_LAYOUT)
    return fig


def create_monthly_trend_chart(monthly_df, metric='Sales'):
    """Create a monthly trend line chart."""
    if monthly_df is None or metric not in monthly_df.columns:
        return None
    
    fig = px.line(monthly_df, x='Month', y=metric, markers=True,
                  title=f'Monthly {metric} Trend')
    fig.update_layout(xaxis_title='', yaxis_title=metric, hovermode='x unified', **CHART_LAYOUT)
    fig.update_traces(line=dict(color=COLORS['primary'], width=3),
                      marker=dict(size=8, color=COLORS['primary']))
    fig.update_xaxes(tickangle=45)
    return fig


def create_top_items_chart(df, metric='Sales'):
    """Create a horizontal bar chart for top items."""
    if df is None or 'Name' not in df.columns or metric not in df.columns:
        return None
    
    df = df.sort_values(metric, ascending=True)
    fig = px.bar(df, x=metric, y='Name', orientation='h',
                 title=f'Top Items by {metric}',
                 color=metric, color_continuous_scale='Reds')
    fig.update_layout(xaxis_title=metric, yaxis_title='', showlegend=False,
                      coloraxis_showscale=False, **CHART_LAYOUT)
    return fig


def create_category_chart(category_df, chart_type='bar'):
    """Create a category breakdown chart (bar or pie)."""
    if category_df is None or 'Sales' not in category_df.columns:
        return None
    
    name_col = category_df.columns[0]
    
    if chart_type == 'pie':
        return create_pie_chart(category_df, 'Sales', name_col, f'Sales by {name_col}')
    
    # Bar chart
    if 'Profit' in category_df.columns:
        fig = px.bar(category_df, x=name_col, y=['Sales', 'Profit'],
                     title=f'Sales & Profit by {name_col}', barmode='group',
                     color_discrete_sequence=[COLORS['primary'], COLORS['success']])
    else:
        fig = px.bar(category_df, x=name_col, y='Sales',
                     title=f'Sales by {name_col}',
                     color='Sales', color_continuous_scale='Reds')
        fig.update_layout(coloraxis_showscale=False)
    
    fig.update_layout(xaxis_title='', yaxis_title='Amount', **CHART_LAYOUT)
    return fig
