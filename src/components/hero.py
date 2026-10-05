import streamlit as st

def render_hero():
    """
    Renders a cinematic, technical F1 race-strategy header.
    """
    html = """
    <div style="text-align: center; padding: 2rem 0; font-family: 'Inter', sans-serif;">
        <h1 style="font-size: 4rem; font-weight: 900; margin: 0; background: -webkit-linear-gradient(#fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -2px;">
            PITPREDICT
        </h1>
        <h3 style="font-size: 1.2rem; font-weight: 400; color: #ff2800; letter-spacing: 4px; text-transform: uppercase; margin-top: 10px;">
            AI-POWERED FORMULA 1 RACE STRATEGY
        </h3>
        <p style="color: #888; font-family: monospace; letter-spacing: 1px; font-size: 0.9rem;">
            [ SYS.STATUS: ONLINE ] | [ ML.PIPELINE: ACTIVE ] | [ THE PIT WALL, REIMAGINED ]
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
