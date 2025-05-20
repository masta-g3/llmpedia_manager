import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import init_auth_sidebar, init_cache_controls
from theme import apply_theme
from plots import create_area_chart, create_bar_chart, create_pie_chart, apply_chart_theme
from db import (
    load_token_usage_logs,
    get_model_stats,
    get_process_stats,
    get_daily_cost_stats
)

# Set page config
st.set_page_config(layout="wide", page_title="Cost Analytics")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access cost analytics")
    st.stop()

# Cache refresh controls
init_cache_controls()

def format_cost(cost):
    """Format cost to display in dollars with appropriate precision."""
    if cost >= 1:
        return f"${cost:.2f}"
    else:
        return f"${cost:.4f}"

def plot_daily_costs(df):
    """Create a stacked area chart of daily costs."""
    # Use the centralized area chart function
    return create_area_chart(
        df=df,
        x_col='date',
        y_cols=['prompt_cost', 'completion_cost'],
        labels={'prompt_cost': 'Prompt Cost', 'completion_cost': 'Completion Cost'},
        colors=['rgba(55, 83, 109, 0.7)', 'rgba(26, 118, 255, 0.7)'],
        height=300,
        xaxis_title="Date",
        yaxis_title="Cost (USD)",
        stacked=True
    )

def plot_model_distribution(df):
    """Create a pie chart of cost distribution by model."""
    # Use the centralized pie chart function
    return create_pie_chart(
        df=df,
        names_col='model_name',
        values_col='total_cost',
        height=400,
        hole=0.4
    )

def plot_process_costs(df):
    """Create a horizontal bar chart of costs by process."""
    # Use the centralized bar chart function
    hover_template = (
        '<b>Process ID:</b> %{y}<br>' +
        '<b>Total Cost:</b> $%{x:.4f}<br>' +
        '<b>Runs:</b> %{customdata[0]:,}<br>' +
        '<b>Prompt Tokens:</b> %{customdata[1]:,}<br>' +
        '<b>Completion Tokens:</b> %{customdata[2]:,}<extra></extra>'
    )
    
    # Sort the dataframe by total_cost to show highest costs first
    df_sorted = df.sort_values('total_cost', ascending=False).head(10)
    
    # Convert process_id to string to ensure proper display
    df_sorted['process_id'] = df_sorted['process_id'].astype(str)
    
    # Check if dark mode based on theme
    is_dark_mode = st.get_option("theme.backgroundColor") in ["#0e1117", "#111111", "#0E0E0E", "#121212"]
    color = '#D9BF8C' if is_dark_mode else '#B5946A'  # Use numeric accent color
    
    return create_bar_chart(
        df=df_sorted,
        x_col='total_cost',
        y_col='process_id',
        color=color,
        height=400,
        xaxis_title="Total Cost (USD)",
        yaxis_title="Process ID",
        horizontal=True,
        hover_template=hover_template,
        custom_data=['total_runs', 'total_prompt_tokens', 'total_completion_tokens']
    )

def main():
    st.title("💰 Cost Analytics")
    
    # Time range selector
    col1, col2 = st.columns([2, 1])
    with col1:
        time_range = st.selectbox(
            "Time Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            index=1
        )
    
    # Calculate date range
    now = datetime.now()
    if time_range == "Last 24 Hours":
        start_date = now - timedelta(days=1)
    elif time_range == "Last 7 Days":
        start_date = now - timedelta(days=7)
    elif time_range == "Last 30 Days":
        start_date = now - timedelta(days=30)
    else:
        start_date = None
    
    # Load data
    daily_costs = get_daily_cost_stats(start_date=start_date)
    model_stats = get_model_stats(start_date=start_date)
    process_stats = get_process_stats(start_date=start_date)
    
    # Calculate total metrics
    total_cost = model_stats['total_cost'].sum()
    total_prompt_cost = model_stats['total_prompt_cost'].sum()
    total_completion_cost = model_stats['total_completion_cost'].sum()
    total_runs = model_stats['total_runs'].sum()
    
    # Display high-level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cost", format_cost(total_cost))
    with col2:
        st.metric("Prompt Cost", format_cost(total_prompt_cost))
    with col3:
        st.metric("Completion Cost", format_cost(total_completion_cost))
    with col4:
        st.metric("Total Runs", f"{total_runs:,}")
    
    # Daily cost trend
    st.subheader("Daily Cost Trend")
    st.plotly_chart(plot_daily_costs(daily_costs), use_container_width=True)
    
    # Model distribution and process costs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost by Model")
        st.plotly_chart(plot_model_distribution(model_stats), use_container_width=True)
    
    with col2:
        st.subheader("Cost by Process")
        # Create a more descriptive title for the chart
        fig = plot_process_costs(process_stats)
        fig.update_layout(title="")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed tables
    tab1, tab2 = st.tabs(["Model Details", "Process Details"])
    
    with tab1:
        st.dataframe(
            model_stats.style
            .format({
                'total_prompt_cost': lambda x: format_cost(x),
                'total_completion_cost': lambda x: format_cost(x),
                'total_cost': lambda x: format_cost(x),
                'total_runs': '{:,}'.format,
                'total_prompt_tokens': '{:,}'.format,
                'total_completion_tokens': '{:,}'.format
            })
        )
    
    with tab2:
        st.dataframe(
            process_stats.style
            .format({
                'total_prompt_cost': lambda x: format_cost(x),
                'total_completion_cost': lambda x: format_cost(x),
                'total_cost': lambda x: format_cost(x),
                'total_runs': '{:,}'.format,
                'total_prompt_tokens': '{:,}'.format,
                'total_completion_tokens': '{:,}'.format
            })
        )

if __name__ == "__main__":
    main() 