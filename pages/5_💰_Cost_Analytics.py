import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import init_auth_sidebar
from theme import apply_theme
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

def format_cost(cost):
    """Format cost to display in dollars with appropriate precision."""
    if cost >= 1:
        return f"${cost:.2f}"
    else:
        return f"${cost:.4f}"

def plot_daily_costs(df):
    """Create a stacked area chart of daily costs."""
    fig = go.Figure()
    
    # Add prompt costs
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['prompt_cost'],
        name='Prompt Cost',
        fill='tonexty',
        mode='lines',
        line=dict(width=0.5, color='rgba(55, 83, 109, 0.7)'),
        stackgroup='one'
    ))
    
    # Add completion costs
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['completion_cost'],
        name='Completion Cost',
        fill='tonexty',
        mode='lines',
        line=dict(width=0.5, color='rgba(26, 118, 255, 0.7)'),
        stackgroup='one'
    ))
    
    fig.update_layout(
        template='plotly_white',
        height=300,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis_title="Date",
        yaxis_title="Cost (USD)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=st.get_option("theme.textColor")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    
    return fig

def plot_model_distribution(df):
    """Create a pie chart of cost distribution by model."""
    fig = go.Figure(data=[go.Pie(
        labels=df['model_name'],
        values=df['total_cost'],
        hole=.4,
        textinfo='label+percent',
        textposition='outside',
        pull=[0.1 if i == 0 else 0 for i in range(len(df))]
    )])
    
    fig.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=st.get_option("theme.textColor")),
        showlegend=False
    )
    
    return fig

def plot_process_costs(df):
    """Create a horizontal bar chart of costs by process."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['process_id'],
        x=df['total_cost'],
        orientation='h',
        marker_color='rgba(55, 83, 109, 0.7)',
        customdata=df[['total_runs', 'total_prompt_tokens', 'total_completion_tokens']],
        hovertemplate='Process: %{y}<br>' +
                      'Total Cost: $%{x:.4f}<br>' +
                      'Runs: %{customdata[0]}<br>' +
                      'Prompt Tokens: %{customdata[1]}<br>' +
                      'Completion Tokens: %{customdata[2]}<extra></extra>'
    ))
    
    fig.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis_title="Total Cost (USD)",
        yaxis_title="Process ID",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=st.get_option("theme.textColor")),
        showlegend=False
    )
    
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    
    return fig

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
        st.plotly_chart(plot_process_costs(process_stats.head(10)), use_container_width=True)
    
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