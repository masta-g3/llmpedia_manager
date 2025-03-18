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

# Custom CSS for card styling with theme-awareness
st.markdown("""
<style>
    .tweet-card {
        background-color: var(--background-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border-color);
    }
    
    .card-header {
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    .card-meta {
        color: var(--text-color-secondary);
        font-size: 0.9em;
        margin-bottom: 15px;
    }
    
    .original-tweet {
        background-color: var(--background-color-secondary);
        border-left: 4px solid var(--border-color-accent);
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .generated-reply {
        background-color: var(--highlight-background-color);
        border-left: 4px solid var(--primary-color);
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .response-type {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: 600;
        margin-right: 10px;
    }
    
    /* Set light/dark mode variables based on Streamlit's theme */
    :root {
        --background-color: #ffffff;
        --background-color-secondary: #f8f9fa;
        --text-color: #262730;
        --text-color-secondary: #666666;
        --border-color: #f0f0f0;
        --border-color-accent: #6c757d;
        --highlight-background-color: #e8f4f8;
        --primary-color: #0096c7;
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #1e1e1e;
            --background-color-secondary: #2d2d2d;
            --text-color: #fafafa;
            --text-color-secondary: #a0a0a0;
            --border-color: #3d3d3d;
            --border-color-accent: #8c8c8c;
            --highlight-background-color: #2a3b47;
            --primary-color: #00b4d8;
        }
    }
    
    /* Response type styles with better contrast for both modes */
    .type-academic {
        background-color: rgba(0, 102, 204, 0.15);
        color: var(--primary-color);
    }
    
    .type-funny {
        background-color: rgba(255, 102, 0, 0.15);
        color: #ff6600;
    }
    
    .type-common-sense {
        background-color: rgba(0, 204, 102, 0.15);
        color: #00cc66;
    }
    
    .type-unknown {
        background-color: rgba(128, 128, 128, 0.15);
        color: var(--text-color-secondary);
    }
    
    .button-container {
        display: flex;
        gap: 10px;
    }
    
    /* Ensure text is visible in both themes */
    .tweet-card h3, .tweet-card h4 {
        color: var(--text-color);
    }
    
    .original-tweet, .generated-reply {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access tweet approval")
    st.stop()

st.title("📨 Pending Posts")

# Get post_id from URL parameter
post_id = st.query_params.get("post_id", [None])[0]

# Function to get current theme and set JS variables
def inject_theme_detection():
    # Detect theme script
    st.markdown("""
    <script>
        // Function to detect dark mode and set CSS variables
        function updateThemeVariables() {
            const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            // Alternative detection method for Streamlit specifically
            const darkElements = document.querySelectorAll('.st-dark');
            const isStDark = darkElements.length > 0;
            
            // Set variables based on theme
            if (isDark || isStDark) {
                document.documentElement.style.setProperty('--background-color', '#1e1e1e');
                document.documentElement.style.setProperty('--background-color-secondary', '#2d2d2d');
                document.documentElement.style.setProperty('--text-color', '#fafafa');
                document.documentElement.style.setProperty('--text-color-secondary', '#a0a0a0');
                document.documentElement.style.setProperty('--border-color', '#3d3d3d');
                document.documentElement.style.setProperty('--border-color-accent', '#8c8c8c');
                document.documentElement.style.setProperty('--highlight-background-color', '#2a3b47');
                document.documentElement.style.setProperty('--primary-color', '#00b4d8');
            } else {
                document.documentElement.style.setProperty('--background-color', '#ffffff');
                document.documentElement.style.setProperty('--background-color-secondary', '#f8f9fa');
                document.documentElement.style.setProperty('--text-color', '#262730');
                document.documentElement.style.setProperty('--text-color-secondary', '#666666');
                document.documentElement.style.setProperty('--border-color', '#f0f0f0');
                document.documentElement.style.setProperty('--border-color-accent', '#6c757d');
                document.documentElement.style.setProperty('--highlight-background-color', '#e8f4f8');
                document.documentElement.style.setProperty('--primary-color', '#0096c7');
            }
        }
        
        // Run on load
        updateThemeVariables();
        
        // Watch for theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateThemeVariables);
        }
        
        // Additional check for Streamlit theme changes (run periodically)
        setInterval(updateThemeVariables, 1000);
    </script>
    """, unsafe_allow_html=True)

# Inject theme detection logic
inject_theme_detection()

# Function to display tweet details in card format
def display_tweet_card(tweet_row):
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
    response_type_class = f"type-{response_type_desc}"
    
    # Format timestamp
    timestamp = tweet_row["tstp"]
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    formatted_timestamp = timestamp.strftime("%b %d, %Y at %H:%M")
    
    # Render card using HTML with theme-aware classes
    st.markdown(f"""
    <div class="tweet-card">
        <div class="card-header">
            <h3>Tweet #{tweet_row['id']}</h3>
        </div>
        <div class="card-meta">
            <span class="response-type {response_type_class}">{response_type_desc.upper()}</span>
            <span>Generated on {formatted_timestamp}</span>
        </div>
        <h4>Original Tweet</h4>
        <div class="original-tweet">
            {tweet_row["selected_tweet"]}
        </div>
        <h4>Generated Reply</h4>
        <div class="generated-reply">
            {tweet_row["response"]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Context expander (using Streamlit components since it can't be done with HTML)
    if meta_data and "context" in meta_data and meta_data["context"]:
        with st.expander("Show Context"):
            st.write(meta_data["context"])
    
    # Approval buttons
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("✅ Approve", type="primary", key=f"approve_{tweet_row['id']}"):
            if update_tweet_reply_status(tweet_row["id"], "approved"):
                st.success("Tweet approved successfully!")
                st.rerun()
            else:
                st.error("Failed to approve tweet.")
    
    with col2:
        if st.button("❌ Reject", type="secondary", key=f"reject_{tweet_row['id']}"):
            if update_tweet_reply_status(tweet_row["id"], "rejected"):
                st.success("Tweet rejected successfully!")
                st.rerun()
            else:
                st.error("Failed to reject tweet.")
    
    st.markdown("<hr style='border-color: var(--border-color);'>", unsafe_allow_html=True)

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
                display_tweet_card(tweet.iloc[0])
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
        
        # Create a container for all cards to ensure consistent styling
        for _, tweet in pending_tweets.iterrows():
            display_tweet_card(tweet)
    else:
        st.info("No pending tweets found.")

# Add footer
st.markdown("<div style='margin-top: 30px; text-align: center; color: var(--text-color-secondary);'>LLMPedia Tweet Approval System</div>", unsafe_allow_html=True) 