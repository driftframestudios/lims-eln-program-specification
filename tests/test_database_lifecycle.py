"""Independent source-contract expectations; all resource records are synthetic."""

from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import Draft202012Validator

from lims_eln_contracts import AUTHORED_SCHEMA_RESOURCE_NAMES, SCHEMA_RESOURCE_NAMES, authored_schema_bytes, __version__
from lims_eln_contracts.database_lifecycle import (
    CAPABILITY_SCHEMA_BYTES,
    MAX_INPUT_BYTES,
    SCHEMA_BYTES,
    SCHEMA_DIGEST,
    LifecycleAdmissionError,
    LifecycleSource,
    admit_lifecycle_profile,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = LifecycleSource("ref:synthetic-program-source", "1" * 40, SCHEMA_DIGEST)


class DatabaseLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.examples = {
            name: json.loads((ROOT / f"examples/database-lifecycle/{name}.json").read_bytes())
            for name in ("disposable", "retained", "external", "cleanup-failed", "unresolved")
        }
        cls.counterexamples = json.loads(
            (ROOT / "tests/fixtures/database-lifecycle/counterexamples.json").read_bytes()
        )
        cls.capabilities = {
            name: (ROOT / f"examples/workbench-capabilities/{name}.json").read_bytes()
            for name in ("process-local", "postgresql")
        }

    def admit(self, document, **kwargs):
        return admit_lifecycle_profile(json.dumps(document).encode(), expected_source=SOURCE, **kwargs)

    def reject(self, document, code, **kwargs):
        with self.assertRaises(LifecycleAdmissionError) as caught:
            self.admit(document, **kwargs)
        self.assertEqual(code, caught.exception.code)
        return caught.exception

    def planned(self):
        candidate = deepcopy(self.examples["disposable"])
        candidate["operations"] = []
        candidate["resource"]["state"] = "absent"
        return candidate

    def with_composition(self, payload):
        candidate = self.planned()
        candidate["composition"] = {
            "state": "observed", "capability_ref": "ref:synthetic-capability",
            "capability_digest": "sha256:" + hashlib.sha256(payload).hexdigest(),
        }
        return candidate

    def test_schema_and_separate_package_inventories(self):
        schema = json.loads(SCHEMA_BYTES)
        Draft202012Validator.check_schema(schema)
        self.assertEqual("urn:driftframe:lims-eln:database-lifecycle-profile:1.0.0", schema["$id"])
        self.assertEqual("c4b5859d2b543b26970fb3b5b577b11e5f50415be7484c891257f4d2d0d83808", hashlib.sha256(CAPABILITY_SCHEMA_BYTES).hexdigest())
        self.assertEqual("0.7.0", __version__)
        self.assertEqual(("database-lifecycle-profile.v1.schema.json", "workbench-capabilities.v1.schema.json"), AUTHORED_SCHEMA_RESOURCE_NAMES)
        for name in AUTHORED_SCHEMA_RESOURCE_NAMES:
            self.assertEqual((ROOT / "schemas" / name).read_bytes(), authored_schema_bytes(name))
        self.assertEqual(12, len(SCHEMA_RESOURCE_NAMES))
        self.assertFalse(any("lifecycle" in name for name in SCHEMA_RESOURCE_NAMES))

    def test_nonempty_examples_have_literal_results_and_roundtrip(self):
        expected = {
            "disposable": ("disposable", "removed", 3, ()),
            "retained": ("retained", "retained", 4, ()),
            "external": ("external", "present", 2, ()),
            "cleanup-failed": ("disposable", "unresolved", 2, ("ref:synthetic-disposable-database",)),
            "unresolved": ("disposable", "unresolved", 2, ("ref:synthetic-disposable-database",)),
        }
        for name, (disposition, state, count, unresolved) in expected.items():
            with self.subTest(example=name):
                document = self.examples[name]
                accepted = self.admit(document)
                self.assertEqual(disposition, document["requested_profile"]["disposition"])
                self.assertEqual((state, count, 0, unresolved), (
                    accepted.resource_state, accepted.executed_operations,
                    accepted.requested_operations, accepted.unresolved_resource_refs,
                ))
                self.assertEqual(document, json.loads(accepted.canonical_bytes))
                self.assertEqual(accepted, admit_lifecycle_profile(accepted.canonical_bytes, expected_source=SOURCE))

    def test_authored_counterexamples_have_specific_findings(self):
        for fixture in self.counterexamples:
            with self.subTest(fixture=fixture["name"]):
                candidate = deepcopy(self.examples[fixture["example"]])
                for change in fixture["changes"]:
                    target = candidate
                    for part in change["path"][:-1]:
                        target = target[part]
                    target[change["path"][-1]] = deepcopy(change["value"])
                self.reject(candidate, fixture["expected_code"])

    def test_requested_action_and_ready_dependency_prove_no_execution(self):
        candidate = self.planned()
        action = deepcopy(self.examples["disposable"]["operations"][0])
        action.update(outcome="requested", to_state="absent", evidence_ref=None)
        candidate["operations"] = [action]
        candidate["readiness"] = {"state": "ready", "observation_ref": "ref:ready-observation"}
        accepted = self.admit(candidate)
        self.assertEqual(("absent", 0, 1), (accepted.resource_state, accepted.executed_operations, accepted.requested_operations))

    def test_supplied_composition_has_independent_schema_digest_and_adapter(self):
        postgres = self.capabilities["postgresql"]
        candidate = self.with_composition(postgres)
        self.assertEqual(0, self.admit(candidate, capability_payload=postgres).executed_operations)
        self.reject(candidate, "composition_unresolved")
        self.reject(candidate, "composition_digest", capability_payload=postgres + b"\n")
        local = self.capabilities["process-local"]
        self.reject(self.with_composition(local), "composition_mismatch", capability_payload=local)
        malformed = json.dumps({"runtime": {"state_adapter": "postgresql"}}).encode()
        self.reject(self.with_composition(malformed), "composition_contract", capability_payload=malformed)
        self.reject(self.planned(), "composition_mismatch", capability_payload=postgres)

    def test_package_compatibility_is_not_a_readiness_or_execution_assertion(self):
        capability = json.loads(self.capabilities["postgresql"])
        capability["shared_contracts"]["version_compatible"] = False
        payload = json.dumps(capability).encode()
        accepted = self.admit(self.with_composition(payload), capability_payload=payload)
        self.assertEqual((0, "not_observed"), (accepted.executed_operations, json.loads(accepted.canonical_bytes)["readiness"]["state"]))

    def test_source_and_schema_trust_are_independent_receiver_arguments(self):
        payload = json.dumps(self.planned()).encode()
        for source, code in (
            (replace(SOURCE, revision="2" * 40), "stale_source"),
            (replace(SOURCE, source_ref="ref:other-source"), "stale_source"),
            (replace(SOURCE, schema_digest="sha256:" + "2" * 64), "stale_schema"),
            ({"revision": "1" * 40}, "source_binding"),
        ):
            with self.subTest(code=code, source=source):
                with self.assertRaises(LifecycleAdmissionError) as caught:
                    admit_lifecycle_profile(payload, expected_source=source)
                self.assertEqual(code, caught.exception.code)
        with self.assertRaises(LifecycleAdmissionError) as caught:
            replace(SOURCE, revision="0" * 40)
        self.assertEqual("source_binding", caught.exception.code)

    def test_external_owner_can_explicitly_remove_its_resource(self):
        candidate = deepcopy(self.examples["external"])
        action = deepcopy(candidate["operations"][0])
        action.update(operation_ref="ref:owner-cleanup", action="cleanup", to_state="removed")
        action["authority"].update(actor_ref="ref:external-owner", destructive_authorized=True)
        candidate["operations"].append(action)
        candidate["resource"]["state"] = "removed"
        self.assertEqual("removed", self.admit(candidate).resource_state)
        action["authority"]["actor_ref"] = "ref:launcher"
        self.reject(candidate, "external_cleanup_forbidden")

    def test_retained_cleanup_requires_its_owner_decision(self):
        candidate = deepcopy(self.examples["retained"])
        action = deepcopy(candidate["operations"][0])
        action.update(operation_ref="ref:retained-owner-cleanup", action="cleanup", from_state="retained", to_state="removed")
        action["authority"]["destructive_authorized"] = True
        candidate["operations"].append(action)
        candidate["resource"]["state"] = "removed"
        self.assertEqual("removed", self.admit(candidate).resource_state)
        action["authority"]["basis"] = "invocation_owned"
        self.reject(candidate, "owner_decision_required")

    def test_cleanup_retry_preserves_failed_event_and_prior_immutable_result(self):
        candidate = deepcopy(self.examples["cleanup-failed"])
        prior = self.admit(candidate)
        retry = deepcopy(candidate["operations"][1])
        retry.update(operation_ref="ref:cleanup-retry", from_state="unresolved", to_state="removed", outcome="succeeded", failure_code=None, evidence_ref="ref:retry-evidence")
        candidate["operations"].append(retry)
        candidate["resource"]["state"] = "removed"
        candidate["unresolved_resource_refs"] = []
        accepted = self.admit(candidate)
        self.assertEqual(("removed", 3), (accepted.resource_state, accepted.executed_operations))
        self.assertEqual("cleanup_failed", json.loads(accepted.canonical_bytes)["operations"][1]["failure_code"])
        self.assertEqual("unresolved", json.loads(prior.canonical_bytes)["resource"]["state"])
        self.assertEqual(2, len(json.loads(prior.canonical_bytes)["operations"]))

    def test_uncertain_creation_and_stop_preserve_unresolved_resource(self):
        candidate = deepcopy(self.examples["unresolved"])
        stop = deepcopy(candidate["operations"][-1])
        stop.update(operation_ref="ref:stop-after-uncertainty", action="stop", outcome="succeeded", failure_code=None)
        candidate["operations"].append(stop)
        self.assertEqual(("ref:synthetic-disposable-database",), self.admit(candidate).unresolved_resource_refs)
        stop.update(action="cleanup", to_state="removed")
        stop["authority"]["destructive_authorized"] = True
        self.reject(candidate, "unowned_cleanup")

    def test_inspection_resolves_cleanup_uncertainty_with_history(self):
        candidate = deepcopy(self.examples["cleanup-failed"])
        inspect = deepcopy(candidate["operations"][-1])
        inspect.update(operation_ref="ref:inspect-cleanup-result", action="inspect", from_state="unresolved", to_state="removed", outcome="succeeded", failure_code=None)
        inspect["authority"]["destructive_authorized"] = False
        candidate["operations"].append(inspect)
        candidate["resource"]["state"] = "removed"
        candidate["unresolved_resource_refs"] = []
        self.assertEqual("removed", self.admit(candidate).resource_state)

    def resolved_cleanup(self, state):
        candidate = deepcopy(self.examples["cleanup-failed"])
        inspect = deepcopy(candidate["operations"][-1])
        inspect.update(
            operation_ref="ref:confirmed-cleanup-result", action="inspect",
            from_state="unresolved", to_state=state, outcome="succeeded",
            failure_code=None, evidence_ref="ref:confirmed-cleanup-evidence",
        )
        inspect["authority"]["destructive_authorized"] = False
        candidate["operations"].append(inspect)
        candidate["resource"]["state"] = state
        candidate["unresolved_resource_refs"] = []
        return candidate

    def test_uncertain_recreation_cannot_reuse_prior_creation(self):
        for state in ("absent", "removed"):
            for outcome, failure in (("failed", "create_failed"), ("unresolved", "resource_unresolved")):
                with self.subTest(state=state, outcome=outcome):
                    candidate = self.resolved_cleanup(state)
                    self.assertEqual(state, self.admit(candidate).resource_state)
                    create = deepcopy(candidate["operations"][0])
                    create.update(
                        operation_ref="ref:second-create", from_state=state, outcome=outcome,
                        to_state="unresolved", failure_code=failure,
                        evidence_ref="ref:second-create-evidence",
                    )
                    candidate["operations"].append(create)
                    candidate["resource"]["state"] = "unresolved"
                    candidate["unresolved_resource_refs"] = [candidate["resource"]["resource_ref"]]
                    self.assertEqual("unresolved", self.admit(candidate).resource_state)
                    cleanup = deepcopy(candidate["operations"][1])
                    cleanup.update(
                        operation_ref="ref:second-cleanup", from_state="unresolved",
                        to_state="removed", outcome="succeeded", failure_code=None,
                        evidence_ref="ref:second-cleanup-evidence",
                    )
                    candidate["operations"].append(cleanup)
                    candidate["resource"]["state"] = "removed"
                    candidate["unresolved_resource_refs"] = []
                    self.reject(candidate, "unowned_cleanup")

    def test_successful_cleanup_allows_a_fresh_instance(self):
        candidate = deepcopy(self.examples["cleanup-failed"])
        candidate["operations"][1].update(
            outcome="succeeded", to_state="removed", failure_code=None,
        )
        create = deepcopy(candidate["operations"][0])
        create.update(
            operation_ref="ref:second-create", from_state="removed",
            evidence_ref="ref:second-create-evidence",
        )
        cleanup = deepcopy(candidate["operations"][1])
        cleanup.update(operation_ref="ref:second-cleanup", evidence_ref="ref:second-cleanup-evidence")
        candidate["operations"].extend((create, cleanup))
        candidate["resource"]["state"] = "removed"
        candidate["unresolved_resource_refs"] = []
        accepted = self.admit(candidate)
        self.assertEqual(("removed", 4, ()), (
            accepted.resource_state, accepted.executed_operations,
            accepted.unresolved_resource_refs,
        ))
        self.assertEqual(candidate, json.loads(accepted.canonical_bytes))

    def test_successful_recreation_owns_its_cleanup(self):
        candidate = self.resolved_cleanup("absent")
        create = deepcopy(candidate["operations"][0])
        create.update(operation_ref="ref:second-create", evidence_ref="ref:second-create-evidence")
        cleanup = deepcopy(candidate["operations"][1])
        cleanup.update(
            operation_ref="ref:second-cleanup", outcome="succeeded",
            to_state="removed", failure_code=None, evidence_ref="ref:second-cleanup-evidence",
        )
        candidate["operations"].extend((create, cleanup))
        candidate["resource"]["state"] = "removed"
        accepted = self.admit(candidate)
        self.assertEqual(("removed", 5, ()), (
            accepted.resource_state, accepted.executed_operations,
            accepted.unresolved_resource_refs,
        ))
        self.assertEqual(candidate, json.loads(accepted.canonical_bytes))
        self.assertEqual("cleanup_failed", json.loads(accepted.canonical_bytes)["operations"][1]["failure_code"])

    def test_resolved_cleanup_cannot_supply_a_later_removed_observation(self):
        for state in ("absent", "removed"):
            with self.subTest(state=state):
                candidate = self.resolved_cleanup(state)
                self.assertEqual(state, self.admit(candidate).resource_state)
                failed = deepcopy(candidate["operations"][-1])
                failed.update(
                    operation_ref="ref:later-inspection-failed", from_state=state,
                    to_state="unresolved", outcome="failed", failure_code="inspect_failed",
                    evidence_ref="ref:later-inspection-failure",
                )
                removed = deepcopy(candidate["operations"][-1])
                removed.update(
                    operation_ref="ref:later-removed-observation", to_state="removed",
                    evidence_ref="ref:later-removed-evidence",
                )
                candidate["operations"].extend((failed, removed))
                candidate["resource"]["state"] = "removed"
                self.reject(candidate, "invalid_transition")

    def test_transition_permission_identity_and_operation_evidence(self):
        cases = (
            (("operations", 1, "from_state"), "absent", "invalid_transition"),
            (("operations", 1, "operation_ref"), "ref:temporary-create", "duplicate_operation"),
            (("operations", 1, "evidence_ref"), None, "operation_evidence"),
            (("operations", 2, "failure_code"), "cleanup_failed", "operation_evidence"),
            (("requested_profile", "permitted_actions"), ["create", "cleanup"], "action_not_permitted"),
            (("resource", "state"), "present", "invalid_transition"),
            (("operations", 1, "compatibility", "engine_major"), 17, "compatibility_mismatch"),
            (("operations", 1, "compatibility", "state"), "incompatible", "compatibility_required"),
        )
        for path, value, code in cases:
            with self.subTest(path=path):
                candidate = deepcopy(self.examples["disposable"])
                target = candidate
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = value
                self.reject(candidate, code)

    def test_required_fields_and_safe_reference_grammar(self):
        original = self.planned()
        for key in original:
            with self.subTest(missing=key):
                candidate = deepcopy(original)
                del candidate[key]
                self.reject(candidate, "contract_shape")
        for unsafe in ("/private/runtime", "postgresql://fixture", "ref:account@host", "ref:valid\n", "ref:" + "a" * 65):
            with self.subTest(reference=unsafe):
                candidate = deepcopy(original)
                candidate["requested_profile"]["recovery_ref"] = unsafe
                error = self.reject(candidate, "contract_shape")
                self.assertNotIn(unsafe, str(error))
        for key in ("connection_string", "credentials", "absolute_path", "account", "network"):
            candidate = deepcopy(original)
            candidate["requested_profile"][key] = "private-marker"
            self.assertNotIn("private-marker", str(self.reject(candidate, "contract_shape")))

    def test_input_failures_return_fixed_codes_and_keep_prior_bytes(self):
        prior = self.admit(self.examples["retained"])
        before = prior.canonical_bytes
        for payload, code in (
            (b"x" * (MAX_INPUT_BYTES + 1), "input_bytes"),
            (b"\xff", "utf8"),
            (b'{"private-marker":1,"private-marker":2}', "json_duplicate_key"),
            (b'{"private-marker":NaN}', "json_number"),
            (b'{"private-marker":1e9999}', "json_number"),
            (b'{"private-marker":', "json_syntax"),
            (b"[]", "contract_shape"),
        ):
            with self.subTest(code=code):
                with self.assertRaises(LifecycleAdmissionError) as caught:
                    admit_lifecycle_profile(payload, expected_source=SOURCE)
                self.assertEqual(code, caught.exception.code)
                self.assertNotIn("private-marker", str(caught.exception))
                self.assertLess(len(str(caught.exception)), 160)
                self.assertEqual(before, prior.canonical_bytes)

    def test_local_entry_reports_admission_with_unresolved_work_visible(self):
        result = subprocess.run([
            sys.executable, str(ROOT / "scripts/database_lifecycle.py"),
            str(ROOT / "examples/database-lifecycle/cleanup-failed.json"),
            "--source-ref", SOURCE.source_ref, "--source-revision", SOURCE.revision,
            "--schema-digest", SOURCE.schema_digest,
        ], capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("profile_admitted: state=unresolved; unresolved=1; recorded_operations=2; requested_operations=0\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
