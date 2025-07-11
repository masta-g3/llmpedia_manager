import streamlit as st
import hmac
from datetime import datetime, timedelta
import time
import pandas as pd

def init_auth_sidebar():
    """Initialize the authentication sidebar with a subtle design."""
    
    ## Check for password in URL query parameters first
    url_password = st.query_params.get("password")
    if url_password and not st.session_state.get("password_correct", False):
        if hmac.compare_digest(url_password, st.secrets["password"]):
            st.session_state["password_correct"] = True
        else:
            ## Invalid URL password - show warning but don't block sidebar auth
            st.warning("⚠️ Invalid password in URL parameter")
    
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
            auth_method = "via URL" if url_password and hmac.compare_digest(url_password, st.secrets["password"]) else "via form"
            st.markdown(f'<div class="auth-status logged-in">Logged in {auth_method}</div>', unsafe_allow_html=True)
            if st.button("Logout", type="secondary", use_container_width=True):
                st.session_state["password_correct"] = False
                ## Clear URL password parameter on logout
                if "password" in st.query_params:
                    del st.query_params["password"]
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
            st.rerun() 

def format_cost(cost):
    """Format cost to display in dollars with sensible precision based on magnitude."""
    if cost is None or pd.isna(cost):
        return "$0.00"
    
    # Handle negative costs
    is_negative = cost < 0
    abs_cost = abs(cost)
    prefix = "-" if is_negative else ""
    
    if abs_cost >= 1000:
        # Large costs: no decimals (e.g., $1,234)
        return f"{prefix}${abs_cost:,.0f}"
    elif abs_cost >= 100:
        # Medium-large costs: 1 decimal (e.g., $123.4)
        return f"{prefix}${abs_cost:.1f}"
    elif abs_cost >= 1:
        # Medium costs: 2 decimals (e.g., $12.34)
        return f"{prefix}${abs_cost:.2f}"
    elif abs_cost >= 0.01:
        # Small costs: 3 decimals (e.g., $0.123)
        return f"{prefix}${abs_cost:.3f}"
    else:
        # Very small costs: 4 decimals (e.g., $0.0012)
        return f"{prefix}${abs_cost:.4f}"

def format_number(number):
    """Format numbers with sensible abbreviations and precision."""
    if number is None or pd.isna(number):
        return "0"
    
    # Handle negative numbers
    is_negative = number < 0
    abs_number = abs(number)
    prefix = "-" if is_negative else ""
    
    if abs_number >= 1_000_000_000:
        # Billions: 1.2B
        return f"{prefix}{abs_number/1_000_000_000:.1f}B"
    elif abs_number >= 1_000_000:
        # Millions: 1.2M
        return f"{prefix}{abs_number/1_000_000:.1f}M"
    elif abs_number >= 100_000:
        # Hundreds of thousands: 123K
        return f"{prefix}{abs_number/1_000:.0f}K"
    elif abs_number >= 10_000:
        # Ten thousands: 12.3K
        return f"{prefix}{abs_number/1_000:.1f}K"
    elif abs_number >= 1_000:
        # Thousands: 1,234 or 1.2K (prefer comma format for smaller thousands)
        return f"{prefix}{abs_number:,.0f}"
    else:
        # Less than 1000: show as-is with commas if needed
        return f"{prefix}{abs_number:,.0f}" 

def init_date_range_selector(
    key_prefix="",
    default_range="Last 7 Days",
    include_custom=True,
    custom_ranges=None
):
    """
    Create a comprehensive date range selector with optional custom range support.
    
    Args:
        key_prefix (str): Prefix for session state keys to avoid conflicts
        default_range (str): Default time range selection
        include_custom (bool): Whether to include custom range option
        custom_ranges (list): Custom list of predefined ranges
    
    Returns:
        tuple: (start_date, end_date) as datetime objects or (None, None) for "All Time"
    """
    # Default range options
    if custom_ranges is None:
        base_ranges = [
            "Last 24 Hours",
            "Last 7 Days", 
            "Last 30 Days"
        ]
        if include_custom:
            base_ranges.append("Custom Range")
        base_ranges.append("All Time")
        range_options = base_ranges
    else:
        range_options = custom_ranges
    
    # Session state keys with prefix to avoid conflicts
    start_date_key = f"{key_prefix}_custom_start_date"
    end_date_key = f"{key_prefix}_custom_end_date"
    
    # Initialize session state for custom dates
    if start_date_key not in st.session_state:
        st.session_state[start_date_key] = datetime.now().date() - timedelta(days=7)
    if end_date_key not in st.session_state:
        st.session_state[end_date_key] = datetime.now().date()

    # Time range selector
    time_range = st.selectbox(
        "Time Range",
        range_options,
        index=range_options.index(default_range) if default_range in range_options else 1,
        key=f"{key_prefix}_time_range"
    )

    # Calculate date range
    now = datetime.now()
    start_date = None
    end_date = None

    if time_range == "Custom Range" and include_custom:
        # Show custom date range pickers
        st.markdown("**Select Custom Date Range:**")

        date_col1, date_col2 = st.columns(2)

        with date_col1:
            start_date_input = st.date_input(
                "Start Date",
                value=st.session_state[start_date_key],
                max_value=now.date(),
                help="Select the start date for your analysis",
                key=f"{key_prefix}_start_date_input",
            )

        with date_col2:
            end_date_input = st.date_input(
                "End Date",
                value=st.session_state[end_date_key],
                max_value=now.date(),
                help="Select the end date for your analysis",
                key=f"{key_prefix}_end_date_input",
            )

        # Update session state
        st.session_state[start_date_key] = start_date_input
        st.session_state[end_date_key] = end_date_input

        # Validate date range
        if start_date_input > end_date_input:
            st.error("⚠️ Start date must be before or equal to end date")
            st.stop()
        elif start_date_input > now.date():
            st.error("⚠️ Start date cannot be in the future")
            st.stop()

        # Convert to datetime for consistency
        start_date = datetime.combine(start_date_input, datetime.min.time())
        end_date = datetime.combine(end_date_input, datetime.max.time())

        # Display selected range info
        days_diff = (end_date_input - start_date_input).days + 1
        st.info(
            f"📊 **Selected Range:** {start_date_input.strftime('%B %d, %Y')} to {end_date_input.strftime('%B %d, %Y')} ({days_diff} day{'s' if days_diff != 1 else ''})"
        )

    else:
        # Handle predefined time ranges
        if time_range == "Last 24 Hours":
            start_date = now - timedelta(days=1)
        elif time_range == "Last 7 Days":
            start_date = now - timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_date = now - timedelta(days=30)
        else:  # All Time or other custom ranges
            start_date = None

        # For predefined ranges, end_date is always now
        end_date = now if start_date else None

    return start_date, end_date 