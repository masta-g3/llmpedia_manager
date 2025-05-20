import streamlit as st
import hmac
from datetime import datetime
import time

def init_auth_sidebar():
    """Initialize the authentication sidebar with a subtle design."""
    with st.sidebar:
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
            st.markdown('<div class="auth-status logged-in">Logged in</div>', unsafe_allow_html=True)
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

## Reusable UI component for refresh controls
def display_refresh_controls(refresh_interval_seconds=30):
    """Displays refresh button and auto-refresh checkbox."""
    
    ## Initialize session state if not already present
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False

    ## Layout for controls
    col1, col2, col3 = st.columns([1.5, 0.5, 1])
    
    with col1:
        st.session_state.auto_refresh = st.checkbox(f"Auto-refresh ({refresh_interval_seconds}s)", value=st.session_state.auto_refresh, key="auto_refresh_widget")
    
    with col2:
        if st.button("🔄 Refresh", key="refresh_button"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
            
    with col3:
        st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

    ## Auto-refresh logic
    if st.session_state.auto_refresh:
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        if time_since_refresh > refresh_interval_seconds:
            st.session_state.last_refresh = datetime.now()
            time.sleep(0.1) ## Small delay
            st.rerun() 

def init_cache_controls():
    """Add a sidebar button to clear Streamlit caches and rerun."""
    with st.sidebar:
        if st.button("🔄 Refresh Data Cache", type="secondary", use_container_width=True):
            ## Clear both data and resource caches
            st.cache_data.clear()
            st.cache_resource.clear()
            st.experimental_rerun() 