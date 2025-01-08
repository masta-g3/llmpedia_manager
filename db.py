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