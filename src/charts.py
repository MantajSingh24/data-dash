"""
Chart creation for Data Dash.
Simple Plotly visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Color palette
COLORS = ['#ff6b6b', '#feca57', '#48dbfb', '#2ed573', '#ff9ff3', '#54a0ff']


def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False) -> go.Figure:
    """
    Create a bar chart.
    
    Args:
        df: Input dataframe
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
        horizontal: If True, makes bars horizontal
    """
    if horizontal:
        df = df.sort_values(y, ascending=True)
        fig = px.bar(df, x=y, y=x, orientation='h', title=title,
                     color=y, color_continuous_scale='Reds')
    else:
        fig = px.bar(df, x=x, y=y, title=title,
                     color=y, color_continuous_scale='Reds')
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        showlegend=False,
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_pie_chart(df: pd.DataFrame, values: str, names: str, title: str) -> go.Figure:
    """
    Create a donut/pie chart.
    
    Args:
        df: Input dataframe
        values: Column with values
        names: Column with labels
        title: Chart title
    """
    fig = px.pie(
        df,
        values=values,
        names=names,
        title=title,
        color_discrete_sequence=COLORS
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hole=0.4
    )
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    return fig


def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    """
    Create a line chart.
    
    Args:
        df: Input dataframe
        x: Column for x-axis
        y: Column for y-axis
        title: Chart title
    """
    fig = px.line(
        df, x=x, y=y,
        title=title,
        markers=True
    )
    
    fig.update_traces(
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title=y,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig
