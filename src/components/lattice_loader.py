import streamlit as st

def get_lattice_loader_html(message="ANALYZING TELEMETRY"):
    """
    Returns HTML for a premium 'Lattice Loader' inspired CSS animation.
    """
    html = f"""<style>
.lattice-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 240px;
    font-family: monospace;
    color: #e11d48;
    letter-spacing: 2px;
}}
.lattice {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 20px;
}}
.dot {{
    width: 14px;
    height: 14px;
    background-color: #e11d48;
    border-radius: 2px;
    animation: pulse 1.5s infinite ease-in-out;
}}
.dot:nth-child(1) {{ animation-delay: 0.1s; }}
.dot:nth-child(2) {{ animation-delay: 0.2s; }}
.dot:nth-child(3) {{ animation-delay: 0.3s; }}
.dot:nth-child(4) {{ animation-delay: 0.4s; }}
.dot:nth-child(5) {{ background-color: transparent; border: 1px solid #e11d48; }}
.dot:nth-child(6) {{ animation-delay: 0.6s; }}
.dot:nth-child(7) {{ animation-delay: 0.7s; }}
.dot:nth-child(8) {{ animation-delay: 0.8s; }}
.dot:nth-child(9) {{ animation-delay: 0.9s; }}

@keyframes pulse {{
    0%, 100% {{ transform: scale(1); opacity: 0.3; box-shadow: 0 0 0 transparent; }}
    50% {{ transform: scale(1.2); opacity: 1; box-shadow: 0 0 10px #e11d48; }}
}}
</style>
<div class="lattice-container">
<div class="lattice">
<div class="dot"></div><div class="dot"></div><div class="dot"></div>
<div class="dot"></div><div class="dot"></div><div class="dot"></div>
<div class="dot"></div><div class="dot"></div><div class="dot"></div>
</div>
<div style="font-weight: 700;">[ {message} ]</div>
</div>"""
    return html

