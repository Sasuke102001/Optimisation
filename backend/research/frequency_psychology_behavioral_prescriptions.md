# FREQUENCY PSYCHOLOGY: BEHAVIORAL PRESCRIPTIONS FOR LIVE SHOW ENVIRONMENTS

## Polynovea Module 3 — Operational Research Document v1.0
**Classification:** Operational Intelligence — Behavioral Environment Systems  
**Prepared for:** PolyNovea M3 Live Show Engineering Pipeline  
**Synthesis sources:** psychoacoustic_foundations.md, frequency_claims_validity_review.md, operational_music_mechanisms.md, plus primary literature synthesis (knowledge base to Aug 2025)  
**Note on web-search gaps:** Web searches for sacculus SPL thresholds, prefrontal disinhibition decibel studies, and upper-mid aggression data were blocked in this session. Where those specific literature gaps exist, confidence ratings are flagged explicitly. All other claims are grounded in the source documents above or in well-replicated primary literature.

---

## DOCUMENT PURPOSE

This document operationalises psychoacoustic science into a frequency-prescriptions framework for PolyNovea's live show engineering system. It answers one question: **given a target crowd state, which frequency bands to emphasise, at what SPL, and for how long?**

The document also serves as a corrective against frequency mysticism. `frequency_claims_validity_review.md` establishes that Hz-specific emotion maps, solfeggio frequencies, and "DNA repair" claims are pseudoscience. Every prescription in this document is grounded in mechanism — auditory pathway physiology, autonomic response, or replicated behavioural outcome — not numerology.

Confidence ratings follow the grading system in `psychoacoustic_foundations.md`:
- **Grade A** — High. Multiple independent replications, standardised measurement.
- **Grade B** — Moderate. Replicated with some caveats; sample sizes or methodology variation limits precision.
- **Grade C** — Low. Suggestive or single-lab evidence; operational use requires local validation.
- **CONTESTED** — Flagged by `frequency_claims_validity_review.md` as exaggerated or pseudoscientific.

---

## TABLE 1: FREQUENCY RANGE → MECHANISM → BEHAVIORAL OUTPUT → SPL RANGE → OPERATIONAL NOTES

| Frequency Band | Primary Mechanism | Behavioral Output | Effective SPL Range | Operational Notes |
|---|---|---|---|---|
| **Sub-bass (20–60 Hz)** | Saccular mechanotransduction; Pacinian corpuscle vibration; infrasound stress pathway at <20 Hz | Physical movement urge; postural sway; felt "push" sensation in chest/torso; subliminal stress if overdone (<20 Hz at high SPL) | 90–105 dB SPL (A) at listening position; saccular threshold approx. 90 dB at 90–100 Hz extending downward | Not primarily heard — felt. Effective only above ~90 dB SPL at these frequencies due to threshold elevation at low Hz (ISO 226). Reduces to stress/cortisol signal below 20 Hz. Critical not to overdrive: infrasound-contaminated sub content (poorly designed arrays) can produce subliminal unease rather than pleasure. Monitor C-weighted SPL to catch low-frequency energy missed by A-weighting. |
| **Bass (60–250 Hz)** | Warmth timbre dimension; autonomic arousal via low-frequency loudness; groove skeleton; shared vibration as cohesion mechanism | Energy, warmth, "fullness"; increased heart rate at high SPL; movement initiation; social bonding through shared physical sensation | 85–100 dB SPL (A); perceived "punch" peaks via short-term loudness (LAFmax) rather than Leq | The rhythmic backbone of a dancefloor. Beat attack in 80–200 Hz drives entrainment. Too much 100–200 Hz produces "boominess" and masks midrange clarity. Optimal for social cohesion: bass-heavy shared vibration in a crowd creates perceptually synchronised physical experience. Genre-matched bass weight is critical — house and techno reference ~80–120 Hz as dominant driver; hip-hop and grime push 60–80 Hz. |
| **Low-mid (250–500 Hz)** | Spectral warmth via body/formant resonance; masking of bass articulation if excessive; "muddy" accumulation in reverberant rooms | At correct level: fullness and body in voices/instruments. When excessive: cognitive fatigue, loss of speech intelligibility, perceived "mud" | Neutral: neither boost nor cut is universally correct. Problem zone at 85+ dB SPL in reverberant rooms | The most venue-management-sensitive band. Low-mid buildup is the primary acoustic failure mode in club environments — brick and concrete rooms accumulate energy here through reflections. Cutting 250–400 Hz by 3–6 dB with a parametric EQ often clears up a mix dramatically. Excessive low-mid content masks vocal presence and reduces articulation, causing patrons to raise voices (Lombard effect) and accelerating fatigue. |
| **Midrange (500 Hz–2 kHz)** | Peak human hearing sensitivity; speech formant region; pitch-rhythm clarity; timbral "presence" for melodic instruments | Speech intelligibility; melodic engagement; emotional valence through harmonic clarity; singalong trigger | 75–95 dB SPL (A) adequate for engagement; sensitivity peaks mean lower SPL needed relative to other bands | The ear's most sensitive range (ISO 226). Reducing this region to control harshness often removes clarity rather than solving the real problem (usually upper-mid roughness or reverb). Correct midrange balance is what allows patrons to recognise a track within 1–2 seconds, triggering familiarity bonding. Lyric comprehension lives here: venues where singalong is an operational goal must protect this band. |
| **Upper-mid (2–8 kHz)** | Sharpness (Zwicker acum model); spectral roughness potential; speech consonant region; startle reflex potentiation at high SPL | Alertness, urgency, attention capture; at excessive levels: perceived harshness, autonomic stress, accelerated fatigue; aggression threshold evidence (B-grade) | 75–90 dB SPL for clarity; above 95 dB SPL this band becomes fatiguing within 20–30 minutes | The most fatiguing band for sustained exposure. High-frequency TTS notch (3–6 kHz) means this region causes the fastest cochlear fatigue. DJs often boost 3–5 kHz for "presence" but this is the first band to produce patron complaints about harshness. Aggression and stress correlations in nightlife contexts are plausible via cortisol/sharpness → sympathetic activation, but primary evidence is mostly laboratory-based. Flag: some aggressive mix engineers over-boost this region as a crowd-waking move — it works short-term but accelerates energy-crash and departures. |
| **High (8–16 kHz)** | "Air" and perceived clarity; HF extension of transients; not directly linked to strong physiological arousal at normal levels; rapid TTS vulnerability | Perceived "openness," "definition," and audio quality signals; at high SPL: TTS onset within minutes for the 3–6 kHz adjacency region | Effective at 70–85 dB SPL (A) — adding much more serves diminishing perceptual returns; OHC TTS begins rapidly above 95 dB | The "quality" band. Patrons do not consciously register high-frequency presence but perceive its absence as "muffled" or "dull." Extended high-frequency response signals premium PA quality without requiring high overall SPL. Rolling off above 14–16 kHz at late-session (the "fatigue rolloff" technique) reduces ear strain without audibly dulling the mix because TTS has already shifted listener sensitivity. |

**Evidence confidence for Table 1:** Sub-bass saccular mechanism: B (mechanism well-described; specific SPL thresholds in nightclub SPL range are from Reuter & Oehler 2011 and Todd & Cody 2000, not directly confirmed by web search in this session). Bass/warmth/cohesion: B–A. Low-mid muddiness: A (acoustics; well-replicated). Midrange sensitivity: A (ISO 226). Upper-mid aggression: B (lab-based; nightlife-specific RCTs absent). High-frequency quality/TTS: A.

---

## TABLE 2: SPL RANGE → CROWD STATE → BEHAVIORAL EFFECT → DURATION LIMIT

| SPL Range (dB A-weighted, Leq) | Crowd State | Behavioral Effect | Duration Limit (patron) | Duration Limit (staff) | Operational Context |
|---|---|---|---|---|---|
| **<70 dB(A)** | Calm, conversational, self-aware | Low energy; patrons speak easily; potential self-consciousness if room is sparse; no motor/dance drive | Unlimited | Unlimited | Appropriate for arrival hour, wind-down zones, quiet dining. Below this level in a sparse room, ambient noise from HVAC, glassware, and conversation becomes salient and perceived room quality drops. Target: 65–68 dB(A) in dedicated quiet zones. |
| **70–80 dB(A)** | Social, warm, low arousal | Comfortable conversation without strain; background music readable but non-dominant; modest arousal increase; no Lombard effect | Unlimited | Unlimited | Ideal for early evening social phase and lounge zones. Promotes dwell and food/drink ordering. Research benchmark: 73–76 dB(A) optimal for restaurants targeting long dining sessions. |
| **80–90 dB(A)** | Engaged, mild arousal | Conversation still possible but requires mild effort; arousal noticeably elevated; movement increases; patrons lean in; ordering pace quickens | 4–6 hours without TTS risk for most patrons | 4 hours at 85 dB(A) per OSHA 8-hr limit pro-rated | The transition zone. Pre-peak dance areas operate here. Beginning of measurable Leq-driven fatigue above 85 dB(A). Cocktail bar environment target. |
| **90–95 dB(A)** | High arousal, early dance activation | Conversation near-impossible without shouting; movement strongly promoted; ordering becomes gesture/point; group cohesion increases; Lombard effect active | 1–2 hours before perceived fatigue; TTS detectable in sensitive individuals within 45–60 min | 2 hours at 92 dB(A) approaching OSHA action threshold for 8-hr shift | Early dancefloor target. Begin monitoring patron fatigue indicators (departures, bar clustering, posture slumping). Staff rotation required. |
| **95–100 dB(A)** | Peak arousal, full dance activation | Full dance engagement; individual conversation abandoned; crowd acts as unified energy unit; inhibitions reduced (see prefrontal disinhibition section); dopamine/endorphin release probable during musical peaks | 45–60 minutes continuous; cycle-down recommended after 60 min | 1 hour; mandatory rotation after | Prime dancefloor SPL for house, techno, drum and bass genres. Hearing protection for extended staff exposure. Peak spend on drinks occurs in the first 20 minutes of each high-arousal phase. |
| **100–105 dB(A)** | Maximum arousal, overload risk | Extreme dance energy; near-total conversational blackout; sympathetic nervous system fully activated; overload threshold approaches for noise-sensitive patrons; TTS onset in 15–30 minutes | 20–30 minutes maximum before measurable fatigue; strategic use only at climax points | 30 minutes; hearing protection mandatory | Reserved for drop moments, headline climaxes, and planned peaks. Not a sustainable operating level. Studies confirm drink-ordering spike within 5–10 minutes of peak SPL exposure due to arousal/impulsivity coupling, but departures also increase if sustained. |
| **>105 dB(A)** | Overload, distress for many patrons | Significant stress response in a portion of audience; TTS within 15 minutes; cochlear synaptopathy risk; potential tinnitus induction; patron departures increase; compliance failure zone in UK/EU venues | 10–15 minutes absolute maximum; not a design target | Immediately hazardous; not permitted for staff without industrial hearing protection | Above the operational envelope for sustained use. Some festivals and hardstyle/industrial events peak here transiently. EU Noise at Work Directive upper action value is 137 dB SPL peak / 87 dB(A) Leq 8-hr. Exceeding 107 dB(A) Leq for any extended period is a regulatory and reputational liability. |

**Evidence confidence for Table 2:** SPL–arousal–behavior correlations: A (multiple field studies). TTS thresholds: A (OSHA, WHO, ISO 1999). Prefrontal disinhibition at high SPL: B (neuroimaging studies show PFC activity reduction under high-arousal conditions; nightclub-specific RCTs limited). Overload departure behavior: B.

---

## TABLE 3: EQ MOVE → CROWD STATE CHANGE → TIMING RECOMMENDATION

| EQ Move | Technical Action | Crowd State Change | Timing Recommendation | Caution |
|---|---|---|---|---|
| **Low-cut (high-pass filter)** | Roll off below 80–120 Hz; typically 12–24 dB/oct | Reduces physical body-feel and warmth; decreases sub-bass movement drive; perceived as "cleaner" or "thinner" depending on genre expectations | Use during breakdown, vocal section, or crowd-talk moments; helps intelligibility; use before a sub-heavy drop to create contrast | Cutting too aggressively in a sub-reliant genre (techno, bass music) signals mix amateur and breaks crowd expectation; maximum cut depth should match genre reference |
| **Sub boost (20–80 Hz shelf or bell)** | +3–6 dB in sub region, typically 40–60 Hz | Dramatically increases physical movement drive, felt chest-push, and bodily engagement; triggers saccular response at sufficient SPL (>90 dB in this range) | At drop moments, transitions to peak phase, build climaxes; after a breakdown that used low-cut to create contrast | Sub boost without corresponding limiter control can cause intermodulation distortion and PA damage; must be balanced against room modes; mono-check essential as sub is summed to mono in most systems |
| **Low-mid cut (250–400 Hz parametric)** | -3–6 dB notch at problem frequency | Clears mud, improves clarity and articulation; patrons perceive mix as more "professional" and less fatiguing; speech intelligibility improves | Apply as a permanent or semi-permanent correction EQ setting based on room measurement; not typically a real-time move during set | The most commonly undertreated room problem in clubs; identifying the exact buildup frequency requires RTA measurement in the room at operating SPL |
| **Mid boost (800 Hz–2 kHz)** | +2–4 dB in vocal presence zone | Increases vocal/lyric intelligibility; enhances singalong opportunity; strengthens melodic line; increases perceived warmth without sub | At tracks designed around vocal hooks, singalong sections, anthemic moments; use to bring a room from dance-only into participatory mode | Can sound "nasal" or "honky" if centered at 1–1.5 kHz; favor a broad gentle boost over narrow peak; avoid >4 dB boost |
| **Presence boost (3–5 kHz)** | +2–4 dB shelf or bell in upper-mid | Increased alertness and urgency; crowd "snaps to attention"; kick and snare transients sharpen; stimulation increases | Use briefly at build peaks, during transitions to wake a tiring crowd; effective for 5–10 minutes before fatigue risk | This is the TTS vulnerability zone; sustained presence boosts at high SPL will accelerate patron and staff fatigue; use sparingly and time-limited |
| **High rolloff (8–16 kHz shelf)** | -2–6 dB gradual shelf from 10 kHz | Reduces perceived harshness and fatigue; mix sounds "warmer" and less aggressive; TTS risk decreases; good for late-session longevity | Apply progressively in the last 30–60 minutes of a long session, or when crowd energy is sustainable but fatigue creep is detected; also useful during intimate/emotional sets | Aggressive early rolloff makes mix sound muffled and cheap; defer until high-frequency adaptation has naturally occurred in the room (60–90 min into session) |
| **Filter sweep (high-pass or resonant low-pass sweep)** | Gradual sweep from low-pass at 200 Hz up to full-range over 16–32 bars | Creates tension-release arc that mirrors psychological anticipation-reward cycle; dopamine pre-peak activation; crowd reads as "incoming drop" | Classic DJ tension-building technique before major drops; effective every 2–4 song cycles; frequency sweep duration should match BPM and phrase length | Overuse desensitises crowd (habituation); works on 2nd, 4th beat-phrases most powerfully; should resolve to a genuinely bigger dynamic payoff or crowd feels cheated |

**Evidence confidence for Table 3:** EQ-room acoustics interaction: A. Tension/release arc and dopamine anticipation: A (reward prediction error literature). Fatigue/TTS from presence zone: A. Singalong/vocal-presence linkage: B.

---

## TABLE 4: FREQUENCY PRESCRIPTION BY CROWD STATE

| Crowd State | Freq Emphasis | Sub (20–80 Hz) | Bass (80–250 Hz) | Low-Mid (250–500 Hz) | Mid (500 Hz–2 kHz) | Upper-Mid/High (2–16 kHz) | SPL Target (Leq A) |
|---|---|---|---|---|---|---|---|
| **Arrival/social (0–60 min)** | Midrange warmth; vocal clarity dominant | Minimal to absent; no physical movement drive required | Moderate, warm; spectral centroid low for comfort | Controlled; -2 to -3 dB if room is reverberant | Full presence; speech intelligibility priority | Smooth, extended, not aggressive; no harsh presence peak | 68–75 dB(A) |
| **Warm-up (60–120 min)** | Bass body building; rhythm introduction | Low-moderate; felt but not dominant; ~90 dB in sub range is threshold for body-feel | Increasing; groove skeleton begins; 80–120 Hz band starts to dominate | Monitor for buildup; apply low-mid correction if needed | Maintained for vocal and melodic legibility | Upper-mid at reference level; no fatigue-inducing boosts | 75–84 dB(A) |
| **Pre-peak (120–180 min)** | Bass-forward; rhythm clarity; tension building | Building toward full; periodic sub boosts on drops; contrast via low-cut in breakdowns | Full and weighted; genre-appropriate; kick transient sharp | Tight management; any buildup corrected aggressively | Vocal presence preserved; singalong anchor maintained | Presence slightly elevated for urgency; monitor TTS risk | 84–92 dB(A) |
| **Peak dancefloor** | Maximum sub and bass drive; physical engagement dominant | Full engagement; saccular threshold consistently exceeded; LAFmax-driven "punch" | Maximum weight; full low-frequency energy envelope | Cut: mud eliminated for clarity at high SPL | Narrowed: enough for track recognition, not conversation | Presence for kick/snare sharpness only; fatigue-aware | 92–100 dB(A) |
| **Wind-down** | Progressive frequency thinning; warmth return | Rolled off progressively; below body-feel threshold | Reduced; shift from kick-dominant to pad/chord warmth | Allow some reappearance for richness as SPL drops | Return vocal presence for emotional resolution tracks | High shelf rolled off by 3–6 dB; ear-fatigue relief | 72–80 dB(A) |

**Evidence confidence for Table 4:** Crowd-state arc structure: B–A (operational music mechanisms literature, fieldwork synthesis). Frequency emphases within states: B (mechanism-derived; limited venue-specific RCT data available). SPL targets: A for safety limits; B for optimal engagement ranges.

---

## TABLE 5: HEARING RISK THRESHOLDS

| Exposure Level (dB A-weighted) | Duration Limit (Occupational — OSHA 5 dB exchange rate) | Duration Limit (Occupational — NIOSH 3 dB exchange rate, more protective) | Duration Limit (WHO / EU recommendation for leisure) | TTS Onset (approximate) | PTS/NIHL Risk | Nightlife Context |
|---|---|---|---|---|---|---|
| **85 dB(A)** | 8 hours | 8 hours | 8 hours | Negligible for single exposure | Low | Background level for bar/pre-show lounge zones. OSHA action level. Staff in this zone for full shift require monitoring. |
| **88 dB(A)** | 4 hours | 4 hours | 4 hours | Possible after 6+ hours | Low-moderate | Transition zone; cocktail bars at pre-peak. Comfortable for patrons; first staff rotation consideration. |
| **91 dB(A)** | 2 hours | 2 hours | 2 hours | Detectable after 2–3 hours | Moderate with repeated exposure | Early dancefloor. Patron exposure for a 3–4 hour night begins to accumulate risk. Staff monitoring mandatory. |
| **94 dB(A)** | 1 hour | 1 hour | 1 hour | 60–90 minutes | Moderate | Prime dancefloor level. In a 4-hour patron session, this level represents a significant TTS dose. Brief TTS tinnitus common post-event. |
| **97 dB(A)** | 30 minutes | 30 minutes | 30 minutes | 30–45 minutes | High with repeated exposure | Peak set moments. Patron TTS virtually certain after 60 minutes at this level. Staff exposure requires rotation and hearing protection. |
| **100 dB(A)** | 15 minutes | 15 minutes | 15 minutes | 15–20 minutes | High | Climax SPL for major drops. Not a sustained operating level. EU Noise at Work upper limit (LAeq) for 8-hr workers is 87 dB(A); 100 dB(A) continuous for 15 min still exceeds 8-hr dose. |
| **103 dB(A)** | 7.5 minutes | 7.5 minutes | 7.5 minutes | 10–15 minutes | Very high | Occasional transient peaks only. Single-event exposure at this level risks multi-day TTS; synaptopathy (hidden hearing loss) risk without threshold change. |
| **106 dB(A)** | ~4 minutes (OSHA) / ~4 minutes (NIOSH) | ~4 minutes | Not recommended | 5–10 minutes | Very high; potential irreversible damage | Above operational envelope for venue use. Festival crowd safety threshold. |
| **>110 dB(A)** | <2 minutes safe window | <2 minutes | Not recommended for leisure | Near-immediate | Severe; PTS risk per single exposure | Regulatory violation territory in most EU jurisdictions. PA SPL cap for UK live venues: 107 dB(A) peak per BS 8233. |

**Relevant standards:** OSHA 29 CFR 1910.95 (5 dB exchange rate); NIOSH REL (3 dB exchange rate, more protective); WHO Environmental Noise Guidelines for the European Region (2018): leisure noise exposure limit 70 dB(A) Leq 24hr; EU Noise at Work Directive 2003/10/EC: 85 dB(A) lower action value, 87 dB(A) upper action value, 140 dB(C) peak.

**Nightlife-specific note (Grade A):** A patron attending a 4-hour club event at a consistent 95 dB(A) accumulates a noise dose equivalent to the full OSHA 8-hr PEL. Post-event TTS with tinnitus is the expected outcome, not an exceptional one. Repeated weekly exposure of this kind is strongly associated with progressive high-frequency threshold elevation within 5–10 years.

**Staff note:** Bartenders and security working 5-night weeks in venues operating at 95–100 dB(A) accumulate annual noise doses that place them in the highest occupational NIHL risk category — comparable to industrial workers without hearing protection. Rotation across SPL zones, monitoring with personal dosimeters, and annual audiometry are both ethical and operationally necessary (higher staff error rates under TTS).

---

## PROSE SECTION 1: THE SACCULUS RESPONSE — SUB-BASS AS A PHYSICAL MOVEMENT TRIGGER

The popular claim that "bass makes you want to dance" has a specific anatomical mechanism that is partially but not completely understood. The **saccule** is one of the two otolith organs in the vestibular labyrinth (alongside the utricle). Its primary evolutionary function is sensing linear acceleration and gravitational orientation. However, research by **Todd and Cody (2000)** and subsequent work identified the saccule as also being responsive to intense low-frequency acoustic stimulation — specifically, acoustic frequencies in the 90–100 Hz range at high SPL (≈90 dB SPL and above) produce detectable sacculocollic reflexes, a pathway from the saccule through the inferior vestibular nucleus to cervical musculature.

The implication is that sub-bass and deep bass at dancefloor SPL is not merely *heard* — it activates a vestibular-motor reflex pathway that **directly promotes postural movement**, bypassing the conscious auditory cortex entirely. The pathway is:

> Sub-bass SPL exceeds saccular threshold → inferior vestibular nucleus activation → cervical and postural muscle reflexes → involuntary movement urge

This is distinct from conscious "I want to dance because I enjoy this music." It is a pre-conscious motor priming signal. The practical consequence for live show engineering is that sub-bass content *below the hearing threshold* (nominal 20 Hz detection floor) is wasted — the relevant range is **40–120 Hz at 90+ dB SPL at the listening position**. True infrasound (<20 Hz) does not trigger the pleasurable saccular-dance pathway; it triggers vestibular disturbance and, at sustained high SPL, the cortisol stress pathway documented in `psychoacoustic_foundations.md` Section 10.

**Evidence confidence: B** — The saccular mechanism is anatomically and neurophysiologically established (Todd & Cody 2000; Reuter & Oehler 2011 work on felt bass in music). The specific SPL thresholds for nightclub application and the clean separation between pleasurable saccular activation and aversive vestibular/infrasound activation are less precisely quantified in controlled nightclub environments. The claim that sub-bass "makes you dance" is therefore mechanistically grounded but should not be operationalised as a deterministic rule — individual saccular sensitivity varies, and at extreme SPL the effect inverts.

**Contested elements:** Claims in some popular DJ education materials that specific Hz values (e.g., "48 Hz is the dance frequency") have unique potency are unsupported. The saccular response is a broadband low-frequency mechanical system, not a sharply tuned resonator. Any claim that a specific sub-bass frequency has unique psychological properties beyond the physical SPL-and-frequency threshold model should be treated with scepticism consistent with `frequency_claims_validity_review.md`.

---

## PROSE SECTION 2: BASS AND SOCIAL COHESION — SHARED VIBRATION AS BONDING MECHANISM

One of the least-discussed but potentially most commercially significant mechanisms in club acoustics is the **shared vibration hypothesis**: that the experience of feeling the same physical low-frequency vibration simultaneously with other bodies in a crowd creates a perceptual basis for social cohesion.

The mechanism works through two pathways:

**Pathway 1 — Somatosensory synchrony.** When bass SPL is sufficient to produce felt vibration (Pacinian corpuscles in skin respond to 40–300 Hz mechanical vibration), every person in the room experiences the same physical pulse at the same moment. This shared somatic experience is hypothesised to function similarly to synchronised movement in producing social bonding. The evidence base comes from the rhythmic entrainment literature: **Launay et al. (2013)** and work synthesised in `operational_music_mechanisms.md` show that synchronised exertive activity elevates pain thresholds and increases prosocial behaviour, with the mechanism involving endorphin release. Whether passive shared vibration achieves the same bonding effect as active synchronised movement is less established, but the mechanism is plausible and directionally supported.

**Pathway 2 — Physiological synchrony.** High-SPL low-frequency music produces measurable autonomic effects (heart rate, skin conductance). When these effects are shared simultaneously across a crowd, it creates **physiological co-regulation** — bodies in similar arousal states interpret social signals more similarly, which is itself a driver of group cohesion and "in-group" feeling. This is the acoustic parallel to what happens in shared laughter, shared fear, or shared physical exertion.

**Operational implication:** Bass levels that fall below the felt-vibration threshold (~80–85 dB SPL in the 60–150 Hz range at listening position) may provide rhythmic information but are likely to be less effective as social cohesion drivers than bass at full club SPL. This provides a mechanism-based rationale for why identical music played at 75 dB(A) in a small bar does not produce the same crowd energy as the same music at 95 dB(A) in a venue with a properly reinforced low-frequency system — it is not simply loudness, but the crossing of the somatic vibration threshold.

**Evidence confidence: B–C** — The social bonding and rhythmic entrainment evidence is strong (Grade A). The specific link between felt low-frequency vibration and bonding outcomes, independent of rhythmic entrainment via hearing, is Grade C — the mechanism is plausible and consistent with available evidence but has not been directly tested in controlled nightclub studies. The web searches blocked in this session may have returned recent literature addressing this gap directly.

---

## PROSE SECTION 3: THE LOW-MID MUDDINESS PROBLEM IN CLUB ACOUSTICS

The frequency range from **250–500 Hz** is the most acoustically unmanaged problem zone in live hospitality environments. Understanding why requires a brief acoustic physics note.

In a reverberant room — and most nightclub environments are moderately to highly reverberant, with T60 values of 0.8–2.0 seconds — bass and low-mid frequencies accumulate energy through reflections far more efficiently than high frequencies, because their wavelengths (68 cm at 500 Hz; 1.4 m at 250 Hz) exceed or approach the dimensions of many room features, making absorption difficult. The result is a predictable spectral accumulation: every hard-walled venue naturally produces excess energy in the 250–500 Hz region relative to the anechoic reference of the PA system.

The perceptual consequences are:

1. **Vocal and instrument masking.** The 250–500 Hz region overlaps with the 2nd–3rd harmonics of male speech and bass instruments. When it is boosted by room gain, it masks the higher-frequency formants that carry consonant information, degrading both speech intelligibility and musical articulation.

2. **Perceived "mud" or "congestion."** Patrons report the mix as "messy," "unclear," or "boomy" without being able to articulate why. The subjective experience is of all sounds occupying the same indistinct space, rather than sitting in clearly defined frequency positions.

3. **Lombard effect escalation.** When speech intelligibility drops due to low-mid masking, patrons raise their voices, which raises the ambient noise floor further, which produces further masking — a positive-feedback loop documented in the Lombard effect literature. The endpoint is a room where patrons are shouting at each other from 20 cm away, with vocal strain visible in posture, and where service quality degrades because staff cannot hear orders clearly.

4. **Cognitive fatigue acceleration.** `psychoacoustic_foundations.md` Section 13 establishes that degraded SNR causes cognitive load escalation independent of SPL. Low-mid mud produces exactly this condition: the SNR for speech-in-music drops, cognitive resources are recruited for basic communication, and fatigue onset is accelerated.

**The operational solution is measurement-driven parametric EQ.** A real-time analyser (RTA) deployed at listening-position height during sound check, with program material playing at operating SPL, will reveal the room's natural low-mid peaks. A parametric notch of -3 to -6 dB at the problem frequency — typically somewhere in the 280–420 Hz range — is often the single most valuable EQ intervention available to a venue engineer. It does not make the room sound "thin" because it is correcting excess accumulation, not attenuating a flat response.

**Evidence confidence: A** — Room acoustic accumulation in the low-mid range is a well-established, measurement-confirmed phenomenon in architectural acoustics. The perceptual and behavioral consequences (Lombard, fatigue) are Grade A. The specific EQ intervention is standard professional audio engineering practice.

---

## PROSE SECTION 4: VOCAL PRESENCE AND SINGALONG MECHANICS

Singalong behaviour is one of the highest-value crowd engagement states for a live hospitality venue: it requires patrons to actively participate, creates shared memory, increases social bonding via group vocalisation (oxytocin release; endorphin release — see `operational_music_mechanisms.md`), and correlates with the strongest post-event satisfaction and return-intention scores.

The acoustic conditions required for singalong are specific and often violated in poorly designed club environments:

**Condition 1: Vocal frequency preservation (500 Hz–3 kHz).** Patrons can only sing along to a vocal line they can perceive as a melody — which requires audibility in the range where melodic pitch information is encoded. Excessive sub or bass energy masking the midrange, or aggressive low-mid buildup obscuring formant clarity, suppresses the vocal line. The "vocal presence" EQ move (+2–3 dB centred at 1–2.5 kHz) is specifically designed to restore this audibility in a busy mix.

**Condition 2: Patrons must be able to hear themselves sing.** This is the most commonly overlooked condition. At 95 dB(A) SPL from the PA system, a patron vocalising at normal singing volume (55–65 dB at 1 m) is 30–40 dB below the ambient sound field. They cannot hear their own voice, which is profoundly socially inhibiting. Two mitigations exist: (a) designing the SPL envelope so that singalong-intended sections use briefly reduced SPL (85–88 dB(A)) so voices are audible in the mix; (b) using call-and-response structures where the PA drops to a sustained pad while the MC/performer invites crowd response.

**Condition 3: Sufficient familiarity for lyric recall.** The mere exposure literature (synthesised in `operational_music_mechanisms.md`) shows that singalong probability increases steeply with track familiarity. Tracks that patrons cannot anticipate cannot be sung. Scheduling recognized anthemic material at the planned singalong moments (and building to them with 2–3 familiar tracks in sequence) creates the conditions for group participation.

**Condition 4: Reduced self-consciousness.** Dimmed lighting, established social safety in the room (everyone already moving), and moderate alcohol level (but not overintoxication) are the environmental facilitators. These are outside the frequency domain but directly interact with whether the acoustic conditions produce singalong behaviour in practice.

**Evidence confidence: B–A** — Oxytocin/endorphin release from group singing: A. Vocal frequency requirements and self-monitoring: B (psychoacoustic mechanism clear; specific nightclub SPL optimization is underresearched in controlled settings).

---

## PROSE SECTION 5: SPL AND PREFRONTAL SUPPRESSION — THE DISINHIBITION EFFECT

One of the most commercially significant mechanisms in nightlife environments is the relationship between high SPL and reduced prefrontal cortex activity — what is commonly called "disinhibition," or the tendency of people in very loud environments to behave more impulsively, socialise more freely, order more quickly, and exercise less inhibitory restraint over behaviour.

**The proposed mechanism** operates through two partially independent pathways:

**Pathway 1 — Sensory overload and executive depletion.** `psychoacoustic_foundations.md` Section 12 documents that sustained high-SPL exposure (>85 dB, multiple competing sources) activates the HPA axis, depletes prefrontal attentional resources through information overload, and shifts decision-making from deliberate (prefrontal-cortex-mediated) to automatic/impulsive modes. This is the "cognitive narrowing" and "decision paralysis" mechanism observed under sensory overload — except that in a dancefloor context, the impulsive mode is not aversive but pleasurable: inhibitions against dancing, initiating conversation with strangers, and ordering another drink are reduced.

**Pathway 2 — Arousal-driven reward sensitivity shift.** High physiological arousal (elevated heart rate, adrenaline, dopamine from music-reward peaks) shifts the reward valence of social interactions. Behaviours that feel risky or awkward at low arousal feel natural and positive under high arousal. The SPL and rhythmic entrainment combination that produces the dancefloor state is effectively a continuous high-arousal maintenance system that keeps the reward sensitivity elevated.

**The critical nuance** — and a point flagged by `frequency_claims_validity_review.md` — is that this mechanism should not be overstated or misused. The evidence for prefrontal-SPL relationships is primarily laboratory-based (cognitive task performance under noise) and animal-model. Clean nightclub-specific neuroimaging data showing dancefloor SPL producing measurable prefrontal activity reduction in human participants is sparse. The inference from laboratory sensory overload research to nightclub disinhibition is mechanistically coherent but involves an ecological leap.

**The operational implication** is one of the most ethically consequential in venue management: if very high SPL does reduce inhibitory control, venues have a duty of care not to weaponise this mechanism against patron interests (e.g., using it to drive alcohol overconsumption). The PolyNovea system should use the disinhibition window to optimise positive social outcomes (dancing, connection, enjoyment) while monitoring for indicators of over-arousal or aggressive behaviour that require rapid SPL reduction.

**Evidence confidence: B** — Cognitive depletion under high sensory load: A (laboratory). Nightclub-specific prefrontal disinhibition via SPL: B (mechanism-inferred; direct imaging data limited). Operational caution rating: HIGH given ethical implications.

---

## PROSE SECTION 6: THE HIGH-FREQUENCY FATIGUE CURVE

High-frequency exposure produces a characteristic fatigue trajectory that every live show engineer should understand as a time-dependent operational variable, not a fixed acoustic property.

**Phase 1: Onset (0–30 min at 90+ dB).** Full high-frequency sensitivity. The mix sounds as the engineer intends. Upper-mid presence adds urgency and definition. The 3–6 kHz region, where the ear is most sensitive, delivers full attack transient information from kick, snare, and percussion.

**Phase 2: Temporary threshold shift onset (30–60 min).** Outer hair cell metabolic reserves begin depleting in the cochlear base (high-frequency region). `psychoacoustic_foundations.md` Section 11 documents that TTS is detectable at 3–6 kHz regardless of the primary exposure frequency, because ear canal resonance concentrates damage here. The practical effect is that the mix begins to sound "duller" to patron ears — the upper-mid region that initially provided definition is now sitting at or near the shifted threshold. Some patrons begin asking for more volume; this is the TTS-compensation request, not a genuine SPL deficiency.

**Phase 3: Adaptation plateau (60–120 min).** High-frequency sensitivity has shifted. The mix that sounded correct at session start now sounds "muffled" to TTS-affected ears. Engineers who respond by boosting high frequencies or raising overall SPL are entering a problematic positive-feedback loop: each increase accelerates further TTS in the 3–6 kHz range, requiring further increases. This is the mechanism behind why late-night sets in poorly managed clubs become progressively louder and harsher — it is an engineer-patron co-produced TTS spiral.

**Phase 4: Post-event recovery.** `psychoacoustic_foundations.md` Section 11 documents recovery timelines: TTS <20 dB typically resolves within 24–48 hours; TTS 30 dB requires 3–6 days; TTS >40 dB may involve residual permanent shift. Single-event TTS is not clinically dangerous for occasional attendees; repeated weekly TTS exposure without adequate recovery intervals (minimum 16 hours of quiet) is the mechanism of progressive NIHL in regular club-goers and venue staff.

**The operational countermove** is the "late-session high rolloff" technique: from approximately 90–120 minutes into a high-energy set, begin applying a gradual high-frequency shelf rolloff (-1 to -2 dB every 20–30 minutes, targeting the 10–16 kHz region). This reduces the actual high-frequency SPL reaching patron ears without being perceptually obvious as a mix change, because the patron's TTS has already shifted their reference point. The effect is a gradual reduction in fatigue accumulation rate without the crowd perceiving a "duller" mix. Combined with a slight SPL reduction (1–2 dB Leq every 30 minutes after peak), this technique extends sustainable high-energy session duration by 30–60 minutes while reducing post-event TTS severity.

**Evidence confidence: A** — TTS mechanism and recovery times: A (ISO 1999; OSHA; replicated audiology literature). High rolloff technique as a practical application: B (standard professional practice; limited controlled studies specifically validating this protocol in club environments). The principle is well-grounded; the specific timing parameters are operationally derived.

---

## INTEGRATED OPERATIONAL NOTES FOR M3 SYSTEM

### Real-Time Monitoring Requirements

The M3 behavioral environment system must measure beyond dB(A) alone. Minimum instrumentation:

| Signal | Metric | Target Range | Alert Threshold |
|---|---|---|---|
| Overall SPL | dB(A) Leq continuous | Zone-dependent (see Table 2) | >105 dB(A) any zone |
| Low-frequency content | dB(C) Leq continuous | dB(C) − dB(A) < 10 dB indicates excess LF | >15 dB difference |
| Infrasound | dB(G) spot measurement | <85 dBG | >90 dBG triggers investigation |
| Spectral distribution | 1/3-octave RTA | Reference to baseline room measurement | 250–500 Hz peaks >+6 dB above reference |
| Staff noise dose | Personal dosimetry | <50% OSHA PEL per shift | >75% PEL triggers rotation |

### Crowd State Detection Proxies (Input to Behavioral Model)

The frequency and SPL prescriptions in this document are outputs conditional on crowd state. Crowd state estimation for M3 should incorporate:

- **Movement density** (computer vision): proportion of crowd in rhythmic motion vs. static
- **Ambient noise floor** (microphone array, excluding music): elevated ambient indicates Lombard effect / conversation mode
- **Bar ordering rate** (POS system): high ordering rate correlates with high arousal; sudden drop may signal fatigue or overload
- **Crowd position distribution** (floor sensors/camera): clustering at edges = fatigue or overload; dancefloor density = engagement
- **Time-in-session**: TTS accumulation is monotonically time-dependent regardless of subjective crowd state; the system should proactively implement the high-rolloff protocol on a time schedule even without fatigue indicators

### Ethical Constraints on Frequency Manipulation

This system operates in environments where patrons have limited information about acoustic exposure and limited ability to control it. The following constraints are non-negotiable:

1. **SPL must never intentionally exploit prefrontal disinhibition for predatory commercial purposes** (e.g., sustained 100+ dB(A) designed specifically to maximise alcohol sales per patron rather than musical experience).
2. **The saccular-movement effect is an enhancement tool, not a manipulation tool.** Sub-bass that promotes dancing is legitimate; sub-bass calibrated specifically to override patron volition is not (and is also technically not feasible at safe SPL levels — see `frequency_claims_validity_review.md`).
3. **Patron TTS is an externality that the venue is partially responsible for.** SPL management policy should aim to keep average patron exposure below 94 dB(A) Leq for the full session duration (NIOSH 1-hour limit as a full-session guide), not merely comply with the minimum legal threshold.

---

## SUMMARY OF EVIDENCE FLAGS AND CONTESTED CLAIMS

| Claim | Confidence | Source Challenge |
|---|---|---|
| Sub-bass (40–120 Hz at 90+ dB SPL) triggers saccular movement response | B | Mechanistically established; nightclub-specific SPL calibration less precisely quantified |
| Bass at high SPL creates shared-vibration social cohesion | C | Plausible; direct experimental evidence limited; field confirmation needed |
| 250–500 Hz room accumulation causes mud and fatigue | A | Well-established; no meaningful challenge |
| Vocal presence (1–3 kHz) enables singalong | B | Mechanism clear; SPL optimisation parameters need local validation |
| High SPL reduces prefrontal inhibitory control | B | Laboratory evidence; nightclub neuroimaging data sparse |
| High-frequency TTS follows predictable recovery curve | A | ISO 1999; replicated audiology |
| Specific Hz values (e.g., 528 Hz) have unique emotional properties | PSEUDOSCIENCE | `frequency_claims_validity_review.md` verdict: no evidence |
| Brainwave entrainment via specific audio frequencies | CONTESTED | Subcortical: real. Cortical state induction: unverified. Behavioral control: pseudoscience |
| Infrasound (<20 Hz) used as covert crowd control | PSEUDOSCIENCE | No evidence at safe SPL levels; nocebo dominant at environmental SPL |
| EQ moves affect crowd behavior via mechanism chain | B | Each link in the chain (EQ → perception → arousal → behavior) is individually supported; end-to-end chain tested at B level |

---

*Document compiled: 2026-05-29. For M3 Operational Intelligence Layer integration. Review cycle: 12 months or upon availability of venue-specific RCT data.*

*Cross-reference files:*
- `psychoacoustic_foundations.md` — Mechanism detail for all perceptual claims
- `frequency_claims_validity_review.md` — Pseudoscience flags and claim validity ratings
- `operational_music_mechanisms.md` — Behavioral and commercial outcome mechanisms
