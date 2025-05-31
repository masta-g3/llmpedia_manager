import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import init_auth_sidebar, init_cache_controls, init_date_range_selector
from theme import apply_theme
from plots import apply_chart_theme, create_time_series
from db import (
    load_visit_logs,
    load_qna_logs,
    load_error_logs,
    get_top_entrypoints,
    get_hourly_stats,
    get_daily_stats,
    load_poll_results
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

# Cache refresh controls
init_cache_controls()

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

def plot_poll_results_over_time(df, title='Poll Results Over Time'):
    """Plots poll results over time, with a line for each feature."""
    fig = go.Figure()
    
    # Clean feature names
    df['feature_name'] = df['feature_name'].str.split(':').str[0].str.replace('\*\*', '', regex=True)

    features = df['feature_name'].unique()
    
    for feature in features:
        feature_df = df[df['feature_name'] == feature]
        fig.add_trace(
            go.Scatter(
                x=feature_df['date'],
                y=feature_df['vote_count'],
                mode='lines+markers',
                name=feature,
                line=dict(shape='spline', smoothing=0.3),
                marker=dict(size=8)
            )
        )
    
    fig = apply_chart_theme(
        fig,
        height=400, # Adjusted height for better legend visibility
        title=title,
        xaxis_title="Date",
        yaxis_title="Number of Votes"
    )
    fig.update_layout(showlegend=True) # Show legend for features
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
    
    # Time range selector using the new component
    col1, col2 = st.columns(2)
    with col1:
        start_date, end_date = init_date_range_selector(
            key_prefix="telemetry",
            default_range="Last 7 Days",
            include_custom=True
        )
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["Visits", "Q&A", "Errors", "Poll Results"])
    
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

    with tab4:
        st.subheader("🗳️ User Feedback: Poll Insights")

        poll_results_df = load_poll_results(start_date=start_date)

        if not poll_results_df.empty:
            # Clean feature names for all subsequent uses in this tab
            poll_results_df['feature_name'] = poll_results_df['feature_name'].str.split(':').str[0].str.replace('\*\*', '', regex=True)

            st.markdown("#### Feature Popularity Dynamics")
            st.plotly_chart(
                plot_poll_results_over_time(poll_results_df.copy(), 'Feature Popularity Over Time'), # Pass a copy to avoid modifying df used later
                use_container_width=True
            )
            
            # --- Enhanced Vote Summary Section ---
            st.markdown("---") # Visual separator
            st.markdown("#### Overall Vote Summary")
            
            # Aggregate total votes per feature for the selected period
            poll_summary = poll_results_df.groupby('feature_name')['vote_count'].sum().reset_index()
            poll_summary = poll_summary.sort_values(by='vote_count', ascending=False)
            
            # Display as a bar chart
            summary_fig = go.Figure(go.Bar(
                x=poll_summary['feature_name'],
                y=poll_summary['vote_count'],
                marker_color='rgb(26, 118, 255)',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Inter, sans-serif"
                )
            ))
            summary_fig = apply_chart_theme(
                summary_fig,
                height=350,
                title="Total Votes per Feature",
                xaxis_title="Feature",
                yaxis_title="Total Votes"
            )
            summary_fig.update_layout(
                showlegend=False,
                xaxis_tickangle=-45
            )
            st.plotly_chart(summary_fig, use_container_width=True)

            # Display raw summary data in an expander
            with st.expander("🔍 View Detailed Vote Counts", expanded=False):
                st.dataframe(
                    poll_summary.rename(columns={'feature_name': 'Feature', 'vote_count': 'Total Votes'}),
                    use_container_width=True,
                    hide_index=True
                )
            # --- End of Enhanced Vote Summary Section ---

        else:
            st.info("📊 No poll data available for the selected time range. Cast some votes to see results here!", icon="ℹ️")

if __name__ == "__main__":
    main() 