import time
import streamlit as st

def play_split_flap(placeholder):
    """
    Simulates a race-start Split Flap sequence (GET -> SET -> GO) inside a Streamlit container.
    """
    words = ["GET", "SET", "GO!"]
    
    css = """
    <style>
    .split-flap {
        font-family: 'Courier New', monospace;
        font-size: 5rem;
        font-weight: 900;
        color: #fff;
        background: #111;
        border: 2px solid #333;
        border-radius: 12px;
        padding: 2rem 4rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        text-transform: uppercase;
        letter-spacing: 10px;
        position: relative;
        display: inline-block;
        margin: 2rem auto;
    }
    .split-flap::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background: #000;
    }
    .flap-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    for word in words:
        html = f"""
        <div class="flap-container">
            <div class="split-flap">{word}</div>
        </div>
        """
        placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(0.6)
    
    placeholder.empty()
