import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import time
from google import genai

# Ensure the root project directory is in the Python path so 'src' can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.pipeline import pipeline_instance
from src.data.ingestion import fetch_session_data
from src.features.engineering import engineer_features

# Cinematic UI Components
from src.components.gradient_waves import render_gradient_waves
from src.components.hero import render_hero
from src.components.split_flap import play_split_flap
from src.components.lattice_loader import get_lattice_loader_html
from src.components.driver_carousel import inject_carousel_css
from src.components.comet_dial import render_comet_dial

# Set page configuration with collapsible sidebar
st.set_page_config(
    page_title="PitPredict | Race Control",
    layout="wide",
    page_icon="🏎️",
    initial_sidebar_state="expanded"
)

# Manage Unified Theme State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

def on_theme_change():
    selected = st.session_state.theme_selector
    st.session_state.theme_mode = "dark" if "Dark" in selected else "light"

# --- SIDEBAR & API SETUP ---
with st.sidebar:
    st.markdown("<h2 style='font-size: 1.3rem; margin-bottom: 0.5rem;'>⚙️ Race Control Settings</h2>", unsafe_allow_html=True)
    
    # 🎨 Unified Theme Switcher Radio
    st.radio(
        "🎨 App Theme",
        options=["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state.theme_mode == "dark" else 1,
        key="theme_selector",
        horizontal=True,
        on_change=on_theme_change,
        help="Switch instantly between Dark and Light Race Control themes."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Collapsible Gemini API Key Expander
    with st.expander("🔑 Gemini AI Race Engineer Key", expanded=False):
        default_key = os.environ.get("GEMINI_API_KEY", "")
        api_key_input = st.text_input(
            "API Key",
            value=default_key,
            type="password",
            help="Optional: Enables real-time AI radio engineer voice/text messages."
        )
        if api_key_input:
            try:
                gemini_client = genai.Client(api_key=api_key_input)
                st.success("✅ AI Race Engineer connected!")
            except Exception as e:
                gemini_client = None
                st.error("Invalid API Key.")
        else:
            gemini_client = None
            st.info("AI Race Engineer is optional.")
            
    st.markdown("---")
    st.markdown("<h4 style='font-size: 1rem;'>📡 System Telemetry</h4>", unsafe_allow_html=True)
    st.caption("• FastF1 Telemetry Cache: **Online**\n• XGBoost Engine: **Ready**\n• Strategy Pipeline: **Active**")

# Apply Theme & Render Header
render_gradient_waves(theme_mode=st.session_state.theme_mode)
render_hero()

is_dark = (st.session_state.theme_mode == "dark")
chart_font_color = "#f8fafc" if is_dark else "#0f172a"
chart_grid_color = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.1)"
chart_axis_color = "#94a3b8" if is_dark else "#475569"

@st.cache_resource
def get_pipeline():
    if not pipeline_instance.load_models():
        pipeline_instance.train([(2021, 'Spain')])
    else:
        if pipeline_instance.data.empty:
            df_raw = fetch_session_data(2021, 'Spain')
            pipeline_instance.data = engineer_features(df_raw)
    return pipeline_instance

# Setup State
if "strategy_run" not in st.session_state:
    st.session_state.strategy_run = False

loader_placeholder = st.empty()
if not pipeline_instance.is_trained:
    loader_placeholder.markdown(get_lattice_loader_html("INITIALIZING PIPELINE & CACHE"), unsafe_allow_html=True)

pipeline = get_pipeline()
loader_placeholder.empty()

# --- TABS ---
tab1, tab2 = st.tabs(["🚦 Strategy Dashboard", "⚔️ Cross-Era Head-to-Head"])

with tab1:
    if pipeline.is_trained:
        st.markdown("<h3 style='text-align: center; font-family: monospace; color: var(--text-secondary, #94a3b8); letter-spacing: 2px; margin-top: 15px;'>SELECT DRIVER</h3>", unsafe_allow_html=True)
        
        # Driver Selector Chips
        inject_carousel_css()
        drivers = pipeline.data['Driver'].dropna().unique().tolist()
        drivers = sorted(list(drivers))
        selected_driver = st.radio("Driver", drivers, horizontal=True, index=drivers.index('HAM') if 'HAM' in drivers else 0, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # The Run Strategy CTA
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("▶ RUN STRATEGY PIPELINE", use_container_width=True, type="primary"):
                st.session_state.strategy_run = True
                
                # Sequence Animations
                anim_ph = st.empty()
                play_split_flap(anim_ph)
                anim_ph.markdown(get_lattice_loader_html(f"ANALYZING TELEMETRY FOR {selected_driver}"), unsafe_allow_html=True)
                time.sleep(1.0)
                anim_ph.empty()
        
        if st.session_state.strategy_run:
            preds = pipeline.predict_for_driver(selected_driver)
            
            # --- AI RACE ENGINEER ---
            if gemini_client and preds and len(preds['pit_probabilities']) > 0:
                with st.spinner("Connecting to Race Engineer..."):
                    avg_pace = sum(preds['actual_lap_times']) / len(preds['actual_lap_times'])
                    max_pit_prob = max(preds['pit_probabilities']) * 100
                    current_tire_age = preds['tire_age'][-1]
                    
                    prompt = f"""
                    You are the chief race engineer for F1 driver {selected_driver}.
                    Live ML telemetry summary: Average Pace: {avg_pace:.2f}s, Highest Pit Prob: {max_pit_prob:.1f}%, Tire Age: {current_tire_age} laps.
                    Provide a punchy (2 sentence max) radio message to the driver summarizing tire state and advising on pit strategy. Speak like a real F1 race engineer.
                    """
                    try:
                        response = gemini_client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        st.info(f"📻 **RACE ENGINEER RADIO:** '{response.text.strip()}'")
                    except Exception as e:
                        pass
            
            # --- METRICS CARDS ---
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            reg = pipeline.metrics.get('regression', {})
            clf = pipeline.metrics.get('classification', {})
            
            c1.metric("TRACK EVOLUTION", "ACTIVE", "+0.14 grip/lap")
            c2.metric("PACE MODEL MAE", f"{reg.get('MAE', 0):.3f}s", "XGBoost v2.1")
            c3.metric("PIT CONFIDENCE", f"{clf.get('F1', 0)*100:.1f}%", "Optimal Window")

            st.markdown("<br>", unsafe_allow_html=True)

            # --- CHARTS (Theme-Adaptive) ---
            plot_col1, plot_col2 = st.columns(2)
            with plot_col1:
                fig_pace = go.Figure()
                fig_pace.add_trace(go.Scatter(
                    x=preds['laps'],
                    y=preds['actual_lap_times'],
                    mode='lines+markers',
                    name='Actual Pace',
                    line=dict(color='#38bdf8' if is_dark else '#0284c7', width=2.5),
                    marker=dict(size=4)
                ))
                fig_pace.add_trace(go.Scatter(
                    x=preds['laps'],
                    y=preds['predicted_lap_times'],
                    mode='lines',
                    name='Predicted Pace',
                    line=dict(color='#f43f5e' if is_dark else '#e11d48', dash='dash', width=2.5)
                ))
                fig_pace.update_layout(
                    title=dict(text="Tire Degradation Curve", font=dict(color=chart_font_color, size=16, family="Inter")),
                    height=360,
                    margin=dict(l=10, r=10, t=40, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=chart_font_color),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=chart_font_color))
                )
                fig_pace.update_xaxes(title=dict(text="Lap Number", font=dict(color=chart_axis_color)), tickfont=dict(color=chart_axis_color), showgrid=True, gridcolor=chart_grid_color)
                fig_pace.update_yaxes(title=dict(text="Lap Time (s)", font=dict(color=chart_axis_color)), tickfont=dict(color=chart_axis_color), showgrid=True, gridcolor=chart_grid_color)
                st.plotly_chart(fig_pace, use_container_width=True)
                
            with plot_col2:
                fig_pit = go.Figure()
                fig_pit.add_trace(go.Scatter(
                    x=preds['laps'],
                    y=preds['pit_probabilities'],
                    mode='lines',
                    name='Pit Probability',
                    line=dict(color='#f43f5e' if is_dark else '#e11d48', width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(244, 63, 94, 0.2)' if is_dark else 'rgba(225, 29, 72, 0.15)'
                ))
                fig_pit.update_layout(
                    title=dict(text="Pit Stop Probability Window", font=dict(color=chart_font_color, size=16, family="Inter")),
                    height=360,
                    margin=dict(l=10, r=10, t=40, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=chart_font_color),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=chart_font_color))
                )
                fig_pit.update_xaxes(title=dict(text="Lap Number", font=dict(color=chart_axis_color)), tickfont=dict(color=chart_axis_color), showgrid=True, gridcolor=chart_grid_color)
                fig_pit.update_yaxes(title=dict(text="Probability", font=dict(color=chart_axis_color)), tickfont=dict(color=chart_axis_color), showgrid=True, gridcolor=chart_grid_color)
                st.plotly_chart(fig_pit, use_container_width=True)

            # --- UNDERCUT SIMULATOR WITH COMET DIAL ---
            st.markdown("<hr style='border-color: var(--card-border, #1f2937); margin: 2rem 0;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; font-family: monospace; color: var(--text-primary, #f8fafc); letter-spacing: 2px;'>⏱️ UNDERCUT SIMULATOR</h3>", unsafe_allow_html=True)
            sim_col1, sim_col2 = st.columns([1, 1])
            with sim_col1:
                st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                sim_lap_int = int(min(preds['laps'])) + 10
                sim_lap = st.slider("SIMULATE PIT STOP ON LAP:", min_value=int(min(preds['laps'])), max_value=int(max(preds['laps'])), value=sim_lap_int, step=1)
            
            with sim_col2:
                # Find gap at sim_lap
                driver_df = pipeline.data[pipeline.data['Driver'] == selected_driver]
                lap_data = driver_df[driver_df['LapNumber'] == int(sim_lap)]
                
                if not lap_data.empty:
                    gap = lap_data.iloc[0]['Gap_to_Car_Ahead']
                    projected_gap = gap - 22.0 # Pit cost
                    render_comet_dial(projected_gap)
                else:
                    st.warning("No telemetry available for this specific lap.")

with tab2:
    st.markdown("<h3 style='margin-top: 15px;'>⚔️ Cross-Era Head-to-Head Comparison</h3>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        year_A = st.number_input("Year", value=2021, key="yA")
        gp_A = st.text_input("Grand Prix", value="Spain", key="gpA")
        driver_A = st.text_input("Driver Code", value="HAM", key="dA").upper()
    with colB:
        year_B = st.number_input("Year", value=2021, key="yB")
        gp_B = st.text_input("Grand Prix", value="Spain", key="gpB")
        driver_B = st.text_input("Driver Code", value="VER", key="dB").upper()

    @st.cache_data
    def fetch_and_predict(year, gp, driver_id):
        df_raw = fetch_session_data(year, gp)
        if df_raw.empty: return None
        df_feat = engineer_features(df_raw)
        driver_data = df_feat[df_feat['Driver'] == driver_id].copy()
        if driver_data.empty: return None
        
        features_reg = ['Tire_Age', 'Compound_Encoded', 'Track_State', 'Weather_Index', 'Pace_Volatility']
        reg_input = driver_data.dropna(subset=features_reg)
        lap_preds = pipeline.xgb_reg.predict(reg_input[features_reg]).tolist() if not reg_input.empty else []
        return {"laps": driver_data['LapNumber'].dropna().tolist(), "predicted_lap_times": lap_preds}

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("EXECUTE COMPARISON", type="primary"):
        h2h_ph = st.empty()
        h2h_ph.markdown(get_lattice_loader_html("FETCHING HISTORICAL TELEMETRY"), unsafe_allow_html=True)
        
        preds_A = fetch_and_predict(year_A, gp_A, driver_A)
        preds_B = fetch_and_predict(year_B, gp_B, driver_B)
        
        h2h_ph.empty()
        
        if preds_A and preds_B:
            fig_h2h = go.Figure()
            fig_h2h.add_trace(go.Scatter(
                x=preds_A['laps'],
                y=preds_A['predicted_lap_times'],
                mode='lines',
                name=f'{driver_A}',
                line=dict(color='#38bdf8' if is_dark else '#0284c7', width=2.5)
            ))
            fig_h2h.add_trace(go.Scatter(
                x=preds_B['laps'],
                y=preds_B['predicted_lap_times'],
                mode='lines',
                name=f'{driver_B}',
                line=dict(color='#f43f5e' if is_dark else '#e11d48', width=2.5)
            ))
            fig_h2h.update_layout(
                title=dict(text="Pace Degradation Comparison", font=dict(color=chart_font_color, size=16, family="Inter")),
                height=380,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_font_color),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=chart_font_color))
            )
            fig_h2h.update_xaxes(title=dict(text="Lap Number", font=dict(color=chart_axis_color)), tickfont=dict(color=chart_axis_color), showgrid=True, gridcolor=chart_grid_color)
            fig_h2h.update_yaxes(title=dict(text="Predicted Lap Time (s)", font=dict(color=chart_axis_color)), tickfont=dict(color=chart_axis_color), showgrid=True, gridcolor=chart_grid_color)
            st.plotly_chart(fig_h2h, use_container_width=True)
        else:
            st.error("Telemetry unavailable for these parameters.")

