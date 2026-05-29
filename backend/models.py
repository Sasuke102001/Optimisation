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


# ─── Show Engineering ─────────────────────────────────────────────────────────

class ShowBriefRequest(BaseModel):
    venue_id: int
    session_number: int
    show_type: str | None = None
    live_state: dict[str, Any] | None = None
    mode: str = Field(default="council", pattern="^(council|fast)$")


class ShowBriefResponse(BaseModel):
    brief: str
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
