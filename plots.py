import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional, Union, Any, Tuple

def apply_chart_theme(fig, 
                      height: int = 300, 
                      title: Optional[str] = None, 
                      xaxis_title: Optional[str] = None, 
                      yaxis_title: Optional[str] = None) -> go.Figure:
    """
    Apply zen-inspired minimalist theme to a plotly figure.
    
    Args:
        fig: The plotly figure to apply theming to
        height: Chart height in pixels (default: 300)
        title: Optional chart title
        xaxis_title: Optional x-axis title
        yaxis_title: Optional y-axis title
        
    Returns:
        The themed figure
    """
    # Check if we're in dark mode by checking the background color
    is_dark_mode = st.get_option("theme.backgroundColor") in ["#0e1117", "#111111", "#0E0E0E", "#121212"]
    
    # Set colors based on theme
    if is_dark_mode:
        grid_color = 'rgba(80,80,80,0.15)'
        accent_color = '#7F95D1'  # Calm blue accent
        text_color = '#E0E0E0'
    else:
        grid_color = 'rgba(180,180,180,0.15)'
        accent_color = '#5D76B5'  # Calm blue accent
        text_color = '#333333'
    
    fig.update_layout(
        template='plotly_white',
        height=height,
        margin=dict(t=30 if title else 10, b=0, l=0, r=10),
        title=dict(
            text=title,
            font=dict(
                family='Inter, sans-serif',
                size=14,
                color=text_color
            )
        ) if title else None,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='Inter, sans-serif',
            size=12,
            color=text_color
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter, sans-serif',
                size=10
            )
        )
    )
    
    # Update grid color based on theme
    fig.update_xaxes(
        gridcolor=grid_color, 
        zerolinecolor=grid_color,
        title=dict(
            font=dict(
                family='Inter, sans-serif',
                size=11
            )
        ),
        tickfont=dict(
            family='Inter, sans-serif',
            size=10
        )
    )
    
    fig.update_yaxes(
        gridcolor=grid_color, 
        zerolinecolor=grid_color,
        title=dict(
            font=dict(
                family='Inter, sans-serif',
                size=11
            )
        ),
        tickfont=dict(
            family='Inter, sans-serif',
            size=10
        )
    )
    
    # Update color sequence for consistent branding
    if is_dark_mode:
        # Dark mode color sequence - subtle, zen-inspired colors
        colors = ['#7F95D1', '#D9BF8C', '#88A096', '#A8A8A8']
    else:
        # Light mode color sequence - subtle, zen-inspired colors
        colors = ['#5D76B5', '#B5946A', '#6A8475', '#888888']
        
    # Apply colors to traces if they exist
    if fig.data:
        for i, trace in enumerate(fig.data):
            if hasattr(trace, 'marker') and trace.marker:
                # For bar charts
                if trace.type == 'bar':
                    trace.marker.color = colors[i % len(colors)]
                # For scatter plots
                elif trace.type == 'scatter' and trace.mode and 'lines' in trace.mode:
                    trace.line.color = colors[i % len(colors)]
                    if 'markers' in trace.mode:
                        trace.marker.color = colors[i % len(colors)]
    
    return fig

def create_time_series(df: pd.DataFrame, 
                      x_col: str, 
                      y_cols: Union[str, List[str]], 
                      labels: Optional[Dict[str, str]] = None,
                      height: int = 300,
                      title: Optional[str] = None,
                      xaxis_title: Optional[str] = None,
                      yaxis_title: Optional[str] = None,
                      use_markers: bool = True,
                      show_legend: bool = True) -> go.Figure:
    """ Create a time series line chart with consistent styling. """
    fig = go.Figure()
    
    # Convert y_cols to list if it's a string
    if isinstance(y_cols, str):
        y_cols = [y_cols]
    
    # Set default labels if not provided
    if labels is None:
        labels = {col: col for col in y_cols}
    
    # Mode for the scatter plot
    mode = 'lines+markers' if use_markers else 'lines'
    
    # Add traces for each y column
    for y_col in y_cols:
        # Get the label for this column
        label = labels.get(y_col, y_col)
        
        # Get data for this column
        data = df.groupby(x_col)[y_col].sum().reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=data[x_col],
                y=data[y_col],
                name=label,
                mode=mode
            )
        )
    
    # Apply theme
    fig = apply_chart_theme(
        fig, 
        height=height, 
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    
    # Update legend visibility
    fig.update_layout(showlegend=show_legend)
    fig.update_layout(title="")
    
    return fig

def create_bar_chart(df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    color: Optional[str] = None,
                    height: int = 300,
                    title: Optional[str] = None,
                    xaxis_title: Optional[str] = None,
                    yaxis_title: Optional[str] = None,
                    hover_template: Optional[str] = None,
                    custom_data: Optional[List[str]] = None,
                    horizontal: bool = False,
                    sort_values: bool = False) -> go.Figure:
    """
    Create a zen-inspired minimalist bar chart with consistent styling.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis data
        y_col: Column name for y-axis data
        color: Color for the bars (if None, uses theme colors)
        height: Chart height in pixels (default: 300)
        title: Optional chart title
        xaxis_title: Optional x-axis title
        yaxis_title: Optional y-axis title
        hover_template: Optional custom hover template
        custom_data: Optional list of column names to include in hover data
        horizontal: Whether to create a horizontal bar chart (default: False)
        sort_values: Whether to sort by values (default: False)
        
    Returns:
        Plotly figure object
    """
    # Sort the data if requested
    if sort_values:
        df = df.sort_values(y_col)
    
    fig = go.Figure()
    
    # Use theme colors if not specified
    if color is None:
        # Check if dark mode
        is_dark_mode = st.get_option("theme.backgroundColor") in ["#0e1117", "#111111", "#0E0E0E", "#121212"]
        # Use the numeric accent color from our theme
        color = '#D9BF8C' if is_dark_mode else '#B5946A'
    
    # Prepare custom_data for hover template
    customdata = None
    if custom_data:
        customdata = df[custom_data].values
    
    # Create the appropriate bar trace based on orientation
    if horizontal:
        # In horizontal bar charts, x and y are swapped
        fig.add_trace(go.Bar(
            y=df[y_col],  # This is correct - y in horizontal bar chart is the category axis
            x=df[x_col],  # This is correct - x in horizontal bar chart is the value axis
            marker_color=color,
            orientation='h',
            hovertemplate=hover_template,
            customdata=customdata,
            # Add zen styling - subtle opacity and thinner bars
            opacity=0.85,
            width=0.7
        ))
    else:
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker_color=color,
            hovertemplate=hover_template,
            customdata=customdata,
            # Add zen styling - subtle opacity and thinner bars
            opacity=0.85,
            width=0.7
        ))
    
    # Apply theme
    fig = apply_chart_theme(
        fig, 
        height=height, 
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    
    # For horizontal bar charts, we need additional formatting
    if horizontal:
        # Ensure the categorical y-axis displays properly
        fig.update_yaxes(
            automargin=True,  # Make sure there's enough room for labels
            tickmode='array',  # Use explicit ticks
            tickvals=list(range(len(df))),  # One tick per category
            ticktext=df[y_col].tolist()  # Use the actual category names
        )
    
    return fig

def create_grouped_bar_chart(df: pd.DataFrame,
                           x_col: str,
                           y_cols: List[str],
                           labels: Optional[Dict[str, str]] = None,
                           colors: Optional[List[str]] = None,
                           height: int = 300,
                           title: Optional[str] = None,
                           xaxis_title: Optional[str] = None,
                           yaxis_title: Optional[str] = None,
                           barmode: str = 'group') -> go.Figure:
    """
    Create a grouped or stacked bar chart with consistent styling.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis data
        y_cols: List of column names for y-axis data
        labels: Optional dictionary mapping column names to display labels
        colors: Optional list of colors for the bars
        height: Chart height in pixels (default: 300)
        title: Optional chart title
        xaxis_title: Optional x-axis title
        yaxis_title: Optional y-axis title
        barmode: Bar mode - 'group' or 'stack' (default: 'group')
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Default colors if not provided
    if colors is None:
        colors = ['rgba(55, 83, 109, 0.7)', 'rgba(26, 118, 255, 0.7)', 
                 'rgba(78, 121, 167, 0.7)', 'rgba(242, 142, 43, 0.7)']
    
    # Set default labels if not provided
    if labels is None:
        labels = {col: col for col in y_cols}
    
    # Add a trace for each y column
    for i, y_col in enumerate(y_cols):
        color = colors[i % len(colors)]  # Cycle through colors if more columns than colors
        label = labels.get(y_col, y_col)
        
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=label,
            marker_color=color
        ))
    
    # Apply theme and set barmode
    fig = apply_chart_theme(
        fig, 
        height=height, 
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    fig.update_layout(barmode=barmode)
    
    return fig

def create_area_chart(df: pd.DataFrame,
                     x_col: str,
                     y_cols: List[str],
                     labels: Optional[Dict[str, str]] = None,
                     colors: Optional[List[str]] = None,
                     height: int = 300,
                     title: Optional[str] = None,
                     xaxis_title: Optional[str] = None,
                     yaxis_title: Optional[str] = None,
                     stacked: bool = True) -> go.Figure:
    """
    Create a stacked or overlapping area chart with consistent styling.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis data
        y_cols: List of column names for y-axis data
        labels: Optional dictionary mapping column names to display labels
        colors: Optional list of colors for the areas
        height: Chart height in pixels (default: 300)
        title: Optional chart title
        xaxis_title: Optional x-axis title
        yaxis_title: Optional y-axis title
        stacked: Whether to create a stacked area chart (default: True)
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Default colors if not provided
    if colors is None:
        colors = ['rgba(55, 83, 109, 0.7)', 'rgba(26, 118, 255, 0.7)', 
                 'rgba(78, 121, 167, 0.7)', 'rgba(242, 142, 43, 0.7)']
    
    # Set default labels if not provided
    if labels is None:
        labels = {col: col for col in y_cols}
    
    # Add a trace for each y column
    for i, y_col in enumerate(y_cols):
        color = colors[i % len(colors)]  # Cycle through colors if more columns than colors
        label = labels.get(y_col, y_col)
        
        # Set up stackgroup for stacked charts
        stackgroup = 'one' if stacked else None
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            name=label,
            mode='lines',
            line=dict(width=0.5, color=color),
            fill='tonexty',
            stackgroup=stackgroup
        ))
    
    # Apply theme
    fig = apply_chart_theme(
        fig, 
        height=height, 
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    
    return fig

def create_pie_chart(df: pd.DataFrame,
                    names_col: str,
                    values_col: str,
                    height: int = 300,
                    title: Optional[str] = None,
                    hole: float = 0.4,
                    color_sequence: Optional[List[str]] = None) -> go.Figure:
    """
    Create a pie or donut chart with consistent styling.
    
    Args:
        df: DataFrame containing the data
        names_col: Column name for segment labels
        values_col: Column name for segment values
        height: Chart height in pixels (default: 300)
        title: Optional chart title
        hole: Size of hole for donut chart (0 for pie chart, default: 0.4)
        color_sequence: Optional list of colors for the segments
        
    Returns:
        Plotly figure object
    """
    # Create the pie chart
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        height=height,
        title=title,
        hole=hole,
        color_discrete_sequence=color_sequence
    )
    
    # Apply theme - simplified for pie charts
    fig.update_layout(
        margin=dict(t=30 if title else 10, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=st.get_option("theme.textColor")),
        title=""
    )
    
    return fig

def create_heatmap(df: pd.DataFrame,
                  x_col: str,
                  y_col: str,
                  z_col: str,
                  height: int = 300,
                  title: Optional[str] = None,
                  xaxis_title: Optional[str] = None,
                  yaxis_title: Optional[str] = None,
                  colorscale: str = 'Blues') -> go.Figure:
    """
    Create a heatmap with consistent styling.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis data
        y_col: Column name for y-axis data
        z_col: Column name for z-axis data (color intensity)
        height: Chart height in pixels (default: 300)
        title: Optional chart title
        xaxis_title: Optional x-axis title
        yaxis_title: Optional y-axis title
        colorscale: Colorscale for the heatmap (default: 'Blues')
        
    Returns:
        Plotly figure object
    """
    # Pivot the data for heatmap if needed
    if len(df.columns) > 3:
        pivot_df = df.pivot(index=y_col, columns=x_col, values=z_col)
        z_values = pivot_df.values
        x_values = pivot_df.columns
        y_values = pivot_df.index
    else:
        # Assume already in the right format
        z_values = df[z_col].values
        x_values = df[x_col].unique()
        y_values = df[y_col].unique()
    
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale=colorscale
    ))
    
    # Apply theme
    fig = apply_chart_theme(
        fig, 
        height=height, 
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    
    return fig

def format_hover_template(metric_name: str, date_format: str = '%Y-%m-%d') -> str:
    """
    Generate consistent hover templates for charts.
    
    Args:
        metric_name: Name of the metric to display
        date_format: Format for date display (default: '%Y-%m-%d')
        
    Returns:
        Hover template string
    """
    return f"{metric_name}: %{{y:,.0f}}<br>Date: %{{x|{date_format}}}<extra></extra>"

def get_theme_colors(is_dark_mode=None):
    """Get theme colors for consistent chart styling."""
    if is_dark_mode is None:
        is_dark_mode = st.get_option("theme.backgroundColor") in ["#0e1117", "#111111", "#0E0E0E", "#121212"]
    
    if is_dark_mode:
        return {
            'primary': '#7F95D1',
            'secondary': '#D9BF8C', 
            'tertiary': '#88A096',
            'quaternary': '#A8A8A8',
            'palette': ['#7F95D1', '#D9BF8C', '#88A096', '#A8A8A8', '#C9A96E', '#6B8E88']
        }
    else:
        return {
            'primary': '#5D76B5',
            'secondary': '#B5946A',
            'tertiary': '#6A8475', 
            'quaternary': '#888888',
            'palette': ['#5D76B5', '#B5946A', '#6A8475', '#888888', '#A67C52', '#5A7169']
        }

def create_grouped_time_series(df: pd.DataFrame,
                             chart_type: str = "area",
                             group_by: str = "token_type",
                             height: int = 300,
                             title: Optional[str] = None,
                             xaxis_title: Optional[str] = "Date",
                             yaxis_title: Optional[str] = "Cost (USD)") -> go.Figure:
    """
    Create a flexible time series chart that can group by different dimensions.
    
    Args:
        df: DataFrame with columns: date, category, cost, runs
        chart_type: Either "area" or "bar" 
        group_by: The grouping dimension (for color mapping)
        height: Chart height in pixels
        title: Optional chart title
        xaxis_title: X-axis title
        yaxis_title: Y-axis title
        
    Returns:
        Plotly figure object
    """
    if df.empty:
        ## Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        return apply_chart_theme(fig, height=height, title=title, 
                               xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    
    ## Get theme colors
    colors = get_theme_colors()
    color_palette = colors['palette']
    
    ## Pivot data for plotting
    pivot_df = df.pivot(index='date', columns='category', values='cost').fillna(0)
    
    ## Sort categories for consistent legend order
    categories = sorted(pivot_df.columns.tolist())
    
    ## Create figure
    fig = go.Figure()
    
    if chart_type == "area":
        ## Create stacked area chart
        for i, category in enumerate(categories):
            if category in pivot_df.columns:
                color = color_palette[i % len(color_palette)]
                ## Make colors semi-transparent for area charts
                if color.startswith('#'):
                    color = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.7)"
                
                fig.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df[category],
                    name=category,
                    mode='lines',
                    line=dict(width=0.5),
                    fill='tonexty',
                    stackgroup='one',
                    fillcolor=color,
                    line_color=color
                ))
    
    elif chart_type == "bar":
        ## Create stacked bar chart
        for i, category in enumerate(categories):
            if category in pivot_df.columns:
                color = color_palette[i % len(color_palette)]
                
                fig.add_trace(go.Bar(
                    x=pivot_df.index,
                    y=pivot_df[category],
                    name=category,
                    marker_color=color,
                    opacity=0.85
                ))
        
        ## Set bar mode to stacked
        fig.update_layout(barmode='stack')
    
    ## Apply theme
    fig = apply_chart_theme(
        fig, 
        height=height, 
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    
    # Explicitly clear title since we use Streamlit section headers
    fig.update_layout(title="")
    
    return fig