import streamlit as st

def render_gradient_waves(theme_mode="dark"):
    """
    Injects a high-performance, high-contrast theme layout into Streamlit.
    Ensures complete readability and sleek styling in both Dark and Light modes.
    """
    is_light = (theme_mode == "light")
    
    if is_light:
        css_theme_vars = """
            --bg-primary: #f8fafc;
            --bg-secondary: #f1f5f9;
            --text-primary: #0f172a !important;
            --text-secondary: #475569 !important;
            --card-bg: #ffffff !important;
            --card-border: #cbd5e1 !important;
            --hero-gradient: linear-gradient(135deg, #0f172a 0%, #334155 100%);
            --dial-bg-arc: #cbd5e1 !important;
            --dial-text-color: #0f172a !important;
            --dial-subtext-color: #475569 !important;
            --sidebar-bg: #ffffff !important;
            --sidebar-text: #0f172a !important;
            --sidebar-border: #e2e8f0 !important;
            --metric-bg: #ffffff !important;
            --metric-border: #e2e8f0 !important;
            --accent-red: #e11d48 !important;
            --accent-blue: #0284c7 !important;
        """
        extra_css = """
        /* Light Mode Specific Overrides */
        .stApp {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }

        /* Sidebar in Light Mode */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] p {
            color: #475569 !important;
        }

        /* Headings & Text */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #0f172a !important;
        }
        .stApp p, .stApp span, .stApp label {
            color: #1e293b;
        }

        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-left: 4px solid #e11d48 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }
        div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 800 !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-weight: 600 !important;
        }

        /* Expanders & Inputs */
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
        }
        input[type="text"], input[type="password"] {
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }
        """
    else:
        css_theme_vars = """
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --text-primary: #f8fafc !important;
            --text-secondary: #94a3b8 !important;
            --card-bg: #111827 !important;
            --card-border: #1f2937 !important;
            --hero-gradient: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
            --dial-bg-arc: #374151 !important;
            --dial-text-color: #ffffff !important;
            --dial-subtext-color: #9ca3af !important;
            --sidebar-bg: #111827 !important;
            --sidebar-text: #f8fafc !important;
            --sidebar-border: #1f2937 !important;
            --metric-bg: #111827 !important;
            --metric-border: #1f2937 !important;
            --accent-red: #f43f5e !important;
            --accent-blue: #38bdf8 !important;
        """
        extra_css = """
        /* Dark Mode Specific Overrides */
        .stApp {
            background-color: #0b0f19 !important;
            background-image: radial-gradient(at 0% 0%, rgba(2, 132, 199, 0.08) 0px, transparent 50%),
                              radial-gradient(at 100% 100%, rgba(225, 29, 72, 0.08) 0px, transparent 50%) !important;
            color: #f8fafc !important;
        }

        /* Sidebar in Dark Mode */
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1f2937 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] p {
            color: #94a3b8 !important;
        }

        /* Headings & Text */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #f8fafc !important;
        }
        .stApp p, .stApp span, .stApp label {
            color: #e2e8f0;
        }

        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-left: 4px solid #f43f5e !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-weight: 800 !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-weight: 600 !important;
        }

        /* Expanders & Inputs */
        div[data-testid="stExpander"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 8px !important;
        }
        input[type="text"], input[type="password"] {
            background-color: #1f2937 !important;
            color: #f8fafc !important;
            border: 1px solid #374151 !important;
        }
        """

    css = f"""
    <style>
        :root {{
            {css_theme_vars}
        }}

        /* Buttons Styling */
        button[kind="primary"] {{
            background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 14px rgba(225, 29, 72, 0.4) !important;
            transition: all 0.2s ease !important;
        }}
        button[kind="primary"]:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(225, 29, 72, 0.6) !important;
        }}

        /* Metric styling polish */
        div[data-testid="stMetric"] {{
            border-radius: 10px;
            padding: 16px 20px;
        }}

        /* Tabs styling */
        button[data-baseweb="tab"] {{
            font-weight: 700 !important;
            font-size: 1rem !important;
            letter-spacing: 0.5px !important;
            padding: 10px 20px !important;
        }}

        {extra_css}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

