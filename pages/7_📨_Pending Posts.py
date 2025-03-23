import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import json
from utils import init_auth_sidebar
from theme import apply_theme
import llm

# Add project path to sys.path
PROJECT_PATH = os.environ.get("PROJECT_PATH", os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)

from db import get_pending_tweet_replies, update_tweet_reply_status, update_tweet_reply_text_and_status, delete_tweet_reply

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

st.title("📨 Pending Posts")

# Get post_id from URL parameter
post_id = st.query_params.get("post_id", [None])[0]

@st.dialog("Confirm Deletion")
def confirm_delete_dialog(tweet_id, tweet_text):
    st.markdown('<div class="dialog-content">', unsafe_allow_html=True)
    st.warning("⚠️ This action cannot be undone")
    st.write("Are you sure you want to delete this tweet?")
    
    st.markdown('<div class="tweet-preview">', unsafe_allow_html=True)
    st.markdown(f"**Original tweet:** {tweet_text[:100]}{'...' if len(tweet_text) > 100 else ''}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Yes, Delete", type="primary", key=f"confirm_delete_btn_{tweet_id}"):
            if delete_tweet_reply(tweet_id):
                st.session_state.delete_success = True
                st.rerun()
            else:
                st.error("Failed to delete tweet.")
    
    with col2:
        if st.button("Cancel", key=f"cancel_delete_btn_{tweet_id}"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Extract context if available
    context = meta_data.get("context", "") if meta_data else ""
    
    # Context expander (using Streamlit components since it can't be done with HTML)
    if context:
        with st.expander("Show Context"):
            st.write(context)
    
    # Add edit functionality
    with st.expander("Edit Reply"):
        # Manual editing
        edited_response = st.text_area("Edit generated reply", tweet_row["response"], key=f"edit_{tweet_row['id']}")
        
        # Divider
        st.markdown('<div class="ai-divider"></div>', unsafe_allow_html=True)
        
        # LLM-assisted editing
        st.markdown('<h3 class="ai-editing-header">AI-Assisted Editing</h3>', unsafe_allow_html=True)
        
        edit_col1, edit_col2 = st.columns([3, 1])
        
        with edit_col1:
            edit_instructions = st.text_area("Provide instructions for AI to edit the reply", 
                                         placeholder="e.g., Make it more concise and professional", 
                                         key=f"instructions_{tweet_row['id']}", 
                                         height=100)
        
        with edit_col2:
            st.markdown('<div class="ai-edit-button">', unsafe_allow_html=True)
            ai_edit_button = st.button("✨ Apply AI Edit", key=f"apply_ai_{tweet_row['id']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if ai_edit_button:
            with st.spinner("Applying AI edits..."):
                # Call the LLM to edit the reply
                ai_edited_response = llm.edit_tweet_reply(
                    original_tweet=tweet_row["selected_tweet"],
                    generated_reply=tweet_row["response"],
                    edit_instructions=edit_instructions,
                    context=context
                )
                # Update the text area with AI-edited response
                st.session_state[f"edit_{tweet_row['id']}"] = ai_edited_response
                st.rerun()
        
        # Check if edited
        was_edited = edited_response != tweet_row["response"]
        if was_edited:
            st.info("Reply has been modified. Click 'Approve with Edit' to save changes.")
    
    # Approval buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("✅ Approve", type="primary", key=f"approve_{tweet_row['id']}"):
            if update_tweet_reply_status(tweet_row["id"], "approved"):
                st.success("Tweet approved successfully!")
                st.rerun()
            else:
                st.error("Failed to approve tweet.")
    
    with col2:
        if was_edited and st.button("📝 Approve with Edit", type="primary", key=f"approve_edit_{tweet_row['id']}"):
            if update_tweet_reply_text_and_status(tweet_row["id"], edited_response, "approved"):
                st.success("Tweet edited and approved successfully!")
                st.rerun()
            else:
                st.error("Failed to edit and approve tweet.")
    
    with col3:
        if st.button("❌ Reject", type="secondary", key=f"reject_{tweet_row['id']}"):
            if update_tweet_reply_status(tweet_row["id"], "rejected"):
                st.success("Tweet rejected successfully!")
                st.rerun()
            else:
                st.error("Failed to reject tweet.")
    
    with col4:
        if st.button("🗑️ Delete", type="secondary", key=f"delete_{tweet_row['id']}"):
            confirm_delete_dialog(tweet_row["id"], tweet_row["selected_tweet"])
    
    # Check for deletion success and show message
    if hasattr(st.session_state, 'delete_success') and st.session_state.delete_success:
        st.success("Tweet deleted successfully!")
        # Clear the success flag so the message doesn't persist
        del st.session_state.delete_success
        st.rerun()
    
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