import os
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Database connection parameters
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

# Create database URL
database_url = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

def get_db_connection():
    """Create and return a database connection"""
    return create_engine(database_url)

def load_visit_logs(start_date=None, end_date=None):
    """Load visit logs with optional date filtering"""
    query = "SELECT * FROM visit_logs"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY tstp DESC"
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def load_qna_logs(start_date=None, end_date=None):
    """Load Q&A logs with optional date filtering"""
    query = "SELECT * FROM qna_logs"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY tstp DESC"
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def load_error_logs(start_date=None, end_date=None):
    """Load error logs with optional date filtering"""
    query = "SELECT * FROM error_logs"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY tstp DESC"
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_top_entrypoints(limit=10, start_date=None, end_date=None):
    """Get the most common entrypoints"""
    query = """
    SELECT entrypoint, COUNT(*) as count
    FROM visit_logs
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY entrypoint
    ORDER BY count DESC
    LIMIT %d
    """ % limit
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_hourly_stats(table_name, start_date=None, end_date=None):
    """Get hourly statistics for any of the log tables"""
    query = f"""
    SELECT 
        EXTRACT(HOUR FROM tstp) as hour,
        COUNT(*) as count
    FROM {table_name}
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY EXTRACT(HOUR FROM tstp)
    ORDER BY hour
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_daily_stats(table_name, start_date=None, end_date=None):
    """Get daily statistics for any of the log tables"""
    query = f"""
    SELECT 
        DATE(tstp) as date,
        COUNT(*) as count
    FROM {table_name}
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY DATE(tstp)
    ORDER BY date
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def load_workflow_runs(start_date=None, end_date=None):
    """Load workflow runs with optional date filtering."""
    query = "SELECT * FROM workflow_runs"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY tstp DESC"
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def load_token_usage_logs(start_date=None, end_date=None):
    """Load token usage logs with optional date filtering."""
    query = "SELECT * FROM token_usage_logs"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY tstp DESC"
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_model_stats(start_date=None, end_date=None):
    """Get aggregated stats per model."""
    query = """
    SELECT 
        model_name,
        COUNT(*) as total_runs,
        SUM(prompt_tokens) as total_prompt_tokens,
        SUM(completion_tokens) as total_completion_tokens,
        SUM(prompt_cost) as total_prompt_cost,
        SUM(completion_cost) as total_completion_cost,
        SUM(prompt_cost + completion_cost) as total_cost
    FROM token_usage_logs
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY model_name
    ORDER BY total_cost DESC
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_process_stats(start_date=None, end_date=None):
    """Get aggregated stats per process."""
    query = """
    SELECT 
        process_id,
        COUNT(*) as total_runs,
        SUM(prompt_tokens) as total_prompt_tokens,
        SUM(completion_tokens) as total_completion_tokens,
        SUM(prompt_cost) as total_prompt_cost,
        SUM(completion_cost) as total_completion_cost,
        SUM(prompt_cost + completion_cost) as total_cost
    FROM token_usage_logs
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY process_id
    ORDER BY total_cost DESC
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_daily_cost_stats(start_date=None, end_date=None):
    """Get daily cost statistics."""
    query = """
    SELECT 
        DATE(tstp) as date,
        SUM(prompt_cost) as prompt_cost,
        SUM(completion_cost) as completion_cost,
        SUM(prompt_cost + completion_cost) as total_cost,
        COUNT(*) as total_runs
    FROM token_usage_logs
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY DATE(tstp)
    ORDER BY date
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def load_tweet_analysis(start_date=None, end_date=None) -> pd.DataFrame:
    """Load tweet analysis results with optional date filtering."""
    query = "SELECT * FROM tweet_analysis"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY tstp DESC"
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_tweet_stats(start_date=None, end_date=None) -> pd.DataFrame:
    """Get high-level tweet statistics."""
    query = """
    SELECT 
        COUNT(*) as total_tweets,
        COUNT(DISTINCT author) as unique_authors,
        SUM(CASE WHEN has_media THEN 1 ELSE 0 END) as tweets_with_media,
        SUM(CASE WHEN is_verified THEN 1 ELSE 0 END) as verified_authors,
        AVG(reply_count) as avg_replies,
        AVG(repost_count) as avg_reposts,
        AVG(like_count) as avg_likes,
        AVG(view_count) as avg_views,
        AVG(bookmark_count) as avg_bookmarks
    FROM llm_tweets
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tweet_timestamp >= '{start_date}'")
    if end_date:
        conditions.append(f"tweet_timestamp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_daily_tweet_stats(start_date=None, end_date=None) -> pd.DataFrame:
    """Get daily tweet statistics."""
    query = """
    SELECT 
        DATE(tweet_timestamp) as date,
        COUNT(*) as tweet_count,
        COUNT(DISTINCT author) as unique_authors,
        SUM(reply_count) as total_replies,
        SUM(repost_count) as total_reposts,
        SUM(like_count) as total_likes,
        SUM(view_count) as total_views
    FROM llm_tweets
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tweet_timestamp >= '{start_date}'")
    if end_date:
        conditions.append(f"tweet_timestamp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY DATE(tweet_timestamp)
    ORDER BY date
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_top_authors(limit: int = 10, start_date=None, end_date=None) -> pd.DataFrame:
    """Get most active authors based on engagement metrics."""
    query = """
    SELECT 
        author,
        username,
        COUNT(*) as tweet_count,
        SUM(reply_count) as total_replies,
        SUM(repost_count) as total_reposts,
        SUM(like_count) as total_likes,
        SUM(view_count) as total_views,
        BOOL_OR(is_verified) as is_verified
    FROM llm_tweets
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tweet_timestamp >= '{start_date}'")
    if end_date:
        conditions.append(f"tweet_timestamp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY author, username
    ORDER BY total_likes DESC
    LIMIT %d
    """ % limit
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def get_pending_tweet_replies(limit=10):
    """Load pending tweet replies for approval."""
    query = f"""
    SELECT 
        id, 
        tstp, 
        selected_tweet, 
        response, 
        meta_data,
        approval_status
    FROM tweet_replies
    WHERE approval_status = 'pending'
    ORDER BY tstp DESC
    LIMIT {limit}
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

def update_tweet_reply_status(tweet_id, status):
    """Update the status of a tweet reply."""
    if status not in ['approved', 'rejected']:
        return False
    
    try:
        conn = get_db_connection()
        with conn.connect() as connection:
            result = connection.execute(
                f"""
                UPDATE tweet_replies
                SET approval_status = '{status}', 
                    updated_at = NOW()
                WHERE id = {tweet_id}
                """
            )
            return True
    except Exception as e:
        print(f"Error updating tweet reply status: {e}")
        return False 