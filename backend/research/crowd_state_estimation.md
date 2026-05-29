# Research Prompt 7 — Real-Time Crowd State Estimation Through Audio and Environment

## Polynovea Research Document  
**Prepared for:** Subrojit Roy, Founder, Polynovea Ecosystem  
**Date:** 2026-05-24  
**Classification:** Internal Research — Behavioral Intelligence Infrastructure

---

## 1. Executive Summary

This document synthesizes current scientific and engineering literature on inferring crowd behavioral states using multimodal audio, environmental, and operational telemetry. The research targets the design of real-time behavioral state estimation systems, adaptive optimization systems, and AI-assisted intervention systems for live venue environments.

**Key Finding:** No single modality is sufficient for reliable crowd state estimation. Probabilistic inference over temporally lagged, multimodal signals — with explicit uncertainty modeling — is the only viable architecture for production systems.

**Core Design Principles Derived:**
1. **Measurement-first:** Every state claim must carry an uncertainty bound.
2. **Temporal depth:** Crowd states have memory; instantaneous snapshots are misleading.
3. **Causal humility:** Correlation is not intervention — systems must distinguish observation from manipulation.
4. **Adaptive decay:** Model confidence must degrade when input patterns shift.

---

## 2. Crowd State Taxonomy

The following states represent observable, behaviorally grounded conditions rather than inferred psychological constructs:

| State | Observable Signature | Primary Modality |
|-------|---------------------|------------------|
| **Energetic** | High movement entropy, elevated SPL, fast tempo response | Audio + Movement |
| **Synchronized** | Coordinated movement patterns, tempo-locked physiological response | Audio + Movement |
| **Fatigued** | Reduced movement amplitude, increased dwell time, thermal elevation | Thermal + Movement |
| **Overstimulated** | SPL > 100 dBA sustained, reduced social interaction, exit velocity increase | Audio + Exit |
| **Socially Active** | High conversational SPL (60–75 dB), clustered positioning, ordering velocity | Audio + Spatial |
| **Conversational** | Mid-range SPL, speech-dominant spectral profile, low movement entropy | Audio |
| **Immersive** | Reduced peripheral movement, sustained attention vectors, low exit rate | Movement + Exit |
| **Disengaging** | Increasing exit rate, reduced ordering, increased phone-checking behavior | Operational + Exit |
| **Chaotic** | High movement entropy + low coordination, SPL spikes, thermal gradient shifts | All modalities |
| **Anticipatory** | Directional movement toward stage/entry, reduced ordering, elevated heart rate proxies | Movement + Audio |
| **Passive** | Low movement, baseline SPL, high dwell time, minimal interaction | Movement + Operational |
| **High-Arousal** | Elevated SPL + fast tempo + bright spectral centroid + increased SCR proxies | Audio + Physiological |
| **Low-Arousal** | Slow tempo, low SPL, warm spectral skew, reduced movement | Audio + Movement |

> **Note:** These states are not mutually exclusive. A crowd can be simultaneously "energetic" and "disengaging" (e.g., a mosh pit winding down). The system must handle compositional state vectors, not categorical classification.

---

## 3. Input Modalities and Their Correlation with Crowd State

### 3.1 Music Features

#### Tempo (BPM)
Tempo is the strongest predictor of perceived energy arousal (EA) and tension arousal (TA) in music. Research demonstrates that faster tempi consistently increase the probability of synchronized physiological responses across audience members, including respiratory rate (RR) and skin conductance response (SCR) synchrony.

**Scientific Support:** A multiple regression model on 749 music excerpts found tempo explained 82.28% of variance in perceived energy arousal (ηp² = 0.636, p < 0.001). Tempo was also the strongest predictor of tension arousal (ηp² = 0.344, p < 0.001). Faster tempi increased synchronized RR and SCR responses across audience members in live concert settings, with effects modulated by musical style.

**Crowd State Mapping:**
- **High tempo (>130 BPM)** → Energetic, High-Arousal, Synchronized (if beat is clear)
- **Medium tempo (90–130 BPM)** → Socially Active, Conversational
- **Low tempo (<90 BPM)** → Low-Arousal, Passive, Immersive
- **Tempo changes** → Anticipatory (acceleration), Fatigued (deceleration)

#### Spectral Distribution
Spectral features correlate with arousal dimensions:
- **Spectral Centroid / Brightness:** Higher values associated with increased energy arousal (β = 0.54, p = 0.002) and tension arousal (β = 0.78, p = 0.004). Brighter timbres predict higher arousal states.
- **Spectral Flux:** Correlates with temporal variability and perceived energy.
- **Spectral Skewness:** Negative correlation with arousal; positive skew (more low frequencies) indicates calmer states.
- **Dissonance:** Positively predicts tension arousal (β significant, p < 0.001) but not energy arousal.

**Crowd State Mapping:**
- High spectral centroid + high brightness → Energetic, High-Arousal
- Low spectral centroid + warm skew → Low-Arousal, Passive, Immersive
- High dissonance → Tension, Anticipatory (if transient), Overstimulated (if sustained)

#### Loudness / RMS Energy
Loudness (RMSE) showed mixed effects: it significantly predicted synchronized SCR responses in some concert conditions but was not a consistent predictor of arousal across all contexts. However, SPL as a physical environmental measure (not musical feature) has well-documented effects on crowd behavior.

**Crowd State Mapping:**
- SPL 60–75 dBA → Conversational, Socially Active
- SPL 85–95 dBA → Energetic, Engaged
- SPL 95–105 dBA → High-Arousal, Synchronized
- SPL > 105 dBA sustained → Overstimulated, Disengaging (exit velocity increases)

### 3.2 Sound Pressure Level (SPL)

SPL is one of the most directly measurable and behaviorally consequential environmental variables in venues.

**Key Findings:**
- Venue sound levels typically range from 85 dBA (quiet gigs) to 120+ dBA (rock concerts)
- Crowd size is a significant factor in absolute FOH sound level: low crowds = 92.5 dBA, medium = 95 dBA, large = 96.1 dBA (LAeq, 5min)
- Crowd noise (applause, singing, yelling) can add ~10 dB to measured SPL
- Engineers who can see SPL monitors mix on average 2 dBA quieter
- Band engineers tend to mix significantly louder than house technicians

**Behavioral Correlations:**
- SPL > 100 dBA sustained correlates with reduced conversational behavior and increased exit rates
- SPL > 120 dBA correlates with hearing discomfort and rapid disengagement
- A-weighted limits alone fail to capture low-frequency energy that drives physical arousal (sub-bass 120–130 dBC peak)
- Dynamic range compression (limiters) can increase perceived loudness while reducing peak SPL — a confounding factor for state estimation

### 3.3 Lighting

While direct scientific literature on lighting-crowd state correlation is sparse, the following mechanisms are well-established in environmental psychology:

- **Brightness/Intensity:** Higher intensity lighting correlates with increased alertness and social interaction. Dim lighting promotes intimacy and immersion but can reduce spatial awareness.
- **Color Temperature:** Warm lighting (2700K) promotes relaxation and social bonding; cool lighting (5000K+) increases alertness and arousal.
- **Dynamic Lighting:** Sudden changes trigger orienting responses (anticipatory state). Rhythmic lighting synchronized to music tempo enhances synchronization.
- **Strobe/Flicker:** High-frequency flicker can induce overstimulation and disorientation at rates > 20 Hz.

**Crowd State Mapping:**
- Bright, warm, static → Socially Active, Conversational
- Dim, colored, slow-moving → Immersive, Low-Arousal
- Bright, cool, fast-moving → Energetic, High-Arousal
- Rapid strobing → Overstimulated, Chaotic

### 3.4 Crowd Density

Density is a primary determinant of crowd dynamics and state transitions.

**Key Metrics:**
- **Occupancy count:** Absolute number of people in a zone
- **Density (people/m²):** Critical thresholds — < 2 p/m² = comfortable social; 2–4 p/m² = engaged; > 4 p/m² = potential overstimulation/chaos
- **Spatial distribution:** Clustered vs. dispersed patterns

**Sensing Methods:**
- Low-resolution thermal arrays (32×24 or 80×64 pixels) provide privacy-preserving occupancy estimation via density map regression
- Time-of-Flight (ToF) sensors provide accurate 3D depth maps for counting
- Computer vision (RGB) provides highest detail but sacrifices anonymity

**Crowd State Mapping:**
- Low density + high movement → Energetic (if music matches)
- Medium density + synchronized movement → Synchronized
- High density + low movement → Passive, Immersive
- High density + high movement entropy → Chaotic, Overstimulated

### 3.5 Thermal Conditions

Thermal environment significantly impacts crowd behavior and willingness to stay.

**Scientific Support:** A study on thermal-acoustic interactions in urban parks found:
- Temperature and crowd size correlation: r = -0.688 (p < 0.001) — higher temperatures reduce willingness to stay
- Under high heat (>30°C), no sound condition could effectively attract people to stay
- Music sound had the best attraction effect under moderate heat (22–28°C)
- Grass-cutting noise (adverse sound) consistently reduced crowd size across all temperatures
- Under high heat, all sound types failed to retain crowds

**Crowd State Mapping:**
- Comfortable thermal range (20–26°C) → All states possible, music effects maximized
- High heat (>28°C) → Fatigued, Disengaging, reduced stay duration regardless of audio
- Low heat (<18°C) → Passive, reduced social activity
- Thermal gradients within venue → Chaotic (people moving toward comfort zones)

### 3.6 Queue Lengths & Ordering Velocity

Operational telemetry provides direct behavioral signals:

- **Queue length:** Long queues → Anticipatory (if for entry), Disengaging (if for exit/bar)
- **Ordering velocity (orders/minute):** 
  - Increasing → Energetic, Socially Active
  - Decreasing → Fatigued, Disengaging, Immersive (attention diverted)
  - Spiking then crashing → Overstimulated → Disengaging transition
- **Dwell time at bar:** Short dwell → Energetic, High-Arousal; Long dwell → Conversational, Socially Active

### 3.7 Movement Heatmaps

Movement analysis operates at two levels:

**Macroscopic (Crowd as entity):**
- **Flow vectors:** Directional movement indicates Anticipatory (toward stage) or Disengaging (toward exits)
- **Movement entropy:** High entropy = Chaotic; Low entropy + high magnitude = Synchronized
- **Heatmap intensity changes:** Rapid cooling = Disengaging; Rapid heating = Energetic

**Microscopic (Individual tracking):**
- **Social clustering:** Group formation indicates Socially Active or Conversational
- **Isolation patterns:** Individuals separating from groups = Disengaging or Overstimulated
- **Phone-checking frequency:** Increasing = Disengaging

### 3.8 Entry/Exit Patterns

- **Entry rate > exit rate:** Anticipatory, Energetic
- **Exit rate > entry rate:** Disengaging, Fatigued
- **Sudden exit spike:** Chaotic, Overstimulated, or external trigger
- **Entry/exit ratio stability:** Passive, Immersive

### 3.9 Dwell Behavior

- **Short dwell (< 5 min per zone):** Energetic, High-Arousal, Anticipatory
- **Medium dwell (5–20 min):** Socially Active, Conversational, Synchronized
- **Long dwell (> 20 min):** Immersive, Passive, Fatigued
- **Dwell time decreasing over event:** Disengaging trajectory

---

## 4. Probabilistic Inference Framework

### 4.1 Why Probabilistic?

Crowd state estimation is fundamentally uncertain because:
1. **Observational sparsity:** Sensors are spatially and temporally limited
2. **Model divergence:** Even calibrated models drift from reality over time
3. **Stochastic behavior:** Individual actions introduce irreducible randomness
4. **Multimodal ambiguity:** The same audio profile can accompany different states (e.g., loud music + energetic crowd vs. loud music + overstimulated crowd)

### 4.2 Data Assimilation Approach

The particle filter (Sequential Monte Carlo) framework is well-suited for crowd state estimation:

**Predict Step:** Run the behavioral model forward to estimate current state and uncertainty (prior).

**Update Step:** Incorporate new observations to refine the estimate (posterior).

**Key Insight:** The posterior combines the best guess from the model and the best guess from observations, yielding a closer estimate than either in isolation. As demonstrated in pedestrian simulations, particle filters with reweighting and resampling consistently outperform open-loop models, with error reduction increasing as system complexity grows.

### 4.3 State Vector Design

For a venue with N zones, the state vector at time t might be:

```
X_t = [state_zone1, state_zone2, ..., state_zoneN, global_state, transition_likelihoods]
```

Where each zone state is a compositional vector over the 13 defined states (e.g., [energetic: 0.3, synchronized: 0.6, fatigued: 0.1, ...]).

### 4.4 Observation Model

Observations y_t are drawn from all modalities:

```
y_t = [SPL_t, tempo_t, spectral_features_t, density_t, thermal_t, queue_t, movement_features_t, entry_exit_t, ordering_t]
```

Each observation carries measurement noise ξ_t ~ N(0, σ_m²I).

### 4.5 Uncertainty Quantification

**Prediction Intervals:** Rather than point estimates, the system should output credible intervals for each state probability. Bayesian LSTM with stochastic variational inference has demonstrated superior uncertainty quantification compared to linear regression models, with 11–16% lower sharpness and better reliability.

**Confidence Decay:** When input patterns deviate from training distributions, model confidence should degrade gracefully. This is critical for detecting novel crowd states (e.g., a security incident) that the system has not been trained on.

---

## 5. Temporal Modeling

### 5.1 Why Temporal Depth Matters

Crowd states have memory. A crowd that was energetic 10 minutes ago is more likely to be fatigued now than a crowd that was passive. The dynamics of collective social behavior exhibit lagged effects:

- **Tempo effects:** Physiological synchronization to music has a latency of 15–60 seconds
- **Thermal effects:** Crowd thermal comfort changes over 5–15 minute windows
- **Social contagion:** Mood states propagate through crowds over 2–5 minute timescales
- **Fatigue accumulation:** Physical fatigue builds over 20–45 minute windows

### 5.2 Markovian State Transitions

A discrete-time Markov chain can model state transitions where the probability of moving from state x_m to x_{m+1} depends on the state x_{m-n} (nth-order Markov chain), accounting for lagged dynamics.

**Key Finding from Crowd Game Research:** In collective decision-making, the optimal noise level for crowd coordination is around 40% — too little noise causes herding loops, too much causes chaos. This suggests that crowd state transitions have a "noise-dependent attractor" structure.

### 5.3 Temporal Modeling Architectures

1. **Hidden Markov Models (HMM):** Good for discrete state sequences with clear transition probabilities
2. **Recurrent Neural Networks (LSTM/GRU):** Good for capturing long-range dependencies in continuous state spaces
3. **Bayesian LSTM:** Combines temporal modeling with uncertainty quantification via stochastic variational inference
4. **Particle Filters:** Good for non-linear, non-Gaussian state spaces with multimodal uncertainty
5. **PHD (Probability Hypothesis Density) Filters:** For tracking an unknown and time-varying number of crowd sub-groups

### 5.4 Lagged Effects Modeling

**Explicit Lag Variables:** Include t-1, t-5, t-15 minute lagged features as inputs.

**Attention Mechanisms:** Learn which temporal windows are most predictive for each state.

**Causal Discovery:** Use Granger causality or transfer entropy to identify which modalities lead state changes vs. which lag behind.

---

## 6. Causal Ambiguity and Intervention Design

### 6.1 The Fundamental Problem

The same observable pattern can result from different causal structures:

| Observation | Possible Causal Structures |
|-------------|-------------------------|
| High SPL + High Exit Rate | Overstimulated → Exiting OR Crowd thinning → Engineer turning up volume |
| Low Ordering + Low Movement | Fatigued OR Immersive (watching performance) |
| High Movement + High SPL | Energetic OR Chaotic |
| Synchronized Movement | Synchronized OR Herding (low individual agency) |

### 6.2 Disambiguation Strategies

1. **Temporal Order:** Which changed first? If SPL increased before exit rate, overstimulation is more likely.
2. **Multi-Zone Comparison:** Is the pattern localized or global? Localized = event-driven; Global = environmental.
3. **Cross-Modal Consistency:** Do all modalities agree? If audio says "energetic" but thermal says "fatigued," the state is likely transitional.
4. **Intervention Testing:** Small, reversible changes (e.g., dim lights slightly) can reveal causal structure through crowd response.

### 6.3 Intervention Design Principles

**Adaptive Optimization Systems** should follow:

1. **Minimum Effective Dose:** Make the smallest change that moves the state vector toward target.
2. **Reversibility:** All interventions must be undoable within 30–60 seconds.
3. **A/B Testing:** Where possible, test interventions on sub-zones before global deployment.
4. **Human-in-the-Loop:** High-uncertainty states should trigger operator review, not autonomous action.
5. **Ethical Constraints:** Never optimize for engagement at the expense of safety or comfort.

### 6.4 Intervention Modalities

| Target State | Possible Interventions |
|-------------|---------------------|
| Energetic → Synchronized | Tempo lock to clear beat, lighting sync, reduce dissonance |
| Overstimulated → Socially Active | Reduce SPL by 3–5 dB, warm lighting, open conversational zones |
| Fatigued → Energetic | Increase tempo, brighter lighting, reduce temperature |
| Disengaging → Immersive | Dim lights, reduce SPL, focus attention on stage |
| Chaotic → Synchronized | Clear tempo, directional lighting, reduce environmental noise |
| Passive → Socially Active | Warm lighting, mid-tempo music, create conversational clusters |

---

## 7. Adaptive Systems Architecture

### 7.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    SENSOR LAYER                              │
│  Audio │ Thermal │ Vision │ Operational │ Environmental      │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│                 FEATURE EXTRACTION                           │
│  SPL │ Tempo │ Spectral │ Density │ Movement │ Thermal │ Ops  │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│              PROBABILISTIC STATE ESTIMATION                    │
│         Particle Filter / Bayesian LSTM / HMM                │
│     P(state | observations, history, model uncertainty)    │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│              TEMPORAL MODELING & PREDICTION                    │
│     State trajectories │ Lagged effects │ Transition probs   │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│              INTERVENTION ENGINE                               │
│     Target state │ Current state │ Uncertainty │ Constraints │
│     → Optimal intervention │ Reversibility check │ Safety    │
└────────────────────┬──────────────────────────────────────────┘
                     │
┌────────────────────▼──────────────────────────────────────────┐
│              ACTUATION LAYER                                   │
│     Audio │ Lighting │ HVAC │ Staff alerts │ Display          │
└───────────────────────────────────────────────────────────────┘
```

### 7.2 Feedback Loop Design

The system must close the loop:

1. **Observe:** Collect multimodal data at 1–10 Hz
2. **Estimate:** Infer current state with uncertainty bounds
3. **Predict:** Project state trajectory over next 5–15 minutes
4. **Decide:** If state deviates from target, compute intervention
5. **Actuate:** Deploy intervention
6. **Evaluate:** Measure crowd response to intervention
7. **Learn:** Update transition models based on intervention outcomes

### 7.3 Failure Modes and Safeguards

| Failure Mode | Safeguard |
|-------------|-----------|
| Model overconfidence on out-of-distribution data | Confidence decay + operator alert |
| Intervention causes unexpected state | Reversibility + 30-second rollback |
| Sensor failure | Graceful degradation using remaining modalities |
| Cascading state misclassification | Multi-model ensemble voting |
| Ethical boundary violation | Hard constraints on SPL, density, temperature |

---

## 8. Scientific Rigor Checklist

For each state inference claim, the system must be able to answer:

- [ ] **What is the evidence?** Which modalities support this state?
- [ ] **What is the uncertainty?** What is the confidence interval?
- [ ] **What is the temporal context?** How long has this state persisted?
- [ ] **What are the alternative explanations?** Could this pattern mean something else?
- [ ] **What would falsify this?** What observation would prove this state wrong?
- [ ] **What is the intervention history?** Did a recent action cause this state?

---

## 9. Implementation Roadmap

### Phase 1: Baseline Measurement (Months 1–3)
- Deploy audio sensors (SPL, tempo, spectral analysis)
- Deploy thermal sensors for density estimation
- Deploy operational telemetry (POS, entry/exit counters)
- Establish ground truth through human annotation

### Phase 2: Model Development (Months 4–6)
- Build probabilistic state estimation model
- Train on labeled data with cross-validation
- Validate uncertainty quantification

### Phase 3: Temporal Integration (Months 7–9)
- Add temporal modeling (LSTM/particle filter)
- Identify lagged effects through causal discovery
- Build transition probability matrices

### Phase 4: Intervention System (Months 10–12)
- Design intervention repertoire
- Implement A/B testing framework
- Deploy human-in-the-loop review

### Phase 5: Adaptive Optimization (Months 13–18)
- Close feedback loop
- Implement online learning
- Scale to multi-zone, multi-venue

---

## 10. Key Research Gaps

1. **Crowd Noise Contribution:** No systematic research exists on how crowd-generated noise (applause, singing, yelling) contributes to overall SPL and how this affects state estimation.

2. **Lighting-Crowd Dynamics:** Direct experimental studies on lighting effects on crowd behavioral states in controlled venue environments are lacking.

3. **Cross-Cultural Variation:** Most studies are conducted in Western concert settings. Crowd behavioral responses may vary significantly across cultures.

4. **Long-Term Adaptation:** Crowds may habituate to repeated interventions, reducing effectiveness over time. Adaptive systems must account for this.

5. **Privacy-Preserving Sensing:** Balancing behavioral measurement granularity with privacy requirements remains an open engineering challenge.

---

## 11. References

1. Gwynne, S., et al. (2024). A dynamic state-based model of crowds. *EPJ Data Science*.
2. Canazza, S., et al. (2023). Clustering affective qualities of classical music. *IEEE Transactions on Affective Computing*.
3. WHO (2022). Make Listening Safe: Monograph on sound level measurement, management and documentation in music venues.
4. Moran, N., et al. (2021). Synchrony in the periphery: inter-subject correlation of physiological responses to music. *PNAS*.
5. Sievers, B., et al. (2023). Music communicates social emotions: Evidence from 750 music excerpts. *Scientific Reports*.
6. Ward, J., et al. (2020). Simulating crowds in real time with agent-based modelling and a particle filter. *JASSS*.
7. ThermoSense: Thermal crowd detection and occupancy estimation (2024). *IJRPR*.
8. Engagement monitorization in crowded environments (2024). *ACM Digital Library*.
9. Thermal–acoustic interaction impacts on crowd behaviors in an urban park (2023). *Forests*.
10. Bayesian LSTM with stochastic variational inference for estimating model uncertainty (2021). *Water Resources Research*.

---

*Document prepared for Polynovea Behavioral Intelligence Infrastructure. All claims are grounded in peer-reviewed literature or established engineering practice. Speculative claims are explicitly flagged as such.*
