import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import init_auth_sidebar, init_cache_controls, format_cost, format_number, init_date_range_selector
from theme import apply_theme
from plots import (
    create_area_chart,
    create_bar_chart,
    create_pie_chart,
    create_grouped_time_series,
    apply_chart_theme,
)
from db import (
    load_token_usage_logs,
    get_model_stats,
    get_process_stats,
    get_daily_cost_stats,
    get_daily_cost_stats_grouped,
    get_available_models,
    get_available_processes,
)

# Set page config
st.set_page_config(layout="wide", page_title="Cost Analytics")

# Apply theme
apply_theme()

# Initialize authentication sidebar
is_authenticated = init_auth_sidebar()
if not is_authenticated:
    st.error("⚠️ Please login using the sidebar to access cost analytics")
    st.stop()

# Cache refresh controls
init_cache_controls()


@st.cache_data(ttl=3600)
def load_all_cost_data(start_date=None, end_date=None):
    """Load all cost data once and return structured datasets for local filtering."""
    # Load the raw token usage data for flexible local filtering
    raw_data = load_token_usage_logs(start_date=start_date, end_date=end_date)
    
    if raw_data.empty:
        return {
            'raw_data': pd.DataFrame(),
            'model_stats': pd.DataFrame(), 
            'process_stats': pd.DataFrame(),
            'daily_costs': pd.DataFrame(),
            'available_models': [],
            'available_processes': []
        }
    
    # Get aggregated stats for initial display (these will be re-filtered locally)
    model_stats = get_model_stats(start_date=start_date, end_date=end_date)
    process_stats = get_process_stats(start_date=start_date, end_date=end_date) 
    daily_costs = get_daily_cost_stats(start_date=start_date, end_date=end_date)
    
    # Get available options for filters
    available_models = raw_data['model_name'].unique().tolist()
    available_processes = raw_data['process_id'].dropna().unique().tolist()
    
    return {
        'raw_data': raw_data,
        'model_stats': model_stats,
        'process_stats': process_stats, 
        'daily_costs': daily_costs,
        'available_models': sorted(available_models),
        'available_processes': sorted(available_processes)
    }


def apply_comprehensive_filters(data_dict, selected_models, selected_processes):
    """Apply filters to all datasets with proper cross-filtering."""
    raw_data = data_dict['raw_data'].copy()
    
    # Apply filters to raw data first
    if selected_models:
        raw_data = raw_data[raw_data['model_name'].isin(selected_models)]
    if selected_processes:
        raw_data = raw_data[raw_data['process_id'].isin(selected_processes)]
    
    if raw_data.empty:
        return {
            'filtered_model_stats': pd.DataFrame(),
            'filtered_process_stats': pd.DataFrame(), 
            'filtered_daily_costs': pd.DataFrame(),
            'filtered_raw_data': pd.DataFrame()
        }
    
    # Recalculate aggregations from filtered raw data for consistency
    # Model stats
    model_agg = raw_data.groupby('model_name').agg({
        'prompt_tokens': 'sum',
        'completion_tokens': 'sum', 
        'cache_creation_input_tokens': 'sum',
        'cache_read_input_tokens': 'sum',
        'prompt_cost': 'sum',
        'completion_cost': 'sum',
        'cache_creation_cost': 'sum',
        'cache_read_cost': 'sum',
        'id': 'count'  # total runs
    }).reset_index()
    
    # Rename and calculate total cost
    model_agg.columns = ['model_name', 'total_prompt_tokens', 'total_completion_tokens',
                        'total_cache_creation_tokens', 'total_cache_read_tokens', 
                        'total_prompt_cost', 'total_completion_cost',
                        'total_cache_creation_cost', 'total_cache_read_cost', 'total_runs']
    model_agg['total_cost'] = (model_agg['total_prompt_cost'] + model_agg['total_completion_cost'] + 
                              model_agg['total_cache_creation_cost'].fillna(0) + 
                              model_agg['total_cache_read_cost'].fillna(0))
    
    # Process stats
    process_agg = raw_data.groupby('process_id').agg({
        'prompt_tokens': 'sum',
        'completion_tokens': 'sum',
        'cache_creation_input_tokens': 'sum', 
        'cache_read_input_tokens': 'sum',
        'prompt_cost': 'sum',
        'completion_cost': 'sum',
        'cache_creation_cost': 'sum',
        'cache_read_cost': 'sum',
        'id': 'count'
    }).reset_index()
    
    process_agg.columns = ['process_id', 'total_prompt_tokens', 'total_completion_tokens',
                          'total_cache_creation_tokens', 'total_cache_read_tokens',
                          'total_prompt_cost', 'total_completion_cost', 
                          'total_cache_creation_cost', 'total_cache_read_cost', 'total_runs']
    process_agg['total_cost'] = (process_agg['total_prompt_cost'] + process_agg['total_completion_cost'] +
                                process_agg['total_cache_creation_cost'].fillna(0) +
                                process_agg['total_cache_read_cost'].fillna(0))
    
    # Daily costs 
    raw_data['date'] = pd.to_datetime(raw_data['tstp']).dt.date
    daily_agg = raw_data.groupby('date').agg({
        'prompt_cost': 'sum',
        'completion_cost': 'sum', 
        'cache_creation_cost': 'sum',
        'cache_read_cost': 'sum',
        'id': 'count'
    }).reset_index()
    
    daily_agg.columns = ['date', 'prompt_cost', 'completion_cost', 
                        'cache_creation_cost', 'cache_read_cost', 'total_runs']
    daily_agg['total_cost'] = (daily_agg['prompt_cost'] + daily_agg['completion_cost'] +
                              daily_agg['cache_creation_cost'].fillna(0) + 
                              daily_agg['cache_read_cost'].fillna(0))
    
    return {
        'filtered_model_stats': model_agg,
        'filtered_process_stats': process_agg,
        'filtered_daily_costs': daily_agg,
        'filtered_raw_data': raw_data
    }


def get_filtered_grouped_data(raw_data, group_by, selected_models=None, selected_processes=None):
    """Generate grouped time series data from filtered raw data."""
    if raw_data.empty:
        return pd.DataFrame()
        
    # Apply filters
    filtered_data = raw_data.copy()
    if selected_models:
        filtered_data = filtered_data[filtered_data['model_name'].isin(selected_models)]
    if selected_processes:
        filtered_data = filtered_data[filtered_data['process_id'].isin(selected_processes)]
    
    if filtered_data.empty:
        return pd.DataFrame()
    
    # Add date column
    filtered_data['date'] = pd.to_datetime(filtered_data['tstp']).dt.date
    
    if group_by == "token_type":
        # Unpivot token costs by type
        prompt_data = filtered_data.groupby('date')['prompt_cost'].sum().reset_index()
        prompt_data['category'] = 'Prompt'
        prompt_data['cost'] = prompt_data['prompt_cost']
        
        completion_data = filtered_data.groupby('date')['completion_cost'].sum().reset_index()
        completion_data['category'] = 'Completion'
        completion_data['cost'] = completion_data['completion_cost']
        
        cache_creation_data = filtered_data.groupby('date')['cache_creation_cost'].sum().reset_index()
        cache_creation_data['category'] = 'Cache Creation'
        cache_creation_data['cost'] = cache_creation_data['cache_creation_cost'].fillna(0)
        
        cache_read_data = filtered_data.groupby('date')['cache_read_cost'].sum().reset_index()
        cache_read_data['category'] = 'Cache Read'
        cache_read_data['cost'] = cache_read_data['cache_read_cost'].fillna(0)
        
        result = pd.concat([
            prompt_data[['date', 'category', 'cost']],
            completion_data[['date', 'category', 'cost']],
            cache_creation_data[['date', 'category', 'cost']], 
            cache_read_data[['date', 'category', 'cost']]
        ], ignore_index=True)
        
    elif group_by == "model":
        # Group by model
        result = filtered_data.groupby(['date', 'model_name']).agg({
            'prompt_cost': 'sum',
            'completion_cost': 'sum',
            'cache_creation_cost': 'sum', 
            'cache_read_cost': 'sum'
        }).reset_index()
        
        result['cost'] = (result['prompt_cost'] + result['completion_cost'] + 
                         result['cache_creation_cost'].fillna(0) + result['cache_read_cost'].fillna(0))
        result['category'] = result['model_name']
        result = result[['date', 'category', 'cost']]
        
    return result.sort_values(['date', 'category']).reset_index(drop=True)


def plot_daily_costs(df):
    """Create a stacked area chart of daily costs (legacy function for token type view)."""
    ## Handle null values in cache columns by filling with 0
    df_plot = df.copy()
    df_plot["cache_creation_cost"] = df_plot["cache_creation_cost"].fillna(0)
    df_plot["cache_read_cost"] = df_plot["cache_read_cost"].fillna(0)
    
    # Use the centralized area chart function
    return create_area_chart(
        df=df_plot,
        x_col="date",
        y_cols=["prompt_cost", "completion_cost", "cache_creation_cost", "cache_read_cost"],
        labels={
            "prompt_cost": "Prompt Cost", 
            "completion_cost": "Completion Cost",
            "cache_creation_cost": "Cache Creation Cost",
            "cache_read_cost": "Cache Read Cost"
        },
        colors=[
            "rgba(55, 83, 109, 0.7)",
            "rgba(26, 118, 255, 0.7)", 
            "rgba(217, 191, 140, 0.7)",
            "rgba(169, 140, 76, 0.7)"
        ],
        height=400,
        xaxis_title="Date",
        yaxis_title="Cost (USD)",
        stacked=True,
    )


def plot_model_distribution(df):
    """Create a pie chart of cost distribution by model."""
    # Use the centralized pie chart function
    return create_pie_chart(
        df=df, names_col="model_name", values_col="total_cost", height=400, hole=0.4
    )


def plot_process_costs(df):
    """Create a horizontal bar chart of costs by process."""
    ## Handle null values in cache columns by filling with 0
    df_plot = df.copy()
    df_plot["total_cache_creation_tokens"] = df_plot["total_cache_creation_tokens"].fillna(0)
    df_plot["total_cache_read_tokens"] = df_plot["total_cache_read_tokens"].fillna(0)
    
    # Use the centralized bar chart function
    hover_template = (
        "<b>Process ID:</b> %{y}<br>"
        + "<b>Total Cost:</b> $%{x:.4f}<br>"
        + "<b>Runs:</b> %{customdata[0]:,}<br>"
        + "<b>Prompt Tokens:</b> %{customdata[1]:,}<br>"
        + "<b>Completion Tokens:</b> %{customdata[2]:,}<br>"
        + "<b>Cache Creation Tokens:</b> %{customdata[3]:,}<br>"
        + "<b>Cache Read Tokens:</b> %{customdata[4]:,}<extra></extra>"
    )

    # Sort the dataframe by total_cost to show lowest costs first (reversed order)
    df_sorted = df_plot.sort_values("total_cost", ascending=True).head(10)

    # Convert process_id to string to ensure proper display
    df_sorted["process_id"] = df_sorted["process_id"].astype(str)

    # Check if dark mode based on theme
    is_dark_mode = st.get_option("theme.backgroundColor") in [
        "#0e1117",
        "#111111",
        "#0E0E0E",
        "#121212",
    ]
    color = "#D9BF8C" if is_dark_mode else "#B5946A"  # Use numeric accent color

    fig = create_bar_chart(
        df=df_sorted,
        x_col="total_cost",
        y_col="process_id",
        color=color,
        height=400,
        xaxis_title="Total Cost (USD)",
        yaxis_title="Process ID",
        horizontal=True,
        hover_template=hover_template,
        custom_data=["total_runs", "total_prompt_tokens", "total_completion_tokens", "total_cache_creation_tokens", "total_cache_read_tokens"],
    )
    
    # Explicitly clear title since we use Streamlit section headers
    fig.update_layout(title="")
    
    return fig


def get_high_cost_days(daily_costs, top_n=10):
    """Get the top N highest cost days from filtered data."""
    if daily_costs.empty:
        return pd.DataFrame()
    
    return daily_costs.nlargest(top_n, 'total_cost')[['date', 'total_cost', 'total_runs']].copy()


def main():
    st.title("💰 Cost Analytics")

    # Time range selector using the new component
    col1, col2 = st.columns([2, 1])
    with col1:
        start_date, end_date = init_date_range_selector(
            key_prefix="cost",
            default_range="Last 7 Days",
            include_custom=True
        )

    # Load all data once (cached)
    data_dict = load_all_cost_data(start_date=start_date, end_date=end_date)
    
    if data_dict['raw_data'].empty:
        st.warning("No data available for the selected time period.")
        return

    # Global Filters Section
    st.markdown("---")
    st.subheader("🎛️ Filters & View Options")
    
    # Create filter controls using loaded data
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        selected_models = st.multiselect(
            "Filter by Models",
            options=data_dict['available_models'],
            default=[],
            help="Select specific models to analyze (leave empty for all models)"
        )
    
    with filter_col2:
        selected_processes = st.multiselect(
            "Filter by Processes", 
            options=data_dict['available_processes'],
            default=[],
            help="Select specific processes to analyze (leave empty for all processes)"
        )

    # Time Series Controls
    ts_col1, ts_col2 = st.columns(2)
    
    with ts_col1:
        group_by = st.selectbox(
            "📊 Group Time Series By",
            options=["Token Type", "Model"],
            index=0,
            help="Change how the time series chart groups the data"
        )
    
    with ts_col2:
        chart_type = st.radio(
            "📈 Chart Type",
            options=["Area", "Bar"],
            index=0,
            horizontal=True,
            help="Switch between stacked area and stacked bar chart"
        )

    # Apply comprehensive filters to all data
    filtered_data = apply_comprehensive_filters(data_dict, selected_models, selected_processes)
    
    if filtered_data['filtered_model_stats'].empty:
        st.warning("No data matches the selected filters.")
        return

    # Calculate total metrics from filtered data
    total_cost = filtered_data['filtered_model_stats']["total_cost"].sum()
    total_prompt_cost = filtered_data['filtered_model_stats']["total_prompt_cost"].sum()
    total_completion_cost = filtered_data['filtered_model_stats']["total_completion_cost"].sum()
    total_cache_creation_cost = filtered_data['filtered_model_stats']["total_cache_creation_cost"].fillna(0).sum()
    total_cache_read_cost = filtered_data['filtered_model_stats']["total_cache_read_cost"].fillna(0).sum()
    total_runs = filtered_data['filtered_model_stats']["total_runs"].sum()

    # Display high-level metrics
    st.markdown("---")
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.metric("Total Cost", format_cost(total_cost))
    with col2:
        st.metric("Prompt Cost", format_cost(total_prompt_cost))
    with col3:
        st.metric("Completion Cost", format_cost(total_completion_cost))
    with col4:
        st.metric("Cache Creation", format_cost(total_cache_creation_cost))
    with col5:
        st.metric("Cache Read", format_cost(total_cache_read_cost))
    with col6:
        st.metric("Total Runs", format_number(total_runs))
    with col7:
        st.metric("Period Total", format_cost(total_cost))

    # Get grouped time series data based on selection
    group_by_map = {
        "Token Type": "token_type",
        "Model": "model"
    }
    
    grouped_data = get_filtered_grouped_data(
        data_dict['raw_data'], 
        group_by_map[group_by],
        selected_models, 
        selected_processes
    )

    # Time series chart
    st.markdown("---")
    st.subheader(f"💰 Daily Costs by {group_by}")
    
    if not grouped_data.empty:
        fig = create_grouped_time_series(
            df=grouped_data,
            chart_type=chart_type.lower(),
            group_by=group_by_map[group_by],
            height=400,
            xaxis_title="Date",
            yaxis_title="Cost (USD)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected time period and filters.")

    # Secondary views with tabs
    st.markdown("---")
    st.subheader("🔍 Detailed Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Model Analysis", "Process Analysis", "High-Cost Days", "Data Tables"])

    with tab1:
        if not filtered_data['filtered_model_stats'].empty:
            st.plotly_chart(plot_model_distribution(filtered_data['filtered_model_stats']), use_container_width=True)
            
            # Add download button for model data
            csv_data = filtered_data['filtered_model_stats'].to_csv(index=False)
            st.download_button(
                label="📥 Download Model Data (CSV)",
                data=csv_data,
                file_name=f"model_costs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No model data available for the selected filters.")

    with tab2:
        if not filtered_data['filtered_process_stats'].empty:
            st.plotly_chart(plot_process_costs(filtered_data['filtered_process_stats']), use_container_width=True)
            
            # Add download button for process data
            csv_data = filtered_data['filtered_process_stats'].to_csv(index=False)
            st.download_button(
                label="📥 Download Process Data (CSV)",
                data=csv_data,
                file_name=f"process_costs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No process data available for the selected filters.")

    with tab3:
        # Now uses filtered daily costs data
        high_cost_days = get_high_cost_days(filtered_data['filtered_daily_costs'], top_n=10)
        if not high_cost_days.empty:
            st.markdown("**Top 10 Highest Cost Days**")
            
            # Format the data for display
            display_df = high_cost_days.copy()
            display_df["total_cost"] = display_df["total_cost"].apply(format_cost)
            display_df["total_runs"] = display_df["total_runs"].apply(format_number)
            display_df.columns = ["Date", "Total Cost", "Total Runs"]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No daily cost data available for the selected filters.")

    with tab4:
        # Model details table
        st.markdown("**Model Details**")
        if not filtered_data['filtered_model_stats'].empty:
            st.dataframe(
                filtered_data['filtered_model_stats'].style.format(
                    {
                        "total_prompt_cost": lambda x: format_cost(x),
                        "total_completion_cost": lambda x: format_cost(x),
                        "total_cache_creation_cost": lambda x: format_cost(x),
                        "total_cache_read_cost": lambda x: format_cost(x),
                        "total_cost": lambda x: format_cost(x),
                        "total_runs": lambda x: format_number(x),
                        "total_prompt_tokens": lambda x: format_number(x),
                        "total_completion_tokens": lambda x: format_number(x),
                        "total_cache_creation_tokens": lambda x: format_number(x),
                        "total_cache_read_tokens": lambda x: format_number(x),
                    }
                ),
                use_container_width=True
            )
        
        st.markdown("**Process Details**")
        if not filtered_data['filtered_process_stats'].empty:
            st.dataframe(
                filtered_data['filtered_process_stats'].style.format(
                    {
                        "total_prompt_cost": lambda x: format_cost(x),
                        "total_completion_cost": lambda x: format_cost(x),
                        "total_cache_creation_cost": lambda x: format_cost(x),
                        "total_cache_read_cost": lambda x: format_cost(x),
                        "total_cost": lambda x: format_cost(x),
                        "total_runs": lambda x: format_number(x),
                        "total_prompt_tokens": lambda x: format_number(x),
                        "total_completion_tokens": lambda x: format_number(x),
                        "total_cache_creation_tokens": lambda x: format_number(x),
                        "total_cache_read_tokens": lambda x: format_number(x),
                    }
                ),
                use_container_width=True
            )


if __name__ == "__main__":
    main()
