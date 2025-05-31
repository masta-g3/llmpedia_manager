import os
import pandas as pd
from sqlalchemy import create_engine, text
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

@st.cache_resource
def get_db_connection():
    """Create and return a database connection"""
    return create_engine(database_url)

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
def get_model_stats(start_date=None, end_date=None):
    """Get aggregated stats per model."""
    query = """
    SELECT 
        model_name,
        COUNT(*) as total_runs,
        SUM(prompt_tokens) as total_prompt_tokens,
        SUM(completion_tokens) as total_completion_tokens,
        SUM(cache_creation_input_tokens) as total_cache_creation_tokens,
        SUM(cache_read_input_tokens) as total_cache_read_tokens,
        SUM(prompt_cost) as total_prompt_cost,
        SUM(completion_cost) as total_completion_cost,
        SUM(cache_creation_cost) as total_cache_creation_cost,
        SUM(cache_read_cost) as total_cache_read_cost,
        SUM(prompt_cost + completion_cost + COALESCE(cache_creation_cost, 0) + COALESCE(cache_read_cost, 0)) as total_cost
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

@st.cache_data(ttl=3600)
def get_process_stats(start_date=None, end_date=None):
    """Get aggregated stats per process."""
    query = """
    SELECT 
        process_id,
        COUNT(*) as total_runs,
        SUM(prompt_tokens) as total_prompt_tokens,
        SUM(completion_tokens) as total_completion_tokens,
        SUM(cache_creation_input_tokens) as total_cache_creation_tokens,
        SUM(cache_read_input_tokens) as total_cache_read_tokens,
        SUM(prompt_cost) as total_prompt_cost,
        SUM(completion_cost) as total_completion_cost,
        SUM(cache_creation_cost) as total_cache_creation_cost,
        SUM(cache_read_cost) as total_cache_read_cost,
        SUM(prompt_cost + completion_cost + COALESCE(cache_creation_cost, 0) + COALESCE(cache_read_cost, 0)) as total_cost
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

@st.cache_data(ttl=3600)
def get_daily_cost_stats(start_date=None, end_date=None):
    """Get daily cost statistics."""
    query = """
    SELECT 
        DATE(tstp) as date,
        SUM(prompt_cost) as prompt_cost,
        SUM(completion_cost) as completion_cost,
        SUM(cache_creation_cost) as cache_creation_cost,
        SUM(cache_read_cost) as cache_read_cost,
        SUM(prompt_cost + completion_cost + COALESCE(cache_creation_cost, 0) + COALESCE(cache_read_cost, 0)) as total_cost,
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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

@st.cache_data(ttl=3600)
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
            query = text("""
                UPDATE tweet_replies
                SET approval_status = :status, 
                    tstp = NOW()
                WHERE id = :tweet_id
                """)
            result = connection.execute(query, {"status": status, "tweet_id": tweet_id})
            connection.commit()
            return True
    except Exception as e:
        print(f"Error updating tweet reply status: {e}")
        return False

def update_tweet_reply_text_and_status(tweet_id, new_text, status='approved'):
    """Update both the response text and status of a tweet reply."""
    if status not in ['approved', 'rejected']:
        return False
    
    try:
        conn = get_db_connection()
        with conn.connect() as connection:
            query = text("""
                UPDATE tweet_replies
                SET approval_status = :status,
                    response = :new_text,
                    tstp = NOW()
                WHERE id = :tweet_id
                """)
            result = connection.execute(query, {"status": status, "new_text": new_text, "tweet_id": tweet_id})
            connection.commit()
            return True
    except Exception as e:
        print(f"Error updating tweet reply text and status: {e}")
        return False

def delete_tweet_reply(tweet_id):
    """Delete a tweet reply from the database."""
    try:
        conn = get_db_connection()
        with conn.connect() as connection:
            query = text("""
                DELETE FROM tweet_replies
                WHERE id = :tweet_id
                """)
            result = connection.execute(query, {"tweet_id": tweet_id})
            connection.commit()
            return True
    except Exception as e:
        print(f"Error deleting tweet reply: {e}")
        return False

@st.cache_data(ttl=3600)
def load_poll_results(start_date=None, end_date=None):
    """Load poll results, aggregated by day and feature_name, with optional date filtering"""
    query = """
    SELECT 
        DATE(tstp) as date,
        feature_name,
        COUNT(*) as vote_count
    FROM feature_poll_votes
    """
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
    GROUP BY DATE(tstp), feature_name
    ORDER BY date, feature_name
    """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

@st.cache_data(ttl=3600)
def get_daily_cost_stats_grouped(start_date=None, end_date=None, group_by="token_type"):
    """
    Get daily cost statistics grouped by different dimensions.
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter  
        group_by: Grouping dimension - "token_type", "model", or "process"
        
    Returns:
        DataFrame with columns: date, category, prompt_cost, completion_cost, 
        cache_creation_cost, cache_read_cost, total_cost, total_runs
    """
    if group_by == "token_type":
        # Return the existing token type structure - unpivoted for consistency
        query = """
        SELECT 
            DATE(tstp) as date,
            'Prompt' as category,
            SUM(prompt_cost) as cost,
            COUNT(*) as runs
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
        UNION ALL
        SELECT 
            DATE(tstp) as date,
            'Completion' as category,
            SUM(completion_cost) as cost,
            COUNT(*) as runs
        FROM token_usage_logs
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY DATE(tstp)
        UNION ALL
        SELECT 
            DATE(tstp) as date,
            'Cache Creation' as category,
            SUM(cache_creation_cost) as cost,
            COUNT(*) as runs
        FROM token_usage_logs
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY DATE(tstp)
        UNION ALL
        SELECT 
            DATE(tstp) as date,
            'Cache Read' as category,
            SUM(cache_read_cost) as cost,
            COUNT(*) as runs
        FROM token_usage_logs
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
        GROUP BY DATE(tstp)
        ORDER BY date, category
        """
        
    elif group_by == "model":
        query = """
        SELECT 
            DATE(tstp) as date,
            model_name as category,
            SUM(prompt_cost + completion_cost + COALESCE(cache_creation_cost, 0) + COALESCE(cache_read_cost, 0)) as cost,
            COUNT(*) as runs
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
        GROUP BY DATE(tstp), model_name
        ORDER BY date, model_name
        """
        
    elif group_by == "process":
        query = """
        SELECT 
            DATE(tstp) as date,
            process_id as category,
            SUM(prompt_cost + completion_cost + COALESCE(cache_creation_cost, 0) + COALESCE(cache_read_cost, 0)) as cost,
            COUNT(*) as runs
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
        GROUP BY DATE(tstp), process_id
        ORDER BY date, process_id
        """
    
    conn = get_db_connection()
    return pd.read_sql(query, conn)

@st.cache_data(ttl=3600)
def get_available_models(start_date=None, end_date=None):
    """Get list of available models in the date range."""
    query = "SELECT DISTINCT model_name FROM token_usage_logs"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY model_name"
    
    conn = get_db_connection()
    result = pd.read_sql(query, conn)
    return result["model_name"].tolist()

@st.cache_data(ttl=3600)
def get_available_processes(start_date=None, end_date=None):
    """Get list of available processes in the date range."""
    query = "SELECT DISTINCT process_id FROM token_usage_logs WHERE process_id IS NOT NULL"
    conditions = []
    
    if start_date:
        conditions.append(f"tstp >= '{start_date}'")
    if end_date:
        conditions.append(f"tstp <= '{end_date}'")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += " ORDER BY process_id"
    
    conn = get_db_connection()
    result = pd.read_sql(query, conn)
    return result["process_id"].tolist() 