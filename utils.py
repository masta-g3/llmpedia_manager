import streamlit as st
import hmac

def init_auth_sidebar():
    """Initialize the authentication sidebar with a subtle design."""
    with st.sidebar:
        st.markdown("""
        <style>
        /* Auth-specific styles only - general theme is now in theme.py */
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