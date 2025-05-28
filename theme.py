import streamlit as st

def apply_theme():
    """Apply a modern, accessible theme with proper design system foundation."""
    st.markdown(_get_theme_css(), unsafe_allow_html=True)

def _get_theme_css():
    """Generate optimized CSS with design tokens and component architecture."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        :root {{
            /* Design Tokens - Colors */
            --color-primary: #2563eb;
            --color-primary-hover: #1d4ed8;
            --color-success: #059669;
            --color-warning: #d97706;
            --color-error: #dc2626;
            --color-info: #0891b2;
            
            /* Semantic Colors - Light Mode */
            --color-bg-primary: #ffffff;
            --color-bg-secondary: #f8fafc;
            --color-bg-tertiary: #f1f5f9;
            --color-text-primary: #0f172a;
            --color-text-secondary: #475569;
            --color-text-tertiary: #64748b;
            --color-border: #e2e8f0;
            --color-border-hover: #cbd5e1;
            --color-shadow: rgba(15, 23, 42, 0.08);
            --color-shadow-hover: rgba(15, 23, 42, 0.12);
            
            /* Typography Scale */
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-size-xs: 0.75rem;
            --font-size-sm: 0.875rem;
            --font-size-base: 1rem;
            --font-size-lg: 1.125rem;
            --font-size-xl: 1.25rem;
            --font-size-2xl: 1.5rem;
            --font-size-3xl: 1.875rem;
            
            /* Spacing Scale (8px grid) */
            --space-1: 0.25rem;
            --space-2: 0.5rem;
            --space-3: 0.75rem;
            --space-4: 1rem;
            --space-5: 1.25rem;
            --space-6: 1.5rem;
            --space-8: 2rem;
            --space-10: 2.5rem;
            --space-12: 3rem;
            
            /* Border Radius */
            --radius-sm: 0.25rem;
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
            --radius-xl: 0.75rem;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px 0 var(--color-shadow);
            --shadow-md: 0 4px 6px -1px var(--color-shadow);
            --shadow-lg: 0 10px 15px -3px var(--color-shadow);
            
            /* Transitions */
            --transition-fast: 150ms ease;
            --transition-normal: 250ms ease;
        }}
        
        /* Dark Mode */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --color-bg-primary: #0f172a;
                --color-bg-secondary: #1e293b;
                --color-bg-tertiary: #334155;
                --color-text-primary: #f8fafc;
                --color-text-secondary: #cbd5e1;
                --color-text-tertiary: #94a3b8;
                --color-border: #334155;
                --color-border-hover: #475569;
                --color-shadow: rgba(0, 0, 0, 0.25);
                --color-shadow-hover: rgba(0, 0, 0, 0.35);
            }}
        }}
        
        /* Global Styles */
        html, body, [class*="css"] {{
            font-family: var(--font-family) !important;
            color: var(--color-text-primary) !important;
            line-height: 1.6;
        }}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600 !important;
            letter-spacing: -0.025em;
            color: var(--color-text-primary) !important;
        }}
        h1 {{ font-size: var(--font-size-3xl) !important; margin-bottom: var(--space-6); }}
        h2 {{ font-size: var(--font-size-2xl) !important; margin-bottom: var(--space-5); }}
        h3 {{ font-size: var(--font-size-xl) !important; margin-bottom: var(--space-4); }}
        h4 {{ font-size: var(--font-size-lg) !important; margin-bottom: var(--space-3); }}
        
        /* Layout */
        .block-container {{
            padding: var(--space-10) var(--space-8) !important;
            max-width: 1200px !important;
        }}
        
        section[data-testid="stSidebar"] {{
            background-color: var(--color-bg-secondary) !important;
            border-right: 1px solid var(--color-border) !important;
            padding-top: var(--space-8) !important;
        }}
        
        /* Form Elements */
        .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {{
            border: 1px solid var(--color-border) !important;
            border-radius: var(--radius-md) !important;
            background-color: var(--color-bg-primary) !important;
            color: var(--color-text-primary) !important;
            transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
        }}
        
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--color-primary) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            outline: none !important;
        }}
        
        /* Buttons */
        .stButton button {{
            border: 1px solid var(--color-border) !important;
            border-radius: var(--radius-md) !important;
            background-color: var(--color-bg-primary) !important;
            color: var(--color-text-primary) !important;
            font-weight: 500 !important;
            padding: var(--space-2) var(--space-4) !important;
            transition: all var(--transition-fast);
        }}
        
        .stButton button:hover {{
            border-color: var(--color-primary) !important;
            background-color: var(--color-primary) !important;
            color: white !important;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }}
        
        /* Component Classes */
        .main-header {{
            padding-bottom: var(--space-6);
            margin-bottom: var(--space-8);
            border-bottom: 1px solid var(--color-border);
        }}
        
        .card, .zen-panel, .post-card, .tweet-card {{
            background-color: var(--color-bg-primary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            padding: var(--space-6);
            margin-bottom: var(--space-6);
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-normal);
        }}
        
        .card:hover, .zen-panel:hover, .post-card:hover, .tweet-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--color-border-hover);
        }}
        
        /* Status Indicators */
        .auth-status {{
            display: flex;
            align-items: center;
            padding: var(--space-3) var(--space-4);
            border-radius: var(--radius-md);
            font-weight: 500;
            font-size: var(--font-size-sm);
            margin: var(--space-4) 0;
        }}
        
        .auth-status.logged-in {{
            background-color: rgba(5, 150, 105, 0.1);
            color: var(--color-success);
            border-left: 3px solid var(--color-success);
        }}
        
        .auth-status.logged-in::before {{
            content: '●';
            margin-right: var(--space-2);
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        /* Metrics */
        .metric-box {{
            background-color: var(--color-bg-tertiary);
            border-radius: var(--radius-md);
            padding: var(--space-4);
            text-align: center;
            margin: var(--space-2);
            min-width: 120px;
            transition: transform var(--transition-fast);
        }}
        
        .metric-box:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-label {{
            font-size: var(--font-size-xs);
            color: var(--color-text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: var(--space-1);
        }}
        
        .metric-value {{
            font-size: var(--font-size-2xl);
            font-weight: 600;
            color: var(--color-text-primary);
        }}
        
        /* Tags and Badges */
        .metadata-tag, .response-type {{
            display: inline-flex;
            align-items: center;
            padding: var(--space-1) var(--space-3);
            border-radius: var(--radius-sm);
            font-size: var(--font-size-xs);
            font-weight: 500;
            margin: var(--space-1);
            transition: transform var(--transition-fast);
        }}
        
        .metadata-tag:hover, .response-type:hover {{
            transform: translateY(-1px);
        }}
        
        /* Status-specific colors */
        .response-type.pending {{ background-color: rgba(217, 119, 6, 0.1); color: var(--color-warning); }}
        .response-type.approved {{ background-color: rgba(5, 150, 105, 0.1); color: var(--color-success); }}
        .response-type.rejected {{ background-color: rgba(220, 38, 38, 0.1); color: var(--color-error); }}
        .response-type.scheduled {{ background-color: rgba(8, 145, 178, 0.1); color: var(--color-info); }}
        
        /* AI Components */
        .ai-divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, var(--color-border), transparent);
            margin: var(--space-6) 0;
        }}
        
        .ai-editing-header {{
            color: var(--color-primary);
            font-size: var(--font-size-lg) !important;
            display: flex;
            align-items: center;
            margin: var(--space-4) 0;
        }}
        
        .ai-editing-header::before {{
            content: '✨';
            margin-right: var(--space-2);
        }}
        
        /* Gallery */
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: var(--space-4);
            margin: var(--space-6) 0;
        }}
        
        .gallery-image {{
            border-radius: var(--radius-lg);
            overflow: hidden;
            transition: transform var(--transition-normal);
        }}
        
        .gallery-image:hover {{
            transform: scale(1.02);
        }}
        
                 /* Additional Component Classes */
         .auth-container, .dialog-content, .tweet-preview, .original-post, .generated-reply {{
             background-color: var(--color-bg-secondary);
             border: 1px solid var(--color-border);
             border-radius: var(--radius-md);
             padding: var(--space-4);
             margin-bottom: var(--space-4);
         }}
         
         .card-header {{
             margin-bottom: var(--space-4);
             padding-bottom: var(--space-3);
             border-bottom: 1px solid var(--color-border);
         }}
         
         .card-meta {{
             display: flex;
             justify-content: space-between;
             align-items: center;
             margin-bottom: var(--space-4);
             font-size: var(--font-size-sm);
             color: var(--color-text-secondary);
         }}
         
         .metrics-container {{
             border-bottom: 1px solid var(--color-border);
             padding-bottom: var(--space-3);
             margin: var(--space-4) 0 var(--space-6) 0;
         }}
         
         .metrics-header {{
             font-size: var(--font-size-sm);
             font-weight: 500;
             margin-bottom: var(--space-4);
             color: var(--color-text-secondary);
         }}
         
         .metric-card {{
             background-color: var(--color-bg-primary);
             border: 1px solid var(--color-border);
             border-radius: var(--radius-md);
             padding: var(--space-4);
             margin-bottom: var(--space-3);
             text-align: center;
             transition: transform var(--transition-fast);
         }}
         
         .metric-card:hover {{
             transform: translateY(-2px);
             box-shadow: var(--shadow-md);
         }}
         
         .tweet-text, .date-display {{
             color: var(--color-text-primary);
             line-height: 1.6;
             margin: var(--space-3) 0;
         }}
         
         .paper-preview {{
             background-color: var(--color-bg-tertiary);
             border-radius: var(--radius-md);
             padding: var(--space-3);
             margin: var(--space-3) 0;
             font-size: var(--font-size-sm);
         }}
         
         .pagination-container {{
             display: flex;
             justify-content: center;
             align-items: center;
             margin: var(--space-6) 0;
         }}
         
         .ai-edit-button {{
             margin: var(--space-4) 0;
         }}
         
         /* Utility Classes */
         .text-center {{ text-align: center; }}
         .text-sm {{ font-size: var(--font-size-sm); }}
         .text-xs {{ font-size: var(--font-size-xs); }}
         .font-medium {{ font-weight: 500; }}
         .font-semibold {{ font-weight: 600; }}
        
        /* Accessibility */
        *:focus {{
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .block-container {{
                padding: var(--space-6) var(--space-4) !important;
            }}
            
            .gallery-grid {{
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: var(--space-3);
            }}
        }}
    </style>
    """