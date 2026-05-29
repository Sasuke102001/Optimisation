from __future__ import annotations

import json
from pathlib import Path

from research_extraction.config import PipelineConfig
from research_extraction.ids import build_canonical_id
from research_extraction.schemas import ContradictionObject, NormalizationDecision, OntologyObject, ReviewQueueItem


def build_review_queue(
    objects: list[OntologyObject],
    normalization_decisions: list[NormalizationDecision],
    config: PipelineConfig,
) -> list[ReviewQueueItem]:
    queue: list[ReviewQueueItem] = []

    for obj in objects:
        object_id = get_object_id(obj)
        if obj.confidence_score < config.review_confidence_threshold:
            queue.append(
                ReviewQueueItem(
                    review_id=build_canonical_id("review", f"low_confidence_{obj.__class__.__name__}_{object_id}"),
                    review_target_id=object_id,
                    object_type=obj.__class__.__name__,
                    review_bucket="low_confidence",
                    proposed_object=obj.model_dump(),
                    raw_text=obj.raw_text,
                    confidence=obj.confidence_score,
                    review_reason="Low final confidence requires human validation.",
                )
            )
        if obj.contradictions:
            queue.append(
                ReviewQueueItem(
                    review_id=build_canonical_id("review", f"contradiction_{obj.__class__.__name__}_{object_id}"),
                    review_target_id=object_id,
                    object_type=obj.__class__.__name__,
                    review_bucket="contradiction_review",
                    proposed_object=obj.model_dump(),
                    raw_text=obj.raw_text,
                    confidence=obj.confidence_score,
                    review_reason="Embedded contradiction markers require contradiction resolution review.",
                )
            )
        if isinstance(obj, ContradictionObject) and _needs_contradiction_review(obj):
            queue.append(
                ReviewQueueItem(
                    review_id=build_canonical_id("review", f"contradiction_object_{object_id}"),
                    review_target_id=object_id,
                    object_type=obj.__class__.__name__,
                    review_bucket="contradiction_review",
                    proposed_object=obj.model_dump(),
                    raw_text=obj.raw_text,
                    confidence=obj.confidence_score,
                    review_reason="Contradiction objects require human contradiction resolution.",
                )
            )
        if obj.contextual_limitations or obj.invalid_contexts:
            queue.append(
                ReviewQueueItem(
                    review_id=build_canonical_id("review", f"ontology_conflict_{obj.__class__.__name__}_{object_id}"),
                    review_target_id=object_id,
                    object_type=obj.__class__.__name__,
                    review_bucket="ontology_conflict",
                    proposed_object=obj.model_dump(),
                    raw_text=obj.raw_text,
                    confidence=obj.confidence_score,
                    review_reason="Contextual boundaries or ontology conflicts require review.",
                )
            )
        if _has_actionable_warning(obj) and obj.confidence_score >= config.review_confidence_threshold:
            queue.append(
                ReviewQueueItem(
                    review_id=build_canonical_id("review", f"promotion_{obj.__class__.__name__}_{object_id}"),
                    review_target_id=object_id,
                    object_type=obj.__class__.__name__,
                    review_bucket="promotion_review",
                    proposed_object=obj.model_dump(),
                    raw_text=obj.raw_text,
                    confidence=obj.confidence_score,
                    review_reason="Object is promotable but carries validation warnings worth a final human pass.",
                )
            )

    for decision in normalization_decisions:
        if decision.merge_action != "flagged_for_review":
            continue
        target_id = f"{decision.entity_type}:{decision.canonical_id}:{decision.candidate_id}"
        queue.append(
            ReviewQueueItem(
                review_id=build_canonical_id("review", target_id),
                review_target_id=target_id,
                object_type="NormalizationDecision",
                review_bucket="merge_review",
                proposed_object=decision.model_dump(),
                raw_text=decision.rationale,
                confidence=decision.similarity_score,
                review_reason="Potential duplicate requires human merge decision.",
            )
        )
    return queue


def _needs_contradiction_review(obj: ContradictionObject) -> bool:
    return bool(
        obj.affected_entities
        or obj.affected_entity_ids
        or obj.applicable_contexts
        or obj.invalid_contexts
        or obj.audience_dependencies
        or obj.environment_dependencies
        or obj.canonical_mechanism_id
        or obj.canonical_transition_id
        or obj.canonical_state_id
    )


def _has_actionable_warning(obj: OntologyObject) -> bool:
    actionable_tokens = (
        "unresolved",
        "canonical",
        "context",
        "ontology",
        "merge",
        "boundary",
    )
    return any(token in warning.lower() for warning in obj.validation.warnings for token in actionable_tokens)


def promote_approved_objects(
    objects: list[OntologyObject],
    review_queue: list[ReviewQueueItem],
    decisions_file: Path | None,
) -> tuple[list[dict], dict]:
    if not decisions_file or not decisions_file.exists():
        return [], {"status": "skipped", "reason": "no_review_decisions_file"}

    payload = json.loads(decisions_file.read_text(encoding="utf-8"))
    rows = payload if isinstance(payload, list) else payload.get("decisions", [])
    decisions_by_id = {str(row.get("review_id", "")): row for row in rows if isinstance(row, dict)}
    object_reviews: dict[str, list[ReviewQueueItem]] = {}
    for item in review_queue:
        if item.object_type == "NormalizationDecision":
            continue
        object_reviews.setdefault(item.review_target_id, []).append(item)

    promoted: list[dict] = []
    skipped_pending = 0
    skipped_rejected = 0
    for obj in objects:
        object_id = get_object_id(obj)
        related = object_reviews.get(object_id, [])
        if not related:
            promoted.append(obj.model_dump())
            continue

        statuses = [decisions_by_id.get(item.review_id, {}).get("status", "pending") for item in related]
        if any(status == "rejected" for status in statuses):
            skipped_rejected += 1
            continue
        if any(status == "pending" for status in statuses):
            skipped_pending += 1
            continue

        promoted_payload = obj.model_dump()
        for item in related:
            row = decisions_by_id.get(item.review_id, {})
            if row.get("status") == "modified" and isinstance(row.get("modified_object"), dict):
                promoted_payload = {**promoted_payload, **row["modified_object"]}
        promoted.append(promoted_payload)

    reviewed = sum(1 for item in review_queue if item.review_id in decisions_by_id)
    approved = sum(1 for row in decisions_by_id.values() if row.get("status") in {"approved", "modified"})
    rejected = sum(1 for row in decisions_by_id.values() if row.get("status") == "rejected")
    return promoted, {
        "status": "applied",
        "review_items_total": len(review_queue),
        "review_items_with_decisions": reviewed,
        "approved_or_modified": approved,
        "rejected": rejected,
        "skipped_pending_objects": skipped_pending,
        "skipped_rejected_objects": skipped_rejected,
        "promoted_objects": len(promoted),
    }


def get_object_id(obj: OntologyObject) -> str:
    for field_name in (
        "variable_id",
        "state_id",
        "relationship_id",
        "intervention_id",
        "kpi_id",
        "dynamic_id",
        "claim_id",
        "contradiction_id",
    ):
        value = getattr(obj, field_name, "")
        if value:
            return value
    raise ValueError(f"Unsupported ontology object type: {obj.__class__.__name__}")
