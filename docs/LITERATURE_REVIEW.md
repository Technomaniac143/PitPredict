# Literature Review: Machine Learning in Formula 1 Strategy

Formula 1 is a highly data-driven sport, but academic literature on race strategy—specifically tire degradation and pit stop optimization—has only recently started incorporating advanced Machine Learning (ML) techniques. This document reviews the foundational research and explains how **PitPredict** innovates beyond the current state-of-the-art.

## 1. Foundational Research

### A. Pit Stop Optimization via Game Theory
A cornerstone in F1 strategic modeling is the work by **Aguad and Thraves (2022)**, *"Optimizing Pit Stop Strategies in Formula 1 with Dynamic Programming and Game Theory."* They model pit stops as a feedback Stackelberg game.
- **Key Insight:** Pit decisions cannot be made in isolation. The concept of the "undercut" (pitting earlier to gain a tire advantage and jump a competitor) requires modeling the actions of rival cars.
- **Limitation:** While theoretically robust, Game Theory models often rely on deterministic pace degradation assumptions rather than real-time stochastic telemetry.

### B. State-Space Tire Degradation
Recent research focuses on treating tire wear as a latent (hidden) variable. Papers like *"A State-Space Approach to Modeling Tire Degradation in Formula 1 Racing"* model degradation as an unobservable state that decays non-linearly.
- **Key Insight:** Tire life is not just a function of laps completed. It depends on compound (`Soft`, `Medium`, `Hard`), track temperature, and traffic (clean air vs. dirty air).
- **Limitation:** These models are computationally heavy and usually evaluated retrospectively on historical datasets, lacking real-time inference capabilities.

### C. Recurrent Neural Networks (RNNs) for Strategy Simulation
*"AutoF1: An RNN-Based Approach to Simulating Strategic Decision-Making"* uses sequence models to predict the probability of a pit stop given the sequence of past laps.
- **Key Insight:** RNNs capture the temporal dependencies of a race (e.g., a sudden drop in pace over 3 laps is a stronger pit signal than a gradual drop over 15 laps).
- **Limitation:** RNNs operate as black boxes, making it difficult for race engineers to trust the model's recommendation without explainability (e.g., feature importance).

---

## 2. The PitPredict Innovation

PitPredict addresses the limitations of existing research by combining predictive accuracy with **explainability** and **accessibility**. 

### A. Explainable Boosting (XGBoost + SHAP)
Instead of black-box RNNs, PitPredict utilizes **Gradient Boosted Decision Trees (XGBoost)**. XGBoost provides state-of-the-art tabular data performance and natively supports SHAP (SHapley Additive exPlanations) values. This allows us to explain *why* the model recommends a pit stop (e.g., "Tire Age is 18 laps (40% importance), and Gap to Car Ahead is dropping (25% importance)").

### B. Feature Engineering over Pure Deep Learning
We heavily engineer domain-specific features rather than expecting deep learning to infer them:
- **Track Evolution Index:** Accounting for rubber laying down on the track.
- **Traffic Window (Gap_to_Car_Ahead):** Simulating the Stackelberg game theory undercut scenario dynamically.
- **Weather Index:** Modifying base degradation rates.

### C. Democratization of F1 Analytics
The most significant innovation of PitPredict is its **Real-Life Impact**. 
Currently, tools that integrate telemetry, tire degradation models, and pit stop classification are proprietary, costing F1 teams millions to develop and maintain. PitPredict democratizes this technology:
- **Engineering Students:** Can study applied data science and telemetry processing.
- **Motorsport Analysts & Journalists:** Can quantify race narratives (e.g., "Did Ferrari pit too early?") with data rather than intuition.
- **Fans:** Can interact with live race simulations, bridging the gap between spectator and strategist.

By leveraging the public **FastF1 API**, PitPredict takes academic theories out of journals and puts an interactive, explainable "pit wall" into the hands of the public.
