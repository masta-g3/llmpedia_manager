import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from utils import init_auth_sidebar
from theme import apply_theme
from plots import create_bar_chart, apply_chart_theme
from db import load_workflow_runs

# Set page config
st.set_page_config(layout="wide", page_title="Workflow Monitor")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access workflow monitoring")
    st.stop()

# Initialize session state for auto-refresh
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
    
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

def get_workflow_stats(df):
    """Calculate high-level workflow statistics."""
    total_runs = len(df['tstp'].unique())
    success_rate = (df['status'] == 'success').mean() * 100
    last_run = df['tstp'].max()
    error_count = (df['status'] == 'error').sum()
    
    return {
        'total_runs': total_runs,
        'success_rate': success_rate,
        'last_run': last_run,
        'error_count': error_count
    }

def plot_step_performance(df):
    """Create a step performance visualization."""
    step_stats = df.groupby('step_name').agg({
        'status': lambda x: (x == 'success').mean() * 100,
        'id': 'count'
    }).reset_index()
    step_stats.columns = ['step_name', 'success_rate', 'total_runs']
    
    # Sort by workflow order (using the step number prefix)
    step_stats['step_num'] = step_stats['step_name'].str.extract('(\d+)').astype(float)
    step_stats = step_stats.sort_values('step_num')
    
    # Custom hover template
    hover_template = 'Step: %{x}<br>Success Rate: %{y:.1f}%<br>Total Runs: %{customdata}<extra></extra>'
    
    # Use centralized bar chart function
    fig = create_bar_chart(
        df=step_stats,
        x_col='step_name',
        y_col='success_rate',
        color='rgba(55, 83, 109, 0.7)',
        height=400,
        xaxis_title="",
        yaxis_title="Success Rate (%)",
        hover_template=hover_template,
        custom_data=['total_runs']
    )
    
    # Additional customizations specific to this chart
    fig.update_layout(
        xaxis=dict(
            tickangle=45,
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.1)',
            range=[0, 100]
        )
    )
    
    return fig

def plot_timeline(df):
    """Create a timeline visualization of workflow runs with step-based y-axis."""
    # Prepare data for timeline
    timeline_data = df.copy()
    
    # Group runs into workflow executions (clusters)
    timeline_data = timeline_data.sort_values('tstp')
    timeline_data['time_diff'] = timeline_data['tstp'].diff()
    timeline_data['workflow_execution'] = (timeline_data['time_diff'] > pd.Timedelta(minutes=30)).cumsum()
    
    # Get ordered list of steps for y-axis (sorted by step number)
    step_df = pd.DataFrame({'step_name': timeline_data['step_name'].unique()})
    step_df['step_num'] = step_df['step_name'].str.extract('(\d+)').astype(float)
    step_order = step_df.sort_values('step_num')['step_name'].tolist()
    
    fig = go.Figure()
    
    # Add workflow execution clusters with alternating colors
    for workflow_id, workflow_group in timeline_data.groupby('workflow_execution'):
        if len(workflow_group) > 0:
            start_time = workflow_group['tstp'].min()
            end_time = workflow_group['tstp'].max()
            time_padding = pd.Timedelta(minutes=5)
            
            # Add shaded region for workflow execution
            fig.add_vrect(
                x0=start_time - time_padding,
                x1=end_time + time_padding,
                fillcolor=f'rgba(200, 200, 200, {0.1 if workflow_id % 2 == 0 else 0.2})',
                layer='below',
                line_width=0,
                showlegend=False
            )
        
        # Add all runs in this workflow with color indicating status
        fig.add_trace(go.Scatter(
            x=workflow_group['tstp'],
            y=workflow_group['step_name'],
            mode='markers',
            marker=dict(
                color=workflow_group['status'].map({'success': 'rgba(46, 184, 46, 0.7)', 'error': 'rgba(255, 0, 0, 0.7)'}),
                size=8,
                symbol=workflow_group['status'].apply(lambda x: 'x' if x == 'error' else 'circle')
            ),
            name=f'Execution {workflow_id + 1}',
            hovertemplate='Time: %{x}<br>Step: %{y}<br>Status: %{customdata}<extra></extra>',
            customdata=workflow_group['status'],
            showlegend=workflow_id == 0  # Show legend only for first workflow
        ))
    
    # Apply the centralized chart theme
    fig = apply_chart_theme(fig, height=max(300, len(step_order) * 25))
    
    # Apply specific customizations for this chart
    fig.update_layout(
        margin=dict(l=150, r=0),  # Increased left margin for step names
        xaxis=dict(
            title="",
            showgrid=True,
            gridcolor='rgba(128,128,128,0.1)'
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor='rgba(128,128,128,0.1)',
            categoryorder='array',
            categoryarray=step_order,  # Use numerically sorted step order
            tickmode='array',
            ticktext=step_order,
            tickvals=step_order
        ),
        showlegend=True
    )
    
    return fig

def display_error_log(df):
    """Display recent errors in a clean format."""
    error_df = df[df['status'] == 'error'].copy()
    error_df['tstp'] = error_df['tstp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    if len(error_df) == 0:
        st.info("No errors found in the selected time range.")
        return
    
    for _, row in error_df.iterrows():
        with st.expander(f"🔴 {row['step_name']} - {row['tstp']}", expanded=False):
            st.code(row['error_message'], language='python')

def main():
    st.title("🔄 Workflow Monitor")
    
    # Refresh controls
    col1, col2, col3, col4 = st.columns([1.5, 0.5, 1, 1])
    with col1:
        st.session_state.auto_refresh = st.checkbox("Auto-refresh (30s)", value=st.session_state.auto_refresh)
    with col2:
        if st.button("🔄 Refresh"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
    with col3:
        st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh > 30:  # Refresh every 30 seconds
            st.session_state.last_refresh = datetime.now()
            time.sleep(0.1)  # Small delay to prevent excessive refreshes
            st.rerun()
    
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
    
    # Load workflow data
    df = load_workflow_runs(start_date=start_date)
    
    # Calculate stats
    stats = get_workflow_stats(df)
    
    # Display high-level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Workflow Runs", f"{stats['total_runs']:,}")
    with col2:
        st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
    with col3:
        st.metric("Last Run", stats['last_run'].strftime('%Y-%m-%d %H:%M:%S'))
    with col4:
        st.metric("Total Errors", f"{stats['error_count']:,}")
    
    # Step Performance
    st.subheader("Step Performance")
    st.plotly_chart(plot_step_performance(df), use_container_width=True)
    
    # Timeline
    st.subheader("Success Rate Timeline")
    st.plotly_chart(plot_timeline(df), use_container_width=True)
    
    # Error Log
    st.subheader("Error Log")
    display_error_log(df)

if __name__ == "__main__":
    main() 