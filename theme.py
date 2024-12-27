import streamlit as st

def apply_theme():
    """Apply a minimal, clean theme across the app."""
    st.markdown("""
    <style>
        /* Global styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 500 !important;
            letter-spacing: -0.02em !important;
            color: var(--text-color);
        }
        
        /* Cards and containers */
        .card {
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            background: var(--background-color);
            margin: 0.5rem 0;
        }
        
        /* Metrics and stats */
        .metric-box {
            padding: 0.75rem;
            border-radius: 4px;
            background: var(--background-color);
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            text-align: center;
        }
        
        .metric-box strong {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.8;
        }
        
        /* Tweet styling */
        .tweet-card {
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            background: var(--background-color);
            margin: 0.5rem 0;
        }
        
        .thread-indicator {
            color: #1DA1F2;
            font-size: 0.75rem;
            margin-bottom: 0.25rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        
        .thread-item {
            margin-left: 1rem;
            padding-left: 0.75rem;
            border-left: 1px solid rgba(var(--primary-color-rgb), 0.1);
            margin-top: 0.5rem;
        }
        
        /* Links */
        a {
            color: rgb(var(--primary-color-rgb));
            text-decoration: none;
        }
        
        /* Buttons */
        .stButton button {
            border-radius: 4px;
            font-weight: 500;
            padding: 0.25rem 0.75rem;
        }
        
        /* Auth container */
        .auth-container {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 4px;
            background: var(--background-color);
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
        }
        
        .auth-status {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        
        .auth-status.logged-in {
            color: #00C853;
            background: rgba(0, 200, 83, 0.1);
        }
        
        /* Main header */
        .main-header {
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 1rem;
        }
        
        /* Feature cards */
        .feature-card {
            height: 100%;
            padding: 1.25rem;
            border-radius: 6px;
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            background: var(--background-color);
        }
        
        /* Image gallery */
        .gallery-image {
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }

        /* Additional spacing refinements */
        .stMarkdown {
            margin-top: 0 !important;
        }
        
        .row-widget {
            margin-bottom: 0.5rem !important;
        }
        
        /* Streamlit default overrides */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        
        section[data-testid="stSidebar"] {
            padding-top: 1rem !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 0.5rem !important;
        }
        
        div[data-testid="stToolbar"] {
            display: none;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(var(--primary-color-rgb), 0.1);
            border-radius: 3px;
        }
    </style>
    """, unsafe_allow_html=True) 