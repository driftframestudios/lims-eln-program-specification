from __future__ import annotations

from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lims_eln_contracts.canonical import (  # noqa: E402
    canonical_json_bytes,
    canonical_sha256,
    model_from_strict_json,
    strict_json_loads,
)
from lims_eln_contracts.administrative_admission import (  # noqa: E402
    AdministrativeAdmissionError,
    AdministrativeAdmissionLimits,
    admit_administrative_contract,
)
from lims_eln_contracts.external_administrative import (  # noqa: E402
    AdministrativeAdapterContract,
    AdministrativeContext,
    AdministrativeDecision,
    ClassificationDisposition,
    ClassificationState,
    ConflictBehavior,
    CoverageEnrollment,
    DecisionImpactObservation,
    ExternalAdministrativeContractSet,
    InsuranceClassification,
    MissingInputBehavior,
    PolicyEvaluation,
    PolicyEvaluationState,
    PolicyInputDigestMaterial,
    PolicyInputRequirement,
    PolicyRuleSet,
    PopulationCalibrationStanding,
    PopulationScenario,
    ProvenanceAssertion,
    ProvenanceFormation,
    ProvenanceResolutionStatus,
    ReviewDisposition,
    build_policy_input_digest_material,
    external_administrative_schema_documents,
)


RESOURCE_ROOT = ROOT / "src" / "lims_eln_contracts" / "resources"
CONTRACT_SET_PATH = RESOURCE_ROOT / "external-administrative-contracts.v1.json"
ADAPTER_EXAMPLE_PATH = (
    RESOURCE_ROOT / "administrative" / "insurance-administrative-adapter.v1.json"
)
POLICY_EXAMPLE_PATH = (
    RESOURCE_ROOT / "administrative" / "independent-multilabel-policy.v1.json"
)
COUNTERFACTUAL_EXAMPLE_PATH = (
    RESOURCE_ROOT / "administrative" / "administrative-counterfactual.v1.json"
)
SCHEMA_ROOT = RESOURCE_ROOT / "schemas"


def document(path: Path) -> dict:
    value = strict_json_loads(path.read_bytes())
    if not isinstance(value, dict):
        raise AssertionError(f"{path} does not contain one JSON object")
    return value


def parse(model, value: dict):
    return model_from_strict_json(model, json.dumps(value))


def source_calibrated_contract(value: dict) -> dict:
    contract = deepcopy(value)
    scenario = contract["population_scenarios"][0]
    scenario_id = scenario["scenario_id"]
    observation_id = "OBSERVATION-POPULATION-CALIBRATION-V1"
    source_id = "SOURCE-POPULATION-CALIBRATION-V1"
    source_assertion_id = "PROV-POPULATION-CALIBRATION-SOURCE-001"
    scenario_assertion_id = scenario["provenance_refs"][0]
    contract["source_observations"] = [
        {
            "observation_version": "1.0.0",
            "observation_id": observation_id,
            "source_id": source_id,
            "source_version": "1",
            "observed_at": "2026-09-30T12:00:00Z",
            "integrity_standing": "locally_computed_digest",
            "content_digest": "sha256:" + "3" * 64,
            "payload_observed": True,
            "execution_observed": False,
            "supported_claims": [
                "source_field_provenance",
                "population_calibration",
            ],
            "claim_boundary": "The observation supports only the named population-calibration evidence route.",
        }
    ]
    contract["provenance_assertions"].append(
        {
            "assertion_version": "1.0.0",
            "assertion_id": source_assertion_id,
            "subject_refs": [observation_id],
            "formation": "source_exact",
            "standing": "artifact_verified",
            "resolution_status": "resolved",
            "claim": "The observed source bytes supply the declared calibration input.",
            "source_coordinate": {
                "source_observation_ref": observation_id,
                "record": {
                    "namespace_id": source_id,
                    "release_id": "1",
                    "record_type": {
                        "term_id": "record-type:calibration-input",
                        "label": "Calibration input",
                        "vocabulary_id": "urn:driftframe:record-types",
                        "vocabulary_version": "1.0.0",
                    },
                    "local_id": "CALIBRATION-INPUT-001",
                    "source_observation_ref": observation_id,
                },
                "field_path": "population_dimensions",
            },
            "method": None,
            "derived_from_assertion_refs": [],
            "evidence_digest": "sha256:" + "4" * 64,
            "review": None,
        }
    )
    scenario_assertion = next(
        item
        for item in contract["provenance_assertions"]
        if item["assertion_id"] == scenario_assertion_id
    )
    scenario_assertion["derived_from_assertion_refs"] = [source_assertion_id]
    scenario["calibration_standing"] = "source_calibrated"
    scenario["calibration_source_refs"] = [observation_id]
    scenario["calibration_evidence_refs"] = [scenario_assertion_id]
    scenario["claim_boundary"] = (
        "The scenario calibration claim is limited to the observed source and evidence route."
    )
    return contract


class ReleasedExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_document = document(CONTRACT_SET_PATH)
        cls.contract = model_from_strict_json(
            ExternalAdministrativeContractSet,
            CONTRACT_SET_PATH.read_bytes(),
        )

    def test_nine_public_objects_and_three_examples_are_indexed(self) -> None:
        self.assertEqual(
            {
                "AdministrativeAdapterContract",
                "AdministrativeContext",
                "InsuranceClassification",
                "CoverageEnrollment",
                "PolicyRuleSet",
                "AdministrativeDecision",
                "DecisionImpactObservation",
                "PopulationScenario",
                "ProvenanceAssertion",
            },
            {item.object_name for item in self.contract.public_objects},
        )
        self.assertEqual(
            {
                "administrative/insurance-administrative-adapter.v1.json",
                "administrative/independent-multilabel-policy.v1.json",
                "administrative/administrative-counterfactual.v1.json",
            },
            {item.path for item in self.contract.examples},
        )
        self.assertEqual("pending_reviewed_merge", self.contract.adoption_event.state)

    def test_adapter_example_is_source_neutral_modular_and_replay_safe(self) -> None:
        adapter = model_from_strict_json(
            AdministrativeAdapterContract,
            ADAPTER_EXAMPLE_PATH.read_bytes(),
        )
        self.assertEqual("program_authored_synthetic", adapter.data_standing)
        self.assertEqual("design_only", adapter.execution_standing)
        self.assertEqual(
            ("extract", "validate", "normalize", "classify", "map_contract", "emit"),
            tuple(stage.kind.value for stage in adapter.stages),
        )
        self.assertTrue(all(stage.idempotent for stage in adapter.stages))
        self.assertEqual(
            ("record_id", "input_version"),
            adapter.idempotency.key_fields,
        )
        self.assertEqual(
            "same_output_no_additional_effect",
            adapter.idempotency.duplicate_input_effect,
        )
        self.assertEqual(adapter, self.contract.adapter_contracts[0])
        adapter_assertion = next(
            item
            for item in self.contract.provenance_assertions
            if item.assertion_id == "PROV-ADAPTER-CONTRACT-001"
        )
        self.assertEqual("constellation_derived", adapter_assertion.standing.value)
        self.assertLess(ADAPTER_EXAMPLE_PATH.stat().st_size, 10_000)

    def test_population_scenario_declares_its_calibration_boundary(self) -> None:
        scenario = self.contract.population_scenarios[0]
        self.assertEqual(
            PopulationCalibrationStanding.NOT_CALIBRATED,
            scenario.calibration_standing,
        )
        self.assertEqual((), scenario.calibration_source_refs)
        self.assertEqual((), scenario.calibration_evidence_refs)

    def test_independent_example_exercises_exact_classification_boundaries(
        self,
    ) -> None:
        example = model_from_strict_json(
            ExternalAdministrativeContractSet,
            POLICY_EXAMPLE_PATH.read_bytes(),
        )
        self.assertEqual(self.contract.adapter_contracts, example.adapter_contracts)
        classifications = {
            item.classification_id: item for item in example.insurance_classifications
        }
        expected = {
            "CLASS-INSURANCE-MULTI-001": (
                "Commercial + community support bridge",
                ClassificationState.CLASSIFIED,
                (
                    "insurance-category:commercial",
                    "insurance-category:supplemental",
                ),
                True,
            ),
            "CLASS-INSURANCE-SINGLE-001": (
                "Commercial",
                ClassificationState.CLASSIFIED,
                ("insurance-category:commercial",),
                False,
            ),
            "CLASS-INSURANCE-ABSTAIN-001": (
                "Community support arrangement",
                ClassificationState.ABSTAINED,
                (),
                False,
            ),
            "CLASS-INSURANCE-UNKNOWN-001": (
                None,
                ClassificationState.UNKNOWN,
                (),
                False,
            ),
        }
        self.assertEqual(set(expected), set(classifications))
        for classification_id, expectation in expected.items():
            with self.subTest(classification_id=classification_id):
                raw_label, state, assigned_term_ids, multiple = expectation
                classification = classifications[classification_id]
                self.assertEqual(raw_label, classification.raw_label)
                self.assertEqual(state, classification.state)
                self.assertEqual(
                    assigned_term_ids,
                    tuple(term.term_id for term in classification.assigned_terms),
                )
                self.assertEqual(multiple, classification.multiple)
                self.assertEqual(
                    ClassificationDisposition.ACCEPTED,
                    classification.disposition,
                )
                self.assertIsNotNone(classification.review)

        unknown = classifications["CLASS-INSURANCE-UNKNOWN-001"]
        self.assertIn("no raw insurance label", unknown.ambiguity)
        self.assertIn("source evidence", unknown.ambiguity)
        pending = next(
            item
            for item in example.coverage_enrollments
            if item.enrollment_id == "ENROLLMENT-SYNTHETIC-PENDING-001"
        )
        self.assertEqual("pending", pending.state.value)
        self.assertTrue(
            all(decision.review is not None for decision in example.administrative_decisions)
        )

    def test_policy_examples_preserve_conflict_missing_input_and_review_override(
        self,
    ) -> None:
        decisions = {
            item.decision_id: item for item in self.contract.administrative_decisions
        }
        policy = self.contract.policy_rule_sets[0]
        baseline = decisions["DECISION-ADMIN-BASELINE-001"]
        baseline_evaluation = baseline.policy_evaluation
        self.assertEqual(
            (
                "RULE-MULTILABEL-001",
                "RULE-COMMERCIAL-ACTIVE-FALLBACK-001",
            ),
            baseline_evaluation.matched_rule_refs,
        )
        self.assertEqual(
            baseline_evaluation.matched_rule_refs,
            baseline_evaluation.conflicting_rule_refs,
        )
        self.assertEqual(
            "RULE-MULTILABEL-001", baseline_evaluation.selected_rule_ref
        )
        self.assertEqual(PolicyEvaluationState.ASSIGNED, baseline_evaluation.state)
        self.assertEqual(
            "policy-outcome:manual_review", baseline_evaluation.outcome.term_id
        )
        self.assertEqual("policy-outcome:evidence_request", baseline.outcome.term_id)
        self.assertEqual(ReviewDisposition.REVISE, baseline.review.disposition)

        missing = decisions["DECISION-ADMIN-MISSING-INPUT-001"]
        missing_evaluation = missing.policy_evaluation
        self.assertEqual(("enrollment_state",), missing_evaluation.missing_input_ids)
        self.assertEqual((), missing_evaluation.matched_rule_refs)
        self.assertEqual((), missing_evaluation.conflicting_rule_refs)
        self.assertIsNone(missing_evaluation.selected_rule_ref)
        self.assertEqual(PolicyEvaluationState.ABSTAINED, missing_evaluation.state)
        self.assertIsNone(missing_evaluation.outcome)
        self.assertEqual((), missing.enrollment_refs)
        self.assertEqual("policy-outcome:evidence_request", missing.outcome.term_id)
        self.assertEqual(ReviewDisposition.ACCEPT, missing.review.disposition)

        for decision in decisions.values():
            with self.subTest(decision_id=decision.decision_id):
                self.assertEqual(
                    policy.policy_digest,
                    decision.policy_evaluation.policy_digest,
                )

    def test_counterfactual_example_keeps_clinical_digests_equal(self) -> None:
        observation = model_from_strict_json(
            DecisionImpactObservation,
            COUNTERFACTUAL_EXAMPLE_PATH.read_bytes(),
        )
        self.assertEqual(
            observation.baseline.clinical_evidence_digest,
            observation.counterfactual.clinical_evidence_digest,
        )
        self.assertEqual(
            observation.baseline.clinical_output_digest,
            observation.counterfactual.clinical_output_digest,
        )
        self.assertNotEqual(
            observation.baseline.administrative_input_digest,
            observation.counterfactual.administrative_input_digest,
        )
        self.assertNotEqual(
            observation.baseline.administrative_output_digest,
            observation.counterfactual.administrative_output_digest,
        )
        self.assertEqual(
            "urn:driftframe:lims-eln:policy-input-digest:1.0.0",
            observation.baseline.administrative_input_digest_profile,
        )
        self.assertEqual(
            "urn:driftframe:lims-eln:administrative-decision-digest:1.0.0",
            observation.baseline.administrative_output_digest_profile,
        )
        self.assertEqual(observation, self.contract.impact_observations[0])


class StrictBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract_document = document(CONTRACT_SET_PATH)

    def test_adapter_contract_rejects_coercion_and_unknown_fields(self) -> None:
        adapter = document(ADAPTER_EXAMPLE_PATH)
        coerced = deepcopy(adapter)
        coerced["stages"][0]["sequence"] = "1"
        with self.assertRaises(ValidationError):
            parse(AdministrativeAdapterContract, coerced)

        expanded = deepcopy(adapter)
        expanded["repository_url"] = "https://example.invalid/source"
        with self.assertRaises(ValidationError):
            parse(AdministrativeAdapterContract, expanded)

    def test_adapter_contract_requires_the_modular_stage_order(self) -> None:
        adapter = document(ADAPTER_EXAMPLE_PATH)
        adapter["stages"][2]["kind"] = "classify"
        with self.assertRaisesRegex(ValidationError, "adapter stages retain"):
            parse(AdministrativeAdapterContract, adapter)

    def test_adapter_contract_requires_a_connected_replay_safe_chain(self) -> None:
        adapter = document(ADAPTER_EXAMPLE_PATH)
        adapter["stages"][1]["input_resource"] = "UNRELATED-RESOURCE-V1"
        with self.assertRaisesRegex(ValidationError, "share one resource boundary"):
            parse(AdministrativeAdapterContract, adapter)

        changed_key = document(ADAPTER_EXAMPLE_PATH)
        changed_key["idempotency"]["key_fields"] = ["record_id"]
        with self.assertRaisesRegex(ValidationError, "record_id and input_version"):
            parse(AdministrativeAdapterContract, changed_key)

        changed_input = document(ADAPTER_EXAMPLE_PATH)
        changed_input["input_contract_id"] = "UNRELATED-INPUT-V1"
        with self.assertRaisesRegex(ValidationError, "declared input contract"):
            parse(AdministrativeAdapterContract, changed_input)

        changed_output = document(ADAPTER_EXAMPLE_PATH)
        changed_output["output_bundle_id"] = "UNRELATED-OUTPUT-V1"
        with self.assertRaisesRegex(ValidationError, "declared output bundle"):
            parse(AdministrativeAdapterContract, changed_output)

    def test_bundle_index_binds_schema_and_example_carriers(self) -> None:
        swapped_schema_roots = deepcopy(self.contract_document)
        roots = swapped_schema_roots["schema_roots"]
        roots[0]["root_object"], roots[1]["root_object"] = (
            roots[1]["root_object"],
            roots[0]["root_object"],
        )
        with self.assertRaisesRegex(ValidationError, "schema-root index binds"):
            parse(ExternalAdministrativeContractSet, swapped_schema_roots)

        changed_schema_ids = deepcopy(self.contract_document)
        for index, schema in enumerate(changed_schema_ids["schema_roots"], start=1):
            schema["schema_id"] = f"urn:example:changed-schema:{index}"
        with self.assertRaisesRegex(ValidationError, "schema-root index binds"):
            parse(ExternalAdministrativeContractSet, changed_schema_ids)

        swapped_example_roots = deepcopy(self.contract_document)
        examples = swapped_example_roots["examples"]
        examples[0]["root_object"], examples[2]["root_object"] = (
            examples[2]["root_object"],
            examples[0]["root_object"],
        )
        with self.assertRaisesRegex(ValidationError, "example index binds"):
            parse(ExternalAdministrativeContractSet, swapped_example_roots)

    def test_open_terms_remain_identified_records(self) -> None:
        classification = deepcopy(self.contract_document["insurance_classifications"][0])
        classification["assigned_terms"][0] = "commercial"
        with self.assertRaises(ValidationError):
            parse(InsuranceClassification, classification)

        strict_confidence = deepcopy(
            self.contract_document["insurance_classifications"][0]
        )
        strict_confidence["confidence"] = "0.94"
        with self.assertRaises(ValidationError):
            parse(InsuranceClassification, strict_confidence)

    def test_unknown_classification_can_name_missing_raw_evidence(self) -> None:
        unknown = deepcopy(self.contract_document["insurance_classifications"][0])
        unknown["raw_label"] = None
        unknown["assigned_terms"] = []
        unknown["candidate_terms"] = []
        unknown["state"] = "unknown"
        unknown["multiple"] = False
        unknown["confidence"] = None
        unknown["ambiguity"] = "The source supplies no raw insurance label."
        parsed = parse(InsuranceClassification, unknown)
        self.assertIsNone(parsed.raw_label)
        self.assertEqual(ClassificationState.UNKNOWN, parsed.state)

        missing_classified_label = deepcopy(
            self.contract_document["insurance_classifications"][0]
        )
        missing_classified_label["raw_label"] = None
        with self.assertRaisesRegex(ValidationError, "only unknown"):
            parse(InsuranceClassification, missing_classified_label)

        unknown_with_candidate = deepcopy(unknown)
        unknown_with_candidate["candidate_terms"] = deepcopy(
            self.contract_document["insurance_classifications"][0][
                "assigned_terms"
            ]
        )
        with self.assertRaisesRegex(ValidationError, "assigned or candidate"):
            parse(InsuranceClassification, unknown_with_candidate)

        unexplained_unknown = deepcopy(unknown)
        unexplained_unknown["ambiguity"] = None
        with self.assertRaisesRegex(ValidationError, "evidence boundary"):
            parse(InsuranceClassification, unexplained_unknown)

    def test_final_classification_requires_matching_accountable_review(self) -> None:
        final = deepcopy(self.contract_document["insurance_classifications"][0])
        final["review"] = None
        with self.assertRaisesRegex(ValidationError, "accountable review"):
            parse(InsuranceClassification, final)

        proposed = deepcopy(self.contract_document["insurance_classifications"][0])
        proposed["disposition"] = "proposed"
        with self.assertRaisesRegex(ValidationError, "awaits accountable review"):
            parse(InsuranceClassification, proposed)

    def test_coverage_enrollment_cannot_claim_payer_decision_effect(self) -> None:
        for enrollment in self.contract_document["coverage_enrollments"]:
            self.assertEqual("none", enrollment["payer_decision_effect"])
        mutated = deepcopy(self.contract_document["coverage_enrollments"][0])
        mutated["payer_decision_effect"] = "coverage_granted"
        with self.assertRaises(ValidationError):
            parse(CoverageEnrollment, mutated)

    def test_policy_binds_digest_precedence_missing_and_conflict_behavior(self) -> None:
        policy = parse(PolicyRuleSet, self.contract_document["policy_rule_sets"][0])
        self.assertEqual(policy.policy_digest, policy.calculated_digest())
        self.assertEqual(
            (
                "RULE-ABSTAIN-001",
                "RULE-MULTILABEL-001",
                "RULE-COMMERCIAL-ACTIVE-FALLBACK-001",
            ),
            policy.precedence,
        )
        self.assertEqual(MissingInputBehavior.ABSTAIN, policy.missing_input_behavior)
        self.assertEqual(ConflictBehavior.HIGHEST_PRECEDENCE, policy.conflict_behavior)
        with self.assertRaises(ValueError):
            MissingInputBehavior("use_declared_defaults")

        stale_digest = deepcopy(self.contract_document["policy_rule_sets"][0])
        stale_digest["rules"][0]["description"] = "Changed without a new digest."
        with self.assertRaisesRegex(ValidationError, "policy_digest"):
            parse(PolicyRuleSet, stale_digest)

        incomplete_precedence = deepcopy(self.contract_document["policy_rule_sets"][0])
        incomplete_precedence["precedence"] = ["RULE-ABSTAIN-001"]
        with self.assertRaisesRegex(ValidationError, "every declared rule"):
            parse(PolicyRuleSet, incomplete_precedence)

        single_rule_conflict = deepcopy(
            self.contract_document["administrative_decisions"][0][
                "policy_evaluation"
            ]
        )
        single_rule_conflict["conflicting_rule_refs"] = ["RULE-MULTILABEL-001"]
        with self.assertRaisesRegex(ValidationError, "at least two matched rules"):
            parse(PolicyEvaluation, single_rule_conflict)

    def test_final_decision_requires_review_and_contiguous_history(self) -> None:
        decision = deepcopy(self.contract_document["administrative_decisions"][0])
        decision["review"] = None
        with self.assertRaisesRegex(ValidationError, "accountable review"):
            parse(AdministrativeDecision, decision)

        broken_history = deepcopy(self.contract_document["administrative_decisions"][0])
        broken_history["transitions"][1]["from_state"] = "draft"
        with self.assertRaises(ValidationError):
            parse(AdministrativeDecision, broken_history)

        declining_review = deepcopy(
            self.contract_document["administrative_decisions"][0]
        )
        declining_review["review"]["disposition"] = "decline"
        with self.assertRaisesRegex(ValidationError, "authorizing review disposition"):
            parse(AdministrativeDecision, declining_review)

        self_review = deepcopy(self.contract_document["administrative_decisions"][0])
        self_review["review"]["reviewer_id"] = self_review["actor"]["actor_id"]
        with self.assertRaisesRegex(ValidationError, "actor distinct"):
            parse(AdministrativeDecision, self_review)

        regressing_time = deepcopy(
            self.contract_document["administrative_decisions"][0]
        )
        regressing_time["transitions"][1]["transitioned_at"] = (
            "2026-10-01T14:09:59Z"
        )
        with self.assertRaisesRegex(ValidationError, "progress monotonically"):
            parse(AdministrativeDecision, regressing_time)

        late_review = deepcopy(self.contract_document["administrative_decisions"][0])
        late_review["review"]["reviewed_at"] = "2026-10-01T14:12:01Z"
        with self.assertRaisesRegex(ValidationError, "no later than"):
            parse(AdministrativeDecision, late_review)

        late_evaluation = deepcopy(
            self.contract_document["administrative_decisions"][0]
        )
        late_evaluation["policy_evaluation"]["evaluated_at"] = (
            "2026-10-01T14:10:01Z"
        )
        with self.assertRaisesRegex(ValidationError, "no later than the decision proposal"):
            parse(AdministrativeDecision, late_evaluation)

        early_review = deepcopy(self.contract_document["administrative_decisions"][0])
        early_review["review"]["reviewed_at"] = "2026-10-01T14:10:59Z"
        with self.assertRaisesRegex(ValidationError, "after the decision enters review"):
            parse(AdministrativeDecision, early_review)

        unrelated_proposer = deepcopy(
            self.contract_document["administrative_decisions"][0]
        )
        unrelated_proposer["transitions"][0]["actor_id"] = "ACTOR-UNRELATED-001"
        with self.assertRaisesRegex(ValidationError, "declared decision actor"):
            parse(AdministrativeDecision, unrelated_proposer)

        unrelated_reviewer = deepcopy(
            self.contract_document["administrative_decisions"][0]
        )
        unrelated_reviewer["transitions"][2]["actor_id"] = "ACTOR-UNRELATED-001"
        with self.assertRaisesRegex(ValidationError, "accountable reviewer"):
            parse(AdministrativeDecision, unrelated_reviewer)

    def test_population_calibration_requires_source_and_evidence_together(self) -> None:
        scenario = deepcopy(self.contract_document["population_scenarios"][0])
        scenario["calibration_standing"] = "source_calibrated"
        with self.assertRaisesRegex(ValidationError, "source and evidence references"):
            parse(PopulationScenario, scenario)

        uncalibrated_with_source = deepcopy(
            self.contract_document["population_scenarios"][0]
        )
        uncalibrated_with_source["calibration_source_refs"] = [
            "ADAPTER-INSURANCE-ADMINISTRATIVE-V1"
        ]
        with self.assertRaisesRegex(ValidationError, "references empty"):
            parse(PopulationScenario, uncalibrated_with_source)

    def test_provenance_separates_formation_resolution_and_review(self) -> None:
        with self.assertRaises(ValueError):
            ProvenanceFormation("unresolved_flagged")

        deterministic = next(
            deepcopy(item)
            for item in self.contract_document["provenance_assertions"]
            if item["assertion_id"] == "PROV-CLASSIFICATION-MULTI-001"
        )
        accepted_review = next(
            deepcopy(item["review"])
            for item in self.contract_document["provenance_assertions"]
            if item["assertion_id"] == "PROV-POLICY-RULESET-001"
        )
        deterministic["standing"] = "accountably_reviewed"
        deterministic["review"] = accepted_review
        parsed = parse(ProvenanceAssertion, deterministic)
        self.assertEqual(
            ProvenanceResolutionStatus.RESOLVED,
            parsed.resolution_status,
        )

        declined = deepcopy(deterministic)
        declined["review"]["disposition"] = "decline"
        with self.assertRaisesRegex(ValidationError, "non-declining review"):
            parse(ProvenanceAssertion, declined)

        unresolved = deepcopy(deterministic)
        unresolved["resolution_status"] = "unresolved_flagged"
        with self.assertRaisesRegex(ValidationError, "resolved status"):
            parse(ProvenanceAssertion, unresolved)

        wrong_method = deepcopy(deterministic)
        wrong_method["method"]["kind"] = "generated_fixture"
        wrong_method["method"].pop("code")
        with self.assertRaisesRegex(ValidationError, "matching method kind"):
            parse(ProvenanceAssertion, wrong_method)

        source_exact = next(
            deepcopy(item)
            for item in self.contract_document["provenance_assertions"]
            if item["assertion_id"] == "PROV-ADAPTER-CONTRACT-001"
        )
        source_exact["formation"] = "source_exact"
        source_exact["standing"] = "source_reported"
        source_exact["source_coordinate"] = {
            "source_observation_ref": "OBSERVATION-REPRESENTATIVE-INPUT-V1",
            "record": {
                "namespace_id": "SOURCE-REPRESENTATIVE-INPUT-V1",
                "release_id": "1",
                "record_type": {
                    "term_id": "record-type:adapter-input",
                    "label": "Adapter input",
                    "vocabulary_id": "urn:driftframe:record-types",
                    "vocabulary_version": "1.0.0"
                },
                "local_id": "ADAPTER-INPUT-MULTILABEL-001",
                "source_observation_ref": "OBSERVATION-REPRESENTATIVE-INPUT-V1"
            },
            "field_path": "values.raw_insurance_label"
        }
        source_exact["method"] = deepcopy(
            self.contract_document["population_scenarios"][0][
                "construction_method"
            ]
        )
        with self.assertRaisesRegex(ValidationError, "no local method"):
            parse(ProvenanceAssertion, source_exact)

        source_exact["method"] = None
        source_exact["standing"] = "constellation_derived"
        with self.assertRaisesRegex(ValidationError, "source-reported"):
            parse(ProvenanceAssertion, source_exact)

    def test_counterfactual_rejects_clinical_drift_and_equal_administrative_output(
        self,
    ) -> None:
        observation = document(COUNTERFACTUAL_EXAMPLE_PATH)
        clinical_drift = deepcopy(observation)
        clinical_drift["counterfactual"]["clinical_output_digest"] = (
            "sha256:" + "0" * 64
        )
        with self.assertRaisesRegex(ValidationError, "clinical output unchanged"):
            parse(DecisionImpactObservation, clinical_drift)

        no_administrative_change = deepcopy(observation)
        no_administrative_change["counterfactual"]["administrative_output_digest"] = (
            no_administrative_change["baseline"]["administrative_output_digest"]
        )
        with self.assertRaisesRegex(ValidationError, "changes administrative digests"):
            parse(DecisionImpactObservation, no_administrative_change)

        same_context = deepcopy(observation)
        same_context["counterfactual"]["context_ref"] = same_context["baseline"][
            "context_ref"
        ]
        with self.assertRaisesRegex(ValidationError, "distinct contexts"):
            parse(DecisionImpactObservation, same_context)

        same_decision = deepcopy(observation)
        same_decision["counterfactual"]["decision_ref"] = same_decision["baseline"][
            "decision_ref"
        ]
        with self.assertRaisesRegex(ValidationError, "distinct decisions"):
            parse(DecisionImpactObservation, same_decision)


class RelationshipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract_document = document(CONTRACT_SET_PATH)

    def test_adapter_records_and_stages_keep_unique_identities(self) -> None:
        duplicate_record = deepcopy(self.contract_document)
        records = duplicate_record["adapter_contracts"][0]["representative_records"]
        records[1]["record_id"] = records[0]["record_id"]
        with self.assertRaisesRegex(ValidationError, "record identifiers remain unique"):
            parse(ExternalAdministrativeContractSet, duplicate_record)

        duplicate_stage = deepcopy(self.contract_document)
        stages = duplicate_stage["adapter_contracts"][0]["stages"]
        stages[1]["stage_id"] = stages[0]["stage_id"]
        with self.assertRaisesRegex(ValidationError, "stage identifiers remain unique"):
            parse(ExternalAdministrativeContractSet, duplicate_stage)

    def test_population_calibration_resolves_a_source_observation(self) -> None:
        broken = deepcopy(self.contract_document)
        scenario = broken["population_scenarios"][0]
        scenario["calibration_standing"] = "source_calibrated"
        scenario["calibration_source_refs"] = [
            "ADAPTER-INSURANCE-ADMINISTRATIVE-V1"
        ]
        scenario["calibration_evidence_refs"] = ["PROV-ADAPTER-CONTRACT-001"]
        with self.assertRaisesRegex(ValidationError, "calibration source reference"):
            parse(ExternalAdministrativeContractSet, broken)

        calibrated = source_calibrated_contract(self.contract_document)
        parsed = parse(ExternalAdministrativeContractSet, calibrated)
        self.assertEqual(
            PopulationCalibrationStanding.SOURCE_CALIBRATED,
            parsed.population_scenarios[0].calibration_standing,
        )

        unsupported = deepcopy(calibrated)
        unsupported["source_observations"][0]["supported_claims"] = [
            "source_field_provenance"
        ]
        with self.assertRaisesRegex(
            ValidationError, "source observation supports the calibration claim"
        ):
            parse(ExternalAdministrativeContractSet, unsupported)

        unrelated = deepcopy(calibrated)
        unrelated["population_scenarios"][0]["calibration_evidence_refs"] = [
            "PROV-ADAPTER-CONTRACT-001"
        ]
        with self.assertRaisesRegex(
            ValidationError, "evidence names the population scenario"
        ):
            parse(ExternalAdministrativeContractSet, unrelated)

        untraced = deepcopy(calibrated)
        scenario_assertion = next(
            item
            for item in untraced["provenance_assertions"]
            if item["assertion_id"] == "PROV-POPULATION-SCENARIO-001"
        )
        scenario_assertion["derived_from_assertion_refs"] = []
        with self.assertRaisesRegex(
            ValidationError, "evidence traces exactly to its declared source observations"
        ):
            parse(ExternalAdministrativeContractSet, untraced)

    def test_source_exact_provenance_resolves_integrity_observation(self) -> None:
        contract = deepcopy(self.contract_document)
        contract["source_observations"] = [
            {
                "observation_version": "1.0.0",
                "observation_id": "OBSERVATION-REPRESENTATIVE-INPUT-V1",
                "source_id": "SOURCE-REPRESENTATIVE-INPUT-V1",
                "source_version": "1",
                "observed_at": "2026-09-30T12:00:00Z",
                "integrity_standing": "reported_digest",
                "content_digest": "sha256:" + "1" * 64,
                "payload_observed": False,
                "execution_observed": False,
                "supported_claims": ["source_field_provenance"],
                "claim_boundary": "The observation establishes only the named source identity, version, and reported digest."
            }
        ]
        assertion = next(
            item
            for item in contract["provenance_assertions"]
            if item["assertion_id"] == "PROV-ADAPTER-CONTRACT-001"
        )
        assertion["formation"] = "source_exact"
        assertion["standing"] = "source_reported"
        assertion["source_coordinate"] = {
            "source_observation_ref": "OBSERVATION-REPRESENTATIVE-INPUT-V1",
            "record": {
                "namespace_id": "SOURCE-REPRESENTATIVE-INPUT-V1",
                "release_id": "1",
                "record_type": {
                    "term_id": "record-type:adapter-input",
                    "label": "Adapter input",
                    "vocabulary_id": "urn:driftframe:record-types",
                    "vocabulary_version": "1.0.0"
                },
                "local_id": "ADAPTER-INPUT-MULTILABEL-001",
                "source_observation_ref": "OBSERVATION-REPRESENTATIVE-INPUT-V1"
            },
            "field_path": "values.raw_insurance_label"
        }
        assertion["method"] = None
        parsed = parse(ExternalAdministrativeContractSet, contract)
        self.assertEqual(1, len(parsed.source_observations))

        mismatched = deepcopy(contract)
        mismatched["source_observations"][0]["source_version"] = "2"
        with self.assertRaisesRegex(ValidationError, "source identity and version"):
            parse(ExternalAdministrativeContractSet, mismatched)

        overclaimed = deepcopy(contract)
        source_assertion = next(
            item
            for item in overclaimed["provenance_assertions"]
            if item["assertion_id"] == "PROV-ADAPTER-CONTRACT-001"
        )
        source_assertion["standing"] = "artifact_verified"
        with self.assertRaisesRegex(ValidationError, "locally computed digest"):
            parse(ExternalAdministrativeContractSet, overclaimed)

    def test_external_context_uses_one_resolved_source_observation(self) -> None:
        contract = deepcopy(self.contract_document)
        contract["source_observations"] = [
            {
                "observation_version": "1.0.0",
                "observation_id": "OBSERVATION-EXTERNAL-CONTEXT-V1",
                "source_id": "SOURCE-EXTERNAL-CONTEXT-V1",
                "source_version": "1",
                "observed_at": "2026-09-30T12:00:00Z",
                "integrity_standing": "reported_digest",
                "content_digest": "sha256:" + "2" * 64,
                "payload_observed": False,
                "execution_observed": False,
                "supported_claims": ["administrative_context"],
                "claim_boundary": "The observation establishes only the named source identity, version, and reported digest."
            }
        ]
        for context in contract["administrative_contexts"]:
            context["source_class"] = "observed_external_source"
            context["evidence_standing"] = "source_reported"
            for scoped_name in ("subject", "episode"):
                scoped = context[scoped_name]
                scoped["namespace_id"] = "SOURCE-EXTERNAL-CONTEXT-V1"
                scoped["release_id"] = "1"
                scoped["source_observation_ref"] = (
                    "OBSERVATION-EXTERNAL-CONTEXT-V1"
                )
        parsed = parse(ExternalAdministrativeContractSet, contract)
        self.assertEqual(2, len(parsed.administrative_contexts))

        overclaimed = deepcopy(contract)
        for context in overclaimed["administrative_contexts"]:
            context["evidence_standing"] = "artifact_verified"
        with self.assertRaisesRegex(ValidationError, "locally computed digest"):
            parse(ExternalAdministrativeContractSet, overclaimed)

    def test_authorized_effect_requires_operational_context_evidence(self) -> None:
        broken = deepcopy(self.contract_document)
        decision = broken["administrative_decisions"][0]
        decision["effect"] = "authorized_administrative"
        broken["impact_observations"][0]["baseline"][
            "administrative_output_digest"
        ] = canonical_sha256(parse(AdministrativeDecision, decision))
        with self.assertRaisesRegex(
            ValidationError,
            "authorized operational context.*operationally observed evidence",
        ):
            parse(ExternalAdministrativeContractSet, broken)

    def test_cross_record_references_resolve(self) -> None:
        broken = deepcopy(self.contract_document)
        broken["administrative_decisions"][0]["classification_refs"] = [
            "CLASS-MISSING-001"
        ]
        with self.assertRaisesRegex(ValidationError, "reference .* resolves"):
            parse(ExternalAdministrativeContractSet, broken)

    def test_object_provenance_assertions_name_their_subject(self) -> None:
        broken = deepcopy(self.contract_document)
        broken["insurance_classifications"][0]["provenance_refs"] = [
            "PROV-CONTEXT-BASELINE-001"
        ]
        with self.assertRaisesRegex(
            ValidationError,
            "provenance assertion names the referenced object",
        ):
            parse(ExternalAdministrativeContractSet, broken)

    def test_policy_evaluation_retains_policy_digest(self) -> None:
        broken = deepcopy(self.contract_document)
        broken["administrative_decisions"][0]["policy_evaluation"][
            "policy_digest"
        ] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValidationError, "released policy digest"):
            parse(ExternalAdministrativeContractSet, broken)

    def test_policy_input_digest_binds_cited_normalized_inputs(self) -> None:
        stale_digest = deepcopy(self.contract_document)
        stale_digest["administrative_decisions"][0]["policy_evaluation"][
            "input_digest"
        ] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValidationError, "cited normalized inputs"):
            parse(ExternalAdministrativeContractSet, stale_digest)

        stale_material = deepcopy(self.contract_document)
        stale_material["administrative_decisions"][0]["policy_evaluation"][
            "input_material"
        ]["context_ref"] = "CTX-ADMIN-COUNTERFACTUAL-001"
        with self.assertRaisesRegex(ValidationError, "material equals"):
            parse(ExternalAdministrativeContractSet, stale_material)

        changed_term = deepcopy(self.contract_document)
        changed_term["insurance_classifications"][0]["assigned_terms"][0][
            "term_id"
        ] = "insurance-category:changed"
        with self.assertRaisesRegex(ValidationError, "cited normalized inputs"):
            parse(ExternalAdministrativeContractSet, changed_term)

        changed_enrollment = deepcopy(self.contract_document)
        changed_enrollment["coverage_enrollments"][0]["state"] = "pending"
        with self.assertRaisesRegex(ValidationError, "cited normalized inputs"):
            parse(ExternalAdministrativeContractSet, changed_enrollment)

        changed_labels = deepcopy(self.contract_document)
        changed_labels["insurance_classifications"][0]["raw_label"] = (
            "A display-only revision"
        )
        changed_labels["insurance_classifications"][0]["assigned_terms"][0][
            "label"
        ] = "Commercial display revision"
        parse(ExternalAdministrativeContractSet, changed_labels)

    def test_impact_arm_digests_bind_referenced_decision_records(self) -> None:
        wrong_input = deepcopy(self.contract_document)
        wrong_input["impact_observations"][0]["baseline"][
            "administrative_input_digest"
        ] = "sha256:" + "9" * 64
        wrong_input["impact_observations"][0]["changed_variable"][
            "baseline_digest"
        ] = "sha256:" + "9" * 64
        with self.assertRaisesRegex(ValidationError, "policy input digest"):
            parse(ExternalAdministrativeContractSet, wrong_input)

        wrong_output = deepcopy(self.contract_document)
        wrong_output["impact_observations"][0]["baseline"][
            "administrative_output_digest"
        ] = "sha256:" + "9" * 64
        with self.assertRaisesRegex(ValidationError, "canonical decision digest"):
            parse(ExternalAdministrativeContractSet, wrong_output)

        wrong_profile = deepcopy(self.contract_document)
        wrong_profile["impact_observations"][0]["baseline"][
            "administrative_output_digest_profile"
        ] = "urn:example:undefined-profile:1"
        with self.assertRaises(ValidationError):
            parse(ExternalAdministrativeContractSet, wrong_profile)

    def _repeated_impacts(self, count: int) -> dict:
        value = deepcopy(self.contract_document)
        impact = value["impact_observations"][0]
        provenance = next(
            row for row in value["provenance_assertions"]
            if row["assertion_id"] == impact["provenance_refs"][0]
        )
        for index in range(1, count):
            repeated = deepcopy(impact)
            repeated["observation_id"] = f"IMPACT-REUSED-{index}"
            proof = deepcopy(provenance)
            proof["assertion_id"] = f"PROV-IMPACT-REUSED-{index}"
            proof["subject_refs"] = [repeated["observation_id"]]
            repeated["provenance_refs"] = [proof["assertion_id"]]
            value["impact_observations"].append(repeated)
            value["provenance_assertions"].append(proof)
        return value

    def test_impact_digest_preparation_is_owned_by_each_admission(self) -> None:
        value = self._repeated_impacts(32)
        payload = canonical_json_bytes(value)
        expected_output = canonical_json_bytes(parse(ExternalAdministrativeContractSet, value))
        expected_ids = {
            value["impact_observations"][0][arm]["decision_ref"]
            for arm in ("baseline", "counterfactual")
        }
        calls = Counter()
        limits = AdministrativeAdmissionLimits(
            max_input_bytes=2 * 1024 * 1024, max_json_depth=32,
            max_decoded_values=200_000, max_records=2_000,
            max_provenance_edges=8_000, max_graph_steps=100_000,
            max_output_bytes=2 * 1024 * 1024,
        )

        def observe(item):
            if isinstance(item, AdministrativeDecision):
                calls[item.decision_id] += 1
            return canonical_sha256(item)

        with patch("lims_eln_contracts.external_administrative.canonical_sha256", side_effect=observe):
            for invocation in (1, 2):
                admitted = admit_administrative_contract(payload, limits=limits)
                self.assertEqual(expected_output, admitted.canonical_bytes)
                self.assertEqual({key: invocation for key in expected_ids}, calls)
        self.assertEqual(payload, canonical_json_bytes(value))

    def test_later_impact_arm_still_checks_its_own_output_digest(self) -> None:
        value = self._repeated_impacts(3)
        value["impact_observations"][-1]["baseline"]["administrative_output_digest"] = "sha256:" + "9" * 64
        with self.assertRaisesRegex(ValidationError, "canonical decision digest"):
            parse(ExternalAdministrativeContractSet, value)

    def test_reused_decisions_retain_each_later_arms_relationship_checks(self) -> None:
        value = self._repeated_impacts(3)
        first = value["impact_observations"][0]
        changed_digest = "sha256:" + "9" * 64
        cases = (
            (
                "unresolved context",
                {"baseline": {"context_ref": "CONTEXT-UNRESOLVED"}},
                "impact context reference",
            ),
            (
                "exchanged contexts",
                {
                    "baseline": {"context_ref": first["counterfactual"]["context_ref"]},
                    "counterfactual": {"context_ref": first["baseline"]["context_ref"]},
                },
                "decision retains the arm context",
            ),
            (
                "paired clinical evidence",
                {
                    "baseline": {"clinical_evidence_digest": changed_digest},
                    "counterfactual": {"clinical_evidence_digest": changed_digest},
                },
                "clinical evidence equals its context evidence",
            ),
            (
                "administrative input",
                {
                    "baseline": {"administrative_input_digest": changed_digest},
                    "changed_variable": {"baseline_digest": changed_digest},
                },
                "administrative input equals its policy input digest",
            ),
        )
        limits = AdministrativeAdmissionLimits(
            max_input_bytes=2 * 1024 * 1024, max_json_depth=32,
            max_decoded_values=200_000, max_records=2_000,
            max_provenance_edges=8_000, max_graph_steps=100_000,
            max_output_bytes=2 * 1024 * 1024,
        )
        for label, changes, expected_error in cases:
            with self.subTest(relationship=label):
                changed = deepcopy(value)
                later = changed["impact_observations"][-1]
                for owner, fields in changes.items():
                    later[owner].update(fields)
                # The arm pair is locally valid; its links into the admitted graph differ.
                parse(DecisionImpactObservation, later)
                with self.assertRaisesRegex(ValidationError, expected_error):
                    parse(ExternalAdministrativeContractSet, changed)
                payload = canonical_json_bytes(changed)
                with self.assertRaises(AdministrativeAdmissionError) as caught:
                    admit_administrative_contract(payload, limits=limits)
                self.assertEqual("contract_validation", caught.exception.code)

    def test_changed_decision_content_is_rechecked_in_a_later_invocation(self) -> None:
        value = self._repeated_impacts(3)
        parse(ExternalAdministrativeContractSet, value)
        value["administrative_decisions"][0]["reason_terms"][0]["label"] = "A revised decision explanation"
        with self.assertRaisesRegex(ValidationError, "canonical decision digest"):
            parse(ExternalAdministrativeContractSet, value)

    def test_policy_input_profile_derives_missing_and_order_stably(self) -> None:
        classifications = {
            item["classification_id"]: parse(InsuranceClassification, item)
            for item in self.contract_document["insurance_classifications"]
        }
        enrollments = {
            item["enrollment_id"]: parse(CoverageEnrollment, item)
            for item in self.contract_document["coverage_enrollments"]
        }
        policy = parse(PolicyRuleSet, self.contract_document["policy_rule_sets"][0])

        baseline_document = deepcopy(
            self.contract_document["administrative_decisions"][0]
        )
        baseline_document["classification_refs"] = [
            "CLASS-INSURANCE-MULTI-001",
            "CLASS-INSURANCE-SINGLE-001",
        ]
        forward = parse(AdministrativeDecision, baseline_document)
        baseline_document["classification_refs"].reverse()
        reverse = parse(AdministrativeDecision, baseline_document)
        self.assertEqual(
            build_policy_input_digest_material(
                forward, policy, classifications, enrollments
            ).calculated_digest(),
            build_policy_input_digest_material(
                reverse, policy, classifications, enrollments
            ).calculated_digest(),
        )

        missing_document = deepcopy(
            self.contract_document["administrative_decisions"][2]
        )
        missing = parse(AdministrativeDecision, missing_document)
        material = build_policy_input_digest_material(
            missing, policy, classifications, enrollments
        )
        by_id = {item.input_id: item for item in material.inputs}
        self.assertEqual("present", by_id["classification_term_ids"].availability)
        self.assertEqual((), by_id["classification_term_ids"].values)
        self.assertEqual("missing", by_id["enrollment_state"].availability)

        unsupported_policy = policy.model_copy(
            update={
                "input_requirements": policy.input_requirements
                + (
                    PolicyInputRequirement(
                        input_id="unsupported_input",
                        description="A profile-external input.",
                        required=False,
                    ),
                )
            }
        )
        with self.assertRaisesRegex(ValueError, "does not define input"):
            build_policy_input_digest_material(
                missing,
                unsupported_policy,
                classifications,
                enrollments,
            )

    def test_policy_matches_and_missing_inputs_are_derived(self) -> None:
        wrong_matches = deepcopy(self.contract_document)
        wrong_matches["administrative_decisions"][0]["policy_evaluation"][
            "matched_rule_refs"
        ] = ["RULE-MULTILABEL-001"]
        wrong_matches["administrative_decisions"][0]["policy_evaluation"][
            "conflicting_rule_refs"
        ] = []
        with self.assertRaisesRegex(ValidationError, "declared predicates"):
            parse(ExternalAdministrativeContractSet, wrong_matches)

        wrong_missing = deepcopy(self.contract_document)
        wrong_missing["administrative_decisions"][2]["policy_evaluation"][
            "missing_input_ids"
        ] = []
        with self.assertRaisesRegex(ValidationError, "absent required inputs"):
            parse(ExternalAdministrativeContractSet, wrong_missing)

    def test_policy_evaluation_occurs_during_policy_effectivity(self) -> None:
        broken = deepcopy(self.contract_document)
        broken["administrative_decisions"][0]["policy_evaluation"][
            "evaluated_at"
        ] = "2025-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValidationError, "effective interval"):
            parse(ExternalAdministrativeContractSet, broken)

    def test_selected_rule_evaluation_and_decision_outcomes_agree(self) -> None:
        wrong_evaluation = deepcopy(self.contract_document)
        wrong_evaluation["administrative_decisions"][0]["policy_evaluation"][
            "outcome"
        ] = deepcopy(
            wrong_evaluation["policy_rule_sets"][0]["rules"][0]["outcome"]
        )
        with self.assertRaisesRegex(ValidationError, "selected rule outcome"):
            parse(ExternalAdministrativeContractSet, wrong_evaluation)

        wrong_decision = deepcopy(self.contract_document)
        wrong_decision["administrative_decisions"][1]["outcome"] = deepcopy(
            wrong_decision["policy_rule_sets"][0]["rules"][1]["outcome"]
        )
        with self.assertRaisesRegex(ValidationError, "policy evaluation outcome"):
            parse(ExternalAdministrativeContractSet, wrong_decision)

        parsed = parse(
            ExternalAdministrativeContractSet,
            deepcopy(self.contract_document),
        )
        baseline = parsed.administrative_decisions[0]
        self.assertEqual(ReviewDisposition.REVISE, baseline.review.disposition)
        self.assertNotEqual(baseline.outcome, baseline.policy_evaluation.outcome)

        unchanged_revision = deepcopy(self.contract_document)
        unchanged_revision["administrative_decisions"][0]["outcome"] = deepcopy(
            unchanged_revision["administrative_decisions"][0]["policy_evaluation"][
                "outcome"
            ]
        )
        with self.assertRaisesRegex(ValidationError, "revision changes"):
            parse(ExternalAdministrativeContractSet, unchanged_revision)

    def test_provenance_graph_rejects_missing_parent_and_cycle(self) -> None:
        missing = deepcopy(self.contract_document)
        classification = next(
            item
            for item in missing["provenance_assertions"]
            if item["assertion_id"] == "PROV-CLASSIFICATION-MULTI-001"
        )
        classification["derived_from_assertion_refs"] = ["PROV-MISSING-001"]
        with self.assertRaisesRegex(ValidationError, "provenance parent"):
            parse(ExternalAdministrativeContractSet, missing)

        cyclic = deepcopy(self.contract_document)
        baseline_context = next(
            item
            for item in cyclic["provenance_assertions"]
            if item["assertion_id"] == "PROV-CONTEXT-BASELINE-001"
        )
        baseline_context["derived_from_assertion_refs"] = [
            "PROV-DECISION-BASELINE-001"
        ]
        with self.assertRaisesRegex(ValidationError, "acyclic"):
            parse(ExternalAdministrativeContractSet, cyclic)

    def test_accountable_review_evidence_references_resolve(self) -> None:
        broken = deepcopy(self.contract_document)
        broken["insurance_classifications"][0]["review"]["evidence_refs"] = [
            "PROV-MISSING-REVIEW-001"
        ]
        with self.assertRaisesRegex(ValidationError, "review provenance"):
            parse(ExternalAdministrativeContractSet, broken)


class GeneratedSchemaTests(unittest.TestCase):
    def test_policy_input_profile_is_machine_carried_and_public(self) -> None:
        import lims_eln_contracts

        schema = external_administrative_schema_documents()[
            "external-administrative-contract-set.v1.schema.json"
        ]
        self.assertIn("PolicyInputDigestMaterial", schema["$defs"])
        self.assertIs(
            PolicyInputDigestMaterial,
            lims_eln_contracts.PolicyInputDigestMaterial,
        )
        self.assertIs(
            build_policy_input_digest_material,
            lims_eln_contracts.build_policy_input_digest_material,
        )

    def test_external_schema_helper_delegates_to_schema_artifact_registry(self) -> None:
        from lims_eln_contracts.schema_artifacts import SCHEMA_ARTIFACTS

        expected = {
            artifact.filename: artifact.document()
            for artifact in SCHEMA_ARTIFACTS
            if artifact.filename
            in {
                "administrative-adapter-contract.v1.schema.json",
                "external-administrative-contract-set.v1.schema.json",
            }
        }
        self.assertEqual(expected, external_administrative_schema_documents())

    def test_repository_schema_index_names_current_schema_identities(self) -> None:
        index = (ROOT / "schemas" / "README.md").read_text(encoding="utf-8")
        schema_paths = (
            ROOT / "schemas" / "program-release-observation.v1.schema.json",
            ROOT / "schemas" / "promotion-receipt.schema.json",
            SCHEMA_ROOT / "administrative-adapter-contract.v1.schema.json",
            SCHEMA_ROOT / "external-administrative-contract-set.v1.schema.json",
        )
        for path in schema_paths:
            with self.subTest(path=path.name):
                self.assertIn(document(path)["$id"], index)

    def test_schema_roots_are_identified_self_contained_draft_2020_12(self) -> None:
        schemas = external_administrative_schema_documents()
        self.assertEqual(
            {
                "administrative-adapter-contract.v1.schema.json",
                "external-administrative-contract-set.v1.schema.json",
            },
            set(schemas),
        )
        for name, schema in schemas.items():
            with self.subTest(name=name):
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema",
                    schema["$schema"],
                )
                self.assertTrue(schema["$id"].startswith("urn:driftframe:lims-eln:"))
                self.assertEqual("object", schema["type"])
                self.assertTrue(schema["x-semantic-invariants"])

                pending = [schema]
                while pending:
                    value = pending.pop()
                    if isinstance(value, dict):
                        reference = value.get("$ref")
                        if reference is not None:
                            self.assertTrue(
                                reference.startswith("#/$defs/"),
                                f"external dependency in {name}: {reference}",
                            )
                        if value.get("type") == "object" and "properties" in value:
                            self.assertFalse(value.get("additionalProperties", True))
                        pending.extend(value.values())
                    elif isinstance(value, list):
                        pending.extend(value)

    def test_committed_schema_bytes_match_model_generation(self) -> None:
        for name, schema in external_administrative_schema_documents().items():
            with self.subTest(name=name):
                expected = (
                    json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True)
                    + "\n"
                ).encode("utf-8")
                self.assertEqual(expected, (SCHEMA_ROOT / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
