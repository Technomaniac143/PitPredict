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

st.set_page_config(page_title="PitPredict | Race Control", layout="wide", page_icon="🏎️", initial_sidebar_state="collapsed")

# Apply Global CSS Overrides
render_gradient_waves()
render_hero()

# --- SIDEBAR & API SETUP ---
with st.sidebar:
    st.title("⚙️ Race Control Settings")
    api_key_input = st.text_input("Gemini API Key (For Race Engineer)", type="password")
    if api_key_input:
        try:
            gemini_client = genai.Client(api_key=api_key_input)
            st.success("API Key configured!")
        except Exception as e:
            gemini_client = None
            st.error("Invalid API Key.")
    else:
        gemini_client = None

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

# We use a custom placeholder for the initial loading so it matches the cinematic vibe
loader_placeholder = st.empty()
if not pipeline_instance.is_trained:
    loader_placeholder.markdown(get_lattice_loader_html("INITIALIZING PIPELINE & CACHE"), unsafe_allow_html=True)

pipeline = get_pipeline()
loader_placeholder.empty()

# --- TABS ---
tab1, tab2 = st.tabs(["🚦 Strategy Dashboard", "⚔️ Cross-Era Head-to-Head"])

with tab1:
    if pipeline.is_trained:
        st.markdown("<h3 style='text-align: center; font-family: monospace; color: #888;'>SELECT DRIVER</h3>", unsafe_allow_html=True)
        
        # Depth Carousel Style Driver Selection
        inject_carousel_css()
        drivers = pipeline.data['Driver'].dropna().unique().tolist()
        drivers = sorted(list(drivers))
        selected_driver = st.radio("Driver", drivers, horizontal=True, index=drivers.index('HAM') if 'HAM' in drivers else 0, label_visibility="collapsed")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # The Run Strategy Cinematic CTA
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("▶ RUN STRATEGY", use_container_width=True, type="primary"):
                st.session_state.strategy_run = True
                
                # Cinematic Sequence Phase 1 & 2
                anim_ph = st.empty()
                play_split_flap(anim_ph)
                anim_ph.markdown(get_lattice_loader_html(f"ANALYZING TELEMETRY FOR {selected_driver}"), unsafe_allow_html=True)
                time.sleep(1.5)
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
            
            # --- RESULTS CARDS ---
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            reg = pipeline.metrics.get('regression', {})
            clf = pipeline.metrics.get('classification', {})
            
            c1.metric("TRACK EVOLUTION", "ACTIVE", "+0.14 grip/lap")
            c2.metric("PACE MODEL MAE", f"{reg.get('MAE', 0):.3f}s", "XGBoost")
            c3.metric("PIT CONFIDENCE", f"{clf.get('F1', 0)*100:.1f}%", "Optimal")

            # --- CHARTS ---
            plot_col1, plot_col2 = st.columns(2)
            with plot_col1:
                fig_pace = go.Figure()
                fig_pace.add_trace(go.Scatter(x=preds['laps'], y=preds['actual_lap_times'], mode='lines', name='Actual Pace', line=dict(color='white')))
                fig_pace.add_trace(go.Scatter(x=preds['laps'], y=preds['predicted_lap_times'], mode='lines', name='Predicted Pace', line=dict(color='#00e5ff', dash='dash')))
                fig_pace.update_layout(title="Tire Degradation Curve", xaxis_title="Lap Number", yaxis_title="Lap Time (s)", template="plotly_dark", height=350, margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pace, width='stretch')
                
            with plot_col2:
                fig_pit = px.area(x=preds['laps'], y=preds['pit_probabilities'], title="Pit Stop Probability Window", template="plotly_dark", height=350)
                fig_pit.update_traces(line_color='#ff2800', fillcolor='rgba(255, 40, 0, 0.3)')
                fig_pit.update_layout(margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pit, width='stretch')

            # --- UNDERCUT SIMULATOR WITH COMET DIAL ---
            st.markdown("---")
            st.markdown("<h3 style='text-align: center; font-family: monospace;'>⏱️ UNDERCUT SIMULATOR</h3>", unsafe_allow_html=True)
            sim_col1, sim_col2 = st.columns([1, 1])
            with sim_col1:
                st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
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
    st.markdown("### ⚔️ Cross-Era Head-to-Head Comparison")
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

    if st.button("EXECUTE COMPARISON", type="primary"):
        h2h_ph = st.empty()
        h2h_ph.markdown(get_lattice_loader_html("FETCHING HISTORICAL TELEMETRY"), unsafe_allow_html=True)
        
        preds_A = fetch_and_predict(year_A, gp_A, driver_A)
        preds_B = fetch_and_predict(year_B, gp_B, driver_B)
        
        h2h_ph.empty()
        
        if preds_A and preds_B:
            fig_h2h = go.Figure()
            fig_h2h.add_trace(go.Scatter(x=preds_A['laps'], y=preds_A['predicted_lap_times'], mode='lines', name=f'{driver_A}', line=dict(color='#00e5ff')))
            fig_h2h.add_trace(go.Scatter(x=preds_B['laps'], y=preds_B['predicted_lap_times'], mode='lines', name=f'{driver_B}', line=dict(color='#ff2800')))
            fig_h2h.update_layout(title="Pace Degradation Comparison", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_h2h, width='stretch')
        else:
            st.error("Telemetry unavailable for these parameters.")
