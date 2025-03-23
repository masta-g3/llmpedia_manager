import streamlit as st

def apply_theme():
    """Apply a minimal, clean theme across the app."""
    # Apply CSS
    _apply_theme_css()
    
    # Apply JavaScript for theme detection
    _inject_theme_detection()

def _apply_theme_css():
    """Apply theme CSS styling."""
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
            background: var(--background-color);
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            border-radius: 6px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }
        
        .tweet-card:hover {
            border-color: rgba(var(--primary-color-rgb), 0.2);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }
        
        .card-header {
            border-bottom: 1px solid rgba(var(--primary-color-rgb), 0.1);
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
        
        /* Response type styles */
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
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        /* Input elements */
        .stTextArea textarea {
            border-radius: 6px;
            border: 1px solid rgba(var(--primary-color-rgb), 0.2);
            font-size: 0.95em;
            padding: 10px;
            min-height: 120px;
            transition: all 0.2s ease;
        }
        
        .stTextArea textarea:focus {
            border-color: rgba(var(--primary-color-rgb), 0.5);
            box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.1);
        }
        
        /* Alert styling */
        .stAlert {
            border-radius: 6px;
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
        
        /* Dialog styling */
        .dialog-content {
            padding: 0.5rem 0;
        }
        
        .tweet-preview {
            background: var(--background-color-secondary);
            border-left: 3px solid rgba(var(--primary-color-rgb), 0.5);
            padding: 0.75rem;
            margin: 1rem 0;
            border-radius: 4px;
            font-size: 0.95rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-weight: 500;
            letter-spacing: -0.02em;
        }
        
        .streamlit-expanderContent {
            border-left: 1px solid rgba(var(--primary-color-rgb), 0.1);
            padding-left: 1rem;
        }
        
        /* AI editing styles */
        h3.ai-editing-header {
            margin-top: 20px;
            font-size: 1.1em;
            padding-top: 10px;
            border-top: 1px solid rgba(var(--primary-color-rgb), 0.1);
            font-weight: 500;
            letter-spacing: -0.02em;
        }
        
        .ai-divider {
            margin: 15px 0;
            border-top: 1px dashed rgba(var(--primary-color-rgb), 0.1);
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

def _inject_theme_detection():
    """Inject JavaScript for theme detection and variable setting."""
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
                document.documentElement.style.setProperty('--primary-color-rgb', '0, 180, 216');
            } else {
                document.documentElement.style.setProperty('--background-color', '#ffffff');
                document.documentElement.style.setProperty('--background-color-secondary', '#f8f9fa');
                document.documentElement.style.setProperty('--text-color', '#262730');
                document.documentElement.style.setProperty('--text-color-secondary', '#666666');
                document.documentElement.style.setProperty('--border-color', '#f0f0f0');
                document.documentElement.style.setProperty('--border-color-accent', '#6c757d');
                document.documentElement.style.setProperty('--highlight-background-color', '#e8f4f8');
                document.documentElement.style.setProperty('--primary-color', '#0096c7');
                document.documentElement.style.setProperty('--primary-color-rgb', '0, 150, 199');
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