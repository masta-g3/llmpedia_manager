import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import json
from utils import init_auth_sidebar, display_refresh_controls, init_cache_controls
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
    st.error("⚠️ Please login using the sidebar to access post approval")
    st.stop()

# Cache refresh controls
init_cache_controls()

st.title("📨 Pending Posts")

# Add refresh controls
display_refresh_controls(refresh_interval_seconds=60) # Refresh every 60 seconds

# Get post_id from URL parameter
post_id = st.query_params.get("post_id", [None])[0]

@st.dialog("Confirm Deletion")
def confirm_delete_dialog(post_id, post_text):
    st.markdown('<div class="dialog-content">', unsafe_allow_html=True)
    st.warning("⚠️ This action cannot be undone")
    st.write("Are you sure you want to delete this post?")
    
    st.markdown('<div class="tweet-preview">', unsafe_allow_html=True)
    st.markdown(f"**Original post:** {post_text[:100]}{'...' if len(post_text) > 100 else ''}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Yes, Delete", type="primary", key=f"confirm_delete_btn_{post_id}"):
            if delete_tweet_reply(post_id):
                st.session_state.delete_success = True
                st.rerun()
            else:
                st.error("Failed to delete post.")
    
    with col2:
        if st.button("Cancel", key=f"cancel_delete_btn_{post_id}"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Function to display post details in card format
def display_post_card(post_row):
    # Parse metadata
    meta_data = post_row["meta_data"]
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
    timestamp = post_row["tstp"]
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    formatted_timestamp = timestamp.strftime("%b %d, %Y at %H:%M")
    
    # Render card using HTML with theme-aware classes
    st.markdown(f"""
    <div class="post-card">
        <div class="card-header">
            <h2>Post #{post_row['id']}</h2>
        </div>
        <div class="card-meta">
            <span class="response-type {response_type_class}">{response_type_desc.upper()}</span>
            <span>Generated on {formatted_timestamp}</span>
        </div>
        <h3>Original Post</h3>
        <div class="original-post">
            {post_row["selected_tweet"]}
        </div>
        <h3>Generated Reply</h3>
        <div class="generated-reply">
            {post_row["response"]}
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
        edited_response = st.text_area("Edit generated reply", post_row["response"], key=f"edit_{post_row['id']}")
        
        # Divider
        st.markdown('<div class="ai-divider"></div>', unsafe_allow_html=True)
        
        # LLM-assisted editing
        st.markdown('<h3 class="ai-editing-header">AI-Assisted Editing</h3>', unsafe_allow_html=True)
        
        edit_col1, edit_col2 = st.columns([3, 1])
        
        with edit_col1:
            edit_instructions = st.text_area("Provide instructions for AI to edit the reply", 
                                         placeholder="e.g., Make it more concise and professional", 
                                         key=f"instructions_{post_row['id']}", 
                                         height=100)
        
        with edit_col2:
            st.markdown('<div class="ai-edit-button">', unsafe_allow_html=True)
            ai_edit_button = st.button("✨ Apply AI Edit", key=f"apply_ai_{post_row['id']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if ai_edit_button:
            with st.spinner("Applying AI edits..."):
                # Call the LLM to edit the reply
                ai_edited_response = llm.edit_tweet_reply(
                    original_tweet=post_row["selected_tweet"],
                    generated_reply=post_row["response"],
                    edit_instructions=edit_instructions,
                    context=context
                )
                # Update the text area with AI-edited response
                st.session_state[f"edit_{post_row['id']}"] = ai_edited_response
                st.rerun()
        
        # Check if edited
        was_edited = edited_response != post_row["response"]
        if was_edited:
            st.info("Reply has been modified. Click 'Approve with Edit' to save changes.")
    
    # Approval buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        if st.button("✅ Approve", type="primary", key=f"approve_{post_row['id']}"):
            if update_tweet_reply_status(post_row["id"], "approved"):
                st.success("Post approved successfully!")
                st.rerun()
            else:
                st.error("Failed to approve post.")
    
    with col2:
        if was_edited and st.button("📝 Approve with Edit", type="primary", key=f"approve_edit_{post_row['id']}"):
            if update_tweet_reply_text_and_status(post_row["id"], edited_response, "approved"):
                st.success("Post edited and approved successfully!")
                st.rerun()
            else:
                st.error("Failed to edit and approve post.")
    
    with col3:
        if st.button("❌ Reject", type="secondary", key=f"reject_{post_row['id']}"):
            if update_tweet_reply_status(post_row["id"], "rejected"):
                st.success("Post rejected successfully!")
                st.rerun()
            else:
                st.error("Failed to reject post.")
    
    with col4:
        if st.button("🗑️ Delete", type="secondary", key=f"delete_{post_row['id']}"):
            confirm_delete_dialog(post_row["id"], post_row["selected_tweet"])
    
    # Check for deletion success and show message
    if hasattr(st.session_state, 'delete_success') and st.session_state.delete_success:
        st.success("Post deleted successfully!")
        # Clear the success flag so the message doesn't persist
        del st.session_state.delete_success
        st.rerun()
    
    st.markdown("<hr style='border-color: var(--border-color);'>", unsafe_allow_html=True)

# Main app logic
if post_id:
    # Get specific post
    pending_posts = get_pending_tweet_replies(limit=100)
    
    if not pending_posts.empty:
        # Find the post with the specified ID
        try:
            post_id = int(post_id)
            post = pending_posts[pending_posts["id"] == post_id]
            
            if not post.empty:
                display_post_card(post.iloc[0])
            else:
                st.warning(f"No pending post found with ID: {post_id}")
        except ValueError:
            st.error("Invalid post ID")
    else:
        st.info("No pending posts found.")
else:
    # Show all pending posts
    pending_posts = get_pending_tweet_replies(limit=10)
    
    if not pending_posts.empty:
        st.write(f"Found {len(pending_posts)} pending posts")
        
        # Create a container for all cards to ensure consistent styling
        for _, post in pending_posts.iterrows():
            display_post_card(post)
    else:
        st.info("No pending posts found.")

# Add footer
st.markdown("<div class='footer'>LLMPedia Post Approval System</div>", unsafe_allow_html=True) 