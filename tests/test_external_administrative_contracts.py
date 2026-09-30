from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lims_eln_contracts.canonical import (  # noqa: E402
    canonical_sha256,
    model_from_strict_json,
    strict_json_loads,
)
from lims_eln_contracts.external_administrative import (  # noqa: E402
    AdministrativeContext,
    AdministrativeDecision,
    ClassificationDisposition,
    ClassificationState,
    ConflictBehavior,
    CoverageEnrollment,
    DecisionImpactObservation,
    ExternalAdministrativeContractSet,
    ExternalSourceManifest,
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
SOURCE_EXAMPLE_PATH = (
    RESOURCE_ROOT / "administrative" / "synthetic-hospital-v1.3.v1.json"
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
                "ExternalSourceManifest",
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
                "administrative/synthetic-hospital-v1.3.v1.json",
                "administrative/independent-multilabel-policy.v1.json",
                "administrative/administrative-counterfactual.v1.json",
            },
            {item.path for item in self.contract.examples},
        )
        self.assertEqual("pending_reviewed_merge", self.contract.adoption_event.state)

    def test_source_example_pins_exact_v1_3_coordinates_without_database_bytes(
        self,
    ) -> None:
        source = model_from_strict_json(
            ExternalSourceManifest,
            SOURCE_EXAMPLE_PATH.read_bytes(),
        )
        self.assertEqual("v1.3", source.release_tag)
        self.assertEqual(
            "77cc57e9c595ce731bbdde4fabdcbd25a8458ae2",
            source.release_commit,
        )
        self.assertEqual("benchmark_v1.3.db", source.asset.asset_name)
        self.assertEqual("application/octet-stream", source.asset.media_type)
        self.assertEqual(92_430_336, source.asset.byte_count)
        self.assertEqual(
            "sha256:8fb8eb114508f272588b6121ca78cff53a6fc2e5f47d7aa01bfbb5bcef4e6ddb",
            source.asset.digest,
        )
        self.assertEqual("metadata_only", source.asset.inclusion_mode)
        self.assertFalse(source.asset.payload_included)
        self.assertFalse(source.asset_observation.download_performed)
        self.assertFalse(source.asset_observation.execution_performed)
        self.assertEqual("api_reported_metadata", source.asset_observation.observation_kind)
        documents = {item.role.value: item for item in source.pinned_documents}
        self.assertEqual(
            {
                "data_card": (
                    "DATA_CARD.md",
                    "310457cad3ebd66fe135bb2a45a4332957e2d750",
                    9639,
                ),
                "license": (
                    "LICENSE",
                    "5954e9b76b3e647ab0606811efce40407d28ba52",
                    1067,
                ),
                "citation": (
                    "CITATION.cff",
                    "249b36a010ab5970470ee2a22558e77a78a299e2",
                    1049,
                ),
            },
            {
                role: (item.path, item.blob_sha, item.byte_count)
                for role, item in documents.items()
            },
        )
        self.assertEqual(1, len(source.upstream_limitations))
        self.assertEqual(3, source.upstream_limitations[0].issue_number)
        self.assertEqual("open", source.upstream_limitations[0].state)
        self.assertIn("FHIR", source.upstream_limitations[0].limitation)
        self.assertEqual(source, self.contract.source_manifests[0])
        source_assertion = next(
            item
            for item in self.contract.provenance_assertions
            if item.assertion_id == "PROV-SOURCE-MANIFEST-001"
        )
        self.assertEqual("source_reported", source_assertion.standing.value)
        self.assertLess(SOURCE_EXAMPLE_PATH.stat().st_size, 10_000)

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
        self.assertEqual((), example.source_manifests)
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

    def test_external_manifest_rejects_coercion_and_unknown_fields(self) -> None:
        source = document(SOURCE_EXAMPLE_PATH)
        coerced = deepcopy(source)
        coerced["asset"]["byte_count"] = "92430336"
        with self.assertRaises(ValidationError):
            parse(ExternalSourceManifest, coerced)

        expanded = deepcopy(source)
        expanded["asset"]["database_bytes"] = "not carried"
        with self.assertRaises(ValidationError):
            parse(ExternalSourceManifest, expanded)

    def test_external_manifest_requires_all_three_pinned_document_roles(self) -> None:
        source = document(SOURCE_EXAMPLE_PATH)
        source["pinned_documents"] = [
            item for item in source["pinned_documents"] if item["role"] != "citation"
        ]
        with self.assertRaisesRegex(
            ValidationError,
            "data card, license, and citation",
        ):
            parse(ExternalSourceManifest, source)

    def test_local_hash_observation_requires_a_recorded_download(self) -> None:
        source = document(SOURCE_EXAMPLE_PATH)
        source["asset_observation"]["observation_kind"] = "locally_hashed"
        with self.assertRaisesRegex(ValidationError, "requires.*download"):
            parse(ExternalSourceManifest, source)

        aggregate = deepcopy(self.contract_document)
        aggregate["source_manifests"][0]["asset_observation"][
            "observation_kind"
        ] = "locally_hashed"
        with self.assertRaisesRegex(ValidationError, "requires.*download"):
            parse(ExternalAdministrativeContractSet, aggregate)

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

    def test_public_https_locators_reject_userinfo_and_queries(self) -> None:
        source = document(SOURCE_EXAMPLE_PATH)
        with_userinfo = deepcopy(source)
        with_userinfo["repository_url"] = (
            "https://reader@github.com/sparkcpark/synthetic_hospital"
        )
        with self.assertRaisesRegex(ValidationError, "no user information"):
            parse(ExternalSourceManifest, with_userinfo)

        with_query = deepcopy(source)
        with_query["release_url"] += "?token=unstable"
        with self.assertRaisesRegex(ValidationError, "no query string"):
            parse(ExternalSourceManifest, with_query)

        with_fragment = deepcopy(source)
        with_fragment["release_url"] += "#release-notes"
        parsed = parse(ExternalSourceManifest, with_fragment)
        self.assertTrue(parsed.release_url.endswith("#release-notes"))

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
            "EXTSRC-SYNTHETIC-HOSPITAL-V1-3"
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
            if item["assertion_id"] == "PROV-SOURCE-MANIFEST-001"
        )
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

    def test_release_scoped_source_coordinates_must_match_manifest(self) -> None:
        broken = deepcopy(self.contract_document)
        source_assertion = next(
            item
            for item in broken["provenance_assertions"]
            if item["assertion_id"] == "PROV-SOURCE-MANIFEST-001"
        )
        source_assertion["source_coordinate"]["record"]["release_id"] = "v1.2"
        with self.assertRaisesRegex(ValidationError, "manifest namespace and release"):
            parse(ExternalAdministrativeContractSet, broken)

    def test_api_metadata_cannot_claim_artifact_verified_provenance(self) -> None:
        broken = deepcopy(self.contract_document)
        source_assertion = next(
            item
            for item in broken["provenance_assertions"]
            if item["assertion_id"] == "PROV-SOURCE-MANIFEST-001"
        )
        source_assertion["standing"] = "artifact_verified"
        with self.assertRaisesRegex(ValidationError, "locally hashed download"):
            parse(ExternalAdministrativeContractSet, broken)

    def test_api_metadata_cannot_support_artifact_verified_context(self) -> None:
        broken = deepcopy(self.contract_document)
        for context in broken["administrative_contexts"]:
            context["source_class"] = "external_synthetic_release"
            context["evidence_standing"] = "artifact_verified"
            for scoped_name in ("subject", "episode"):
                scoped = context[scoped_name]
                scoped["namespace_id"] = "EXTSRC-SYNTHETIC-HOSPITAL-V1-3"
                scoped["release_id"] = "v1.3"
                scoped["source_manifest_ref"] = (
                    "EXTSRC-SYNTHETIC-HOSPITAL-V1-3"
                )
        with self.assertRaisesRegex(ValidationError, "locally hashed download"):
            parse(ExternalAdministrativeContractSet, broken)

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
                "external-source-manifest.v1.schema.json",
                "external-administrative-contract-set.v1.schema.json",
            }
        }
        self.assertEqual(expected, external_administrative_schema_documents())

    def test_repository_schema_index_names_current_schema_identities(self) -> None:
        index = (ROOT / "schemas" / "README.md").read_text(encoding="utf-8")
        schema_paths = (
            ROOT / "schemas" / "program-release-observation.v1.schema.json",
            ROOT / "schemas" / "promotion-receipt.schema.json",
            SCHEMA_ROOT / "external-source-manifest.v1.schema.json",
            SCHEMA_ROOT / "external-administrative-contract-set.v1.schema.json",
        )
        for path in schema_paths:
            with self.subTest(path=path.name):
                self.assertIn(document(path)["$id"], index)

    def test_schema_roots_are_identified_self_contained_draft_2020_12(self) -> None:
        schemas = external_administrative_schema_documents()
        self.assertEqual(
            {
                "external-source-manifest.v1.schema.json",
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
