# PSYCHOACOUSTIC FOUNDATIONS FOR BEHAVIORAL ENVIRONMENT SYSTEMS

## Research Document v1.0 — Operational Intelligence Layer
**Prepared for:** Polynovea Behavioral Intelligence Infrastructure  
**Classification:** Scientific synthesis for ML/behavioral model integration  
**Confidence mandate:** Mechanism-first; no unsupported phenomenological claims

---

## DOCUMENT STRUCTURE & INTEGRATION PROTOCOL

This document is organized for direct ingestion into:
- **Machine learning feature engineering pipelines** (acoustic → behavioral predictors)
- **Causal inference frameworks** (sound parameter → physiological/psychological outcome)
- **Operational optimization systems** (real-time venue acoustic tuning)
- **Behavioral measurement models** (quantified human response functions)

Each section follows a standardized output schema:
1. **Scientific Explanation** — Mechanism description
2. **Mechanism of Perception** — Neurophysiological pathway
3. **Known Measurable Variables** — Quantified parameters with units
4. **Known Physiological Effects** — Body-level responses
5. **Known Psychological Effects** — Cognitive/affective responses
6. **Time-Dependent Effects** — Temporal dynamics
7. **Environmental Dependencies** — Context moderators
8. **Hospitality/Live-Event Relevance** — Operational translation
9. **Commercial Implications** — Revenue/behavioral outcome linkage
10. **Reliability/Confidence of Evidence** — Certainty grading (A–D)

---

## 1. HUMAN FREQUENCY SENSITIVITY

### Scientific Explanation
The human auditory system does not respond uniformly across the frequency spectrum. Sensitivity peaks between **2–5 kHz** and declines toward both low and high extremes. This non-linearity is quantified by equal-loudness contours (isophonic curves), standardized in **ISO 226:2023**, which map sound pressure level (dB SPL) to perceived loudness (phon) across frequencies.

The original Fletcher-Munson curves (1933) were revised by Robinson-Dadson (1956) and subsequently by the international ISO 226:2003/2023 standards based on multi-laboratory data from Japan, Germany, Denmark, and the United States.

### Mechanism of Perception
- **Basilar membrane tonotopy:** Hair cells at the cochlear base respond to high frequencies; apex responds to low frequencies.
- **Mechanical advantage of the ossicular chain:** Middle-ear transmission efficiency varies with frequency, boosting mid-range energy delivery to the cochlea.
- **Neural phase-locking:** Temporal coding precision degrades above ~4–5 kHz, forcing a transition from temporal to place coding.

### Known Measurable Variables
| Variable | Unit | Operational Range | Measurement Method |
|----------|------|-------------------|-------------------|
| Hearing threshold | dB SPL | 0–20 dB (1–4 kHz); ~60 dB (20 Hz) | Pure-tone audiometry |
| Equal-loudness level | phon | 0–90 phon per ISO 226 | Matching paradigm |
| Frequency discrimination | Hz/cent | ~0.2% of center frequency (Weber fraction) | 2AFC frequency discrimination |
| Critical bandwidth | Hz | ~1/3 octave (ERB scale: 24.7 + 0.108f) | Notched-noise masking |

### Known Physiological Effects
- **Otoacoustic emission amplitude** varies with frequency, peaking in the mid-range.
- **Cochlear amplifier gain** (outer hair cell motility) is frequency-dependent, with metabolic demand scaling inversely with sensitivity.
- **High-frequency vulnerability:** Outer hair cells at the cochlear base (high-frequency region) are more susceptible to acoustic trauma due to higher metabolic demand and mechanical stress.

### Known Psychological Effects
- **Perceived "presence" or "air"** in sound reproduction correlates with extended high-frequency response (>12 kHz), though audibility thresholds rise sharply above 15 kHz in adults.
- **Localization precision** degrades below ~1 kHz (ITD-dominated) and above ~4 kHz (ILD-dominated), creating a "blur zone" in the 1–4 kHz range where both cues are weak.

### Time-Dependent Effects
- **Temporary threshold shift (TTS)** manifests most prominently at 3–6 kHz regardless of exposure frequency, due to ear canal resonance and cochlear vulnerability patterns.
- **Presbycusis:** Age-related high-frequency threshold elevation progresses at ~1 dB/year above 4 kHz after age 60.

### Environmental Dependencies
- **Ambient temperature:** Cochlear blood flow affects metabolic capacity and thus temporary susceptibility.
- **Altitude:** Middle-ear pressure equalization dysfunction can alter low-frequency transmission.
- **Background noise:** Elevated ambient levels mask the audibility of low- and high-frequency signals disproportionately.

### Hospitality/Live-Event Relevance
- **Venue equalization** must compensate for reduced low-frequency human sensitivity: a 30 Hz tone requires ~20 dB more SPL than a 1 kHz tone to achieve equal perceived loudness at low monitoring levels.
- **Speech intelligibility optimization** concentrates energy in the 2–4 kHz region where the ear is most efficient, reducing required SPL and minimizing fatigue.

### Commercial Implications
- **Mis-calibrated bass response** in hospitality venues leads to compensatory volume increases that accelerate patron fatigue and shorten dwell time.
- **High-frequency extension** in live PA systems improves perceived "clarity" and "definition" at lower overall SPL, reducing TTS risk.

### Reliability/Confidence of Evidence
- **Grade A (High):** ISO 226:2023 is empirically robust across multiple populations. Contour shapes are stable; spacing between contours is well-validated.
- **Contradictions:** Some critiques note mathematical inconsistencies in ISO 226:2003 formulation, though the 2023 revision addressed notation issues.

---

## 2. LOUDNESS PERCEPTION

### Scientific Explanation
Loudness is the subjective magnitude of auditory sensation. It scales nonlinearly with physical intensity according to **Stevens' power law**: L = k(I – I₀)^α, where α ≈ 0.3 for a 1 kHz tone (intensity exponent), or equivalently ~0.6 for sound pressure.

The **sone** scale provides a ratio scale where 1 sone = 40 phon, and loudness doubles every 10 phon. The **phon** scale is an equal-loudness contour reference: N phon = loudness level of a 1 kHz tone at N dB SPL.

### Mechanism of Perception
- **Rate–place integration:** Loudness is computed by the central auditory system from the summed neural activity across auditory nerve fibers, weighted by critical band rate (specific loudness).
- **Compression at the periphery:** The cochlear amplifier provides ~40 dB of gain at threshold, compressing as input level rises, producing the nonlinear loudness growth function.
- **Binaural summation:** Binaural presentation increases loudness by ~3–6 dB equivalent (binaural loudness summation).

### Known Measurable Variables
| Variable | Unit | Notes |
|----------|------|-------|
| Loudness level | phon | dB SPL of equally loud 1 kHz tone |
| Loudness | sone | Ratio scale; 1 sone = 40 phon |
| Stevens' exponent | dimensionless | 0.25–0.33 depending on method/methodology |
| Specific loudness | sone/Bark | Loudness per critical band |

### Known Physiological Effects
- **Stapedial reflex:** Activates at ~85 dB SPL, providing ~15 dB attenuation; latency 25–150 ms.
- **Cochlear blood flow reduction:** Vasoconstriction at high SPL reduces outer hair cell oxygenation.
- **Metabolic load:** Outer hair cell motility (prestin-mediated) increases energy demand proportionally with SPL.

### Known Psychological Effects
- **Perceived "impact" or "punch"** correlates with short-term loudness peaks (LAFmax) more than equivalent continuous level (Leq).
- **Annoyance** scales non-monotonically with loudness, showing sharp inflection above 65–70 dB(A) in residential contexts.

### Time-Dependent Effects
- **Temporal integration:** The ear integrates energy over ~100–200 ms (time constant of loudness). Impulses shorter than this require higher peak SPL for equal loudness.
- **Loudness adaptation:** Continuous steady tones show ~10–20% loudness reduction over 2–3 minutes; highly variable across individuals.

### Environmental Dependencies
- **Reverberation:** Increases effective loudness through energy accumulation, particularly for continuous sources.
- **Spectral content:** Broadband noise sounds louder than pure tones of equal SPL due to multi-band summation.
- **Visual context:** Visual cues can modulate loudness perception by ±3 dB equivalent (cross-modal effect).

### Hospitality/Live-Event Relevance
- **Leq monitoring alone is insufficient:** Peak loudness (LAFmax) drives perceived "energy" and patron arousal; Leq drives fatigue.
- **Dose-response for TTS:** OSHA uses 85 dBA Leq for 8 hr; live events often exceed 95–105 dBA, creating TTS in <15 minutes.

### Commercial Implications
- **Loudness optimization curve:** Venues operating at 82–86 dBA Leq maximize perceived energy while minimizing post-visit TTS and negative word-of-mouth.
- **Dynamic range compression** in PA systems increases loudness perception without increasing peak SPL—a cost-efficient energy strategy.

### Reliability/Confidence of Evidence
- **Grade A:** Stevens' power law and ISO 226 are foundational. The exponent 0.3 at 1 kHz is confirmed across doubling/halving, magnitude estimation, and multi-tone methods.
- **Unresolved debate:** Whether the loudness function should use intensity exponent 0.3 (additivity-based) or 0.27 (magnitude estimation, corrected for number assignment bias). ISO 226:2003 used 0.25; 2023 revision uses 0.3. Difference produces <0.6 dB contour deviation.

---

## 3. TEMPORAL AUDITORY PROCESSING

### Scientific Explanation
Temporal processing refers to the auditory system's capacity to resolve, sequence, and encode acoustic events in time. It encompasses **temporal resolution** (minimum discriminable gap), **temporal integration** (energy summation over time), **temporal masking** (forward and backward), and **temporal fine structure** (TFS) processing.

Gap detection thresholds in normal-hearing adults typically range from **2–3 ms** for broadband noise, with longer thresholds for narrowband signals.

### Mechanism of Perception
- **Peripheral temporal coding:** For frequencies below ~4–5 kHz, neural firing phase-locks to the stimulus waveform (TFS coding). Above this, only envelope periodicities are encoded.
- **Central integration:** The auditory cortex integrates peripheral timing information; gap detection relies on cortical detection of cessation/return of neural activity.
- **Forward masking:** Neural adaptation and recovery cycles in the auditory nerve elevate thresholds for signals following maskers.

### Known Measurable Variables
| Variable | Unit | Typical Value | Clinical Test |
|----------|------|---------------|---------------|
| Gap detection threshold | ms | 2–5 ms (broadband); 10–20 ms (narrowband) | Gaps-in-Noise (GIN) test |
| Forward masking recovery rate | dB/ms | ~0.5–2 dB/ms | Masked threshold vs. delay |
| Backward masking threshold | dB | Elevated 10–30 dB at 0 ms ISI | Backward masking test |
| Temporal modulation transfer | dB | Peak ~4–16 Hz modulation freq | TMTF psychophysics |

### Known Physiological Effects
- **Age-related slowing:** Older adults (>60 yrs) with normal audiograms show slower recovery from forward masking, indicating degraded central temporal resolution independent of peripheral hearing loss.
- **Cortical resource allocation:** Degraded temporal cues require greater cortical processing effort, measurable via EEG/MEG latency increases.

### Known Psychological Effects
- **Speech-in-noise deficits:** Poor temporal resolution predicts difficulty understanding speech in reverberant or noisy environments even when pure-tone thresholds are normal.
- **Rhythm perception:** Temporal acuity sets the lower bound for beat and meter extraction in musical contexts.

### Time-Dependent Effects
- **Short-term fatigue:** Temporal resolution degrades measurably after 2–4 hours of continuous noise exposure >85 dBA.
- **Recovery:** Forward masking effects decay within 50–200 ms in young adults; older adults show residual masking at 500+ ms.

### Environmental Dependencies
- **Reverberation:** Long reverberation times (>1.0 s) smear temporal cues, effectively reducing temporal resolution by 30–50%.
- **Noise type:** Modulated noise (e.g., HVAC, traffic) produces greater temporal masking than steady noise.

### Hospitality/Live-Event Relevance
- **PA system transient response:** Poorly aligned speaker arrays smear temporal cues through multi-path interference, degrading speech intelligibility even when frequency response is flat.
- **DJ transition timing:** Human temporal resolution limits create a "perceptual window" of ~5–10 ms for seamless beat-matching; deviations beyond this register as "sloppy."

### Commercial Implications
- **Temporal fidelity as a luxury signal:** High-end venues with precise time-alignment (sub-5 ms inter-speaker delay) produce perceptible "tightness" that justifies premium pricing.
- **Aging patron base:** Venues serving demographics >50 yrs must reduce reverberation and increase SNR by 3–6 dB to compensate for temporal processing degradation.

### Reliability/Confidence of Evidence
- **Grade A:** Gap detection and forward masking are well-established paradigms. GIN test is clinically validated.
- **Grade B:** Backward masking is more variable and less clinically standardized; results depend heavily on paradigm design.

---

## 4. AUDITORY MASKING

### Scientific Explanation
Auditory masking occurs when the presence of one sound (masker) elevates the detection threshold of another (target). Two distinct mechanisms operate:
- **Energetic masking:** Target energy is swamped by masker energy within the same critical band(s).
- **Informational masking:** Target and masker are perceptually similar (e.g., same voice), causing central confusion even when peripheral SNR is favorable.

### Mechanism of Perception
- **Critical band filtering:** The cochlea analyzes sound through ~24 overlapping critical bands (Bark scale). Masking is maximal when target and masker occupy the same critical band.
- **Suppression:** Nonlinear cochlear mechanics suppress weaker signals in the presence of stronger ones within the same frequency region.
- **Central interference:** Informational masking occurs at cortical levels when target and masker engage the same neural representations (e.g., phonemic, speaker identity).

### Known Measurable Variables
| Variable | Unit | Notes |
|----------|------|-------|
| Masking level difference (MLD) | dB | Binaural release from masking; typically 6–15 dB |
| Critical bandwidth | Hz | ERB = 24.7 + 0.108f |
| Informational masking magnitude | dB | Can exceed energetic masking by 20+ dB |
| Simultaneous masking slope | dB/dB | ~0.5–1.0 (near 0 dB at threshold) |

### Known Physiological Effects
- **Cochlear compression:** The active process reduces gain in masked frequency regions, protecting but also desensitizing those channels.
- **Effort-related autonomic response:** Informational masking (e.g., competing talkers) elevates pupil dilation and skin conductance more than energetic masking at equivalent SNR.

### Known Psychological Effects
- **Speech reception threshold (SRT):** The SNR required for 50% intelligibility; typically −6 dB for normal hearing in steady noise, but +5 dB or worse in competing speech.
- **Cognitive fatigue:** Prolonged exposure to informational masking depletes working memory resources.

### Time-Dependent Effects
- **Forward masking:** Persists for 50–200 ms post-masker.
- **Backward masking:** Persists for 20–100 ms; greater in older adults.
- **Central masking:** Can persist for seconds in complex multi-talker environments.

### Environmental Dependencies
- **Reverberation:** Increases effective masking by filling temporal gaps with reflected energy.
- **Spatial separation:** Reduces masking through head shadow and binaural unmasking (see Section 5).

### Hospitality/Live-Event Relevance
- **Cocktail party problem:** In hospitality environments, patrons attempt to segregate target speech from competing talkers. Informational masking dominates when talker density exceeds 2–3 voices within critical distance.
- **Music-on-hold / background music:** Masker-target similarity determines whether background music aids (energetic masking of chatter) or hinders (informational masking of lyrics) communication.

### Commercial Implications
- **Masking system design:** Pink noise or shaped HVAC noise can provide 3–6 dB of energetic masking for speech privacy in hotels/restaurants, but must be spectrally distinct from music to avoid informational masking.
- **Table spacing:** Physical separation reduces informational masking more than equivalent SNR improvement via noise reduction.

### Reliability/Confidence of Evidence
- **Grade A:** Energetic masking is fully modeled (power spectrum model, excitation patterns).
- **Grade B:** Informational masking is less quantitatively predictable; models exist but require context-specific calibration.

---

## 5. SPATIAL HEARING

### Scientific Explanation
Spatial hearing enables sound source localization and segregation using binaural cues:
- **Interaural Time Differences (ITDs):** Dominant below ~1.5 kHz; derived from phase-locked neural firing comparing onset times at the two ears. Maximum useful ITD ~0.6 ms.
- **Interaural Level Differences (ILDs):** Dominant above ~4 kHz; created by acoustic head shadow (~3–15 dB depending on azimuth and frequency).
- **Head-Related Transfer Functions (HRTFs):** Spectral filtering by pinna, head, and torso provides elevation and front/back cues.

### Mechanism of Perception
- **Medial Superior Olive (MSO):** Computes ITDs via coincidence detection of bilateral inputs.
- **Lateral Superior Olive (LSO):** Computes ILDs via excitatory/inhibitory interactions.
- **Auditory cortex:** Integrates binaural cues with spectral and temporal information to form spatial percepts. Cortical IPD (interaural phase difference) responses predict spatial release from masking (SRM) performance.

### Known Measurable Variables
| Variable | Unit | Typical Value |
|----------|------|---------------|
| Minimum audible angle (MAA) | degrees | 1–3° (frontal, 1 kHz); 5–10° (vertical) |
| Spatial release from masking (SRM) | dB | 6–10 dB for speech-on-speech (normal hearing) |
| ITD sensitivity threshold | μs | ~10–30 μs (best at 750–1000 Hz) |
| ILD sensitivity threshold | dB | ~0.5–1 dB |

### Known Physiological Effects
- **Head shadow:** Physical attenuation of contralateral ear by ~3 dB at 500 Hz, increasing to ~15 dB at 6 kHz.
- **Binaural unmasking:** Neural computation of interaural differences provides SNR improvement beyond better-ear listening alone.

### Known Psychological Effects
- **Cocktail party advantage:** Spatial separation of target from maskers improves speech intelligibility primarily through SRM.
- **Spatial acuity degradation:** Older adults show poorer MAA, particularly in adverse SNR conditions, independent of audiometric thresholds.

### Time-Dependent Effects
- **Binaural sluggishness:** The binaural system integrates cues over ~20–100 ms, making it less effective for very brief or rapidly moving sources.
- **Adaptation:** Prolonged exposure to reverberant environments reduces reliance on ITD cues as they become unreliable.

### Environmental Dependencies
- **Reverberation:** Reduces interaural coherence, degrading ITD-based localization and SRM. Effects are more severe for hearing-impaired and cochlear implant users.
- **Room geometry:** Early reflections (<50 ms) support the precedence effect; late reflections (>100 ms) degrade spatial perception.
- **Distance:** Beyond ~1 m in reverberant rooms, distance cues (direct-to-reverberant ratio) dominate over binaural cues.

### Hospitality/Live-Event Relevance
- **Stage design:** Performer placement at ±15–30° azimuth maximizes audience SRM against ambient chatter.
- **Seating geometry:** Circular or shallow-fan arrangements maintain better ITD/ILD cue integrity than deep narrow rooms.
- **PA delay towers:** Misalignment >5 ms between primary and delayed arrays creates precedence effect breakdown and localization confusion.

### Commercial Implications
- **Immersive audio (Dolby Atmos, L-ISA):** Object-based spatial audio systems can artificially enhance SRM by rendering competing sources to distinct spatial positions, effectively increasing perceived SNR by 3–8 dB.
- **VIP seating:** Zones with optimal direct-field-to-reverberant ratio (>6 dB) command premium pricing due to improved intelligibility and reduced listening effort.

### Reliability/Confidence of Evidence
- **Grade A:** Binaural cue physiology (ITD/ILD) is established across mammalian neurophysiology and human psychophysics.
- **Grade A:** SRM of 6–10 dB is robustly replicated across dozens of studies.
- **Unresolved debate:** Relative contributions of better-ear listening vs. true binaural interaction in SRM remain debated; estimates vary from 50/50 to 70/30 depending on masker type.

---

## 6. AUDITORY SCENE ANALYSIS

### Scientific Explanation
Auditory Scene Analysis (ASA), formalized by Bregman (1990), describes how the auditory system segregates incoming sound into perceptual "streams" corresponding to distinct environmental sources. The system uses **primitive (bottom-up)** cues (proximity in frequency, time, space, timbre) and **schema-based (top-down)** cues (learned patterns, linguistic knowledge, attention).

### Mechanism of Perception
- **Frequency co-modulation:** Components with correlated amplitude or frequency fluctuations are grouped.
- **Common fate:** Sounds with synchronous onsets/offsets are grouped.
- **Harmonicity:** Components sharing a common fundamental frequency (F0) are fused into a single percept.
- **Spatial separation:** Binaural disparity promotes segregation.
- **Attentional stream selection:** Top-down attention can "track" a target stream while suppressing others (cocktail party effect).

### Known Measurable Variables
| Variable | Unit | Measurement |
|----------|------|-------------|
| Streaming threshold | Hz/semitone | Frequency separation required for perceptual fission |
| Temporal coherence limit | ms | Onset asynchrony tolerance for fusion (~30–50 ms) |
| F0 discrimination | % | ~0.5–2% for complex tones |
| Attentional modulation | dB | ~3–6 dB "attentional gain" in neural responses |

### Known Physiological Effects
- **Cortical entrainment:** EEG shows phase-locking to attended streams at ~4–8 Hz (theta), with suppression of unattended streams.
- **Pupil dilation:** Increases with scene complexity (number of competing sources).

### Known Psychological Effects
- **Informational masking:** Poor scene analysis leads to target-masker confusion.
- **Musical streaming:** Melodic lines segregate when frequency separation exceeds ~2–3 semitones and tempo is moderate.
- **Speech segregation:** Requires harmonicity, spatial cues, and temporal envelope coherence.

### Time-Dependent Effects
- **Build-up of streaming:** Requires 2–10 seconds of alternating patterns for stable perceptual fission.
- **Switching cost:** Shifting attention between streams costs 200–500 ms in reaction time.

### Environmental Dependencies
- **Reverberation:** Smears temporal cues (onset synchrony), reducing primitive grouping efficacy.
- **Noise:** Energetic masking can obliterate fine structure cues needed for harmonicity-based grouping.
- **Visual input:** Lip-reading and speaker location provide top-down constraints that improve scene analysis by 20–40%.

### Hospitality/Live-Event Relevance
- **Multi-zone audio:** Successful ASA requires that each zone's primary source maintains spectrotemporal coherence; competing zones with overlapping spectra cause central confusion.
- **Live band mixing:** Instruments sharing harmonic series (e.g., guitar and keyboard at same pitch) fuse unless spatially or temporally separated.

### Commercial Implications
- **Acoustic zoning:** Physical or DSP-based separation of frequency content by zone reduces ASA conflict, improving perceived clarity without SPL increases.
- **Speech privacy:** Privacy index (PI) depends on ASA failure—when background speech is just intelligible enough to engage linguistic processing but not enough for comprehension, annoyance peaks.

### Reliability/Confidence of Evidence
- **Grade A:** Primitive grouping cues (frequency, time, space) are robustly demonstrated.
- **Grade B:** Top-down/schema-based ASA is less quantitatively specified; individual differences are large.

---

## 7. SPECTRAL ROUGHNESS

### Scientific Explanation
Spectral roughness (or dissonance) is the perceived "roughness" or "harshness" evoked by simultaneous tones with frequency separations near the critical bandwidth. It arises from **rapid amplitude fluctuations (beating)** at the difference frequency between partials, which modulate the auditory nerve firing pattern at rates too fast to be resolved temporally but too slow to be fused spectrally—typically **~20–200 Hz modulation rates** produce maximum roughness.

The foundational model by **Plomp and Levelt (1965)** established that maximum dissonance occurs when two pure tones are separated by ~0.25–0.5 critical bandwidths.

### Mechanism of Perception
- **Peripheral interaction:** When two tones fall within the same critical band, the basilar membrane cannot resolve them spatially; the resulting envelope fluctuation drives the auditory nerve at the beat frequency.
- **Central modulation coding:** The cochlear nucleus and inferior colliculus encode amplitude modulation rates; roughness correlates with modulation depths in the 30–150 Hz range.
- **Tonalness opposition:** High roughness reduces the perceived "tonalness" or pitch clarity of a sonority.

### Known Measurable Variables
| Variable | Unit | Formula/Range |
|----------|------|---------------|
| Roughness (R) | asper | 1 asper = roughness of 1 kHz tone, 100% modulated at 70 Hz, 60 dB |
| Critical bandwidth ratio | z (Bark) | Maximum roughness at Δf ≈ 0.25–0.5 ERB |
| Modulation frequency | Hz | Peak roughness ~70 Hz (Daniel-Weber model) |
| Dyad roughness | arbitrary | Sum of partial-partial interactions weighted by amplitude |

### Known Physiological Effects
- **Autonomic arousal:** High roughness correlates with increased skin conductance and heart rate variability reduction.
- **Startle response modulation:** Rough sounds potentiate acoustic startle reflex amplitude.

### Known Psychological Effects
- **Tension/unease:** Roughness is a primary predictor of perceived "tension" in music and sound design.
- **Annoyance:** Roughness contributes to noise annoyance independent of loudness.

### Time-Dependent Effects
- **Adaptation:** Roughness perception adapts partially over 5–10 seconds of continuous exposure.
- **Contextual modulation:** Roughness is perceived as more tolerable when expected (e.g., in certain musical genres).

### Environmental Dependencies
- **SPL:** Roughness scales with level; doubling SPL increases roughness by ~1.5–2×.
- **Room acoustics:** Reverberation smears temporal envelope, reducing perceived roughness of transient sounds.

### Hospitality/Live-Event Relevance
- **DJ mixing:** Beat-matched tracks with clashing harmonics produce roughness in the 2–6 kHz range that registers as "clashing" or "unprofessional."
- **HVAC noise:** Fan blade tones with sidebands create roughness that elevates annoyance despite low overall SPL.

### Commercial Implications
- **Roughness as a "quality gate":** Automated roughness metering (e.g., based on Daniel-Weber or Vassilakis models) can flag acoustic environments or mixes that will trigger negative affect before human complaint.
- **Tension-release architecture:** Venues can modulate roughness through sound design to drive arousal curves (high roughness = tension; low roughness = resolution).

### Reliability/Confidence of Evidence
- **Grade A:** Plomp-Levelt curves are replicated extensively. Critical bandwidth-based roughness is well-validated.
- **Grade B:** Absolute roughness scales (asper) vary across models (Daniel-Weber vs. Vassilakis vs. Hutchinson-Knopoff). Inter-model correlations are moderate (r ~0.7–0.8).
- **Contradictions:** Some studies suggest roughness is culturally conditioned in musical contexts, challenging the "purely sensory" claim.

---

## 8. HARMONIC CONSONANCE/DISSONANCE

### Scientific Explanation
Consonance/dissonance is a multidimensional construct comprising:
1. **Sensory consonance** (absence of roughness + high tonalness + low sharpness)
2. **Harmonicity** (alignment of partials with harmonic series)
3. **Pitch commonality** (shared virtual pitch/root)

Helmholtz (1877) attributed dissonance to beating of upper partials; Terhardt's virtual pitch theory added cognitive harmonic template matching.

### Mechanism of Perception
- **Harmonic template matching:** The auditory system expects partials at integer multiples of F0; deviations produce "inharmonicity" perception.
- **Virtual pitch:** The brain infers a missing fundamental from the harmonic pattern; chords sharing virtual pitch roots are perceived as more "related."
- **Roughness integration:** Sensory dissonance is largely explained by integrated roughness across all partial pairs (Hutchinson-Knopoff model).

### Known Measurable Variables
| Variable | Unit | Measurement |
|----------|------|-------------|
| Sensory dissonance | arbitrary | Roughness + inharmonicity index |
| Harmonicity | ratio | Energy in harmonic vs. inharmonic partials |
| Pitch commonality | % | Shared virtual pitch strength (Parncutt model) |
| Root relationship | categorical | Terhardt's virtual pitch theory |

### Known Physiological Effects
- **Pleasantness rating:** Correlates negatively with sensory dissonance (r ~−0.6 to −0.8).
- **Autonomic balance:** Consonant music tends to increase HRV (parasympathetic); dissonant music increases sympathetic tone.

### Known Psychological Effects
- **Emotional valence:** Consonance broadly maps to "positive/resolved"; dissonance to "negative/tense"—though this is modulated strongly by cultural schema and musical context.
- **Memory:** Consonant intervals are recognized more reliably than dissonant intervals in short-term memory tasks.

### Time-Dependent Effects
- **Habituation:** Dissonance tolerance increases with repeated exposure within a single session (10–15 minutes).
- **Chronic exposure:** Long-term exposure to highly dissonant environments shows no evidence of permanent threshold or preference shift.

### Environmental Dependencies
- **Timbre:** Dissonance is most salient for tones with rich harmonic content (e.g., brass, strings); less salient for noise-like or pure tones.
- **Register:** Dissonance increases with register due to narrower critical bandwidths at high frequencies (more partial interactions).

### Hospitality/Live-Event Relevance
- **Background music selection:** Tracks with high pitch commonality and low roughness produce lower cognitive load and longer dwell times.
- **DJ harmonic mixing:** Mixing in key (e.g., Camelot wheel) maximizes pitch commonality and minimizes sensory dissonance during transitions.

### Commercial Implications
- **Consonance as a retention variable:** Retail and hospitality environments using consonant background music show 5–15% longer dwell times in controlled studies (though effect sizes vary and publication bias may exist).
- **Brand alignment:** "Dissonant" sound design can signal edginess/modernity for specific demographics, but carries fatigue risk.

### Reliability/Confidence of Evidence
- **Grade A:** Sensory consonance (roughness-based) is mechanistically sound.
- **Grade C:** Cultural/schematic contributions to consonance are significant but poorly quantified. The "universal consonance" claim is disputed; equal-temperament Western consonance does not generalize to all musical systems.
- **Unresolved debate:** Whether consonance preference is innate (acoustic) or learned (cultural template). Evidence supports both with interaction effects.

---

## 9. PERCEIVED WARMTH / BRIGHTNESS / HARSHNESS

### Scientific Explanation
These are primary **timbre dimensions** derived from multidimensional scaling (MDS) of dissimilarity ratings. They map to spectral energy distribution:
- **Warmth:** Correlates with low-frequency energy concentration (<500 Hz) and spectral centroid <1 kHz.
- **Brightness:** Correlates with spectral centroid and high-frequency energy ratio (>4 kHz).
- **Harshness:** Correlates with spectral irregularity, high-frequency roughness, and sharpness (Zwicker's sharpness model: high-frequency weighted loudness).

### Mechanism of Perception
- **Spectral centroid extraction:** The auditory system computes a "center of gravity" of the spectrum, which strongly predicts brightness.
- **Sharpness:** Zwicker's model weights specific loudness in Bark bands by a factor increasing with critical band rate; unit is acum.
- **Roughness integration:** Harshness combines sharpness with spectral roughness in the 2–8 kHz region.

### Known Measurable Variables
| Variable | Unit | Formula |
|----------|------|---------|
| Spectral centroid | Hz | Σ(f × A(f)) / ΣA(f) |
| Sharpness | acum | Zwicker model; 1 acum = sharpness of 1 kHz band at 60 dB |
| Spectral irregularity | dB | Deviation from smoothed spectral envelope |
| High-frequency ratio | % | Energy >4 kHz / total energy |

### Known Physiological Effects
- **Startle response:** Bright/harsh sounds produce larger startle reflexes than warm sounds at equal loudness.
- **Cortisol:** Harshness in noise contexts correlates with stress hormone elevation.

### Known Psychological Effects
- **Affective valence:** Warmth correlates with positive affect; harshness with negative affect and urgency.
- **Perceived proximity:** Bright sounds are localized as closer; warm sounds as more distant (learned association with atmospheric absorption).

### Time-Dependent Effects
- **Adaptation:** Brightness perception adapts rapidly (~2–5 seconds) to a new spectral balance; warmth perception adapts more slowly.
- **Fatigue-induced shift:** After high-SPL exposure, high-frequency sensitivity drops, making bright sounds seem less bright (but also making warm sounds seem muffled).

### Environmental Dependencies
- **Room absorption:** High-frequency absorption reduces brightness; low-frequency absorption reduces warmth.
- **Air absorption:** At distances >10 m, high-frequency attenuation (~0.1 dB/m at 8 kHz) reduces brightness naturally.

### Hospitality/Live-Event Relevance
- **Lounge vs. club EQ:** Lounge environments optimized for warmth (boost <250 Hz, gentle high-frequency roll-off); clubs optimized for brightness/punch (boost 2–5 kHz transient energy).
- **Microphone proximity effect:** Vocal warmth is enhanced by proximity effect (bass boost <200 Hz at <15 cm), a tool used intentionally by performers.

### Commercial Implications
- **EQ-based mood steering:** Real-time spectral centroid adjustment can shift perceived "energy" of a space without changing SPL, manipulating dwell time and drink purchase velocity.
- **Harshness as an exit cue:** Increasing harshness/brightness ratio is an operationally effective (if unsubtle) method to encourage patron departure during closing.

### Reliability/Confidence of Evidence
- **Grade A:** Spectral centroid → brightness is one of the strongest predictors in timbre research (r > 0.9).
- **Grade B:** Sharpness and harshness models are well-developed but less universally adopted than loudness models.
- **Grade C:** "Warmth" has no standardized metric; operationalization varies across audio engineering and psychoacoustics.

---

## 10. LOW-FREQUENCY PHYSIOLOGICAL EFFECTS

### Scientific Explanation
Frequencies below ~20 Hz (infrasound) and low-frequency noise (20–200 Hz) produce physiological effects that bypass conscious auditory perception. Infrasound is not "heard" in the traditional sense but is detected by the somatosensory system and vestibular apparatus, triggering stress responses.

### Mechanism of Perception
- **Vestibular activation:** The otolithic organs (saccule, utricle) respond to infrasound as low-frequency vibration, not sound.
- **Somatosensory detection:** Pacinian corpuscles and other mechanoreceptors in skin and viscera detect infrasound-induced vibration.
- **HPA axis activation:** Subcortical stress pathways respond to infrasound as an environmental threat signal, elevating cortisol.

### Known Measurable Variables
| Variable | Unit | Operational Range |
|----------|------|-------------------|
| Infrasound frequency | Hz | 1–20 Hz (below conventional hearing) |
| Infrasound level | dB | 75–100 dB (measured with G-weighting) |
| Salivary cortisol | nmol/L | Elevations of 15–30% reported at 75–78 dB, 18 Hz |
| Heart rate variability | ms RMSSD | Reduction under infrasound exposure |

### Known Physiological Effects
- **Cortisol elevation:** 18 Hz infrasound at 75–78 dB produced significant salivary cortisol increases in blinded participants who could not detect the stimulus.
- **Blood pressure reduction:** Infrasound just above threshold correlates with reduced systolic/diastolic pressure and pulse—physiological patterns associated with drowsiness.
- **Sleep architecture disruption:** Low-frequency noise (20–160 Hz) correlates with increased nighttime cortisol and impaired sleep quality.

### Known Psychological Effects
- **Negative affect:** Increased irritability, disinterest, and sadness appraisal without conscious awareness of the stimulus.
- **"Haunted" phenomenology:** Infrasound in old buildings (ventilation, pipes) produces agitation and anxiety frequently misattributed to supernatural causes.
- **Aversive responding:** Zebrafish and human data suggest infrasound may be an evolutionarily conserved aversive signal.

### Time-Dependent Effects
- **Acute exposure:** Cortisol elevation detectable within 20 minutes.
- **Chronic exposure:** Epidemiological data suggest long-term low-frequency noise exposure correlates with chronic cortisol elevation and circadian rhythm disruption.

### Environmental Dependencies
- **Source proximity:** Infrasound from HVAC, traffic, and industrial machinery is ubiquitous in basements and urban interiors.
- **Building resonance:** Structures amplify specific low-frequency modes, creating "hot spots" of high infrasound intensity.
- **Weather:** Wind and atmospheric pressure gradients generate natural infrasound.

### Hospitality/Live-Event Relevance
- **Subwoofer deployment:** Live events use 30–80 Hz energy for "physical" bass impact. While audible low frequencies are pleasurable, infrasound (<20 Hz) from poorly designed subwoofer arrays or HVAC can trigger subliminal stress.
- **Venue location:** Basements and industrial conversions carry elevated infrasound risk from mechanical systems.

### Commercial Implications
- **Invisible liability:** Infrasound-induced cortisol elevation degrades customer experience without generating conscious complaints, making it an unmeasured revenue leak.
- **Measurement gap:** Standard dB(A) weighting completely filters infrasound; venues must use G-weighting or linear measurement below 20 Hz.
- **Mitigation:** Vibration isolation of HVAC and structural decoupling of subwoofer installations reduce infrasound transmission.

### Reliability/Confidence of Evidence
- **Grade B:** Infrasound-cortisol link is replicated but sample sizes are modest (n=36 in key study).
- **Grade C:** Epidemiological links between chronic low-frequency noise and health outcomes are suggestive but confounded by socioeconomic and other environmental variables.
- **Contradictions:** Early infrasound research (1960s–1980s) contained methodological flaws; modern studies with proper controls show more modest but consistent effects.

---

## 11. AUDITORY FATIGUE

### Scientific Explanation
Auditory fatigue is a temporary or permanent reduction in hearing sensitivity after sound exposure. It manifests as **Temporary Threshold Shift (TTS)**—reversible within minutes to days—or **Permanent Threshold Shift (PTS)**—irreversible cochlear damage. TTS is the auditory system's acute stress signal; repeated TTS without adequate recovery evolves into PTS.

### Mechanism of Perception
- **Metabolic exhaustion:** Outer hair cell (OHC) motility via prestin requires ATP. High-level exposure depletes metabolic reserves.
- **Reactive oxygen species (ROS):** Excessive mechanical vibration generates ROS that damage OHCs and supporting cells.
- **Synaptopathy ("hidden hearing loss"):** Noise can destroy ribbon synapses between IHCs and auditory nerve fibers without elevating audiometric thresholds, causing deficits in temporal processing and noise discrimination.

### Known Measurable Variables
| Variable | Unit | Typical Values |
|----------|------|--------------|
| TTS magnitude | dB | 10–40 dB immediately post-exposure |
| Recovery time | min/hr | 2 min–48 hr (TTS <20 dB usually recovers in 48 hr) |
| PTS onset threshold | dB | TTS >40 dB often leaves residual PTS |
| Noise notch frequency | Hz | 3–6 kHz (clinical hallmark of NIHL) |

### Known Physiological Effects
- **Hair cell damage:** Outer hair cells at the cochlear base (high-frequency region) are most vulnerable.
- **Vasoconstriction:** Loud noise triggers blood vessel constriction in the cochlea, reducing oxygen delivery.
- **Tinnitus:** TTS is frequently accompanied by temporary tinnitus; persistent tinnitus signals synaptic or hair cell damage.

### Known Psychological Effects
- **Communication deficits:** TTS in the 3–6 kHz region degrades consonant discrimination, reducing speech intelligibility.
- **Cognitive performance decline:** Workers in high-noise environments show measurable declines in sustained attention, working memory, and reaction time by end of shift.

### Time-Dependent Effects
- **Immediate:** TTS peaks immediately post-exposure.
- **Short-term recovery:** 50% of TTS recovers within 30 seconds; significant recovery in first 15 minutes.
- **Long-term recovery:** TTS <20 dB: 24–48 hours; TTS 30 dB: 3–6 days; TTS >40 dB: may never fully recover.
- **Critical recovery window:** Minimum 16 hours of quiet between high-noise shifts is required for TTS resolution.

### Environmental Dependencies
- **Exposure level:** 85 dBA for 8 hr is OSHA action level; 95 dBA causes TTS in <1 hour.
- **Exposure intermittency:** Interrupted noise causes less TTS than continuous noise of same total energy.
- **Individual susceptibility:** Varies by genotype, prior exposure history, diabetes, smoking, and cardiovascular health.

### Hospitality/Live-Event Relevance
- **Patron TTS:** Live music at 95–105 dBA produces TTS in 15–30 minutes; patrons leave with degraded hearing, reducing post-venue socialization quality and next-day satisfaction.
- **Staff exposure:** Bartenders and security in loud venues accumulate occupational noise dose; TTS accumulation degrades service quality and increases error rates.

### Commercial Implications
- **TTS as a hidden cost:** Patrons experiencing TTS show reduced return intention and negative word-of-mouth.
- **Recovery-driven scheduling:** Venues operating multiple nights should monitor cumulative staff exposure; rotating staff across loud/quiet zones reduces chronic TTS risk.
- **Monitoring:** Personal noise dosimeters for staff and periodic audiometric screening detect TTS trends before PTS develops.

### Reliability/Confidence of Evidence
- **Grade A:** TTS/PTS mechanisms are validated across animal and human studies.
- **Grade A:** Noise notch at 3–6 kHz is a clinical hallmark with high diagnostic specificity.
- **Unresolved debate:** The TTS-to-PTS progression is accepted in principle, but the exact dose-response curve for individual susceptibility remains stochastic rather than deterministic.

---

## 12. SENSORY OVERLOAD

### Scientific Explanation
Sensory overload occurs when the total sensory input to the nervous system exceeds processing capacity. In auditory contexts, it is driven by high SPL, high informational complexity (many simultaneous sources), spatial ambiguity, and cross-modal competition (visual + auditory + tactile). The construct overlaps with **informational masking** and **cognitive load**, but emphasizes the **multisensory integration failure** that occurs at extreme input levels.

### Mechanism of Perception
- **Central resource depletion:** Kahneman's limited-capacity model posits a finite pool of attentional resources; sensory overload exhausts this pool.
- **Multisensory integration breakdown:** Superior temporal sulcus and prefrontal regions fail to bind coherent percepts when input rates exceed ~5–7 Hz for discrete events.
- **HPA axis activation:** Overload triggers stress hormone release, further degrading prefrontal executive function.

### Known Measurable Variables
| Variable | Unit | Threshold/Range |
|----------|------|-----------------|
| Sensory overload threshold | subjective | Varies; typically >85 dBA + 3+ competing sources |
| Pupil dilation | mm | >0.5 mm increase from baseline under overload |
| Skin conductance | μS | Elevated sympathetic response |
| Error rate | % | Increases 2–5× under overload vs. baseline |

### Known Physiological Effects
- **Cortisol and adrenaline elevation:** Sympathetic activation under sustained overload.
- **Pupil dilation:** Objective marker of noradrenergic locus coeruleus activation.
- **Motor slowing:** Reaction times increase by 15–30% under overload conditions.

### Known Psychological Effects
- **Cognitive narrowing:** Attentional field constricts to focus on single dominant stimuli, ignoring peripheral information.
- **Affective dysregulation:** Irritability, anxiety, and desire to escape increase monotonically with overload severity.
- **Decision paralysis:** Choice complexity combined with high noise reduces decision quality and speed.

### Time-Dependent Effects
- **Onset:** Subjective overload typically reported after 10–20 minutes of exposure.
- **Escalation:** Effects compound non-linearly; second hour in overloaded environment produces disproportionately greater impairment than first hour.
- **Recovery:** Requires removal from stimulus environment; partial recovery in 15–30 minutes of quiet.

### Environmental Dependencies
- **Perceived control:** Environments where patrons can modulate their exposure (headphones, quiet zones) show higher overload tolerance.
- **Visual clutter:** Overload threshold drops when visual environment is also complex.
- **Social density:** Crowding reduces overload tolerance by 20–30% at equivalent SPL.

### Hospitality/Live-Event Relevance
- **Peak-hour venues:** Restaurants and bars at 100% capacity with music >85 dBA create overload conditions that shorten visits and reduce per-capita spend.
- **Escape behavior:** Overloaded patrons seek physical exit or "zone out" (phone engagement), reducing social interaction and ancillary purchases.

### Commercial Implications
- **Overload as a throughput mechanism:** Some high-volume venues intentionally induce brief overload to maximize table turnover, but this is a burn-rate strategy with long-term brand cost.
- **Zoning as revenue protection:** Quiet zones, outdoor spaces, or acoustic refuges extend dwell time and increase total spend in multi-zone venues.

### Reliability/Confidence of Evidence
- **Grade B:** Sensory overload is well-described in disability/autism literature and occupational psychology, but less precisely quantified in general hospitality populations.
- **Grade C:** Thresholds are highly individual; operational generalizations require demographic calibration.

---

## 13. COGNITIVE LOAD FROM SOUND

### Scientific Explanation
Cognitive load from sound refers to the working memory and executive function resources consumed by auditory processing, particularly under degraded listening conditions. The **Ease of Language Understanding (ELU) model** and related frameworks posit that when bottom-up speech signals are ambiguous, top-down processing (lexical access, context prediction) must compensate, consuming limited cognitive resources.

### Mechanism of Perception
- **Automatic vs. controlled processing:** Clear speech in quiet is largely automatic; degraded speech requires controlled, effortful processing.
- **Working memory competition:** The same phonological loop resources used for speech comprehension are required for storage and reasoning tasks.
- **Pupillometry:** Task-evoked pupil dilation indexes cognitive effort; larger dilations observed at poorer SNR even when intelligibility is near-ceiling.

### Known Measurable Variables
| Variable | Unit | Measurement |
|----------|------|-------------|
| Working memory span | words | Reading/listening span tests |
| Pupil dilation | mm | Eye-tracking during listening |
| Response time | ms | Delay in secondary tasks during degraded listening |
| Effort rating | scale | Borg CR10 or NASA-TLX |
| Speech intelligibility | % | Keyword correct at given SNR |

### Known Physiological Effects
- **Pupil dilation:** SNR of −1 dB to −3 dB with speech-shaped noise produces significant and sustained pupil dilation even when intelligibility remains >60%.
- **Cardiovascular reactivity:** Elevated heart rate and blood pressure during effortful listening.

### Known Psychological Effects
- **Memory impairment:** Background noise degrades recall of spoken word lists and lectures even when words are correctly identified.
- **Serial position effects:** Noise disproportionately impairs primacy and recency portions of serial recall, suggesting disrupted rehearsal and encoding.
- **Working memory capacity moderation:** Individuals with higher working memory capacity show smaller noise effects on recall.

### Time-Dependent Effects
- **Immediate:** Effort ratings and pupil dilation increase within seconds of noise onset.
- **Cumulative:** Cognitive fatigue develops over 30–60 minutes of effortful listening, degrading performance on concurrent tasks.
- **Recovery:** Rapid (minutes) if noise ceases; slow if noise persists but task demands are removed.

### Environmental Dependencies
- **Reverberation time:** Long RT (>1.0 s) increases cognitive load equivalently to noise; both require greater top-down processing.
- **SNR:** The relationship is non-linear; load increases sharply below +5 dB SNR.
- **Visual cues:** Lip-reading and spatial proximity to speaker reduce cognitive load by 20–40%.

### Hospitality/Live-Event Relevance
- **Speech intelligibility in restaurants:** STI (Speech Transmission Index) <0.50 produces "fair" intelligibility but significantly elevated cognitive load; patrons in these environments converse less and leave sooner.
- **Lecture and conference venues:** Even when audience reports "could hear everything," long RT or noise can degrade retention and engagement measurably.

### Commercial Implications
- **Cognitive load as a hidden cost:** Venues with STI 0.50–0.60 may appear "loud enough" but impose invisible cognitive tax that reduces customer satisfaction scores and return rates.
- **Pupillometry as a venue metric:** Wearable eye-tracking could objectively index cognitive load by zone, enabling data-driven acoustic optimization.

### Reliability/Confidence of Evidence
- **Grade A:** The link between degraded SNR/reverberation and increased listening effort is robust across multiple paradigms and populations.
- **Grade A:** Pupil dilation is a validated proxy for cognitive load in auditory tasks.
- **Grade B:** Working memory capacity moderates noise effects, but individual assessment is rarely operationally feasible.

---

## 14. NOISE VS. STRUCTURED SOUND PERCEPTION

### Scientific Explanation
The auditory system distinguishes between **noise** (stochastic, low-predictability, high-entropy signals) and **structured sound** (periodic, predictable, low-entropy signals). This distinction operates at multiple levels:
- **Peripheral:** Cochlear phase-locking is stronger for periodic signals.
- **Cortical:** Periodic sounds evoke stronger and more synchronous neural population responses.
- **Cognitive:** Structured sound engages predictive coding mechanisms; noise violates predictions, increasing processing cost.

### Mechanism of Perception
- **Temporal envelope periodicity:** The auditory system extracts modulation spectra; structured sound shows concentrated energy at harmonic/modulation frequencies.
- **Predictive coding:** The cortex generates forward models of expected acoustic patterns; prediction error signals distinguish noise from structure.
- **Statistical learning:** Over seconds to minutes, listeners learn sound statistics, reducing cognitive load for structured inputs.

### Known Measurable Variables
| Variable | Unit | Notes |
|----------|------|-------|
| Spectral entropy | bits | Higher = more noise-like |
| Modulation spectrum | Hz | Structured sound shows peaks at F0 and harmonics |
| Predictability (ITPC) | 0–1 | Inter-trial phase coherence; higher for periodic |
| Signal-to-noise ratio | dB | Classic energetic measure |

### Known Physiological Effects
- **Cortical entrainment:** EEG shows stronger phase-locking to structured sound (music, speech) than to noise.
- **Autonomic regulation:** Structured sound (especially music with periodicity) can entrain heart rate and respiratory patterns; noise disrupts these.

### Known Psychological Effects
- **Annoyance:** Noise is rated more annoying than structured sound of equal SPL and spectral content.
- **Cognitive interference:** Noise disrupts working memory more than structured sound, even when the structured sound is irrelevant to the task.
- **Restorative effects:** Natural structured sounds (e.g., bird song, water with rhythmic patterns) show modest attention restoration effects compared to noise.

### Time-Dependent Effects
- **Habituation:** Habituation to noise is slower and less complete than habituation to structured sound.
- **Learning:** Predictability of structured sound improves over 5–10 minutes of exposure, reducing cognitive load.

### Environmental Dependencies
- **Context:** The same sound can be perceived as "noise" or "music" depending on listener intent, cultural framing, and task relevance.
- **Control:** Uncontrollable noise is more stressful than controllable noise of equal SPL.
- **Meaning:** Noise with semantic content (unintelligible speech) is more disruptive than meaningless noise.

### Hospitality/Live-Event Relevance
- **Background music vs. HVAC noise:** Music at 70 dBA is less disruptive to conversation than HVAC noise at 65 dBA because the former is structured and partially predictable.
- **Acoustic privacy:** Speech privacy requires not just SNR but also spectral similarity; masking speech with structurally similar music is less effective than masking with noise.

### Commercial Implications
- **Structured sound as a design tool:** Intentionally designed soundscapes (e.g., "sound branding" with periodic motifs) are processed at lower cognitive cost than generic background music or noise.
- **Noise as a quality signal:** Paradoxically, moderate levels of "good noise" (crowd murmur, kitchen sounds) signal authenticity and popularity in hospitality contexts.

### Reliability/Confidence of Evidence
- **Grade A:** The distinction between periodic/structured and aperiodic/noise signals is fundamental to auditory neuroscience.
- **Grade B:** The cognitive load differential is well-established in laboratory settings but less quantified in ecological hospitality contexts.
- **Contradictions:** The "restorative" claim for natural structured sounds is supported by some studies but criticized for small effect sizes and replication failures.

---

## 15. HUMAN ADAPTATION TO SUSTAINED SOUND EXPOSURE

### Scientific Explanation
Adaptation to sustained sound exposure encompasses **peripheral adaptation** (reduction in afferent neural firing rate), **central habituation** (reduced cortical response to predictable stimuli), and **sensory tolerance** (reduced subjective annoyance over time). These are distinct from fatigue/TTS, which represent pathological or protective threshold shifts.

### Mechanism of Perception
- **Peripheral adaptation:** Auditory nerve fibers show rapid adaptation (ms) and slow adaptation (seconds) to continuous tones.
- **Cortical habituation:** fMRI/EEG responses to repetitive sounds decline within minutes; novel sounds re-engage responses (oddball effect).
- **Stimulus-specific adaptation (SSA):** Inferior colliculus and cortex reduce firing to repeated stimuli while maintaining responsiveness to deviants.

### Known Measurable Variables
| Variable | Unit | Measurement |
|----------|------|-------------|
| Adaptation time constant | ms/s | Single-neuron: 10–100 ms; cortical: 2–10 min |
| Habituation slope | %/min | Decline in subjective loudness or physiological response |
| Dishabituation magnitude | % | Response recovery after novel stimulus insertion |
| Tolerance threshold shift | dB | Increase in acceptable SPL over exposure duration |

### Known Physiological Effects
- **Reduced autonomic response:** Heart rate and skin conductance responses to sustained noise decline over 10–30 minutes.
- **Preserved subcortical encoding:** Brainstem responses (ABR) show minimal habituation, ensuring continued environmental monitoring.

### Known Psychological Effects
- **Loudness reduction:** Continuous steady sounds are perceived as ~10–20% softer after 2–3 minutes.
- **Annoyance reduction:** Annoyance ratings decline over days to weeks of chronic exposure (though physiological stress markers may not).
- **Conscious filtering:** Sustained predictable sounds are filtered from conscious attention, freeing resources for other tasks.

### Time-Dependent Effects
- **Short-term (seconds–minutes):** Rapid peripheral and early cortical adaptation.
- **Medium-term (hours):** Habituation of autonomic and subjective responses; TTS may coexist.
- **Long-term (days–years):** Chronic exposure leads to "sociocusis"—elevated thresholds from non-occupational noise. Complete habituation to loud noise never occurs at the cochlear level.

### Environmental Dependencies
- **Predictability:** Predictable sounds adapt/habituate faster than unpredictable sounds.
- **Task relevance:** Sounds relevant to current goals adapt less than irrelevant sounds.
- **Sleep state:** Adaptation is reduced during sleep, explaining why sleep disruption persists even for "habituated" noises.

### Hospitality/Live-Event Relevance
- **Background music loops:** Short repetitive playlists habituate faster, becoming "wallpaper"; longer, varied playlists maintain engagement.
- **Ambient noise acceptance:** Regular patrons habituate to venue ambient noise; first-time visitors do not, creating divergent experience quality.

### Commercial Implications
- **Novelty scheduling:** Introducing novel acoustic elements every 8–12 minutes prevents habituation and maintains arousal/engagement.
- **First-visit premium:** First-time customer experience is disproportionately shaped by unadapted auditory response; initial acoustic impression carries higher weight than for regulars.

### Reliability/Confidence of Evidence
- **Grade A:** Peripheral adaptation and cortical SSA are established neurophysiological phenomena.
- **Grade B:** Long-term habituation of annoyance is well-documented but confounded by self-selection (annoyed individuals leave).
- **Grade C:** "Sociocusis" as a distinct from occupational NIHL is debated; evidence is epidemiological and correlational.

---

## INTEGRATED OPERATIONAL FRAMEWORK

### Measurable KPIs for Behavioral Environment Systems

| KPI | Measurement Method | Target Range | Frequency |
|-----|-------------------|--------------|-----------|
| **Leq (A-weighted)** | Integrating sound level meter | 78–86 dBA (hospitality); 92–98 dBA (live peak) | Continuous |
| **Leq (C-weighted)** | SLM with C-weighting | Tracks low-frequency energy missed by A-weighting | Continuous |
| **Infrasound level (G-weighted)** | Infrasound microphone + G-weighting | <85 dBG (indoor); <90 dBG (outdoor) | Spot/continuous |
| **STI / RASTI** | Impulse response + STI calculation | >0.60 (speech); >0.50 (music) | Per zone |
| **Reverberation time T60** | Interrupted noise / balloon pop | 0.4–0.8 s (speech); 1.2–2.0 s (music) | Per zone |
| **Spatial Release from Masking** | Binaural speech-in-noise test | SRM >6 dB for normal hearing | Design validation |
| **TTS risk index** | DoseBadge / personal dosimetry | <50% of OSHA PEL per shift | Per staff |
| **Pupil dilation (cognitive load)** | Wearable eye-tracking | <0.3 mm increase from baseline | Spot studies |
| **Spectral centroid** | RTA / FFT analysis | Context-dependent (see Section 9) | Continuous |
| **Roughness / Sharpness** | Psychoacoustic meter (DIN 45692) | <0.5 asper (relaxed); 1.5–3 asper (energized) | Continuous |
| **Cortisol (infrasound stress)** | Salivary assay | Baseline ±15% | Spot studies |

### Contradictions & Unresolved Debates

1. **Loudness function exponent:** ISO 226:2003 used 0.25 (corrected from magnitude estimation); 2023 revision uses 0.30 (additivity-based). Difference is small (<0.6 dB) but theoretically significant for precision modeling.
2. **TTS-to-PTS progression:** While repeated TTS is accepted as a risk factor for PTS, the individual dose-response is stochastic; some individuals accumulate PTS without documented TTS history.
3. **Infrasound effects:** Early literature exaggerated effects; modern controlled studies show consistent but modest cortisol and mood shifts. Mechanism (vestibular vs. somatosensory vs. auditory) remains debated.
4. **Consonance universality:** Sensory consonance (roughness-based) is near-universal; cultural/schematic consonance is highly learned. Operational systems must distinguish these.
5. **Informational masking quantification:** No standardized metric exists; operational prediction requires context-specific calibration.
6. **Cognitive load vs. intelligibility:** High intelligibility does not guarantee low cognitive load. A venue can have "good enough" STI but still impose effort that degrades memory and satisfaction.

### Practical Operational Implications

1. **Measurement beyond dB(A):** dB(A) is insufficient for behavioral optimization. Systems must measure C-weighted (low-frequency), G-weighted (infrasound), STI (speech), and psychoacoustic metrics (roughness, sharpness).
2. **Zone-specific acoustic targets:** A single venue requires multiple acoustic zones with distinct targets (quiet conversation: Leq 65 dBA, STI >0.65; dance floor: Leq 95 dBA, RT 1.5 s; transition zones: Leq 75 dBA).
3. **Staff protection as operational priority:** Staff TTS degrades service quality. Personal dosimetry and rotation schedules are not merely HR compliance issues but service quality controls.
4. **Infrasound audit:** Baseline infrasound measurement should be standard in venue due diligence, particularly for basement/industrial conversions.
5. **Temporal dynamics in programming:** Acoustic environments should vary every 8–12 minutes to prevent habituation; background music playlists should avoid short loops.
6. **Aging-aware design:** Patron demographics >40 years require 3–6 dB better SNR and 30% shorter reverberation than young adult baselines due to temporal processing and spatial hearing degradation.
7. **Predictive modeling integration:** The variables in this document can be engineered into ML features:
   - `spectral_centroid`, `roughness_asper`, `sharpness_acum`, `infrasound_dBG`, `rt60`, `sti`, `leq_A`, `srm_dB`
   - Target variables: `dwell_time_min`, `drink_purchase_rate`, `return_intention`, `staff_error_rate`, `complaint_count`

### Confidence Summary by Domain

| Domain | Confidence | Key Limitation |
|--------|-----------|--------------|
| Frequency sensitivity / loudness | A | ISO standards robust; minor model disputes |
| Temporal processing | A | Age effects well-quantified |
| Auditory masking | A–B | Energetic: A; Informational: B |
| Spatial hearing / SRM | A | Binaural cue models mature |
| Auditory scene analysis | B | Top-down components under-specified |
| Spectral roughness | A–B | Model convergence good; absolute scales vary |
| Consonance/dissonance | B–C | Cultural modulation significant |
| Timbre dimensions | B | Warmth lacks standardized metric |
| Low-frequency physiology | B | Sample sizes modest; effect sizes small-moderate |
| Auditory fatigue / TTS | A | Dose-response well-established |
| Sensory overload | C | Highly individual; few hospitality-specific studies |
| Cognitive load from sound | A | Pupillometry + memory paradigms robust |
| Noise vs. structured sound | B | Ecological validity gaps |
| Adaptation / habituation | B | Long-term habituation confounded by selection |

---

**Document closes.** This synthesis is structured for direct translation into:
- Feature engineering schemas for acoustic ML pipelines
- Causal DAGs (directed acyclic graphs) linking acoustic exposure → physiological response → behavioral outcome
- Operational SOPs for venue acoustic calibration
- Staff health and safety protocols with behavioral performance linkages

All claims are mechanism-first and exclude unsupported phenomenological assertions. Confidence grades flag domains requiring additional primary research before high-stakes operational deployment.
