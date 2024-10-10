import streamlit as st
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
import pandas as pd
import hmac

st.set_page_config(layout="wide")

# Authentication function
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


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
    if not check_password():
        st.stop()

    st.title("LLMpedia Image Manager")

    # Load and sort files
    if "files_df" not in st.session_state or st.button("Refresh"):
        st.session_state.files_df = list_s3_files()

    # Sorting options
    sort_option = st.selectbox("Sort by:", ["Last Modified", "Arxiv Code"])
    if sort_option == "Last Modified":
        st.session_state.files_df = st.session_state.files_df.sort_values(
            "LastModified", ascending=False
        )
    else:
        st.session_state.files_df = st.session_state.files_df.sort_values("ArxivCode")

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
        if st.button("Delete", key=f"delete_{file['Key']}"):
            if delete_s3_file(file["Key"]):
                st.success("File deleted successfully!")
                st.session_state.refresh = True
                st.rerun()
            else:
                st.error("Failed to delete file.")

    # Display grid
    cols = st.columns(5)
    start_idx = st.session_state.page_number * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    for idx, (_, file) in enumerate(
        st.session_state.files_df.iloc[start_idx:end_idx].iterrows()
    ):
        col = cols[idx % 5]
        with col:
            img_url = f"https://{BUCKET_NAME}.s3.us-west-2.amazonaws.com/{file['Key']}"
            st.image(img_url, use_column_width=True)
            if st.button(f"View {file['ArxivCode']}", key=f"view_{file['Key']}"):
                view_image(file)

    # Pagination controls
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("Previous") and st.session_state.page_number > 0:
            st.session_state.page_number -= 1
            st.rerun()
    with col2:
        st.write(f"Page {st.session_state.page_number + 1} of {total_pages}")
    with col3:
        if st.button("Next") and st.session_state.page_number < total_pages - 1:
            st.session_state.page_number += 1
            st.rerun()

    # Check if we need to refresh the page after a deletion
    if st.session_state.get("refresh", False):
        st.session_state.files_df = list_s3_files()
        st.session_state.refresh = False
        st.rerun()


if __name__ == "__main__":
    main()
