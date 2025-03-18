import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import json
from utils import init_auth_sidebar
from theme import apply_theme

# Add project path to sys.path
PROJECT_PATH = os.environ.get("PROJECT_PATH", os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)

from db import get_pending_tweet_replies, update_tweet_reply_status

st.set_page_config(
    page_title="Pending Posts",
    page_icon="📨",
    layout="wide"
)

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access tweet approval")
    st.stop()

st.title("Pending Posts")

# Get post_id from URL parameter
post_id = st.query_params.get("post_id", [None])[0]

# Function to display tweet details
def display_tweet_details(tweet_row):
    st.subheader("Tweet Details")
    
    # Format timestamp
    timestamp = tweet_row["tstp"]
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    st.write(f"**Generated at:** {timestamp}")
    
    # Parse metadata
    meta_data = tweet_row["meta_data"]
    if isinstance(meta_data, str):
        meta_data = json.loads(meta_data)
    
    # Get response type
    response_type = meta_data.get("response_type", "unknown")
    response_type_desc = {
        "a": "academic",
        "b": "funny",
        "c": "common-sense"
    }.get(response_type, "unknown")
    
    st.write(f"**Response Type:** {response_type_desc}")
    
    # Display original tweet
    st.markdown("### Original Tweet")
    st.info(tweet_row["selected_tweet"])
    
    # Display generated reply
    st.markdown("### Generated Reply")
    st.success(tweet_row["response"])
    
    # Display context if available
    if meta_data and "context" in meta_data and meta_data["context"]:
        with st.expander("Show Context"):
            st.write(meta_data["context"])
    
    # Approval buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Approve", type="primary", key=f"approve_{tweet_row['id']}"):
            if update_tweet_reply_status(tweet_row["id"], "approved"):
                st.success("Tweet approved successfully!")
                st.rerun()
            else:
                st.error("Failed to approve tweet.")
    
    with col2:
        if st.button("Reject", type="secondary", key=f"reject_{tweet_row['id']}"):
            if update_tweet_reply_status(tweet_row["id"], "rejected"):
                st.success("Tweet rejected successfully!")
                st.rerun()
            else:
                st.error("Failed to reject tweet.")

# Main app logic
if post_id:
    # Get specific tweet
    pending_tweets = get_pending_tweet_replies(limit=100)
    
    if not pending_tweets.empty:
        # Find the tweet with the specified ID
        try:
            post_id = int(post_id)
            tweet = pending_tweets[pending_tweets["id"] == post_id]
            
            if not tweet.empty:
                display_tweet_details(tweet.iloc[0])
            else:
                st.warning(f"No pending tweet found with ID: {post_id}")
        except ValueError:
            st.error("Invalid post ID")
    else:
        st.info("No pending tweets found.")
else:
    # Show all pending tweets
    pending_tweets = get_pending_tweet_replies(limit=10)
    
    if not pending_tweets.empty:
        st.write(f"Found {len(pending_tweets)} pending tweets")
        
        for _, tweet in pending_tweets.iterrows():
            st.markdown("---")
            display_tweet_details(tweet)
    else:
        st.info("No pending tweets found.")

# Add footer
st.markdown("---")
st.markdown("LLMPedia Tweet Approval System") 