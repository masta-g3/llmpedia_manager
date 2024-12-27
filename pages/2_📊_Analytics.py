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

def display_thread(thread_df):
    """Display a thread of tweets with proper formatting."""
    if thread_df.empty:
        return
        
    with st.container():
        st.markdown("""
            <style>
            .metadata-container {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin: 8px 0;
            }
            .metadata-tag {
                background-color: rgba(128, 128, 128, 0.1);
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.85em;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            .thread-indicator {
                color: #FF9900;
                font-weight: 500;
            }
            .tweet-type-tag {
                color: #1DA1F2;
            }
            .arxiv-tag {
                color: #B31B1B;
            }
            .tweet-text {
                margin: 12px 0;
                line-height: 1.5;
            }
            .date-header {
                margin: 0;
                padding: 0;
                font-size: 1em;
                color: #666;
            }
            .metrics-container {
                display: flex;
                gap: 1rem;
                margin-top: 0.5rem;
            }
            .metric-box {
                background-color: rgba(128, 128, 128, 0.05);
                padding: 8px;
                border-radius: 4px;
                text-align: center;
                flex: 1;
            }
            .date-display {
                color: #888;
                font-size: 0.85em;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
                font-weight: 500;
            }
            .paper-preview {
                display: flex;
                gap: 16px;
                margin: 16px 0;
                background: rgba(128, 128, 128, 0.05);
                padding: 12px;
                border-radius: 8px;
            }
            .paper-preview img {
                border-radius: 4px;
                max-height: 120px;
                object-fit: contain;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Start the tweet card
        st.markdown('<div class="tweet-card">', unsafe_allow_html=True)
        
        # Create two columns for the layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            main_tweet = thread_df.iloc[0]
            
            # Date display with new style
            st.markdown(
                f'<div class="date-display">{main_tweet["Date"].strftime("%B %d, %Y")}</div>',
                unsafe_allow_html=True
            )
            
            # Metadata container with 3 columns
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            
            with meta_col1:
                st.markdown('<span class="metadata-tag thread-indicator">🧵 Thread</span>', unsafe_allow_html=True)
            
            with meta_col2:
                if pd.notna(main_tweet["tweet_type"]):
                    st.markdown(f'<span class="metadata-tag tweet-type-tag">📝 {main_tweet["tweet_type"]}</span>', unsafe_allow_html=True)
            
            with meta_col3:
                if pd.notna(main_tweet["arxiv_code"]):
                    st.markdown(f'<span class="metadata-tag arxiv-tag">📄 {main_tweet["arxiv_code"]}</span>', unsafe_allow_html=True)
            
            # Paper preview if arxiv code exists
            if pd.notna(main_tweet["arxiv_code"]):
                st.markdown('<div class="paper-preview">', unsafe_allow_html=True)
                preview_col1, preview_col2 = st.columns(2)
                with preview_col1:
                    st.image(
                        f"https://arxiv-art.s3.us-west-2.amazonaws.com/{main_tweet['arxiv_code']}.png",
                        use_column_width=True,
                        caption="Paper visualization"
                    )
                with preview_col2:
                    st.image(
                        f"https://arxiv-art.s3.us-west-2.amazonaws.com/arxiv-first-page/{main_tweet['arxiv_code']}.png",
                        use_column_width=True,
                        caption="Paper first page"
                    )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Tweet text
            main_tweet_text = main_tweet['tweet_insight'] if pd.notna(main_tweet['tweet_insight']) else main_tweet['Post text']
            st.markdown(f'<div class="tweet-text">{main_tweet_text}</div>', unsafe_allow_html=True)
            
            # Display thread replies
            for _, tweet in thread_df.iloc[1:].iterrows():
                text = tweet['tweet_insight'] if pd.notna(tweet['tweet_insight']) else tweet['Post text']
                st.markdown(f'<div class="thread-item"><div class="tweet-text">{text}</div></div>', unsafe_allow_html=True)
        
        with col2:
            # Display metrics
            metrics = get_thread_metrics(thread_df, thread_df.iloc[0].name)
            st.markdown("""
                <div style="background-color: rgba(128, 128, 128, 0.05); padding: 12px; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; font-size: 0.9em; color: #666;">Engagement Metrics</h5>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="metrics-container" style="flex-direction: column;">
                    <div class="metric-box">
                        <strong>👁️ Impressions</strong><br>{metrics['Impressions']:,}
                    </div>
                    <div class="metric-box">
                        <strong>❤️ Likes</strong><br>{metrics['Likes']:,}
                    </div>
                    <div class="metric-box">
                        <strong>🔄 Reposts</strong><br>{metrics['Reposts']:,}
                    </div>
                    <div class="metric-box">
                        <strong>💬 Replies</strong><br>{metrics['Replies']:,}
                    </div>
                </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

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
        # Group by thread and calculate thread start date
        thread_starts = df[df['is_thread_start']].copy()
        if sort_by == 'Date':
            thread_starts = thread_starts.sort_values('Date', ascending=ascending)
        else:
            # For other metrics, we need to sum up the thread totals
            numeric_metrics = ['Impressions', 'Likes', 'Engagements', 'Bookmarks', 
                             'Share', 'Replies', 'Reposts', 'Profile visits']
            thread_metrics = df[['thread_id'] + numeric_metrics].groupby('thread_id').sum().reset_index()
            # Merge while keeping all original columns from thread_starts
            thread_starts = thread_starts.merge(
                thread_metrics[['thread_id', sort_by]], 
                on='thread_id',
                suffixes=('', '_sum')  # Changed suffixes to avoid _y suffix
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
            with st.container():
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Date with new style
                    st.markdown(
                        f'<div class="date-display">{row["Date"].strftime("%B %d, %Y")}</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Metadata container with 3 columns
                    meta_col1, meta_col2, meta_col3 = st.columns(3)
                    
                    with meta_col1:
                        if row['is_thread_start']:
                            st.markdown('<span class="metadata-tag thread-indicator">🧵 Thread</span>', unsafe_allow_html=True)
                    
                    with meta_col2:
                        if pd.notna(row["tweet_type"]):
                            st.markdown(f'<span class="metadata-tag tweet-type-tag">📝 {row["tweet_type"]}</span>', unsafe_allow_html=True)
                    
                    with meta_col3:
                        if pd.notna(row["arxiv_code"]):
                            st.markdown(f'<span class="metadata-tag arxiv-tag">📄 {row["arxiv_code"]}</span>', unsafe_allow_html=True)
                    
                    # Paper preview if arxiv code exists
                    if pd.notna(row["arxiv_code"]):
                        st.markdown('<div class="paper-preview">', unsafe_allow_html=True)
                        preview_col1, preview_col2 = st.columns(2)
                        with preview_col1:
                            st.image(
                                f"https://arxiv-art.s3.us-west-2.amazonaws.com/{row['arxiv_code']}.png",
                                use_column_width=True,
                                caption="Paper visualization"
                            )
                        with preview_col2:
                            st.image(
                                f"https://arxiv-first-page.s3.us-east-1.amazonaws.com/{row['arxiv_code']}.png",
                                use_column_width=True,
                                caption="Paper first page"
                            )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Tweet text
                    text = row['tweet_insight'] if pd.notna(row['tweet_insight']) else row['Post text']
                    st.markdown(f'<div class="tweet-text">{text}</div>', unsafe_allow_html=True)
                
                with col2:
                    # Metrics in a container
                    st.markdown("""
                        <div style="background-color: rgba(128, 128, 128, 0.05); padding: 12px; border-radius: 8px;">
                            <h5 style="margin: 0 0 8px 0; font-size: 0.9em; color: #666;">Engagement Metrics</h5>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class="metrics-container" style="flex-direction: column;">
                            <div class="metric-box">
                                <strong>👁️ Impressions</strong><br>{row['Impressions']:,}
                            </div>
                            <div class="metric-box">
                                <strong>❤️ Likes</strong><br>{row['Likes']:,}
                            </div>
                            <div class="metric-box">
                                <strong>🔄 Reposts</strong><br>{row['Reposts']:,}
                            </div>
                            <div class="metric-box">
                                <strong>💬 Replies</strong><br>{row['Replies']:,}
                            </div>
                        </div>
                        </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 