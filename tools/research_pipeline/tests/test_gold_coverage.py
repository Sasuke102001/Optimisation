from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
import site


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VENDOR = ROOT / ".vendor"
if VENDOR.exists():
    site.addsitedir(str(VENDOR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from research_extraction.config import PipelineConfig
from research_extraction.pipeline import run_pipeline


STATE_TRANSITIONS_FILE = "Behavioral State Transitions in Live Hospitality and Music Environments.md"
NEUROSCIENCE_FILE = "behavioral_neuroscience_mechanisms.md"
CONTRADICTIONS_FILE = "Contextual_Behavioral_Contradictions_Hospitality_Nightlife.md"
DEEP_REPORT_FILE = "deep-research-report (2).md"
OPS_FILE = "operational_behavioral_intelligence_nightlife.md"
TEMPORAL_FILE = "Temporal Behavioral Dynamics and Sequencing Intelligence in Nightlife and Live Music.md"


class GoldCoveragePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmpdir = tempfile.TemporaryDirectory()
        research_dir = ROOT.parent / "Module 3 research"
        config = PipelineConfig(
            research_dir=research_dir,
            output_dir=Path(cls._tmpdir.name),
            llm_provider="none",
            enable_embeddings=False,
        )
        cls.outputs = run_pipeline(config)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmpdir.cleanup()

    @classmethod
    def _items_for(cls, attr: str, relative_source_file: str):
        return [item for item in getattr(cls.outputs, attr) if item.relative_source_file == relative_source_file]

    @classmethod
    def _coverage_for(cls, relative_source_file: str) -> dict:
        return cls.outputs.coverage_report.source_file_coverage.get(relative_source_file, {})

    def test_seeded_coverage_is_complete(self) -> None:
        coverage = self.outputs.coverage_report
        self.assertEqual(coverage.missing_canonical_states, [])
        self.assertEqual(coverage.missing_canonical_transitions, [])
        self.assertEqual(coverage.missing_canonical_mechanisms, [])

    def test_research_source_profiles_are_applied(self) -> None:
        expected_files = {
            STATE_TRANSITIONS_FILE,
            NEUROSCIENCE_FILE,
            CONTRADICTIONS_FILE,
            DEEP_REPORT_FILE,
            OPS_FILE,
            TEMPORAL_FILE,
        }
        profiled_sections = [section for section in self.outputs.sections if section.relative_file in expected_files]
        self.assertGreater(len(profiled_sections), 0)
        for section in profiled_sections:
            self.assertEqual(section.source_role, "synthesis")
            self.assertGreater(len(section.domain_tags), 0)
            self.assertGreater(len(section.expected_coverage_tags), 0)

    def test_state_transition_report_yields_seeded_states_and_transitions(self) -> None:
        states = self._items_for("states", STATE_TRANSITIONS_FILE)
        temporals = self._items_for("temporal_dynamics", STATE_TRANSITIONS_FILE)
        interventions = self._items_for("interventions", STATE_TRANSITIONS_FILE)
        kpis = self._items_for("kpis", STATE_TRANSITIONS_FILE)

        self.assertGreaterEqual(len(states), 10)
        self.assertGreaterEqual(len(temporals), 9)
        self.assertGreaterEqual(len(interventions), 8)
        self.assertGreaterEqual(len(kpis), 8)

        state_ids = {item.canonical_state_id for item in states if item.canonical_state_id}
        expected_state_ids = {
            "ST_PASSIVE_OBSERVATION",
            "ST_ENGAGEMENT",
            "ST_PARTICIPATION",
            "ST_SYNCHRONIZED_BEHAVIOR",
            "ST_EUPHORIA",
            "ST_OVERSTIMULATION",
            "ST_FATIGUE",
            "ST_DISENGAGEMENT",
            "ST_RECOVERY",
            "ST_REACTIVATION",
        }
        self.assertTrue(expected_state_ids.issubset(state_ids))

        transition_ids = {item.canonical_transition_id for item in temporals if item.canonical_transition_id}
        expected_transition_ids = {
            "TRN_PASSIVE_OBSERVATION_TO_ENGAGEMENT",
            "TRN_ENGAGEMENT_TO_PARTICIPATION",
            "TRN_PARTICIPATION_TO_SYNCHRONIZED_BEHAVIOR",
            "TRN_SYNCHRONIZED_BEHAVIOR_TO_EUPHORIA",
            "TRN_EUPHORIA_TO_OVERSTIMULATION",
            "TRN_OVERSTIMULATION_TO_FATIGUE",
            "TRN_FATIGUE_TO_DISENGAGEMENT",
            "TRN_DISENGAGEMENT_TO_RECOVERY",
            "TRN_RECOVERY_TO_REACTIVATION",
        }
        self.assertTrue(expected_transition_ids.issubset(transition_ids))

        late_stage_states = [
            item
            for item in states
            if item.canonical_state_id in {"ST_FATIGUE", "ST_DISENGAGEMENT", "ST_RECOVERY", "ST_REACTIVATION"}
        ]
        self.assertTrue(
            any(item.fatigue_characteristics or item.recovery_characteristics for item in late_stage_states)
        )

    def test_neuroscience_report_maps_to_canonical_mechanisms(self) -> None:
        variables = self._items_for("variables", NEUROSCIENCE_FILE)
        relationships = self._items_for("relationships", NEUROSCIENCE_FILE)
        interventions = self._items_for("interventions", NEUROSCIENCE_FILE)
        temporals = self._items_for("temporal_dynamics", NEUROSCIENCE_FILE)

        mechanism_ids = {
            item.canonical_mechanism_id
            for item in [*variables, *relationships, *interventions, *temporals]
            if item.canonical_mechanism_id
        }
        expected_mechanisms = {
            "MECH_DOPAMINE_REWARD_ANTICIPATION",
            "MECH_PREDICTION_ERROR",
            "MECH_NEURAL_ENTRAINMENT",
            "MECH_SYNCHRONIZATION",
            "MECH_EMOTIONAL_CONTAGION",
            "MECH_AROUSAL_REGULATION",
            "MECH_HABITUATION",
            "MECH_NOVELTY_PROCESSING",
            "MECH_SENSORY_FATIGUE_OVERSTIMULATION",
            "MECH_MEMORY_CONSOLIDATION",
            "MECH_MUSIC_INDUCED_CHILLS",
            "MECH_SOCIAL_SYNCHRONIZATION",
            "MECH_COLLECTIVE_EMOTIONAL_AMPLIFICATION",
        }
        self.assertTrue(expected_mechanisms.issubset(mechanism_ids))
        self.assertGreaterEqual(len(temporals), 10)
        self.assertGreaterEqual(len(interventions), 8)
        self.assertTrue(any(item.canonical_mechanism_id for item in interventions))

    def test_contradiction_report_preserves_reversal_contexts(self) -> None:
        contradictions = self._items_for("contradiction_objects", CONTRADICTIONS_FILE)
        self.assertGreaterEqual(len(contradictions), 20)
        self.assertTrue(
            all(
                item.applicable_contexts
                or item.invalid_contexts
                or item.audience_dependencies
                or item.environment_dependencies
                for item in contradictions
            )
        )

        combined_text = " ".join(
            f"{item.raw_text} {item.claim} {item.contradiction_text} {item.normalized_text}".lower()
            for item in contradictions
        )
        for keyword in ("bpm", "loud", "repetition", "density", "peak", "introvert", "extrovert", "intox"):
            self.assertIn(keyword, combined_text)

    def test_temporal_report_yields_kernel_and_recovery_patterns(self) -> None:
        temporals = self._items_for("temporal_dynamics", TEMPORAL_FILE)
        relationships = self._items_for("relationships", TEMPORAL_FILE)

        self.assertGreaterEqual(len(temporals), 8)
        self.assertGreaterEqual(len(relationships), 20)
        self.assertGreaterEqual(sum(1 for item in temporals if item.transition_logic), 5)
        self.assertGreaterEqual(sum(1 for item in temporals if item.duration_minutes), 2)

        combined_text = " ".join(
            f"{item.raw_text} {item.name} {item.transition_logic} {item.estimated_time_window}".lower()
            for item in temporals
        )
        for keyword in ("peak-end", "recovery", "wave", "anticipat", "habitua", "lag"):
            self.assertIn(keyword, combined_text)

    def test_operational_report_yields_operational_chains(self) -> None:
        relationships = self._items_for("relationships", OPS_FILE)
        interventions = self._items_for("interventions", OPS_FILE)
        kpis = self._items_for("kpis", OPS_FILE)
        temporals = self._items_for("temporal_dynamics", OPS_FILE)

        self.assertGreaterEqual(len(relationships), 40)
        self.assertGreaterEqual(len(interventions), 5)
        self.assertGreaterEqual(len(kpis), 10)
        self.assertGreaterEqual(len(temporals), 10)

        combined_text = " ".join(
            " ".join(
                filter(
                    None,
                    [
                        getattr(item, "raw_text", ""),
                        getattr(item, "source_entity", ""),
                        getattr(item, "target_entity", ""),
                        getattr(item, "name", ""),
                        getattr(item, "operator_label", ""),
                    ],
                )
            ).lower()
            for item in [*relationships, *interventions, *kpis]
        )
        for keyword in ("queue", "ingress", "egress", "closing", "staff", "spend", "retention"):
            self.assertIn(keyword, combined_text)

    def test_deep_report_yields_crowd_cascade_logic(self) -> None:
        relationships = self._items_for("relationships", DEEP_REPORT_FILE)
        contradictions = self._items_for("contradiction_objects", DEEP_REPORT_FILE)
        temporals = self._items_for("temporal_dynamics", DEEP_REPORT_FILE)

        self.assertGreaterEqual(len(relationships), 20)
        self.assertGreaterEqual(len(contradictions), 8)
        self.assertGreaterEqual(len(temporals), 1)

        combined_text = " ".join(
            " ".join(
                filter(
                    None,
                    [
                        getattr(item, "raw_text", ""),
                        getattr(item, "source_entity", ""),
                        getattr(item, "target_entity", ""),
                        getattr(item, "claim", ""),
                        getattr(item, "contradiction_text", ""),
                        getattr(item, "name", ""),
                    ],
                )
            ).lower()
            for item in [*relationships, *contradictions, *temporals]
        )
        for keyword in ("crowd", "cascade", "tipping", "transition", "contag", "synchron"):
            self.assertIn(keyword, combined_text)

    def test_expected_coverage_tags_remain_visible_in_report(self) -> None:
        self.assertGreaterEqual(self._coverage_for(STATE_TRANSITIONS_FILE).get("transitions", 0), 9)
        self.assertGreaterEqual(self._coverage_for(NEUROSCIENCE_FILE).get("mechanisms", 0), 13)
        self.assertGreaterEqual(self._coverage_for(CONTRADICTIONS_FILE).get("contradictions", 0), 20)
        self.assertGreaterEqual(self._coverage_for(OPS_FILE).get("temporal_dynamics", 0), 10)
        self.assertGreaterEqual(self._coverage_for(TEMPORAL_FILE).get("temporal_dynamics", 0), 8)


if __name__ == "__main__":
    unittest.main()
