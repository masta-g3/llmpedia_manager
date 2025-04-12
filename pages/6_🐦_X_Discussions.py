import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from utils import init_auth_sidebar
from theme import apply_theme
from plots import create_time_series, create_bar_chart, apply_chart_theme
from db import (
    load_tweet_analysis,
    get_tweet_stats,
    get_daily_tweet_stats,
    get_top_authors
)

# Set page config
st.set_page_config(layout="wide", page_title="Social Media Discussions")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access social media analytics")
    st.stop()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_data(start_date=None):
    """Load and cache all required data."""
    return {
        'stats': get_tweet_stats(start_date=start_date),
        'daily_stats': get_daily_tweet_stats(start_date=start_date),
        'top_authors': get_top_authors(limit=10, start_date=start_date),
        'analysis': load_tweet_analysis(start_date=start_date)
    }

def format_number(num: float) -> str:
    """Format large numbers with K/M suffix."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:.0f}"

def plot_daily_metrics(df: pd.DataFrame) -> go.Figure:
    """Create a multi-line chart for daily metrics."""
    # Define metrics and their display labels
    metrics = {
        'tweet_count': 'Posts',
        'unique_authors': 'Unique Authors',
        'total_likes': 'Likes',
        'total_reposts': 'Reposts'
    }
    
    colors = ['rgba(55, 83, 109, 0.7)', 'rgba(26, 118, 255, 0.7)', 
              'rgba(78, 121, 167, 0.7)', 'rgba(242, 142, 43, 0.7)']
    
    # Use create_time_series from plots.py with customization
    return create_time_series(
        df=df,
        x_col='date',
        y_cols=list(metrics.keys()),
        labels=metrics,
        height=400,
        xaxis_title="Date",
        yaxis_title="Count",
        use_markers=False
    )

def plot_engagement_distribution(df: pd.DataFrame, metric: str) -> go.Figure:
    """Create a horizontal bar chart of top authors by selected metric."""
    metric_configs = {
        'engagement': {
            'value': (df['total_likes'] * 1 + df['total_reposts'] * 2 + df['total_replies'] * 3) / df['tweet_count'],
            'title': 'Engagement Score',
            'format': '.1f'
        },
        'tweets': {
            'value': df['tweet_count'],
            'title': 'Total Posts',
            'format': ',d'
        },
        'likes': {
            'value': df['total_likes'],
            'title': 'Total Likes',
            'format': ',d'
        },
        'reposts': {
            'value': df['total_reposts'],
            'title': 'Total Reposts',
            'format': ',d'
        },
        'replies': {
            'value': df['total_replies'],
            'title': 'Total Replies',
            'format': ',d'
        },
        'views': {
            'value': df['total_views'],
            'title': 'Total Views',
            'format': ',d'
        }
    }
    
    # Calculate the selected metric
    df = df.copy()
    df['metric_value'] = metric_configs[metric]['value']
    
    # Sort by the selected metric
    df = df.sort_values('metric_value', ascending=True).tail(10)
    
    # Add verification badges to author names
    df['display_name'] = df.apply(
        lambda x: f"{'✓ ' if x['is_verified'] else ''}{x['author']}", 
        axis=1
    )
    
    # Custom hover template
    hover_template = (
        'Author: %{y}<br>' +
        f'{metric_configs[metric]["title"]}: %{{x:{metric_configs[metric]["format"]}}}<br>' +
        'Posts: %{customdata[0]:,d}<br>' +
        'Likes: %{customdata[1]:,d}<br>' +
        'Reposts: %{customdata[2]:,d}<br>' +
        'Replies: %{customdata[3]:,d}<br>' +
        'Views: %{customdata[4]:,d}<extra></extra>'
    )
    
    # Use horizontal bar chart with customizations
    return create_bar_chart(
        df=df,
        x_col='metric_value',
        y_col='display_name',
        color='rgba(55, 83, 109, 0.7)',
        height=400,
        xaxis_title=metric_configs[metric]['title'],
        yaxis_title="Author",
        horizontal=True,
        hover_template=hover_template,
        custom_data=['tweet_count', 'total_likes', 'total_reposts', 'total_replies', 'total_views']
    )

def main():
    st.title("🐦 Social Media Discussions")
    
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
    
    # Load cached data
    data = load_cached_data(start_date=start_date)
    stats_df = data['stats']
    daily_stats = data['daily_stats']
    top_authors = data['top_authors']
    analysis_results = data['analysis']
    
    # High-level metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">Total Posts</div>
                <div class="metric-value">{:,}</div>
            </div>
        '''.format(int(stats_df['total_tweets'].iloc[0])), unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">Unique Authors</div>
                <div class="metric-value">{:,}</div>
            </div>
        '''.format(int(stats_df['unique_authors'].iloc[0])), unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">Avg. Likes per Post</div>
                <div class="metric-value">{:,.1f}</div>
            </div>
        '''.format(stats_df['avg_likes'].iloc[0]), unsafe_allow_html=True)
    
    with col4:
        st.markdown('''
            <div class="metric-card">
                <div class="metric-label">Verified Authors</div>
                <div class="metric-value">{:,}</div>
            </div>
        '''.format(int(stats_df['verified_authors'].iloc[0])), unsafe_allow_html=True)
    
    # Engagement trends
    st.markdown("### Engagement Trends")
    st.plotly_chart(plot_daily_metrics(daily_stats), use_container_width=True)
    
    # Top authors and latest analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top Authors by Metric")
        metric_options = {
            'engagement': '🎯 Engagement Score',
            'tweets': '📝 Post Count',
            'likes': '❤️ Likes',
            'reposts': '🔄 Reposts',
            'replies': '💬 Replies',
            'views': '👁️ Views'
        }
        selected_metric = st.selectbox(
            "Select Metric",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            key="top_authors_metric"
        )
        st.plotly_chart(plot_engagement_distribution(top_authors, selected_metric), use_container_width=True)
    
    with col2:
        st.markdown("### Latest Post Analysis")
        if not analysis_results.empty:
            latest_analysis = analysis_results.iloc[0]
            st.markdown(f"""
**Analysis Period:** {latest_analysis['start_date'].strftime('%Y-%m-%d')} to {latest_analysis['end_date'].strftime('%Y-%m-%d')}  
**Unique Posts:** {latest_analysis['unique_tweets']:,}

#### Key Insights:
{latest_analysis['response']}

#### Analysis Process:
{latest_analysis['thinking_process']}
""")
        else:
            st.info("No post analysis results available for the selected time period.")
    
    # Detailed tables
    tab1, tab2 = st.tabs(["Top Authors Details", "Analysis History"])
    
    with tab1:
        st.dataframe(
            top_authors.style
            .format({
                'tweet_count': '{:,}'.format,
                'total_replies': '{:,}'.format,
                'total_reposts': '{:,}'.format,
                'total_likes': '{:,}'.format,
                'total_views': '{:,}'.format
            })
        )
    
    with tab2:
        if not analysis_results.empty:
            for _, analysis in analysis_results.iterrows():
                with st.expander(f"Analysis from {analysis['start_date'].strftime('%Y-%m-%d')} to {analysis['end_date'].strftime('%Y-%m-%d')}"):
                    st.markdown(f"""
**Unique Posts:** {analysis['unique_tweets']:,}

#### Key Insights:
{analysis['response']}

#### Analysis Process:
{analysis['thinking_process']}
""")
        else:
            st.info("No analysis history available for the selected time period.")

if __name__ == "__main__":
    main() 