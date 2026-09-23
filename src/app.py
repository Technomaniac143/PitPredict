import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import google.generativeai as genai

# Ensure the root project directory is in the Python path so 'src' can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.pipeline import pipeline_instance
from src.data.ingestion import fetch_session_data
from src.features.engineering import engineer_features

st.set_page_config(page_title="PitPredict | Showcase", layout="wide", page_icon="🏎️")

# --- SIDEBAR & API SETUP ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key (For Race Engineer)", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Key configured!")
    else:
        st.warning("Please enter your Gemini API Key to enable the AI Race Engineer.")

st.title("PitPredict AI Strategy Showcase 🏎️")
st.markdown("Interactive F1 Telemetry & Machine Learning Engine (Running Locally on GPU)")

@st.cache_resource
def get_pipeline():
    if not pipeline_instance.load_models():
        with st.spinner("Training models from scratch on GPU..."):
            pipeline_instance.train([(2021, 'Spain')])
    else:
        if pipeline_instance.data.empty:
            with st.spinner("Loading telemetry data..."):
                df_raw = fetch_session_data(2021, 'Spain')
                pipeline_instance.data = engineer_features(df_raw)
    return pipeline_instance

pipeline = get_pipeline()

# --- TABS ---
tab1, tab2 = st.tabs(["🚦 Strategy Dashboard & Undercut Sim", "⚔️ Cross-Era Head-to-Head"])

with tab1:
    if pipeline.is_trained:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Model Evaluation")
            reg = pipeline.metrics.get('regression', {})
            clf = pipeline.metrics.get('classification', {})
            
            st.metric("Regression (Pace) MAE", f"{reg.get('MAE', 0):.3f}s")
            st.metric("Pit Stop F1 Score", f"{clf.get('F1', 0)*100:.1f}%")
            
            drivers = pipeline.data['Driver'].dropna().unique().tolist()
            drivers = sorted(list(drivers))
            selected_driver = st.selectbox("Select a Driver to Analyze", drivers, index=drivers.index('HAM') if 'HAM' in drivers else 0)

        with col2:
            st.subheader("🤖 AI Race Engineer")
            if not api_key:
                st.info("Provide a Gemini API Key in the sidebar to activate the AI Race Engineer.")
            else:
                if st.button("Ask Race Engineer for Strategy Brief"):
                    with st.spinner("Analyzing telemetry..."):
                        preds = pipeline.predict_for_driver(selected_driver)
                        if preds and len(preds['pit_probabilities']) > 0:
                            avg_pace = sum(preds['actual_lap_times']) / len(preds['actual_lap_times'])
                            max_pit_prob = max(preds['pit_probabilities']) * 100
                            current_tire_age = preds['tire_age'][-1]
                            
                            prompt = f"""
                            You are the chief race engineer for F1 driver {selected_driver}.
                            Here is the live ML telemetry summary:
                            - Average Pace: {avg_pace:.2f} seconds
                            - Highest Pit Stop Probability computed by XGBoost: {max_pit_prob:.1f}%
                            - Current Tire Age: {current_tire_age} laps
                            
                            Provide a very short, punchy (2-3 sentences max) radio message to the driver summarizing their tire state and advising on pit strategy. Speak like a real F1 race engineer.
                            """
                            try:
                                model = genai.GenerativeModel('gemini-1.5-flash')
                                response = model.generate_content(prompt)
                                st.success(f"📻 **Radio:** '{response.text.strip()}'")
                            except Exception as e:
                                st.error(f"Error calling Gemini: {e}")

        if selected_driver:
            preds = pipeline.predict_for_driver(selected_driver)
            st.markdown("---")
            
            # PACE AND PIT PLOTS
            plot_col1, plot_col2 = st.columns(2)
            with plot_col1:
                fig_pace = go.Figure()
                fig_pace.add_trace(go.Scatter(x=preds['laps'], y=preds['actual_lap_times'], mode='lines', name='Actual Pace (s)', line=dict(color='white')))
                fig_pace.add_trace(go.Scatter(x=preds['laps'], y=preds['predicted_lap_times'], mode='lines', name='XGBoost Predicted', line=dict(color='red', dash='dash')))
                fig_pace.update_layout(title="Tire Degradation Curve", xaxis_title="Lap Number", yaxis_title="Lap Time (s)", template="plotly_dark", height=350)
                st.plotly_chart(fig_pace, width='stretch')
                
            with plot_col2:
                fig_pit = px.area(x=preds['laps'], y=preds['pit_probabilities'], title="Pit Stop Probability Window", labels={'x': 'Lap Number', 'y': 'Probability'}, template="plotly_dark", height=350)
                fig_pit.update_traces(line_color='red', fillcolor='rgba(225, 6, 0, 0.3)')
                st.plotly_chart(fig_pit, width='stretch')

            # UNDERCUT SIMULATOR
            st.markdown("### ⏱️ Undercut Simulator")
            st.markdown("Simulate pitting on a specific lap to project your gap delta. (Assumes a 22s pit cost).")
            sim_lap = st.slider("Simulate Pit Stop on Lap:", min_value=min(preds['laps']), max_value=max(preds['laps']), value=min(preds['laps'])+10)
            
            # Find gap at sim_lap
            driver_df = pipeline.data[pipeline.data['Driver'] == selected_driver]
            lap_data = driver_df[driver_df['LapNumber'] == sim_lap]
            
            if not lap_data.empty:
                gap = lap_data.iloc[0]['Gap_to_Car_Ahead']
                projected_gap = gap - 22.0 # Pit cost
                
                if projected_gap > 0:
                    st.success(f"**SUCCESSFUL UNDERCUT!** You will emerge **{projected_gap:.1f}s AHEAD** of your current track position rival.")
                else:
                    st.error(f"**FAILED UNDERCUT!** You will emerge **{abs(projected_gap):.1f}s BEHIND** your current track position rival in dirty air.")
    else:
        st.error("Failed to load or train models.")


with tab2:
    st.markdown("### ⚔️ Cross-Era Head-to-Head Comparison")
    st.markdown("Compare the predicted tire degradation of any two drivers across different years/races.")
    
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Driver A**")
        year_A = st.number_input("Year", value=2021, key="yA")
        gp_A = st.text_input("Grand Prix", value="Spain", key="gpA")
        driver_A = st.text_input("Driver Code (e.g., HAM)", value="HAM", key="dA").upper()
        
    with colB:
        st.markdown("**Driver B**")
        year_B = st.number_input("Year", value=2021, key="yB")
        gp_B = st.text_input("Grand Prix", value="Spain", key="gpB")
        driver_B = st.text_input("Driver Code (e.g., VER)", value="VER", key="dB").upper()

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
        
        return {
            "laps": driver_data['LapNumber'].dropna().tolist(),
            "predicted_lap_times": lap_preds
        }

    if st.button("Compare Head-to-Head"):
        with st.spinner("Fetching historical telemetry and running XGBoost..."):
            preds_A = fetch_and_predict(year_A, gp_A, driver_A)
            preds_B = fetch_and_predict(year_B, gp_B, driver_B)
            
            if preds_A and preds_B:
                fig_h2h = go.Figure()
                fig_h2h.add_trace(go.Scatter(x=preds_A['laps'], y=preds_A['predicted_lap_times'], mode='lines', name=f'{driver_A} ({year_A} {gp_A})', line=dict(color='cyan')))
                fig_h2h.add_trace(go.Scatter(x=preds_B['laps'], y=preds_B['predicted_lap_times'], mode='lines', name=f'{driver_B} ({year_B} {gp_B})', line=dict(color='magenta')))
                fig_h2h.update_layout(title="Predicted Pace Degradation Comparison", xaxis_title="Lap Number", yaxis_title="Predicted Lap Time (s)", template="plotly_dark")
                st.plotly_chart(fig_h2h, width='stretch')
            else:
                st.error("Could not fetch data for one or both drivers. Check the Year, GP, and Driver code.")
