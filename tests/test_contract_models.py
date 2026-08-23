from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import tomllib
import unittest

from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lims_eln_contracts import (  # noqa: E402
    __version__,
    ApprovalDecision,
    ApprovalDomain,
    AssuranceStage,
    BoundedCallRequest,
    CallerClass,
    DuplicateObjectKeyError,
    EvidenceMode,
    NonFiniteNumberError,
    ObservationApproval,
    ObservationClassification,
    ObservationDataClass,
    ObservationEnvelope,
    OperationSemanticError,
    RedactionStatus,
    SpecimenCommand,
    canonical_json_bytes,
    canonical_sha256,
    load_operation_catalog,
    model_from_strict_json,
    strict_json_loads,
)
from lims_eln_contracts.evidence import EvidenceProvenance, EvidenceSource  # noqa: E402
from lims_eln_contracts.bounded_call import (  # noqa: E402
    InputValueKind,
    OperationInputField,
)


class DistributionMetadataTests(unittest.TestCase):
    def test_runtime_version_matches_distribution_metadata(self) -> None:
        with (ROOT / "pyproject.toml").open("rb") as handle:
            distribution = tomllib.load(handle)

        self.assertEqual(distribution["project"]["version"], __version__)


class CanonicalJsonTests(unittest.TestCase):
    def test_strict_json_preserves_unique_keys_and_finite_numbers(self) -> None:
        self.assertEqual({"value": 1.25}, strict_json_loads('{"value":1.25}'))
        with self.assertRaises(DuplicateObjectKeyError):
            strict_json_loads('{"value":1,"value":2}')
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), self.assertRaises(NonFiniteNumberError):
                strict_json_loads('{"value":' + token + "}")
        with self.assertRaises(NonFiniteNumberError):
            canonical_json_bytes({"value": math.inf})

    def test_canonical_digest_is_stable_across_mapping_order(self) -> None:
        first = {"b": "é", "a": [1, True, None]}
        second = {"a": [1, True, None], "b": "é"}
        expected_bytes = b'{"a":[1,true,null],"b":"\xc3\xa9"}'
        expected_digest = (
            "sha256:6eab153701ef60c995351765c772011bca6739878254f313acc3f11e1fef476b"
        )
        self.assertEqual(expected_bytes, canonical_json_bytes(first))
        self.assertEqual(expected_digest, canonical_sha256(first))
        self.assertEqual(expected_digest, canonical_sha256(second))


class ExternalBoundaryTests(unittest.TestCase):
    def test_specimen_command_keeps_types_and_fields_explicit(self) -> None:
        valid = {
            "schema_version": "1.0.0",
            "command_id": "CMD-SYN-001",
            "tenant_id": "TENANT-SYN-001",
            "specimen_id": "SPM-SYN-001",
            "actor_id": "ACTOR-SYN-001",
            "action": "register",
            "expected_version": 0,
            "occurred_at": "2026-08-17T14:30:00Z",
            "payload": {"specimen_type": "synthetic_plasma"},
        }
        command = model_from_strict_json(SpecimenCommand, json.dumps(valid))
        self.assertEqual(0, command.expected_version)
        self.assertTrue(command.canonical_digest().startswith("sha256:"))

        coerced = {**valid, "expected_version": "0"}
        with self.assertRaises(ValidationError):
            model_from_strict_json(SpecimenCommand, json.dumps(coerced))
        expanded = {**valid, "unreleased_field": "value"}
        with self.assertRaises(ValidationError):
            model_from_strict_json(SpecimenCommand, json.dumps(expanded))

    def test_observed_envelope_carries_exact_provenance_and_reviewed_projection(self) -> None:
        envelope = ObservationEnvelope(
            observation_id="OBS-GOLDEN-001",
            evidence_mode=EvidenceMode.OBSERVED,
            assurance_stage=AssuranceStage.VERIFIED,
            scenario_id="SCN-GOLDEN-SPECIMEN-001",
            source=EvidenceSource(
                environment_id="ENV-LAB-QUAL-001",
                implementation_commit="a" * 40,
                configuration_digest="sha256:" + "b" * 64,
            ),
            result={"lifecycle_state": "released"},
            provenance=EvidenceProvenance(
                raw_artifact_digest="sha256:" + "c" * 64,
                governed_locator="evidence-vault://qualification/golden-001.json",
                performed_by="ACTOR-OPERATOR-001",
                reviewed_by="ACTOR-REVIEWER-001",
            ),
            approvals=(
                ObservationApproval(
                    domain=ApprovalDomain.QUALITY,
                    decision=ApprovalDecision.ACCEPT,
                    approver="ACTOR-QUALITY-001",
                ),
            ),
            classification=ObservationClassification(
                data_class=ObservationDataClass.REDACTED_REGULATED_MANIFEST,
                redaction_status=RedactionStatus.REVIEWED_REDACTED_MANIFEST,
            ),
        )
        self.assertEqual(EvidenceMode.OBSERVED, envelope.evidence_mode)

        payload = envelope.model_dump(mode="json")
        payload["source"]["implementation_commit"] = "candidate-v0.3.0"
        with self.assertRaises(ValidationError):
            model_from_strict_json(ObservationEnvelope, json.dumps(payload))

    def test_assurance_stage_order_is_explicit(self) -> None:
        self.assertTrue(AssuranceStage.VALIDATED.reaches(AssuranceStage.QUALIFIED))
        self.assertFalse(AssuranceStage.VERIFIED.reaches(AssuranceStage.ACCEPTED))


class OperationSemanticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_operation_catalog()

    def narrow_request(self, **payload_updates) -> BoundedCallRequest:
        payload = {
            "tenant_id": "TENANT-SYN-001",
            "specimen_id": "SPM-SYN-001",
            "expected_revision": 3,
            "patch": {"display_name": "Reference specimen"},
            "reason": "correct display label",
            "idempotency_key": "IDEMP-SYN-001",
            **payload_updates,
        }
        return BoundedCallRequest(
            call_id="CALL-SYN-001",
            caller_class=CallerClass.AI_BOUNDED_CALLER,
            caller_identity="CALLER-SYN-001",
            initiating_principal="ACTOR-SYN-001",
            operation_id="OP-METADATA-CORRECT-001",
            operation_version="1.0.0",
            tenant_id="TENANT-SYN-001",
            purpose="correct one approved metadata field",
            payload=payload,
            requested_at="2026-08-17T14:30:00Z",
            correlation_id="CORR-SYN-001",
        )

    def test_catalog_binds_one_released_narrow_write(self) -> None:
        operation = self.catalog.bind(self.narrow_request())
        self.assertEqual("correct_specimen_metadata", operation.name)
        self.assertEqual(1, operation.effect_ceiling.record_limit)
        self.assertEqual(
            {"display_name", "external_reference", "storage_note"},
            set(operation.effect_ceiling.editable_fields),
        )

    def test_catalog_routes_protected_patch_fields_to_review(self) -> None:
        request = self.narrow_request(patch={"scientific_result": "changed"})
        with self.assertRaisesRegex(OperationSemanticError, "accountable review"):
            self.catalog.bind(request)

    def test_input_length_constraints_match_length_bearing_values(self) -> None:
        with self.assertRaisesRegex(ValidationError, "minimum_length accompanies"):
            OperationInputField(
                name="enabled",
                value_kind=InputValueKind.BOOLEAN,
                purpose="Released feature posture.",
                minimum_length=1,
            )

    def test_broad_write_requires_eligible_caller_and_approval(self) -> None:
        operation = self.catalog.operation("OP-MIGRATION-CUTOVER-001")
        self.assertNotIn(CallerClass.AI_BOUNDED_CALLER, operation.allowed_callers)
        request = BoundedCallRequest(
            call_id="CALL-CUTOVER-001",
            caller_class=CallerClass.WORKFLOW_AUTOMATION,
            caller_identity="WORKFLOW-SYN-001",
            initiating_principal="ACTOR-SYN-001",
            operation_id=operation.operation_id,
            operation_version=operation.version,
            tenant_id="TENANT-SYN-001",
            purpose="execute approved migration cutover",
            payload={
                "tenant_id": "TENANT-SYN-001",
                "release_id": "RELEASE-SYN-001",
                "source_snapshot_digest": "sha256:" + "1" * 64,
                "mapping_digest": "sha256:" + "2" * 64,
                "planned_effect_count": 100,
                "rollback_checkpoint": "CHECKPOINT-SYN-001",
                "approval_receipt_id": "APPROVAL-SYN-001",
            },
            requested_at="2026-08-17T14:30:00Z",
            correlation_id="CORR-CUTOVER-001",
        )
        with self.assertRaisesRegex(OperationSemanticError, "accountable approval"):
            self.catalog.bind(request)

        mismatched = request.model_copy(
            update={"approval_receipt_id": "APPROVAL-SYN-002"}
        )
        with self.assertRaisesRegex(OperationSemanticError, "carry one approval"):
            self.catalog.bind(mismatched)

        matching = request.model_copy(
            update={"approval_receipt_id": "APPROVAL-SYN-001"}
        )
        self.assertEqual(operation, self.catalog.bind(matching))


if __name__ == "__main__":
    unittest.main()
