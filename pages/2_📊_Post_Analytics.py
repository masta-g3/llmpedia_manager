import streamlit as st
import pandas as pd
from datetime import datetime
from utils import init_auth_sidebar, init_cache_controls, init_date_range_selector
from theme import apply_theme
from data import load_tweet_analytics, get_thread_metrics
from plots import create_time_series, create_bar_chart, apply_chart_theme
import plotly.graph_objects as go  # Still needed for the tweet-level chart

# Set page config
st.set_page_config(layout="wide", page_title="Post Analytics")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access analytics")
    st.stop()

# Cache refresh controls
init_cache_controls()

## Initialize session state for pagination if it doesn't exist
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

def plot_time_series(df, metrics):
    # Use the centralized time series function
    return create_time_series(
        df=df,
        x_col='Date',
        y_cols=metrics,
        height=500,
        xaxis_title="Date",
        yaxis_title="Count"
    )

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
        <div class="metrics-container">
            <div class="metrics-header">Engagement Metrics</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
            <div class="metric-box">
                <span class="metric-label">Impressions</span>
                <span class="metric-value">{metrics_data['Impressions']:,}</span>
            </div>
            <div class="metric-box">
                <span class="metric-label">Likes</span>
                <span class="metric-value">{metrics_data['Likes']:,}</span>
            </div>
            <div class="metric-box">
                <span class="metric-label">Reposts</span>
                <span class="metric-value">{metrics_data['Reposts']:,}</span>
            </div>
            <div class="metric-box">
                <span class="metric-label">Replies</span>
                <span class="metric-value">{metrics_data['Replies']:,}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_tweet_card(row, is_thread=False):
    """Display a single tweet card with all components."""
    with st.container():
        st.markdown('<div class="tweet-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add spacing after each card
        st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

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
    
    # Apply the chart theme
    fig = apply_chart_theme(
        fig, 
        height=500,
        xaxis_title="Publication Date",
        yaxis_title="Count"
    )
    
    # Additional customizations specific to this chart
    fig.update_layout(
        xaxis=dict(
            type='date',
            tickformat='%Y-%m-%d'
        ),
        barmode='group',  # Options: 'group' (side by side) or 'stack' (stacked)
        bargap=0.15,      # Gap between bars in the same group
        bargroupgap=0.1   # Gap between bar groups
    )
    
    return fig

def display_pagination_controls(total_items, items_per_page, current_page):
    """Display pagination controls and handle page navigation."""
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    
    # Reset current page if it's out of range
    if current_page > total_pages:
        st.session_state.current_page = 1
        current_page = 1
    
    # Calculate start and end indices for the current page
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="pagination-container">', unsafe_allow_html=True)
        
        # Create a flexible layout for pagination
        if total_pages <= 7:  # Show all pages if 7 or fewer
            page_buttons = list(range(1, total_pages + 1))
        else:
            # Always show first, last, current and some neighbors
            if current_page <= 3:
                # Near the beginning
                page_buttons = list(range(1, 6)) + ["…", total_pages]
            elif current_page >= total_pages - 2:
                # Near the end
                page_buttons = [1, "…"] + list(range(total_pages - 4, total_pages + 1))
            else:
                # Middle
                page_buttons = [1, "…"] + list(range(current_page - 1, current_page + 2)) + ["…", total_pages]
        
        # Previous button
        cols = st.columns([1] + [1] * len(page_buttons) + [1])
        
        with cols[0]:
            if current_page > 1:
                if st.button("⬅️", key="prev_page", help="Previous page"):
                    st.session_state.current_page = current_page - 1
                    st.experimental_rerun()
        
        # Page number buttons
        for i, page_num in enumerate(page_buttons, 1):
            with cols[i]:
                if page_num == "…":
                    st.markdown("<div style='text-align: center; padding: 0.25rem;'>…</div>", unsafe_allow_html=True)
                else:
                    button_style = "font-weight: bold;" if page_num == current_page else ""
                    if st.button(f"{page_num}", key=f"page_{page_num}", 
                               help=f"Go to page {page_num}",
                               disabled=page_num == current_page):
                        st.session_state.current_page = page_num
                        st.rerun()
        
        # Next button
        with cols[-1]:
            if current_page < total_pages:
                if st.button("➡️", key="next_page", help="Next page"):
                    st.session_state.current_page = current_page + 1
                    st.rerun()
        
        # Page info text
        st.markdown(f"<div style='text-align: center; margin-top: 0.5rem; font-size: 0.8rem;'>Showing {start_idx + 1}-{min(end_idx, total_items)} of {total_items} items</div>", 
                 unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return current_page, start_idx, end_idx

def main():
    
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📊 Post Analytics")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load data
    df = load_tweet_analytics()
    
    # Controls in a zen panel
    st.markdown('<div class="zen-panel">', unsafe_allow_html=True)
    
    # Date filtering mode selector
    filter_mode = st.radio(
        "Date Filter Style",
        ["Standard Ranges", "Custom Interface"],
        horizontal=True,
        help="Choose between standard range selector or custom date interface"
    )
    
    if filter_mode == "Standard Ranges":
        # Use the standard component
        start_date, end_date = init_date_range_selector(
            key_prefix="posts",
            default_range="Last 30 Days",
            include_custom=True
        )
        
        # Convert to date objects for filtering
        if start_date:
            start_date_filter = start_date.date()
        else:
            start_date_filter = df['Date'].min().date()
            
        if end_date:
            end_date_filter = end_date.date()
        else:
            end_date_filter = df['Date'].max().date()
    
    else:
        # Original custom interface
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
            start_date_col, end_date_col = st.columns(2)
            with start_date_col:
                start_date_filter = st.date_input("Start date", 
                                         value=max(min_date, default_start),
                                         min_value=min_date,
                                         max_value=max_date)
            with end_date_col:
                end_date_filter = st.date_input("End date",
                                       value=max_date,
                                       min_value=min_date,
                                       max_value=max_date)
    
    # Filter dataframe based on date range
    mask = (df['Date'].dt.date >= start_date_filter) & (df['Date'].dt.date <= end_date_filter)
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
    
    # Time series chart in a zen panel
    if selected_metrics:
        st.markdown('<div class="zen-panel">', unsafe_allow_html=True)
        
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
    
    # Gallery controls in a zen panel
    st.markdown('<div class="zen-panel">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 1])
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
    with col4:
        posts_per_page = st.selectbox(
            "Posts per page",
            [5, 10, 15, 20],
            index=1  # Default to 10 posts per page
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Use filtered_df for the gallery display with pagination
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
        
        # Pagination for threads
        total_threads = len(thread_starts)
        current_page = st.session_state.current_page
        current_page, start_idx, end_idx = display_pagination_controls(total_threads, posts_per_page, current_page)
        
        # Display only threads for the current page
        page_thread_starts = thread_starts.iloc[start_idx:end_idx]
        
        for _, thread_start in page_thread_starts.iterrows():
            thread_tweets = filtered_df[filtered_df['thread_id'] == thread_start['thread_id']]
            display_thread(thread_tweets)
            
    else:
        df_sorted = filtered_df.sort_values(by=sort_by, ascending=ascending)
        
        # Pagination for all tweets
        total_tweets = len(df_sorted)
        current_page = st.session_state.current_page
        current_page, start_idx, end_idx = display_pagination_controls(total_tweets, posts_per_page, current_page)
        
        # Display only tweets for the current page
        page_tweets = df_sorted.iloc[start_idx:end_idx]
        
        for _, row in page_tweets.iterrows():
            display_tweet_card(row)

if __name__ == "__main__":
    main() 