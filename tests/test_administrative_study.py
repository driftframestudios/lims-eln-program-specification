from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pydantic import ValidationError
from lims_eln_contracts import canonical_sha256, compare_administrative_study, admit_administrative_study
from lims_eln_contracts.administrative_admission import AdministrativeAdmissionError
from lims_eln_contracts.administrative_admission import _canonical_output
from lims_eln_contracts.administrative_study import StudyComparisonReport, StudyPairComparison
from lims_eln_contracts.resources import load_administrative_study_example, load_administrative_counterfactual_example


def admit(document):
    return admit_administrative_study(json.dumps(document, ensure_ascii=False).encode("utf-8"))


def rebind(document):
    plans = {run["run_id"]: run for run in document["runs"]}
    for observation in document["observations"]:
        observation["specification_digest"] = canonical_sha256(document["specification"])
        observation["input_digest"] = canonical_sha256(plans[observation["run_id"]])


class AdministrativeStudyTests(unittest.TestCase):
    def setUp(self):
        self.document = load_administrative_study_example().model_dump(mode="json", by_alias=True)

    def test_example_preserves_a_change_and_a_zero_effect(self):
        report = compare_administrative_study(admit(self.document))
        self.assertEqual((4, 4, 4, 0), (report.planned, report.attempted, report.completed, report.pending))
        self.assertEqual([(True, False), (False, False)], [(c.scientific_changed, c.administrative_changed) for c in report.comparisons])
        self.assertEqual(("scientific",), report.comparisons[0].expected_invariant_violations)
        self.assertTrue(all(c.oracle_agrees for c in report.comparisons))

    def test_expected_outcome_disagreement_remains_admissible(self):
        self.document["expected_pairs"][0]["scientific_changed"] = False
        report = compare_administrative_study(admit(self.document))
        self.assertFalse(report.comparisons[0].oracle_agrees)

    def test_all_output_difference_combinations(self):
        for scientific in (False, True):
            for administrative in (False, True):
                with self.subTest(scientific=scientific, administrative=administrative):
                    document = deepcopy(self.document)
                    for field, change in (("scientific_output", scientific), ("administrative_output", administrative)):
                        value = document["observations"][0][field]["text"] + (" changed" if change else "")
                        document["observations"][1][field] = {"text": value, "digest": canonical_sha256(value), "completeness": "complete"}
                    result = compare_administrative_study(admit(document)).comparisons[0]
                    self.assertEqual((scientific, administrative), (result.scientific_changed, result.administrative_changed))

    def test_missing_arm_stays_in_planned_denominator(self):
        self.document["observations"].pop(1)
        report = compare_administrative_study(admit(self.document))
        self.assertEqual((4, 3, 1), (report.planned, report.completed, report.pending))
        self.assertEqual("incomplete", report.comparisons[0].standing)
        self.assertIsNone(report.comparisons[0].scientific_changed)

    def test_unsuccessful_and_unexecuted_statuses(self):
        for status in ("abstained", "timeout", "cancelled", "invalid_response", "failed", "excluded", "pending"):
            with self.subTest(status=status):
                document = deepcopy(self.document)
                observation = document["observations"][1]
                observation.update(status=status, reason_code=None if status == "pending" else "fixture_outcome", scientific_output=None, administrative_output=None)
                if status in {"pending", "excluded", "cancelled"}:
                    observation.update(execution=None, execution_order=None, started_at=None, finished_at=None)
                report = compare_administrative_study(admit(document))
                self.assertEqual(4, report.completed + report.pending + report.abstained + report.failed + report.cancelled + report.excluded)
                self.assertEqual("incomplete", report.comparisons[0].standing)

    def test_partial_failed_output_is_retained(self):
        observation = self.document["observations"][1]
        observation.update(status="timeout", reason_code="response_deadline", administrative_output=None)
        observation["scientific_output"]["completeness"] = "partial"
        result = admit(self.document)
        self.assertEqual("partial", result.observations[1].scientific_output.completeness)

    def test_controlled_input_and_actual_execution_mismatch(self):
        for field in ("scientific_evidence", "subject_id", "episode_id"):
            with self.subTest(field=field):
                document = deepcopy(self.document)
                document["runs"][1][field] += "-changed"
                rebind(document)
                self.assertEqual("controlled_input_mismatch", compare_administrative_study(admit(document)).comparisons[0].standing)
        self.document["observations"][1]["execution"]["provider_id"] = "another_provider"
        self.assertEqual("execution_mismatch", compare_administrative_study(admit(self.document)).comparisons[0].standing)

    def test_dimensions_and_references_reject_malformed_records(self):
        def duplicate_run(d): d["runs"][1]["run_id"] = d["runs"][0]["run_id"]
        def missing_arm(d): d["runs"].pop(1)
        def duplicate_arm(d): d["runs"][1]["arm"] = "a"
        def duplicate_factor(d): d["runs"][0]["factors"].append(d["runs"][0]["factors"][0])
        def absent_factor(d): d["runs"][0]["factors"].pop()
        def missing_run(d): d["observations"][0]["run_id"] = "absent_run"
        def duplicate_observation(d): d["observations"].append(d["observations"][0])
        def conflicting_oracle(d): d["expected_pairs"].append(d["expected_pairs"][0])
        def unknown_oracle(d): d["expected_pairs"][0]["pair_id"] = "absent_pair"
        for mutation in (duplicate_run, missing_arm, duplicate_arm, duplicate_factor, absent_factor, missing_run, duplicate_observation, conflicting_oracle, unknown_oracle):
            with self.subTest(mutation=mutation.__name__):
                document = deepcopy(self.document)
                mutation(document)
                with self.assertRaises(AdministrativeAdmissionError): admit(document)

    def test_input_output_and_specification_digest_corruption(self):
        for target, field in (("run", "administrative_input"), ("specification", "question"), ("output", "text")):
            with self.subTest(target=target):
                document = deepcopy(self.document)
                receiver = document["runs"][0] if target == "run" else document["specification"] if target == "specification" else document["observations"][0]["scientific_output"]
                receiver[field] += " changed"
                with self.assertRaises(AdministrativeAdmissionError): admit(document)

    def test_source_text_survives_roundtrip_and_model_ownership(self):
        raw = " \tCommercial\n  plan  \u00a0"
        self.document["runs"][0]["administrative_input"] = raw
        rebind(self.document)
        admitted = admit(self.document)
        self.document["runs"][0]["administrative_input"] = "caller mutation"
        self.assertEqual(raw, admitted.runs[0].administrative_input)
        self.assertEqual(admitted, admit_administrative_study(admitted.model_dump_json(by_alias=True).encode()))
        with self.assertRaises(ValidationError): admitted.runs[0].administrative_input = "mutation"

    def test_retry_retains_failures_and_selects_final_attempt(self):
        self.document["specification"]["max_attempts_per_run"] = 2
        first = self.document["observations"][1]
        later = deepcopy(first)
        first.update(status="timeout", reason_code="response_deadline", scientific_output=None, administrative_output=None)
        later.update(observation_id="observation_retry", attempt=2, execution_order=4, started_at="2026-10-13T00:01:00Z", finished_at="2026-10-13T00:01:01Z")
        self.document["observations"].append(later)
        rebind(self.document)
        admitted = admit(self.document)
        self.assertEqual(5, len(admitted.observations))
        self.assertEqual((4, 4), (compare_administrative_study(admitted).attempted, compare_administrative_study(admitted).completed))

    def test_typed_status_and_temporal_boundaries(self):
        mutations = (
            lambda o: o.update(started_at="2026-10-14T00:00:00Z"),
            lambda o: o.update(execution_order=True),
            lambda o: o.update(attempt=2),
            lambda o: o.update(scientific_output=None),
            lambda o: o.update(reason_code="unexpected_reason"),
            lambda o: o.update(status="excluded"),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                document = deepcopy(self.document)
                mutation(document["observations"][0])
                with self.assertRaises(AdministrativeAdmissionError): admit(document)

    def test_byte_depth_duplicate_and_number_bounds(self):
        payload = json.dumps(self.document).encode()
        for budget in (0, True, 33554433):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                admit_administrative_study(payload, max_input_bytes=budget)
        for options in ({"max_input_bytes": 1}, {"max_output_bytes": 1}):
            with self.subTest(options=options), self.assertRaises(AdministrativeAdmissionError):
                admit_administrative_study(payload, **options)
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'\xff', b'[' * 33 + b']' * 33):
            with self.subTest(raw=raw[:30]), self.assertRaises(AdministrativeAdmissionError):
                admit_administrative_study(raw)

    def test_existing_counterfactual_remains_loadable(self):
        self.assertIsNotNone(load_administrative_counterfactual_example())

    def test_report_schema_and_counts_survive_strict_roundtrip(self):
        report = compare_administrative_study(admit(self.document))
        encoded = report.model_dump_json(by_alias=True)
        self.assertEqual(json.loads(encoded)["$schema"], "urn:driftframe:lims-eln:administrative-study-comparison:1.0.0")
        self.assertEqual(report, StudyComparisonReport.model_validate_json(encoded, strict=True))

    def test_report_rejects_incoherent_counts_and_pair_identity(self):
        original = compare_administrative_study(admit(self.document)).model_dump(mode="json", by_alias=True)
        for field in ("planned", "attempted", "completed", "pending", "abstained", "failed", "cancelled", "excluded"):
            for value in (-1, True, 513):
                with self.subTest(field=field, value=value):
                    document = deepcopy(original)
                    document[field] = value
                    with self.assertRaises(ValidationError):
                        StudyComparisonReport.model_validate_json(json.dumps(document), strict=True)
        for mutation in (
            lambda d: d.update(pending=1),
            lambda d: d.update(attempted=3),
            lambda d: d.update(attempted=5),
            lambda d: d["comparisons"].pop(),
            lambda d: d["comparisons"].__setitem__(1, d["comparisons"][0]),
            lambda d: d.update(completed=2, failed=2),
        ):
            document = deepcopy(original)
            mutation(document)
            with self.subTest(document=document), self.assertRaises(ValidationError):
                StudyComparisonReport.model_validate_json(json.dumps(document), strict=True)

    def test_comparison_variant_findings_are_consistent(self):
        comparable = dict(pair_id="pair", standing="comparable", reason_fields=[], scientific_changed=True, administrative_changed=False, expected_invariant_violations=["scientific"], oracle_agrees=True)
        for standing in ("incomplete", "controlled_input_mismatch", "execution_mismatch"):
            valid = dict(comparable, standing=standing, reason_fields=["explicit reason"], scientific_changed=None, administrative_changed=None, expected_invariant_violations=[], oracle_agrees=None)
            StudyPairComparison.model_validate_json(json.dumps(valid), strict=True)
            for changes in ({"scientific_changed": True}, {"administrative_changed": False}, {"oracle_agrees": True}, {"expected_invariant_violations": ["scientific"]}, {"reason_fields": []}):
                with self.subTest(standing=standing, changes=changes), self.assertRaises(ValidationError):
                    StudyPairComparison.model_validate_json(json.dumps(dict(valid, **changes)), strict=True)
        for changes in ({"scientific_changed": None}, {"reason_fields": ["unexpected"]}, {"expected_invariant_violations": ["administrative"]}, {"expected_invariant_violations": ["scientific", "scientific"]}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                StudyPairComparison.model_validate_json(json.dumps(dict(comparable, **changes)), strict=True)

    def test_executed_retry_order_increases(self):
        self.document["specification"]["max_attempts_per_run"] = 2
        first = self.document["observations"][0]
        later = dict(first, observation_id="retry-observation", attempt=2, execution_order=4, started_at="2026-10-13T00:01:00Z", finished_at="2026-10-13T00:01:01Z")
        first.update(status="timeout", reason_code="deadline", execution_order=100, scientific_output=None, administrative_output=None)
        self.document["observations"].append(later)
        rebind(self.document)
        with self.assertRaises(AdministrativeAdmissionError):
            admit(self.document)

    def test_output_encoder_stops_at_the_first_over_budget_chunk(self):
        study = admit(self.document)
        visited = []
        def chunks():
            visited.append("first")
            yield "{}"
            visited.append("second")
            yield " " * 100
        with patch("lims_eln_contracts.administrative_admission.json.JSONEncoder.iterencode", return_value=chunks()):
            with self.assertRaises(AdministrativeAdmissionError):
                _canonical_output(study, 1)
        self.assertEqual(visited, ["first"])
        with patch("lims_eln_contracts.administrative_study._canonical_output", wraps=_canonical_output) as encoder:
            with self.assertRaises(AdministrativeAdmissionError):
                admit_administrative_study(json.dumps(self.document).encode(), max_output_bytes=1)
        encoder.assert_called_once()

    def test_retry_chronology_spans_an_unexecuted_cancellation(self):
        for order, started_at, accepted in (
            (4, "2026-10-13T00:01:00Z", False),
            (101, "2026-10-12T00:01:00Z", False),
            (101, "2026-10-13T00:01:00Z", True),
        ):
            with self.subTest(order=order, started_at=started_at):
                document = deepcopy(self.document)
                document["specification"]["max_attempts_per_run"] = 3
                first = document["observations"][0]
                third = dict(first, observation_id="retry-third", attempt=3, execution_order=order, started_at=started_at, finished_at=started_at)
                cancellation = dict(first, observation_id="cancelled-second", attempt=2, status="cancelled", reason_code="before_start", execution_order=None, execution=None, started_at=None, finished_at=None, scientific_output=None, administrative_output=None)
                first.update(status="timeout", reason_code="deadline", execution_order=100, scientific_output=None, administrative_output=None)
                document["observations"].extend((cancellation, third))
                rebind(document)
                if accepted:
                    observed = admit(document)
                    self.assertEqual(len(observed.observations), 6)
                    self.assertEqual(compare_administrative_study(observed).completed, 4)
                else:
                    with self.assertRaises(AdministrativeAdmissionError):
                        admit(document)

    def test_comparison_states_bound_completed_counts(self):
        original = compare_administrative_study(admit(self.document)).model_dump(mode="json", by_alias=True)
        for standing, completed, pending in (("incomplete", 4, 0), ("execution_mismatch", 0, 4)):
            document = deepcopy(original)
            document.update(completed=completed, attempted=completed, pending=pending)
            for item in document["comparisons"]:
                item.update(standing=standing, reason_fields=["fixture reason"], scientific_changed=None, administrative_changed=None, expected_invariant_violations=[], oracle_agrees=None)
            with self.subTest(standing=standing), self.assertRaises(ValidationError):
                StudyComparisonReport.model_validate_json(json.dumps(document), strict=True)


if __name__ == "__main__":
    unittest.main()
