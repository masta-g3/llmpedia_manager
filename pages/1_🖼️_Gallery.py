import streamlit as st
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
import pandas as pd
from utils import init_auth_sidebar
from theme import apply_theme

st.set_page_config(layout="wide", page_title="Image Gallery")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access the gallery")
    st.stop()

# AWS S3 setup
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
)
BUCKET_NAME = "arxiv-art"

# Utility functions
def list_s3_files():
    """List all files in the S3 bucket with their last modified dates."""
    paginator = s3.get_paginator("list_objects_v2")
    files = []
    for page in paginator.paginate(Bucket=BUCKET_NAME):
        if "Contents" in page:
            for obj in page["Contents"]:
                files.append(
                    {
                        "Key": obj["Key"],
                        "LastModified": obj["LastModified"],
                        "ArxivCode": os.path.splitext(obj["Key"])[0],
                    }
                )
    return pd.DataFrame(files)

def delete_s3_file(file_key):
    """Delete a file from the S3 bucket."""
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        return True
    except ClientError as e:
        st.error(f"Error deleting file: {e}")
        return False

def main():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🖼️ LLMpedia Image Gallery")
    st.markdown("</div>", unsafe_allow_html=True)

    # Controls in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        # Load and sort files
        if "files_df" not in st.session_state or st.button("🔄 Refresh Gallery"):
            st.session_state.files_df = list_s3_files()
    
    with col2:
        # Sorting options
        sort_option = st.selectbox("Sort by:", ["Last Modified", "Arxiv Code"])
        if sort_option == "Last Modified":
            st.session_state.files_df = st.session_state.files_df.sort_values(
                "LastModified", ascending=False
            )
        else:
            st.session_state.files_df = st.session_state.files_df.sort_values("ArxivCode")
    st.markdown('</div>', unsafe_allow_html=True)

    # Pagination
    ITEMS_PER_PAGE = 20
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    total_pages = len(st.session_state.files_df) // ITEMS_PER_PAGE + (
        1 if len(st.session_state.files_df) % ITEMS_PER_PAGE > 0 else 0
    )

    # Function to view and potentially delete an image
    @st.dialog("Image Viewer")
    def view_image(file):
        img_url = f"https://{BUCKET_NAME}.s3.us-west-2.amazonaws.com/{file['Key']}"
        st.image(img_url)
        if st.button("🗑️ Delete", key=f"delete_{file['Key']}", type="secondary"):
            if delete_s3_file(file["Key"]):
                st.success("File deleted successfully!")
                st.session_state.refresh = True
                st.rerun()
            else:
                st.error("Failed to delete file.")

    # Display grid
    st.markdown('<div class="gallery-grid">', unsafe_allow_html=True)
    cols = st.columns(5)
    start_idx = st.session_state.page_number * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    for idx, (_, file) in enumerate(
        st.session_state.files_df.iloc[start_idx:end_idx].iterrows()
    ):
        col = cols[idx % 5]
        with col:
            img_url = f"https://{BUCKET_NAME}.s3.us-west-2.amazonaws.com/{file['Key']}"
            st.markdown(f'<div class="gallery-image">', unsafe_allow_html=True)
            st.image(img_url, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button(f"View {file['ArxivCode']}", key=f"view_{file['Key']}", type="secondary"):
                view_image(file)

    st.markdown('</div>', unsafe_allow_html=True)

    # Pagination controls in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("← Previous", type="secondary") and st.session_state.page_number > 0:
            st.session_state.page_number -= 1
            st.rerun()
    with col2:
        st.markdown(f'<p style="text-align: center">Page {st.session_state.page_number + 1} of {total_pages}</p>', unsafe_allow_html=True)
    with col3:
        if st.button("Next →", type="secondary") and st.session_state.page_number < total_pages - 1:
            st.session_state.page_number += 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Check if we need to refresh the page after a deletion
    if st.session_state.get("refresh", False):
        st.session_state.files_df = list_s3_files()
        st.session_state.refresh = False
        st.rerun()

if __name__ == "__main__":
    main() 