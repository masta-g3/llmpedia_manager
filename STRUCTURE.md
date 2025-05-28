# LLMpedia Manager: Repository Structure

This document provides an overview of the LLMpedia Manager repository structure, explaining the key components and their relationships to help new engineers understand and navigate the codebase.

## Repository Overview

LLMpedia Manager is a Streamlit-based monitoring and analytics dashboard for the LLMpedia platform. It provides visualizations and tools for monitoring content, user analytics, workflow processes, and cost metrics.

```
/Users/manager/Code/llmpedia_manager/
├── README.md                      # Project overview and setup instructions
├── STRUCTURE.md                   # This file - repository structure documentation
├── app.py                         # Main Streamlit application entry point
├── data.py                        # Data processing and analysis utilities
├── data/                          # Data files directory
│   └── account_analytics_content.csv  # Twitter analytics data
├── db.py                          # Database connector with functions for fetching, manipulating, and aggregating database records (e.g., visit logs, Q&A, errors, poll results)
├── fetch_twitter_analytics.py     # Twitter API integration for fetching data
├── llm.py                         # LLM integration for content editing
├── pages/                         # Streamlit multi-page app components
│   ├── 1_🖼️_Gallery.py           # Image gallery page for LLMpedia assets
│   ├── 2_📊_Post_Analytics.py     # Social media post analytics dashboard
│   ├── 3_📡_App_Telemetry.py      # Application usage telemetry
│   ├── 4_🔄_Workflow_Monitor.py   # Workflow process monitoring
│   ├── 5_💰_Cost_Analytics.py     # Cost tracking and analysis
│   ├── 6_🐦_X_Discussions.py      # Twitter discussions analytics
│   └── 7_📨_Pending Posts.py      # Post approval workflow interface
├── process_account_analytics.py   # Script for processing account analytics data
├── requirements.txt               # Project dependencies
├── theme.py                       # UI theme and styling definitions
└── utils.py                       # Common utility functions (auth, refresh, cache controls)
```

## Core Components

### Main Application Files

- **app.py**: The application entry point containing the main page layout, authentication setup, and an overview of key application modules.
- **data.py**: Provides functions for data processing, cleaning, and analysis.
- **db.py**: Database connector with functions for fetching, manipulating, and aggregating database records (e.g., visit logs, Q&A, errors, poll results).
- **fetch_twitter_analytics.py**: Handles Twitter API integration to fetch account analytics.
- **llm.py**: Integrates with language models for content editing and generation.
- **theme.py**: Modern, accessible UI theme system with design tokens, CSS custom properties for light/dark mode, and component-based architecture. Reduced from 545 to ~250 lines while improving maintainability and accessibility.
- **utils.py**: Contains general utility functions for authentication, common UI components like refresh controls, and cache management (e.g., `init_cache_controls` for clearing Streamlit's data and resource caches).
- **process_account_analytics.py**: Processes raw Twitter analytics data, identifying threads and relationships.

### Streamlit Pages

The application follows Streamlit's multi-page app structure with specialized dashboard pages:

1. **1_🖼️_Gallery.py**: Visual gallery for browsing LLMpedia-generated images stored in AWS S3.
2. **2_📊_Post_Analytics.py**: Detailed analytics for social media posts, including engagement metrics and chronological timelines.
3. **3_📡_App_Telemetry.py**: Monitors application usage patterns, error rates, and user interactions.
4. **4_🔄_Workflow_Monitor.py**: Tracks automated workflows and their performance metrics.
5. **5_💰_Cost_Analytics.py**: Analyzes cost data related to model usage and token consumption.
6. **6_🐦_X_Discussions.py**: Provides insights on Twitter discussions related to LLMpedia.
7. **7_📨_Pending Posts.py**: Interface for reviewing and approving AI-generated social media posts.

### Data Storage

- **data/**: Directory containing data files
- **data/account_analytics_content.csv**: Processed Twitter analytics data with engagement metrics

## Key Features and Functionality

### Authentication & Caching

- Uses a simple password-based authentication system through Streamlit's session state.
- Authentication sidebar is initialized in each page to ensure secure access.
- Implements Streamlit's caching (`st.cache_data`, `st.cache_resource`) for database queries and data loading functions to improve performance.
- A global "Refresh Data Cache" button in the sidebar allows manual invalidation of all caches.

### Data Processing

- Twitter analytics processing with thread identification.
- Data cleaning and normalization for analysis.
- Connection to PostgreSQL database for storing and retrieving application metrics.

### Analytics Dashboards

- Time-series visualizations of engagement metrics.
- Interactive filters for date ranges and specific metrics.
- Tweet-level performance analysis.
- Cost breakdowns by model and process.

### Content Management

- S3-integrated image gallery with viewing and deletion capabilities.
- Tweet approval workflow with AI-assisted editing.
- Error monitoring and analytics.

### Monitoring Systems

- Workflow monitoring with performance tracking.
- Usage pattern analysis with hourly and daily statistics.
- Cost tracking and optimization insights.

## Technical Stack

- **Frontend**: Streamlit for the web interface
- **Data Visualization**: Plotly for interactive charts
- **Database**: PostgreSQL for persistent data storage
- **Cloud Storage**: AWS S3 for image storage
- **API Integrations**: Twitter API (via Tweepy)
- **AI/ML**: LiteLLM for language model access

## Getting Started

To set up and run the application locally:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```
   streamlit run app.py
   ```

Refer to the README.md for detailed setup instructions, including environment variable configuration for the database and Twitter API integration.