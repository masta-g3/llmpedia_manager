import streamlit as st
import streamlit_nested_layout
from utils import init_auth_sidebar, init_cache_controls
from theme import apply_theme

st.set_page_config(
    page_title="LLMpedia Manager",
    page_icon="🤖",
    layout="wide"
)

# Apply theme
apply_theme()

def main():
    # Initialize authentication sidebar
    is_authenticated = init_auth_sidebar()
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🤖 LLMpedia Manager")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if not is_authenticated:
        st.warning("Please login using the sidebar to access the application.")
        st.stop()
    
    ## Cache refresh controls
    init_cache_controls()
    
    # Introduction
    st.markdown("""
    Welcome to the LLMpedia Manager! This application helps you manage and analyze your LLMpedia content.
    Use the sidebar to navigate between different features:
    """)
    
    # Feature cards
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🖼️ Content Management & Publishing</h3>
            <p>Manage assets and review content:</p>
            <ul>
                <li>Browse and manage LLMpedia image assets (Gallery)</li>
                <li>Review and approve AI-generated posts (Pending Posts)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="card">
            <h3>📈 Social Media & Engagement</h3>
            <p>Analyze performance and discussions:</p>
            <ul>
                <li>Track social media post performance (Post Analytics)</li>
                <li>Gain insights into Twitter discussions (X Discussions)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>⚙️ Application & Workflow Performance</h3>
            <p>Monitor system health and processes:</p>
            <ul>
                <li>Oversee application usage and telemetry (App Telemetry)</li>
                <li>Track automated workflow status and metrics (Workflow Monitor)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="card">
            <h3>💰 Financial Oversight</h3>
            <p>Comprehensive cost tracking and analysis:</p>
            <ul>
                <li>Analyze model usage and related costs (Cost Analytics)</li>
                <li>View token consumption and daily cost metrics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
