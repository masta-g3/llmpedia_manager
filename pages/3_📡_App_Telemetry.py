import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import init_auth_sidebar
from theme import apply_theme
from plots import apply_chart_theme, create_time_series
from db import (
    load_visit_logs,
    load_qna_logs,
    load_error_logs,
    get_top_entrypoints,
    get_hourly_stats,
    get_daily_stats
)

# Set page config
st.set_page_config(layout="wide", page_title="Telemetry Dashboard")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access telemetry")
    st.stop()

def plot_hourly_distribution(df, title='Hourly Distribution'):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['hour'],
            y=df['count'],
            mode='lines+markers',
            line=dict(shape='spline', smoothing=0.3),
            marker=dict(size=8)
        )
    )
    
    # Apply consistent chart theme
    fig = apply_chart_theme(
        fig,
        height=300,
        title=title,
        xaxis_title="Hour of Day",
        yaxis_title="Count"
    )
    
    # Additional customizations
    fig.update_layout(showlegend=False)
    
    return fig

def plot_daily_metrics(df, title='Daily Trend'):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['count'],
            mode='lines+markers',
            line=dict(shape='spline', smoothing=0.3),
            marker=dict(size=8)
        )
    )
    
    # Apply consistent chart theme
    fig = apply_chart_theme(
        fig,
        height=300,
        title=title,
        xaxis_title="Date",
        yaxis_title="Count"
    )
    
    # Additional customizations
    fig.update_layout(showlegend=False)
    
    return fig

def main():
    st.markdown('''
        <style>
        .metric-card {
            background-color: rgba(128, 128, 128, 0.05);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #666;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    st.title("📡 System Telemetry")
    
    # Time range selector
    col1, col2 = st.columns(2)
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
    
    # Load data for the selected time range
    visits_df = load_visit_logs(start_date=start_date)
    qna_df = load_qna_logs(start_date=start_date)
    error_df = load_error_logs(start_date=start_date)
    
    # High-level metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">Total Visits</div>
                <div class="metric-value">{:,}</div>
            </div>
        '''.format(len(visits_df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">Questions Asked</div>
                <div class="metric-value">{:,}</div>
            </div>
        '''.format(len(qna_df)), unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">System Errors</div>
                <div class="metric-value">{:,}</div>
            </div>
        '''.format(len(error_df)), unsafe_allow_html=True)
    
    st.markdown("### Temporal Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Visits", "Q&A", "Errors"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            daily_visits = get_daily_stats('visit_logs', start_date=start_date)
            st.plotly_chart(plot_daily_metrics(daily_visits, 'Daily Visits'), use_container_width=True)
        with col2:
            hourly_visits = get_hourly_stats('visit_logs', start_date=start_date)
            st.plotly_chart(plot_hourly_distribution(hourly_visits, 'Hourly Distribution'), use_container_width=True)
        
        # Top entrypoints
        st.markdown("### Top Entry Points")
        entrypoint_counts = get_top_entrypoints(limit=10, start_date=start_date)
        st.bar_chart(entrypoint_counts.set_index('entrypoint')['count'])
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            daily_qna = get_daily_stats('qna_logs', start_date=start_date)
            st.plotly_chart(plot_daily_metrics(daily_qna, 'Daily Questions'), use_container_width=True)
        with col2:
            hourly_qna = get_hourly_stats('qna_logs', start_date=start_date)
            st.plotly_chart(plot_hourly_distribution(hourly_qna, 'Questions by Hour'), use_container_width=True)
        
        # Recent questions
        st.markdown("### Recent Questions")
        st.dataframe(
            qna_df[['tstp', 'user_question', 'response']]
            .head(5)
            .style.format({'tstp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')})
        )
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            daily_errors = get_daily_stats('error_logs', start_date=start_date)
            st.plotly_chart(plot_daily_metrics(daily_errors, 'Daily Errors'), use_container_width=True)
        with col2:
            hourly_errors = get_hourly_stats('error_logs', start_date=start_date)
            st.plotly_chart(plot_hourly_distribution(hourly_errors, 'Errors by Hour'), use_container_width=True)
        
        # Recent errors
        st.markdown("### Recent Errors")
        st.dataframe(
            error_df[['tstp', 'error']]
            .head(5)
            .style.format({'tstp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')})
        )

if __name__ == "__main__":
    main() 