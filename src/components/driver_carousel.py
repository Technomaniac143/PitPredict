import streamlit as st

def inject_carousel_css():
    """
    Injects CSS to make Streamlit horizontal radio buttons look like a Depth Carousel.
    """
    css = """
    <style>
    /* Target the horizontal radio group */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 15px;
        overflow-x: auto;
        padding: 20px 0;
        justify-content: center;
    }
    
    /* Target individual radio items */
    div[role="radiogroup"] > label {
        background: rgba(20, 20, 30, 0.6) !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 20px 30px !important;
        transition: all 0.3s ease !important;
        opacity: 0.6;
        transform: scale(0.9);
        cursor: pointer;
        backdrop-filter: blur(5px);
    }
    
    /* Hide the actual radio circle */
    div[role="radiogroup"] > label span[data-baseweb="radio"] {
        display: none;
    }
    
    /* Text styling inside the card */
    div[role="radiogroup"] > label div {
        font-family: 'Inter', monospace !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }
    
    /* Hover state */
    div[role="radiogroup"] > label:hover {
        opacity: 0.8;
        border-color: #555 !important;
    }
    
    /* Checked (Active) State */
    div[role="radiogroup"] > label[data-checked="true"] {
        opacity: 1 !important;
        transform: scale(1.1) !important;
        border-color: #00e5ff !important;
        box-shadow: 0 10px 20px rgba(0, 229, 255, 0.2) !important;
        background: rgba(0, 229, 255, 0.05) !important;
        z-index: 10;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
