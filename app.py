import streamlit as st
import streamlit_nested_layout
from utils import init_auth_sidebar
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
        <div class="feature-card">
            <h3>📊 Analytics Dashboard</h3>
            <p>Comprehensive analytics and monitoring:</p>
            <ul>
                <li>Visit logs and user activity tracking</li>
                <li>Q&A interaction analysis</li>
                <li>Error monitoring and tracking</li>
                <li>Top entrypoint analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔄 Workflow Management</h3>
            <p>Monitor and analyze workflow performance:</p>
            <ul>
                <li>Workflow run history and status</li>
                <li>Process execution tracking</li>
                <li>Performance metrics visualization</li>
                <li>Error rate monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📡 Telemetry Insights</h3>
            <p>Detailed system performance metrics:</p>
            <ul>
                <li>Hourly and daily usage patterns</li>
                <li>User interaction tracking</li>
                <li>System health monitoring</li>
                <li>Performance bottleneck detection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>💰 Cost Analytics</h3>
            <p>Comprehensive cost tracking and analysis:</p>
            <ul>
                <li>Model usage cost breakdown</li>
                <li>Token consumption metrics</li>
                <li>Daily cost tracking</li>
                <li>Process-level cost analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
