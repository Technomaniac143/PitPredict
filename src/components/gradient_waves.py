import streamlit as st

def render_gradient_waves():
    """
    Injects a subtle, animated dark gradient background into the Streamlit app.
    Designed to look premium and motorsport-inspired without affecting readability.
    """
    css = """
    <style>
        .stApp {
            background: linear-gradient(315deg, #0b0f19 0%, #1a1a24 50%, #0b0f19 100%);
            background-size: 200% 200%;
            animation: gradientAnimation 15s ease infinite;
            color: #e0e0e0;
        }

        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Thin borders, glassmorphism for containers */
        div[data-testid="stVerticalBlock"] > div {
            border-radius: 8px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
