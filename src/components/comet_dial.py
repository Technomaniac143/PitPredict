import streamlit as st

def render_comet_dial(projected_gap):
    """
    Renders an SVG 'Comet Dial' to visualize the Undercut Simulator output.
    """
    is_success = projected_gap > 0
    color = "#00ff88" if is_success else "#ff2800"
    status_text = "SUCCESSFUL UNDERCUT" if is_success else "FAILED UNDERCUT"
    sub_text = f"Emerge {abs(projected_gap):.1f}s {'AHEAD' if is_success else 'BEHIND'}"
    
    # Calculate dial rotation based on gap (max 180 deg)
    rotation = min(max(projected_gap * 10, -90), 90)

    html = f"""
    <style>
    @keyframes sweepDial {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate({rotation}deg); }}
    }}
    .animated-dial {{
        animation: sweepDial 1.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    </style>
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Inter', monospace; margin: 2rem 0;">
        <div style="font-size: 0.8rem; color: #888; letter-spacing: 2px; margin-bottom: 20px;">STRATEGY UPDATE</div>
        <svg width="240" height="120" viewBox="0 0 240 120" style="overflow: visible;">
            <!-- Background Arc -->
            <path d="M 20 100 A 80 80 0 0 1 220 100" fill="none" stroke="#222" stroke-width="8" stroke-linecap="round"/>
            
            <!-- Animated Dial Value Arc -->
            <g transform="translate(120, 100)">
                <g class="animated-dial">
                    <circle cx="0" cy="-80" r="6" fill="{color}" style="box-shadow: 0 0 10px {color};"/>
                    <!-- Comet tail effect -->
                    <path d="M -2 -80 L 0 -20 L 2 -80 Z" fill="{color}" opacity="0.3"/>
                </g>
            </g>
            
            <!-- Center Text -->
            <text x="120" y="90" text-anchor="middle" fill="#fff" font-size="2rem" font-weight="900">{abs(projected_gap):.1f}s</text>
        </svg>
        <div style="color: {color}; font-weight: 700; letter-spacing: 1px; margin-top: 10px;">{status_text}</div>
        <div style="color: #ccc; font-size: 0.9rem; margin-top: 5px;">{sub_text}</div>
    </div>
    """
    st.html(html)
