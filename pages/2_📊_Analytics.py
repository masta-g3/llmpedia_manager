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

def plot_tweet_level_chart(df, metrics):
    """Create a tweet-level visualization showing metrics per tweet."""
    # Create a copy to avoid modifying original dataframe
    plot_df = df.copy()
    
    # Define truncate_text function first
    def truncate_text(text, length=100):
        return text if len(text) <= length else text[:length] + "..."
    
    # Aggregate thread metrics
    thread_metrics = (plot_df[plot_df['thread_id'].notna()]
                     .groupby('thread_id')[metrics]
                     .sum()
                     .reset_index())
    
    # Get the first tweet of each thread
    thread_first_tweets = (plot_df[plot_df['thread_id'].notna()]
                          .sort_values('Date')
                          .groupby('thread_id')
                          .first()
                          .reset_index())
    
    # Merge aggregated metrics with first tweets
    thread_tweets = thread_first_tweets.merge(
        thread_metrics,
        on='thread_id',
        suffixes=('', '_sum')
    )
    
    # For metrics columns, use the summed values
    for metric in metrics:
        thread_tweets[metric] = thread_tweets[f'{metric}_sum']
        thread_tweets = thread_tweets.drop(f'{metric}_sum', axis=1)
    
    # Combine non-thread tweets with aggregated thread tweets
    plot_df = pd.concat([
        plot_df[plot_df['thread_id'].isna()],  # Non-thread tweets
        thread_tweets  # Aggregated thread tweets
    ]).sort_values('Date')
    
    # Prepare hover text - ensure we get the first tweet's text for threads
    plot_df['hover_text'] = plot_df.apply(
        lambda x: (
            x['tweet_insight'] if pd.notna(x.get('tweet_insight')) 
            else (x['Post text'] if pd.isna(x.get('thread_id')) 
                  else thread_first_tweets.loc[
                      thread_first_tweets['thread_id'] == x['thread_id'], 
                      'Post text'
                  ].iloc[0])
        ),
        axis=1
    )
    
    # Truncate the hover text
    plot_df['hover_text'] = plot_df['hover_text'].apply(truncate_text)
    
    fig = go.Figure()
    
    for metric in metrics:
        fig.add_trace(
            go.Bar(
                x=plot_df['Date'],
                y=plot_df[metric],
                name=metric,
                hovertemplate=(
                    f"<b>Tweet {metric}</b><br>" +
                    "Date: %{x|%Y-%m-%d}<br>" +
                    "Value: %{y:,}<br>" +
                    "Tweet: %{customdata[0]}<br>" +
                    "<extra></extra>"
                ),
                customdata=plot_df[['hover_text']].values,
                width=24*60*60*1000 * 0.8,  # 80% of a day in milliseconds
                opacity=0.8  # Added transparency
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
        xaxis=dict(
            title="Publication Date",
            type='date',
            tickformat='%Y-%m-%d'
        ),
        yaxis_title="Count",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color=st.get_option("theme.textColor")
        ),
        barmode='group',  # Options: 'group' (side by side) or 'stack' (stacked)
        bargap=0.15,      # Gap between bars in the same group
        bargroupgap=0.1   # Gap between bar groups
    )
    
    # Update grid color based on theme
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    
    return fig

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
    
    # Date range selector
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Quick date range buttons
        date_range = st.radio(
            "Quick ranges",
            ["Last week", "Last month", "Last 3 months", "Last 6 months", "All time"],
            horizontal=True,
            index=2  # Set default to "Last 3 months" (index 2 in the list)
        )
    
    # Calculate default dates based on selection
    today = pd.Timestamp.now().date()
    if date_range == "Last week":
        default_start = (today - pd.Timedelta(days=7))
    elif date_range == "Last month":
        default_start = (today - pd.Timedelta(days=30))
    elif date_range == "Last 3 months":
        default_start = (today - pd.Timedelta(days=90))
    elif date_range == "Last 6 months":
        default_start = (today - pd.Timedelta(days=180))
    else:  # All time
        default_start = min_date
    
    with col2, col3:
        start_date, end_date = st.columns(2)
        with start_date:
            start_date = st.date_input("Start date", 
                                     value=max(min_date, default_start),
                                     min_value=min_date,
                                     max_value=max_date)
        with end_date:
            end_date = st.date_input("End date",
                                   value=max_date,
                                   min_value=min_date,
                                   max_value=max_date)
    
    # Filter dataframe based on date range
    mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    filtered_df = df[mask].copy()
    
    # Metrics selection
    col1, col2 = st.columns(2)
    with col1:
        view_type = st.radio(
            "Chart Type",
            ["Timeline View", "Tweet-level View"],
            horizontal=True,
            key="chart_view_type"
        )
    
    with col2:
        selected_metrics = st.multiselect(
            "Select metrics to display",
            ['Impressions', 'Likes', 'Engagements', 'Bookmarks', 
             'Share', 'Replies', 'Reposts', 'Profile visits'],
            default=['Impressions', 'Likes', 'Engagements']
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Time series chart in a card
    if selected_metrics:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if view_type == "Timeline View":
            st.plotly_chart(
                plot_time_series(filtered_df, selected_metrics),
                use_container_width=True,
                config={'displayModeBar': False}
            )
        else:  # Tweet-level View
            st.plotly_chart(
                plot_tweet_level_chart(filtered_df, selected_metrics),
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
    
    # Use filtered_df for the gallery display
    if view_mode == "Threads Only":
        thread_starts = filtered_df[filtered_df['is_thread_start']].copy()
        if sort_by == 'Date':
            thread_starts = thread_starts.sort_values('Date', ascending=ascending)
        else:
            numeric_metrics = ['Impressions', 'Likes', 'Engagements', 'Bookmarks', 
                             'Share', 'Replies', 'Reposts', 'Profile visits']
            thread_metrics = filtered_df[['thread_id'] + numeric_metrics].groupby('thread_id').sum().reset_index()
            thread_starts = thread_starts.merge(
                thread_metrics[['thread_id', sort_by]], 
                on='thread_id',
                suffixes=('', '_sum')
            )
            thread_starts = thread_starts.sort_values(sort_by + '_sum', ascending=ascending)
        
        for _, thread_start in thread_starts.iterrows():
            thread_tweets = filtered_df[filtered_df['thread_id'] == thread_start['thread_id']]
            display_thread(thread_tweets)
    else:
        df_sorted = filtered_df.sort_values(by=sort_by, ascending=ascending)
        for _, row in df_sorted.iterrows():
            display_tweet_card(row)

if __name__ == "__main__":
    main() 