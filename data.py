import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime
from thefuzz import fuzz
import re

@st.cache_data(ttl=3600)

def get_database_url():
    """Get database URL from environment variables or streamlit secrets."""
    try:
        db_params = {
            "dbname": os.environ["DB_NAME"],
            "user": os.environ["DB_USER"],
            "password": os.environ["DB_PASS"],
            "host": os.environ["DB_HOST"],
            "port": os.environ["DB_PORT"],
        }
    except:
        db_params = {**st.secrets["postgres"]}
    
    return f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

def clean_text_for_matching(text):
    """Clean text to improve matching accuracy."""
    # Remove line breaks and extra spaces
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove t.co URLs and any trailing text after them
    text = re.sub(r'https://t\.co/\w+.*$', '', text)
    # Remove other URLs
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

def find_best_match(analytics_text, insights_df):
    """Find exact match up to truncation point."""
    analytics_text = clean_text_for_matching(analytics_text)
    matches = []
    
    for _, row in insights_df.iterrows():
        insight_text = clean_text_for_matching(row['tweet_insight'])
        # Check if analytics text (which might be truncated) matches the start of the insight text
        if insight_text.startswith(analytics_text):
            matches.append(row)
    
    return matches[0] if matches else None

@st.cache_data(ttl=3600)

def load_tweet_insights(arxiv_code: str = None, drop_rejected: bool = False):
    """Load tweet insights from database."""
    query = "SELECT * FROM tweet_reviews"
    if arxiv_code:
        query += f" AND arxiv_code = '{arxiv_code}';"
    query += " ORDER BY tstp DESC;"
    
    conn = create_engine(get_database_url())
    tweet_reviews_df = pd.read_sql(query, conn)
    
    if drop_rejected:
        tweet_reviews_df = tweet_reviews_df[tweet_reviews_df["rejected"] == False]
    
    tweet_reviews_df.sort_values(by="tstp", ascending=False, inplace=True)
    tweet_reviews_df.drop(columns=["tstp", "rejected"], inplace=True)
    tweet_reviews_df.rename(columns={"review": "tweet_insight"}, inplace=True)
    
    return tweet_reviews_df

@st.cache_data(ttl=3600)

def load_tweet_analytics():
    """Load and combine tweet analytics with insights."""
    # Load analytics data
    analytics_df = pd.read_csv('data/account_analytics_content.csv')
    analytics_df['Date'] = pd.to_datetime(analytics_df['Date'])
    
    # Now load insights for additional metadata
    insights_df = load_tweet_insights(drop_rejected=True)
    
    # Initialize metadata columns
    analytics_df['tweet_insight'] = None
    analytics_df['arxiv_code'] = None
    analytics_df['tweet_type'] = None
    
    # Match thread start tweets with insights
    # Thread starts are tweets that contain "Insight from"
    thread_starts = analytics_df[
        analytics_df['Post text'].str.contains(
            r'Insight from .+?\([A-Za-z]+ \d{1,2}, \d{4}\)',
            regex=True,
            na=False
        )
    ].copy()
    
    for idx, row in thread_starts.iterrows():
        best_match = find_best_match(row['Post text'], insights_df)
        if best_match is not None:
            analytics_df.loc[idx, 'tweet_insight'] = best_match['tweet_insight']
            analytics_df.loc[idx, 'arxiv_code'] = best_match['arxiv_code']
            analytics_df.loc[idx, 'tweet_type'] = best_match['tweet_type']
    
    return analytics_df

def get_thread_metrics(df, thread_id):
    """Calculate aggregated metrics for a thread."""
    thread_df = df[df['thread_id'] == thread_id]
    metrics = {
        'Impressions': thread_df['Impressions'].sum(),
        'Likes': thread_df['Likes'].sum(),
        'Reposts': thread_df['Reposts'].sum(),
        'Replies': thread_df['Replies'].sum(),
        'Engagements': thread_df['Engagements'].sum(),
        'Bookmarks': thread_df['Bookmarks'].sum(),
        'Profile visits': thread_df['Profile visits'].sum(),
    }
    return metrics 