import streamlit as st

def render_comet_dial(projected_gap):
    """
    Renders an SVG 'Comet Dial' to visualize the Undercut Simulator output,
    with theme-adaptive colors.
    """
    is_success = projected_gap > 0
    color = "#10b981" if is_success else "#ef4444"
    status_text = "SUCCESSFUL UNDERCUT" if is_success else "FAILED UNDERCUT"
    sub_text = f"Emerge {abs(projected_gap):.1f}s {'AHEAD' if is_success else 'BEHIND'}"
    
    # Calculate dial rotation based on gap (max 180 deg)
    rotation = min(max(projected_gap * 10, -90), 90)

    html = f"""<style>
@keyframes sweepDial {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate({rotation}deg); }}
}}
.animated-dial {{
    animation: sweepDial 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}}
.dial-card {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', -apple-system, sans-serif;
    margin: 1rem 0;
    padding: 1.5rem;
    background: var(--card-bg, #111827);
    border: 1px solid var(--card-border, #1f2937);
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}}
</style>
<div class="dial-card">
<div style="font-size: 0.8rem; color: var(--text-secondary, #94a3b8); letter-spacing: 2px; margin-bottom: 15px; font-weight: 700;">STRATEGY TELEMETRY UPDATE</div>
<svg width="240" height="120" viewBox="0 0 240 120" style="overflow: visible;">
<path d="M 20 100 A 80 80 0 0 1 220 100" fill="none" stroke="var(--dial-bg-arc, #374151)" stroke-width="8" stroke-linecap="round"/>
<g transform="translate(120, 100)">
<g class="animated-dial">
<circle cx="0" cy="-80" r="6" fill="{color}" style="box-shadow: 0 0 10px {color};"/>
<path d="M -2 -80 L 0 -20 L 2 -80 Z" fill="{color}" opacity="0.4"/>
</g>
</g>
<text x="120" y="90" text-anchor="middle" fill="var(--dial-text-color, #ffffff)" font-size="2rem" font-weight="900">{abs(projected_gap):.1f}s</text>
</svg>
<div style="color: {color}; font-weight: 800; letter-spacing: 1px; margin-top: 10px; font-size: 1.05rem;">{status_text}</div>
<div style="color: var(--dial-subtext-color, #9ca3af); font-size: 0.9rem; margin-top: 5px; font-weight: 500;">{sub_text}</div>
</div>"""

    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


