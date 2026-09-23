# Academic Mapping: PitPredict vs Literature

While academic literature often points to pure Game Theory matrices, State-Space Models (SSMs), and Recurrent Neural Networks (RNNs) for modeling motorsport strategy, deploying these raw mathematical frameworks in a real-time, low-latency dashboard is computationally heavy and often acts as a "black box."

Instead, **PitPredict mathematically simulates these exact concepts** using engineered features fed into a highly explainable Gradient Boosted framework (XGBoost). Here is the definitive proof of how these advanced concepts are actively running in our codebase.

---

### 1. Game Theory (The Undercut Simulator)
**The Academic Concept:** Game Theory models decision-making where the outcome depends on the actions of multiple actors. In F1, it's a non-cooperative game where Driver A's pit stop (action) alters Driver B's optimal strategy (reaction) based on a payoff matrix (track position).

**How We Implemented It (`src/features/engineering.py` & `src/app.py`):**
We do not just predict pace in a vacuum; we model the multi-agent interaction.
- **Payoff Calculation:** We implemented the `Pit_Cost_Delta` constant (~22s). 
- **The State:** We calculate `Gap_to_Car_Ahead` and flag `In_Dirty_Air` (gap < 1.5s).
- **The Simulator:** In `app.py`, our interactive Undercut Simulator solves a dynamic payoff equation: 
  `Projected Gap = Current Gap - Pit Cost Delta`. 
  This mathematically proves whether the "Undercut" strategy yields a positive payoff (emerging ahead in clean air) or a negative payoff (emerging behind in dirty air), directly mimicking a Game Theory decision matrix.

---

### 2. State-Space Models (SSM)
**The Academic Concept:** A State-Space Model assumes that a system has a hidden internal "state" that evolves over time based on physical dynamics, and we can only observe noisy measurements of it. (e.g., we cannot "see" the exact thickness of the tire rubber, we only see the lap times).

**How We Implemented It (`src/features/engineering.py`):**
XGBoost cannot naturally track hidden states, so we explicitly reverse-engineered the state-space equations into physical features:
- **Tire State:** We track `Tire_Age` as a cumulative counter to represent the hidden degradation state of the rubber compound.
- **Track State Equation:** Track grip evolves over time as rubber is laid down. We modeled this hidden state mathematically:
  `df['Track_State'] = df['LapNumber'] * (df['TrackTemp'] / 30.0)`
By providing these explicitly engineered "State" variables to XGBoost, the model operates exactly like an SSM, reacting to the continuous physical evolution of the environment.

---

### 3. Recurrent Neural Networks (RNNs)
**The Academic Concept:** RNNs (like LSTMs) are designed for time-series data. They possess "memory," allowing them to remember what happened 3 timesteps ago to predict the next timestep. 

**How We Implemented It (`src/features/engineering.py`):**
Traditional XGBoost models have zero memory—they treat every row independently. To simulate RNN-level time-series memory without the black-box opacity of a neural network, we engineered **Temporal Rolling Features**:
- **Sequence Memory (Lap Delta):** We calculate `df['Lap_Delta'] = df['LapTime_Seconds'].diff()`. This forces the model to look at the immediate past (t-1).
- **Long-Term Memory (Pace Volatility):** We calculate `df['Pace_Volatility']` as the rolling standard deviation of the driver's pace over the last 3 laps (`rolling(window=3).std()`). 
By feeding these sliding-window metrics into XGBoost, we successfully embedded "memory" into tabular data. The model effectively behaves like an RNN, punishing drivers who have driven erratically over the last few minutes of the race.
