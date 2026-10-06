import streamlit as st

def render_hero():
    """
    Renders a cinematic, technical F1 race-strategy header adaptable to light and dark themes.
    """
    html = """<div style="text-align: center; padding: 1.2rem 0 0.8rem 0; font-family: 'Inter', -apple-system, sans-serif;">
<h1 style="font-size: 3.2rem; font-weight: 900; margin: 0; background: var(--hero-gradient, linear-gradient(135deg, #ffffff 0%, #94a3b8 100%)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1.5px;">
PITPREDICT
</h1>
<h3 style="font-size: 1.05rem; font-weight: 800; color: #e11d48; letter-spacing: 3px; text-transform: uppercase; margin-top: 4px; margin-bottom: 8px;">
🏎️ AI-POWERED FORMULA 1 RACE STRATEGY ENGINE
</h3>
<div style="display: inline-flex; gap: 12px; font-family: monospace; font-size: 0.8rem; background: var(--card-bg, rgba(17, 24, 39, 0.6)); padding: 6px 16px; border-radius: 20px; border: 1px solid var(--card-border, #1f2937);">
<span style="color: #10b981; font-weight: 700;">● SYS: ONLINE</span>
<span style="color: var(--text-secondary, #94a3b8);">|</span>
<span style="color: #38bdf8; font-weight: 700;">⚡ TELEMETRY: ACTIVE</span>
<span style="color: var(--text-secondary, #94a3b8);">|</span>
<span style="color: #f43f5e; font-weight: 700;">🎯 XGBOOST v2.1</span>
</div>
</div>"""
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)



