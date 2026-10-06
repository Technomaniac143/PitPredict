import streamlit as st

def inject_carousel_css():
    """
    Injects CSS to make Streamlit horizontal radio buttons look like an F1 Driver Badge selector,
    hiding default radio dots completely and styling selected driver chips.
    """
    css = """
    <style>
    /* Target the container for the radio group */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        justify-content: center !important;
        padding: 10px 0 !important;
    }
    
    /* Target individual driver labels */
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: var(--card-bg, #111827) !important;
        border: 1px solid var(--card-border, #1f2937) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* HIDE all default radio circles, inputs, and dots completely */
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child,
    div[data-testid="stRadio"] div[role="radiogroup"] label input,
    div[data-testid="stRadio"] div[role="radiogroup"] label span[data-baseweb="radio"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
    }
    
    /* Driver Text inside the Badge */
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        color: var(--text-primary, #f8fafc) !important;
        margin: 0 !important;
    }
    
    /* Hover State */
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        border-color: #0284c7 !important;
        transform: translateY(-2px) !important;
    }
    
    /* Selected Driver Badge (Checked State) */
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        border-color: #f43f5e !important;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.4) !important;
        transform: scale(1.05) translateY(-2px) !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p {
        color: #ffffff !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

