import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import init_auth_sidebar
from theme import apply_theme
from data import load_tweet_analytics, get_thread_metrics

# Set page config
st.set_page_config(layout="wide", page_title="Analytics Dashboard")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access analytics")
    st.stop()

def plot_time_series(df, metrics):
    fig = go.Figure()
    
    for metric in metrics:
        daily_data = df.groupby('Date')[metric].sum().reset_index()
        fig.add_trace(
            go.Scatter(
                x=daily_data['Date'],
                y=daily_data[metric],
                name=metric,
                mode='lines+markers'
            )
        )
    
    fig.update_layout(
        template='plotly_white',
        height=500,
        margin=dict(t=30, b=0, l=0, r=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_title="Date",
        yaxis_title="Count",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color=st.get_option("theme.textColor")
        )
    )
    
    # Update grid color based on theme
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    
    return fig

def escape_html(text):
    """Escape HTML special characters and wrap in a span to prevent code block rendering."""
    if pd.isna(text):
        return ""
    # Wrap the text in a span to prevent code block rendering of special characters
    return f'<span>{text}</span>'

def display_date(date):
    """Display formatted date."""
    return st.markdown(
        f'<div class="date-display">{date.strftime("%B %d, %Y")}</div>',
        unsafe_allow_html=True
    )

def display_metadata_tags(row):
    """Display metadata tags in columns."""
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    
    with meta_col1:
        if row.get('is_thread_start', False):
            st.markdown('<span class="metadata-tag thread-indicator">🧵 Thread</span>', unsafe_allow_html=True)
    
    with meta_col2:
        if pd.notna(row.get("tweet_type")):
            st.markdown(f'<span class="metadata-tag tweet-type-tag">📝 {row["tweet_type"]}</span>', unsafe_allow_html=True)
    
    with meta_col3:
        if pd.notna(row.get("arxiv_code")):
            st.markdown(f'<span class="metadata-tag arxiv-tag">📄 {row["arxiv_code"]}</span>', unsafe_allow_html=True)

def display_paper_preview(arxiv_code):
    """Display paper preview if arxiv code exists."""
    if pd.notna(arxiv_code):
        st.markdown('<div class="paper-preview">', unsafe_allow_html=True)
        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.markdown(
                f'<img src="https://arxiv-art.s3.us-west-2.amazonaws.com/{arxiv_code}.png" '
                'style="width: 300px; height: 300px; object-fit: contain;" '
                'alt="Paper visualization">',
                unsafe_allow_html=True
            )
        with preview_col2:
            st.markdown(
                f'<img src="https://arxiv-first-page.s3.us-east-1.amazonaws.com/{arxiv_code}.png" '
                'style="width: 300px; height: 300px; object-fit: contain;" '
                'alt="Paper first page">',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

def display_tweet_text(row):
    """Display tweet text content."""
    text = row['tweet_insight'] if pd.notna(row.get('tweet_insight')) else row['Post text']
    st.markdown(f'<div class="tweet-text">{text}</div>', unsafe_allow_html=True)

def display_metrics(metrics_data, is_thread=False):
    """Display engagement metrics in a formatted container."""
    st.markdown("""
        <div style="background-color: rgba(128, 128, 128, 0.05); padding: 12px; border-radius: 8px;">
            <h5 style="margin: 0 0 8px 0; font-size: 0.9em; color: #666;">Engagement Metrics</h5>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="metrics-container" style="flex-direction: column;">
            <div class="metric-box">
                <strong>👁️ Impressions</strong><br>{metrics_data['Impressions']:,}
            </div>
            <div class="metric-box">
                <strong>❤️ Likes</strong><br>{metrics_data['Likes']:,}
            </div>
            <div class="metric-box">
                <strong>🔄 Reposts</strong><br>{metrics_data['Reposts']:,}
            </div>
            <div class="metric-box">
                <strong>💬 Replies</strong><br>{metrics_data['Replies']:,}
            </div>
        </div>
        </div>
    """, unsafe_allow_html=True)

def display_tweet_card(row, is_thread=False):
    """Display a single tweet card with all components."""
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            display_date(row['Date'])
            display_metadata_tags(row)
            display_paper_preview(row.get('arxiv_code'))
            display_tweet_text(row)
            
            # Display thread replies if this is a thread
            if is_thread and 'thread_replies' in row:
                for reply in row['thread_replies']:
                    display_tweet_text(reply)
        
        with col2:
            metrics_data = get_thread_metrics(row['thread_df'], row.name) if is_thread else row
            display_metrics(metrics_data, is_thread)

def display_thread(thread_df):
    """Display a thread of tweets with proper formatting."""
    if thread_df.empty:
        return
        
    main_tweet = thread_df.iloc[0]
    main_tweet['thread_df'] = thread_df
    main_tweet['thread_replies'] = thread_df.iloc[1:].to_dict('records')
    display_tweet_card(main_tweet, is_thread=True)

def main():
    st.markdown('''
        <style>
        .tweet-text {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            white-space: pre-wrap;
            word-wrap: break-word;
            padding: 0.5rem 0;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📊 Twitter Analytics Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load data
    df = load_tweet_analytics()
    
    # Controls in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        # Metrics selection
        selected_metrics = st.multiselect(
            "Select metrics to display",
            ['Impressions', 'Likes', 'Engagements', 'Bookmarks', 
             'Share', 'Replies', 'Reposts', 'Profile visits'],
            default=['Impressions', 'Likes', 'Engagements']
        )
    
    with col2:
        # Time aggregation
        time_agg = st.selectbox(
            "Time aggregation",
            ["Daily", "Weekly", "Monthly"]
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Time series chart in a card
    if selected_metrics:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(
            plot_time_series(df, selected_metrics),
            use_container_width=True,
            config={'displayModeBar': False}
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tweet Gallery
    st.header("Tweet Gallery")
    
    # Gallery controls in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ['Date', 'Impressions', 'Likes', 'Engagements']
        )
    with col2:
        view_mode = st.selectbox(
            "View mode",
            ["Threads Only", "All Tweets"]
        )
    with col3:
        ascending = st.checkbox("Ascending order", value=False)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter and sort data
    if view_mode == "Threads Only":
        thread_starts = df[df['is_thread_start']].copy()
        if sort_by == 'Date':
            thread_starts = thread_starts.sort_values('Date', ascending=ascending)
        else:
            numeric_metrics = ['Impressions', 'Likes', 'Engagements', 'Bookmarks', 
                             'Share', 'Replies', 'Reposts', 'Profile visits']
            thread_metrics = df[['thread_id'] + numeric_metrics].groupby('thread_id').sum().reset_index()
            thread_starts = thread_starts.merge(
                thread_metrics[['thread_id', sort_by]], 
                on='thread_id',
                suffixes=('', '_sum')
            )
            thread_starts = thread_starts.sort_values(sort_by + '_sum', ascending=ascending)
        
        # Display threads
        for _, thread_start in thread_starts.iterrows():
            thread_tweets = df[df['thread_id'] == thread_start['thread_id']]
            display_thread(thread_tweets)
    else:
        # Display individual tweets
        df_sorted = df.sort_values(by=sort_by, ascending=ascending)
        for _, row in df_sorted.iterrows():
            display_tweet_card(row)

if __name__ == "__main__":
    main() 