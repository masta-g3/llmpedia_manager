import streamlit as st

def apply_theme():
    """Apply a refined, minimal theme across the app."""
    # Apply CSS
    _apply_theme_css()

def _apply_theme_css():
    """Apply clean, modern CSS styling."""
    st.markdown("""
    <style>
        /* Global styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            color: #333;
            line-height: 1.5;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 500 !important;
            letter-spacing: -0.01em;
            margin-bottom: 0.75rem;
        }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.1rem !important; }
        h4 { font-size: 1rem !important; font-weight: 500 !important; margin-top: 1rem; margin-bottom: 0.4rem; }
        
        /* Streamlit layout improvements */
        .block-container {
            padding: 2.5rem 2rem !important;
            max-width: 1100px !important;
        }
        
        /* Input elements - refined styling */
        .stTextArea textarea, .stTextInput input {
            border-radius: 4px !important;
            border-width: 1px !important;
            border-color: #e0e0e0 !important;
            padding: 0.6rem !important;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #6c7dd1 !important;
            box-shadow: 0 0 0 1px rgba(108, 125, 209, 0.2) !important;
        }
        
        /* Select boxes and multiselect */
        .stSelectbox div div div, .stMultiselect div div div {
            border-radius: 4px !important;
            border-width: 1px !important; 
            min-height: 40px !important;
        }
        
        /* Authentication status indicator */
        .auth-status {
            display: inline-flex;
            align-items: center;
            padding: 0.4rem 0.75rem;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 500;
            margin: 0.75rem 0;
            width: 100%;
        }
        
        .auth-status.logged-in {
            background-color: rgba(76, 175, 80, 0.15);
            color: #4CAF50;
            border-left: 3px solid #4CAF50;
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.1);
        }
        
        .auth-status.logged-in:before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #4CAF50;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4);
            }
            70% {
                box-shadow: 0 0 0 6px rgba(76, 175, 80, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(76, 175, 80, 0);
            }
        }
        
        /* Cards - refined containers */
        .card {
            padding: 1.4rem;
            margin-bottom: 1.5rem;
            border: none !important;
            border-radius: 6px !important;
            background-color: #f9f9f9;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 3px 8px rgba(0,0,0,0.08) !important;
        }
        
        /* Post card styling */
        .post-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            border: 1px solid #f0f0f0;
            transition: transform 0.2s ease, box-shadow 0.3s ease;
        }
        
        .post-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .card-header {
            margin-bottom: 0.75rem;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 0.5rem;
        }
        
        .card-header h3 {
            margin-bottom: 0;
        }
        
        .card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            font-size: 0.85rem;
            color: #666;
        }
        
        /* AI Editing Components */
        .ai-divider {
            margin: 1.25rem 0;
            height: 1px;
            background: linear-gradient(to right, transparent, #e0e0e0, transparent);
        }
        
        .ai-editing-header {
            margin-top: 0.4rem;
            color: #6c7dd1;
            font-size: 1.1rem !important;
            display: flex;
            align-items: center;
        }
        
        .ai-editing-header:before {
            content: '✨';
            margin-right: 0.4rem;
            font-size: 1rem;
        }
        
        /* Metrics styling */
        .metric-card {
            background-color: #ffffff;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 3px 8px rgba(0,0,0,0.08);
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 0.35rem;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 1.4rem;
            font-weight: 500;
            color: #333;
        }
        
        /* Metrics container for analytics */
        .metrics-container {
            border-bottom: 1px solid #eee;
            padding-bottom: 0.5rem;
            margin: 0.5rem 0 1rem 0;
        }
        
        .metrics-header {
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 0.9rem;
            color: #555;
            display: inline-block;
        }
        
        .metric-box {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #2a2a2a;
            color: #fff;
            border-radius: 6px;
            padding: 0.6rem 0.8rem;
            margin-right: 0.8rem;
            margin-bottom: 0.7rem;
            min-width: 110px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .metric-box .metric-label {
            color: rgba(255,255,255,0.75);
            font-size: 0.8rem;
            font-weight: 400;
            margin-bottom: 0.3rem;
            letter-spacing: 0.02em;
        }
        
        .metric-box .metric-value {
            color: #fff;
            font-size: 1.5rem;
            line-height: 1.2;
            margin-top: 0.1rem;
        }
        
        /* Response type styling */
        .response-type {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 500;
            font-size: 0.75rem;
            letter-spacing: 0.02em;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            position: relative;
            overflow: hidden;
        }
        
        .response-type:after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom, rgba(255,255,255,0.1), rgba(255,255,255,0));
            pointer-events: none;
        }
        
        .response-type:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.12);
        }
        
        .response-type.pending {
            background-color: #FFF4E5;
            color: #F57C00;
            border-left: 2px solid #F57C00;
        }
        
        .response-type.approved {
            background-color: #E8F5E9;
            color: #2E7D32;
            border-left: 2px solid #2E7D32;
        }
        
        .response-type.rejected {
            background-color: #FFEBEE;
            color: #C62828;
            border-left: 2px solid #C62828;
        }
        
        .response-type.scheduled {
            background-color: #E3F2FD;
            color: #1565C0;
            border-left: 2px solid #1565C0;
        }
        
        .response-type.type-academic {
            background-color: #E8EAF6;
            color: #3949AB;
            border-left: 2px solid #3949AB;
        }
        
        .response-type.type-funny {
            background-color: #FFF3E0;
            color: #EF6C00;
            border-left: 2px solid #EF6C00;
        }
        
        .response-type.type-common-sense {
            background-color: #E0F2F1;
            color: #00796B;
            border-left: 2px solid #00796B;
        }
        
        .response-type.type-unknown {
            background-color: #F5F5F5;
            color: #757575;
            border-left: 2px solid #757575;
        }
        
        .original-post, .generated-reply {
            background-color: #f9f9f9;
            border-radius: 6px;
            padding: 0.8rem;
            margin-bottom: 0.8rem;
            border: 1px solid #f0f0f0;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 4px !important;
            text-transform: none !important;
            font-weight: 500 !important;
            padding: 0.4rem 1.1rem !important;
            transition: all 0.2s ease;
            border: 1px solid #e0e0e0 !important;
        }
        
        .stButton button:hover {
            border-color: #6c7dd1 !important;
            color: #6c7dd1 !important;
            background-color: rgba(108, 125, 209, 0.05) !important;
        }
        
        /* Sidebar refinements */
        section[data-testid="stSidebar"] {
            padding-top: 2rem !important;
            background-color: #fafafa !important;
            border-right: 1px solid #f0f0f0 !important;
        }
        
        /* Dark mode compatibility */
        @media (prefers-color-scheme: dark) {
            html, body, [class*="css"] {
                color: #e0e0e0;
            }
            
            .card {
                background-color: #262626;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
            }
            
            .card:hover {
                box-shadow: 0 3px 8px rgba(0,0,0,0.3) !important;
            }
            
            .auth-status.logged-in {
                background-color: rgba(76, 175, 80, 0.15);
                color: #81C784;
                border-left: 3px solid #81C784;
                box-shadow: 0 0 15px rgba(76, 175, 80, 0.08);
            }
            
            .auth-status.logged-in:before {
                background-color: #81C784;
                animation: pulse-dark 2s infinite;
            }
            
            @keyframes pulse-dark {
                0% {
                    box-shadow: 0 0 0 0 rgba(129, 199, 132, 0.4);
                }
                70% {
                    box-shadow: 0 0 0 6px rgba(129, 199, 132, 0);
                }
                100% {
                    box-shadow: 0 0 0 0 rgba(129, 199, 132, 0);
                }
            }
            
            .post-card {
                background-color: #1e1e1e;
                border-color: #333;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }
            
            .post-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            
            .card-header {
                border-color: #333;
            }
            
            .card-meta {
                color: #aaa;
            }
            
            .ai-divider {
                background: linear-gradient(to right, transparent, #444, transparent);
            }
            
            .ai-editing-header {
                color: #7e8fe0;
            }
            
            .metrics-container {
                border-bottom: 1px solid #333;
            }
            
            .metrics-header {
                color: #bbb;
            }
            
            .metric-box {
                background-color: #333;
            }
            
            .metric-box .metric-label {
                color: rgba(255,255,255,0.65);
            }
            
            .metric-box .metric-value {
                color: #fff;
            }
            
            .original-post, .generated-reply {
                background-color: #262626;
                border-color: #333;
            }
            
            /* Dark mode response types */
            .response-type {
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }
            
            .response-type:after {
                background: linear-gradient(to bottom, rgba(255,255,255,0.03), rgba(255,255,255,0));
            }
            
            .response-type:hover {
                box-shadow: 0 2px 5px rgba(0,0,0,0.25);
            }
            
            .response-type.pending {
                background-color: rgba(255, 152, 0, 0.15);
                color: #FFB74D;
                border-left: 2px solid #FFB74D;
            }
            
            .response-type.approved {
                background-color: rgba(76, 175, 80, 0.15);
                color: #81C784;
                border-left: 2px solid #81C784;
            }
            
            .response-type.rejected {
                background-color: rgba(244, 67, 54, 0.15);
                color: #E57373;
                border-left: 2px solid #E57373;
            }
            
            .response-type.scheduled {
                background-color: rgba(33, 150, 243, 0.15);
                color: #64B5F6;
                border-left: 2px solid #64B5F6;
            }
            
            .response-type.type-academic {
                background-color: rgba(57, 73, 171, 0.15);
                color: #7986CB;
                border-left: 2px solid #7986CB;
            }
            
            .response-type.type-funny {
                background-color: rgba(239, 108, 0, 0.15);
                color: #FFB74D;
                border-left: 2px solid #FFB74D;
            }
            
            .response-type.type-common-sense {
                background-color: rgba(0, 121, 107, 0.15);
                color: #4DB6AC;
                border-left: 2px solid #4DB6AC;
            }
            
            .response-type.type-unknown {
                background-color: rgba(117, 117, 117, 0.15);
                color: #BDBDBD;
                border-left: 2px solid #BDBDBD;
            }
            
            .stTextArea textarea, .stTextInput input {
                border-color: #444 !important;
            }
            
            .stTextArea textarea:focus, .stTextInput input:focus {
                border-color: #7e8fe0 !important;
                box-shadow: 0 0 0 1px rgba(126, 143, 224, 0.3) !important;
            }
            
            .stButton button {
                border-color: #444 !important;
            }
            
            .stButton button:hover {
                border-color: #7e8fe0 !important;
                color: #7e8fe0 !important;
                background-color: rgba(126, 143, 224, 0.1) !important;
            }
            
            section[data-testid="stSidebar"] {
                background-color: #1a1a1a !important;
                border-right: 1px solid #333 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)