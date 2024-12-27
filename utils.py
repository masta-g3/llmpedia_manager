import streamlit as st
import hmac

def init_auth_sidebar():
    """Initialize the authentication sidebar with a subtle design."""
    with st.sidebar:
        st.markdown("""
        <style>
        /* Global Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Refined Authentication Styles */
        .auth-status {
            padding: 0.5rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: 0.3px;
        }
        .auth-status.logged-in {
            color: #00CA4E;
            background-color: rgba(0, 202, 78, 0.05);
        }
        .auth-status.logged-out {
            padding: 0;
            margin: 0;
        }
        .auth-container {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.1);
        }
        
        /* Global Container Refinements */
        .stApp {
            background: linear-gradient(to bottom right, rgba(var(--primary-color-rgb), 0.02), rgba(var(--primary-color-rgb), 0.01));
        }
        
        /* Card Styles */
        .card {
            background: var(--background-color);
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }
        .card:hover {
            border-color: rgba(var(--primary-color-rgb), 0.2);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }
        
        /* Typography Refinements */
        h1, h2, h3, h4 {
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        h1 {
            font-size: 2.2rem !important;
            margin-bottom: 2rem !important;
        }
        h2 {
            font-size: 1.8rem !important;
            color: var(--text-color);
            opacity: 0.9;
        }
        h3 {
            font-size: 1.3rem !important;
            margin-bottom: 1rem !important;
        }
        p {
            line-height: 1.6;
            color: var(--text-color);
            opacity: 0.85;
        }
        
        /* Button Refinements */
        .stButton button {
            border-radius: 6px;
            font-weight: 500;
            padding: 0.3rem 1rem;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        /* Input Refinements */
        .stTextInput input {
            border-radius: 6px;
            border: 1px solid rgba(var(--primary-color-rgb), 0.2);
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        .stTextInput input:focus {
            border-color: rgba(var(--primary-color-rgb), 0.5);
            box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.1);
        }
        
        /* Metric Box Refinements */
        .metric-box {
            background: var(--background-color);
            border: 1px solid rgba(var(--primary-color-rgb), 0.1);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            transition: all 0.2s ease;
        }
        .metric-box:hover {
            border-color: rgba(var(--primary-color-rgb), 0.2);
            transform: translateY(-1px);
        }
        .metric-box strong {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.8;
        }
        
        /* Sidebar Refinements */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("#### 🔐 Authentication", help="Login to access all features")
        
        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
                st.session_state["password_correct"] = True
                del st.session_state["password"]
            else:
                st.session_state["password_correct"] = False

        if st.session_state.get("password_correct", False):
            st.markdown('<div class="auth-status logged-in">●&nbsp; Logged in</div>', unsafe_allow_html=True)
            if st.button("Logout", type="secondary", use_container_width=True):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            st.markdown('<div class="auth-status logged-out">', unsafe_allow_html=True)
            st.text_input("Password", type="password", key="password", 
                         on_change=password_entered, label_visibility="collapsed")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Password incorrect")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    return st.session_state.get("password_correct", False) 