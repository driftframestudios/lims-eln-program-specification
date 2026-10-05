from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import json
import unittest
from unittest import mock

from pydantic import ValidationError

from lims_eln_contracts._administrative_graph import reachable_sources, require_acyclic
from lims_eln_contracts.administrative_admission import (
    AdministrativeAdmissionError,
    AdministrativeAdmissionLimits,
    _decoded_values,
    _graph_envelope,
    _json_depth,
    admit_administrative_contract,
)
from lims_eln_contracts.canonical import canonical_json_bytes, model_from_strict_json
from lims_eln_contracts.external_administrative import ExternalAdministrativeContractSet
from test_external_administrative_contracts import (
    CONTRACT_SET_PATH,
    document,
    source_calibrated_contract,
)


# A fixture-owned review envelope, not a package default or production claim.
REVIEW_LIMITS = AdministrativeAdmissionLimits(
    max_input_bytes=2 * 1024 * 1024,
    max_json_depth=32,
    max_decoded_values=200_000,
    max_records=2_000,
    max_provenance_edges=8_000,
    max_graph_steps=100_000,
    max_output_bytes=2 * 1024 * 1024,
)


def calibrated_chain(length: int) -> dict:
    value = source_calibrated_contract(document(CONTRACT_SET_PATH))
    scenario = value["population_scenarios"][0]
    root = next(
        item for item in value["provenance_assertions"]
        if item["assertion_id"] == scenario["provenance_refs"][0]
    )
    source_ref = root["derived_from_assertion_refs"][0]
    chain = []
    for index in range(length):
        node = deepcopy(root)
        node["assertion_id"] = f"PROV-DEPTH-{index:04d}"
        node["derived_from_assertion_refs"] = [
            f"PROV-DEPTH-{index + 1:04d}" if index < length - 1 else source_ref
        ]
        chain.append(node)
    root["derived_from_assertion_refs"] = [chain[0]["assertion_id"]]
    value["provenance_assertions"].extend(chain)
    return value


class ProvenanceTraversalTests(unittest.TestCase):
    def test_cycle_and_component_shapes_retain_inputs(self) -> None:
        cases = (
            ({}, False),
            ({"A": ()}, False),
            ({"A": ("B",), "B": (), "C": ()}, False),
            ({"A": ("B", "C"), "B": ("D",), "C": ("D",), "D": ()}, False),
            ({"A": ("A",)}, True),
            ({"A": ("B",), "B": ("A",)}, True),
            ({"A": (), "B": ("C",), "C": ("B",)}, True),
        )
        for parents, cyclic in cases:
            with self.subTest(parents=parents):
                original = deepcopy(parents)
                if cyclic:
                    with self.assertRaisesRegex(ValueError, "^provenance assertion graph remains acyclic$"):
                        require_acyclic(parents)
                else:
                    require_acyclic(parents)
                self.assertEqual(original, parents)

    def test_shared_ancestors_are_visited_once_per_scenario(self) -> None:
        class CountedParents(dict):
            def __init__(self, value):
                super().__init__(value)
                self.visits = {}

            def __getitem__(self, key):
                self.visits[key] = self.visits.get(key, 0) + 1
                return super().__getitem__(key)

        parents = CountedParents({
            "root": ("left", "right"),
            "left": ("source-a", "source-b"),
            "right": ("source-a", "source-b"),
            "source-a": (),
            "source-b": (),
            "unrelated": (),
        })
        sources = {"source-a": "OBS-A", "source-b": "OBS-B", "unrelated": "OBS-X"}
        self.assertEqual(
            frozenset({"OBS-A", "OBS-B"}),
            reachable_sources(parents, sources, ("root", "left", "root")),
        )
        self.assertEqual(
            {"root": 1, "left": 1, "right": 1, "source-a": 1, "source-b": 1},
            parents.visits,
        )

    def test_deep_calibrated_chain_has_an_explicit_result(self) -> None:
        for depth in (2, 1_200):
            with self.subTest(depth=depth):
                value = calibrated_chain(depth)
                encoded = json.dumps(value).encode("utf-8")
                accepted = admit_administrative_contract(encoded, limits=REVIEW_LIMITS)
                self.assertEqual(
                    ("OBSERVATION-POPULATION-CALIBRATION-V1",),
                    accepted.contract.population_scenarios[0].calibration_source_refs,
                )
                self.assertEqual(value, json.loads(encoded))
                cycle = deepcopy(value)
                cycle["provenance_assertions"][-1]["derived_from_assertion_refs"] = [
                    "PROV-DEPTH-0000"
                ]
                with self.assertRaisesRegex(ValidationError, "graph remains acyclic"):
                    model_from_strict_json(ExternalAdministrativeContractSet, json.dumps(cycle))

    def test_wide_fan_in_keeps_distinct_sources(self) -> None:
        parents = {f"source-{index}": () for index in range(100)}
        sources = {key: f"OBS-{index}" for index, key in enumerate(parents)}
        leaves = tuple(parents)
        parents.update({f"branch-{index}": leaves for index in range(60)})
        parents["root"] = tuple(f"branch-{index}" for index in range(60))
        require_acyclic(parents)
        self.assertEqual(
            frozenset(f"OBS-{index}" for index in range(100)),
            reachable_sources(parents, sources, ("root",)),
        )


class AdministrativeAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = CONTRACT_SET_PATH.read_bytes()
        cls.accepted = admit_administrative_contract(cls.payload, limits=REVIEW_LIMITS)

    def test_exact_output_matches_existing_canonical_contract(self) -> None:
        expected = model_from_strict_json(ExternalAdministrativeContractSet, self.payload)
        self.assertEqual(expected, self.accepted.contract)
        self.assertEqual(canonical_json_bytes(expected), self.accepted.canonical_bytes)
        self.assertEqual(len(self.payload), self.accepted.usage.input_bytes)
        self.assertEqual(len(self.accepted.canonical_bytes), self.accepted.usage.output_bytes)
        self.assertEqual(
            expected,
            admit_administrative_contract(
                self.accepted.canonical_bytes, limits=REVIEW_LIMITS
            ).contract,
        )

    def test_budget_configuration_is_strict_and_immutable(self) -> None:
        for name in REVIEW_LIMITS.__dataclass_fields__:
            for invalid in (True, 1.5, "10", None, -1, 1 << 63):
                with self.subTest(field=name, value=invalid):
                    with self.assertRaisesRegex(ValueError, name):
                        replace(REVIEW_LIMITS, **{name: invalid})
        with self.assertRaisesRegex(ValueError, "128"):
            replace(REVIEW_LIMITS, max_json_depth=129)
        for name in ("max_input_bytes", "max_json_depth", "max_decoded_values", "max_records", "max_output_bytes"):
            with self.subTest(field=name):
                with self.assertRaisesRegex(ValueError, name):
                    replace(REVIEW_LIMITS, **{name: 0})
        replace(REVIEW_LIMITS, max_provenance_edges=0, max_graph_steps=0)
        with self.assertRaises(FrozenInstanceError):
            REVIEW_LIMITS.max_records = 3

    def test_payload_and_profile_boundaries_are_explicit(self) -> None:
        for invalid in ("{}", bytearray(b"{}"), memoryview(b"{}"), None, True):
            with self.subTest(value=type(invalid).__name__):
                with self.assertRaisesRegex(TypeError, "immutable UTF-8 bytes"):
                    admit_administrative_contract(invalid, limits=REVIEW_LIMITS)
        with self.assertRaisesRegex(TypeError, "AdministrativeAdmissionLimits"):
            admit_administrative_contract(self.payload, limits={})

    def test_exact_resource_limits_pass_and_one_over_stops_before_model(self) -> None:
        usage = self.accepted.usage
        counts = {
            "input_bytes": usage.input_bytes,
            "json_depth": usage.json_depth,
            "decoded_values": usage.decoded_values,
            "records": usage.records,
            "provenance_edges": usage.provenance_edges,
            "graph_steps": usage.graph_steps,
        }
        for resource, count in counts.items():
            with self.subTest(resource=resource):
                exact = replace(REVIEW_LIMITS, **{f"max_{resource}": count})
                self.assertEqual(
                    self.accepted.canonical_bytes,
                    admit_administrative_contract(self.payload, limits=exact).canonical_bytes,
                )
                below = replace(exact, **{f"max_{resource}": count - 1})
                with mock.patch.object(
                    ExternalAdministrativeContractSet, "model_validate_json",
                    side_effect=AssertionError("model construction preceded resource admission"),
                ):
                    with self.assertRaises(AdministrativeAdmissionError) as captured:
                        admit_administrative_contract(self.payload, limits=below)
                self.assertEqual(resource, captured.exception.code)
                self.assertEqual(count - 1, captured.exception.limit)

    def test_byte_limit_precedes_utf8_and_parser(self) -> None:
        with mock.patch("lims_eln_contracts.administrative_admission.strict_json_loads") as parser:
            with self.assertRaises(AdministrativeAdmissionError) as captured:
                admit_administrative_contract(b"\xff\xff", limits=replace(REVIEW_LIMITS, max_input_bytes=1))
            self.assertEqual("input_bytes", captured.exception.code)
            parser.assert_not_called()

    def test_depth_preflight_handles_literal_delimiters_and_escapes(self) -> None:
        for value, expected in (
            ({"text": "[[{deep}]]"}, 1),
            ({"text": 'quoted " and slash \\ and [ ]'}, 1),
            ({"nested": [{"value": "[]"}]}, 3),
            ([[0]], 2),
        ):
            with self.subTest(value=value):
                self.assertEqual(expected, _json_depth(json.dumps(value), expected))
        for depth in (32, 128):
            payload = ("[" * depth + "0" + "]" * depth).encode()
            with self.subTest(depth=depth):
                with self.assertRaises(AdministrativeAdmissionError) as captured:
                    admit_administrative_contract(
                        payload, limits=replace(REVIEW_LIMITS, max_json_depth=depth)
                    )
                self.assertEqual("contract_root", captured.exception.code)
                with mock.patch("lims_eln_contracts.administrative_admission.strict_json_loads") as parser:
                    with self.assertRaises(AdministrativeAdmissionError) as captured:
                        admit_administrative_contract(
                            payload, limits=replace(REVIEW_LIMITS, max_json_depth=depth - 1)
                        )
                    self.assertEqual("json_depth", captured.exception.code)
                    parser.assert_not_called()

    def test_decoded_counter_includes_member_names(self) -> None:
        value = {"a": [1, {"b": None}]}
        self.assertEqual(7, _decoded_values(value, 7))
        with self.assertRaises(AdministrativeAdmissionError) as captured:
            _decoded_values(value, 6)
        self.assertEqual(("decoded_values", 7, 6), (
            captured.exception.code, captured.exception.observed, captured.exception.limit
        ))

    def test_graph_budget_accounts_for_each_calibrated_scenario(self) -> None:
        value = {
            "provenance_assertions": [
                {"derived_from_assertion_refs": ["B", "C"]},
                {"derived_from_assertion_refs": ["C"]},
                {"derived_from_assertion_refs": []},
            ],
            "population_scenarios": [
                {"calibration_standing": "source_calibrated", "calibration_evidence_refs": ["A", "B"]},
                {"calibration_standing": "not_calibrated"},
            ],
        }
        self.assertEqual((5, 3, 3, 1, 14), _graph_envelope(value, REVIEW_LIMITS))
        value["population_scenarios"].append({
            "calibration_standing": "source_calibrated", "calibration_evidence_refs": ["B"]
        })
        self.assertEqual((6, 3, 3, 2, 21), _graph_envelope(value, REVIEW_LIMITS))
        with self.assertRaises(AdministrativeAdmissionError) as captured:
            _graph_envelope(value, replace(REVIEW_LIMITS, max_graph_steps=20))
        self.assertEqual("graph_steps", captured.exception.code)

    def test_rejected_inputs_return_bounded_diagnostics(self) -> None:
        cases = (
            (b'{"private-marker": 0, "private-marker": 1}', "json_duplicate_key"),
            (b'{"private-marker": NaN}', "json_number"),
            (b'{"private-marker": 1e9999}', "json_number"),
            (b'{"private-marker":', "json_syntax"),
            (b"\xff", "utf8"),
            ('{"private-marker": 1}'.encode("utf-16"), "utf8"),
            ('{"private-marker": 1}'.encode("utf-16-le"), "json_syntax"),
            (b'{"private-marker": 1}', "contract_validation"),
            (b"null", "contract_root"),
        )
        for payload, code in cases:
            with self.subTest(code=code, payload_length=len(payload)):
                with self.assertRaises(AdministrativeAdmissionError) as captured:
                    admit_administrative_contract(payload, limits=REVIEW_LIMITS)
                self.assertEqual(code, captured.exception.code)
                self.assertNotIn("private-marker", str(captured.exception))
                self.assertLess(len(str(captured.exception)), 240)

    def test_output_boundary_preserves_previous_accepted_result(self) -> None:
        previous = self.accepted
        exact = replace(REVIEW_LIMITS, max_output_bytes=len(previous.canonical_bytes))
        self.assertEqual(
            previous.canonical_bytes,
            admit_administrative_contract(self.payload, limits=exact).canonical_bytes,
        )
        with self.assertRaises(AdministrativeAdmissionError) as captured:
            admit_administrative_contract(
                self.payload, limits=replace(exact, max_output_bytes=exact.max_output_bytes - 1)
            )
        self.assertEqual("output_bytes", captured.exception.code)
        self.assertEqual(canonical_json_bytes(previous.contract), previous.canonical_bytes)


if __name__ == "__main__":
    unittest.main()

