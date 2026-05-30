from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ─── Session ──────────────────────────────────────────────────────────────────

class SessionStartRequest(BaseModel):
    venue_id: int
    session_number: int
    session_mode: str = Field(
        default="observation_only",
        pattern="^(observation_only|engineering_active|post_intervention)$",
    )
    table_config: dict[str, Any] | None = None
    notes: str | None = None


class SessionStartResponse(BaseModel):
    session_id: int
    venue_id: int
    session_number: int
    opened_at: datetime


class SessionEndRequest(BaseModel):
    notes: str | None = None


# ─── KPI ──────────────────────────────────────────────────────────────────────

class KpiSignalReading(BaseModel):
    signal_id: int | None = None
    signal_label: str | None = None
    value_numeric: float | None = None
    value_text: str | None = None


class KpiAssessmentRequest(BaseModel):
    family_id: int
    zone: str | None = None
    rag_status: str = Field(pattern="^(green|amber|red)$")
    notes: str | None = None
    readings: list[KpiSignalReading] = []


class InterventionStartRequest(BaseModel):
    intervention_id: int | None = None
    intervention_label: str | None = None
    operator_notes: str | None = None


class InterventionEndRequest(BaseModel):
    intervention_log_id: int
    operator_notes: str | None = None


class EnvironmentLogRequest(BaseModel):
    zone: str | None = None
    notes: str | None = None
    readings: list[KpiSignalReading] = []


# ─── Session Brief ────────────────────────────────────────────────────────────

class SessionBriefRequest(BaseModel):
    venue_id: int
    session_number: int
    session_mode: str = Field(
        default="pre_session",
        pattern="^(pre_session|mid_session|post_session)$",
    )
    table_config: dict[str, Any] | None = None
    live_state: dict[str, Any] | None = None
    mode: str = Field(default="council", pattern="^(council|fast)$")


class SessionBriefResponse(BaseModel):
    brief: str
    session_number: int
    venue_id: int
    generated_at: datetime


class ReferenceTrack(BaseModel):
    bpm: int                 # exact BPM, e.g. 124
    key: str                 # short notation, e.g. "Am", "Em", "Gm"
    chords: list[str]        # one entry per distinct section, e.g. ["Am-F-C-G", "Em-C-G-D"]
    energy_score: int        # 1–100
    why: str                 # mechanism — what this profile does to the crowd neurologically


class PhaseArcItem(BaseModel):
    phase_name: str          # "Opening", "Build", "Peak", "Wind Down"
    start_time: str          # "21:00"
    end_time: str            # "21:45"
    bpm: str                 # "105–112"
    chord: str               # "I–IV–V"
    key: str                 # "F major — Ionian"
    bass: str                # "55–70Hz · nominal"
    watch_for: list[str]     # 2–3 bullet strings
    action_line: str         # single-line phase instruction for the quick ref strip
    reference_tracks: list[ReferenceTrack] = []   # 3–4 track profiles per phase


class CouncilBrief(BaseModel):
    state: str
    mechanism: str
    lever: str
    action: str
    signal: str


class ShowBriefRequest(BaseModel):
    venue_id: int
    venue_name: str
    area: str | None = None
    city: str | None = None
    primary_type: str | None = None       # "Brewpub", "Night Club" — from m3_venues.primary_type
    cascade_types: list[str] = []         # ["brewpub"] — from m3_venues.cascade_types
    session_number: int
    show_date: str                        # "2026-06-01"
    start_time: str | None = None         # "21:00"
    end_time: str | None = None           # "01:00"
    phase_count: int = 4
    crowd_size: str | None = None         # intimate / medium / large
    crowd_type: str | None = None         # regular / corporate / college / mixed
    show_type: str | None = None          # dj_night / live_band / open_mic / private_event
    notes: str | None = None
    live_state: dict | None = None
    mode: str = Field(default="council", pattern="^(council|fast)$")


class ShowBriefResponse(BaseModel):
    brief: str                        # raw Council synthesis text (keep for logs)
    council_brief: CouncilBrief | None = None
    phase_arc: list[PhaseArcItem] = []
    venue_id: int
    session_number: int
    generated_at: datetime


class ShowOutcomeRequest(BaseModel):
    session_id: int
    intervention_deployed: bool = False
    intervention_worked: bool | None = None
    intervention_type: str | None = None
    avg_dwell_min: int | None = None
    peak_crowd_energy: str | None = Field(
        default=None, pattern="^(LOW|MEDIUM|HIGH)$"
    )
    peak_occupancy_pct: float | None = None
    primary_segment_confirmed: str | None = None
    notes: str | None = None
    data_quality: str = Field(
        default="OPERATOR_LOGGED",
        pattern="^(SURVEY_VALIDATED|OPERATOR_LOGGED|INFERRED)$",
    )


# ─── Council Evidence Package ─────────────────────────────────────────────────

class StructuredEvidence(BaseModel):
    canonical_state: str                    # e.g. "first_mover_inhibition"
    mechanism_chains: list[dict]            # from m3_mechanisms.json traversal
    intervention_candidates: list[dict]     # from m3_interventions.json lookup
    kpi_linkages: list[str]                 # which KPI families are implicated


class NeuroacousticPrescription(BaseModel):
    bpm_range: str | None = None            # e.g. "122–126"
    chord_structure: str | None = None      # e.g. "i-VII-VI-VII"
    frequency_emphasis: str | None = None   # e.g. "sub-bass"
    transition_path: str | None = None      # e.g. "ambient_build → dancefloor_prime"
    raw_passages: list[str] = []            # verbatim prescription text from SE research


class ConversationRequest(BaseModel):
    operator_input: str
    venue_id: int
    venue_name: str
    current_context: dict           # sessionContext fields
    current_plan: dict | None = None  # planOutput.rawBrief or parsed plan


class EvidencePackage(BaseModel):
    session_state: dict
    venue_profile: dict
    structured_evidence: StructuredEvidence | None = None
    theory_passages: list[str] = []
    neuroacoustic_prescription: NeuroacousticPrescription | None = None
    session_history: list[dict] = []
