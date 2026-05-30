"""
Pipeline 2 — SE Prescriptive Entity Schemas

These are the extraction targets for the Show Engineering pipeline. Unlike
Pipeline 1 (mechanistic: BehavioralState, Intervention, Variable), these
entities are prescriptive — they answer "what should the operator play."

Each entity here feeds into Stage 1's Neuroacoustic KAG (Agent 3) and RAG
(Agent 4), which populate `neuroacoustic_prescription` in EvidencePackage.

Entity hierarchy:
  BPMPrescription   — tempo range → brainwave state → crowd behavior
  ChordPrescription — harmony type → neurological effect → deployment context
  RhythmPrescription — rhythmic pattern → entrainment effect → crowd suitability
  IntervalEffect     — musical interval → psychoacoustic mechanism → nightlife use
  RagaProfile        — Indian raga → rasa → crowd state → production deployment
  TransitionRule     — phase pair → trigger signals → execution method

All inherit BaseOntologyObject from schemas.py to stay consistent with Pipeline 1.
"""
from __future__ import annotations

from pydantic import Field

from research_extraction.schemas import BaseOntologyObject


class BPMPrescription(BaseOntologyObject):
    """
    A tempo prescription for a specific show context.

    Source corpus: rhythmic_patterns_neurological_reference.md,
    Tempo Neural Entrainment and Crowd State.md, bpm_neural_entrainment_behavioral_mapping.md
    """
    bpm_id: str                          # e.g. "bpm_opening_90_110"
    bpm_min: int
    bpm_max: int
    brainwave_state: str                 # e.g. "Low-alpha 8-10 Hz"
    neural_mechanism: str                # e.g. "SMA/basal ganglia beat prediction lock"
    behavioral_effect: str               # e.g. "social awareness, ambient engagement, floor priming"
    show_phase_fit: list[str]            # e.g. ["Opening", "early Build"]
    venue_type_fit: list[str]            # e.g. ["Night Club", "Bar"] — empty = universal
    crowd_type_fit: list[str]            # e.g. ["mixed", "regular"] — empty = universal
    transition_target: list[str]         # BPM IDs that naturally follow
    avoid_for: list[str]                 # e.g. ["empty room before 10pm", "post-peak cool-down"]
    energy_level: int                    # 0–100


class ChordPrescription(BaseOntologyObject):
    """
    A chord type or progression with its neurological and behavioral effects.

    Source corpus: neuropsychological_chord_reference.md,
    Chord Voicing Perception and Crowd Control in Live Music.md,
    harmonic_psychology_chord_behavioral_response.md
    """
    chord_id: str                        # e.g. "chord_maj7_opening"
    chord_name: str                      # e.g. "Major 7th", "Dominant 7th", "i-VII-VI-VII"
    chord_type: str                      # "triad" | "seventh" | "extended" | "progression" | "mode"
    is_progression: bool                 # True if this is a multi-chord sequence
    arousal_direction: str               # "increase" | "decrease" | "sustain"
    valence: str                         # "positive" | "negative" | "ambivalent" | "neutral"
    neural_mechanism: str                # e.g. "low prediction error → parasympathetic shift"
    emotional_profile: str               # e.g. "serene, nostalgic, dreamy — lush warmth"
    behavioral_response: str             # observable crowd response
    bpm_interaction: str                 # how BPM modifies the effect
    show_phase_fit: list[str]            # e.g. ["Opening", "Wind Down"]
    avoid_phases: list[str]              # e.g. ["Peak"] if inappropriate there
    venue_type_context: list[str]        # empty = venue-agnostic
    production_note: str                 # how to deploy in live/DJ production


class RhythmPrescription(BaseOntologyObject):
    """
    A rhythmic pattern — Western grid or Indian tala — with entrainment effects.

    Source corpus: rhythmic_patterns_neurological_reference.md,
    Raga-Rasa Engineering for Indian Urban Nightlife.md (tala section),
    groove-neuroscience.md
    """
    rhythm_id: str                       # e.g. "rhythm_4otf_house", "rhythm_keherwa"
    pattern_name: str                    # e.g. "Four-on-the-Floor", "Keherwa", "Breakbeat"
    pattern_type: str                    # "western_grid" | "tala" | "hybrid"
    tala_name: str | None = None         # for Indian rhythms, e.g. "Keherwa", "Teentaal"
    beat_cycle: str | None = None        # e.g. "8 beats, 4+4" for Keherwa
    syncopation_level: str               # "low" | "medium" | "high"
    groove_score: int                    # 0–100 (medium complexity = highest groove)
    bpm_min: int
    bpm_max: int
    neural_mechanism: str                # e.g. "SMA/putamen lock, steady dopamine release"
    behavioral_response: str             # physical and social crowd behavior
    crowd_universal: bool                # True if works across all crowd types
    crowd_type_fit: list[str]            # if not universal, which crowd types
    show_phase_fit: list[str]
    venue_type_context: list[str]        # empty = venue-agnostic


class IntervalEffect(BaseOntologyObject):
    """
    A musical interval (dyad) with its psychoacoustic and neurological effect.

    Source corpus: Neuropsychological Reference for Western Musical Intervals.md
    """
    interval_id: str                     # e.g. "interval_perfect_fifth"
    interval_name: str                   # e.g. "Perfect 5th", "Minor 7th", "Tritone"
    semitones: int
    consonance_class: str                # "consonant" | "mild_dissonance" | "strong_dissonance"
    acoustic_mechanism: str              # roughness, harmonicity, critical band interaction
    neural_pathway: str                  # cortical/subcortical regions activated
    emotional_response: str              # e.g. "stability, power, spaciousness"
    nightlife_deployment: str            # when and how to use
    avoid_contexts: list[str]            # when this interval is counterproductive


class RagaProfile(BaseOntologyObject):
    """
    An Indian raga with its rasa, tonal architecture, and venue deployment context.

    Source corpus: Raga-Rasa Engineering for Indian Urban Nightlife.md,
    Indian Music Psychology and Behavioral Dynamics in Hospitality and Nightlife.md
    """
    raga_id: str                         # e.g. "raga_yaman"
    raga_name: str                       # e.g. "Yaman", "Bhairavi", "Khamaj"
    primary_rasa: list[str]              # e.g. ["Shringara", "Shanta"]
    secondary_rasa: list[str] = []
    traditional_time: str | None = None  # e.g. "Evening / first prahar of night"
    modern_time_relevance: str           # how much traditional time still matters in venues
    scale_notation: str                  # ascending / descending notation
    characteristic_notes: str           # defining intervals and phrases
    nervous_system_profile: str          # arousal/valence/parasympathetic profile
    crowd_state: str                     # observable room state when raga is deployed
    emotional_profile: str              # emotional quality in words
    production_deployment: str           # how to use in DJ/live production
    venue_contexts: list[str]            # e.g. ["rooftop lounge", "post-dinner transition"]
    avoid_contexts: list[str]            # e.g. ["mainstream club peak time"]
    tala_pairings: list[str] = []        # compatible talas from RhythmPrescription


class TransitionRule(BaseOntologyObject):
    """
    A rule for transitioning between two show phases: trigger signals, execution,
    and what to hold for.

    Source corpus: Live Performance Transition Psychology.md,
    Session_Arc_Engineering_Guide.md, musical_transition_architecture.md,
    Crowd Dynamics and Show Engineering.md
    """
    rule_id: str                         # e.g. "trans_build_to_peak"
    from_phase: str                      # e.g. "Build"
    to_phase: str                        # e.g. "Peak"
    from_bpm_range: str                  # e.g. "118–126"
    to_bpm_range: str                    # e.g. "126–134"
    from_energy_level: int               # 0–100
    to_energy_level: int                 # 0–100
    trigger_signals: list[str]           # behavioral signals indicating ready to escalate
    hold_signals: list[str]              # signals indicating should NOT transition yet
    execution_steps: list[str]           # ordered steps to execute the transition
    bpm_change: str                      # e.g. "+8–12 BPM over 2–3 tracks"
    chord_shift: str                     # harmonic change to make
    frequency_shift: str | None = None  # sub-bass or spectral change
    timing_window: str                   # e.g. "15–20 minutes into Build"
    risk_factors: list[str]              # what can go wrong
    recovery_action: str                 # what to do if crowd doesn't follow
