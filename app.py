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
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🖼️ Image Gallery</h3>
            <p>Browse, view, and manage your LLMpedia image collection. Features include:</p>
            <ul>
                <li>Grid view of all images</li>
                <li>Sort by date or Arxiv code</li>
                <li>Delete unwanted images</li>
                <li>Pagination for easy navigation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Analytics Dashboard</h3>
            <p>Analyze your Twitter engagement data with interactive visualizations:</p>
            <ul>
                <li>Time series analysis of engagement metrics</li>
                <li>Customizable metric selection</li>
                <li>Tweet gallery with engagement stats</li>
                <li>Sort and filter capabilities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
