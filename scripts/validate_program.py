from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_RELEASE = "0.3.0"
GOVERNANCE_RELEASE = "2.0.0"
RECEIPT_VOCABULARY_RELEASE = "1.0.0"
PROMOTION_RECEIPT_ID = "RCP-PROGRAM-PROMOTION-003"
CANONICAL_CLOSURE_DIGEST = (
    "sha256:6194029aae98f2d70f3a115eed7c0f6b191667f849c89cd548b0e575192e2af9"
)
PENDING_COMMIT = "0" * 40
PENDING_TREE_DIGEST = "git-tree-sha1:" + ("0" * 40)
RELEASE_PATTERNS = {
    "specification": re.compile(r"^spec-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "simulation": re.compile(
        r"^forecast-(?:[0-9]{4}-Q[1-4]-r[1-9][0-9]*|"
        r"[0-9]{4}-FR-v[1-9][0-9]*)$"
    ),
    "implementation": re.compile(r"^candidate-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "comparison": re.compile(r"^comparison-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "governance": re.compile(r"^governance-v[0-9]+\.[0-9]+\.[0-9]+$"),
}


class NonFiniteNumberError(ValueError):
    """Signal a numeric token outside the JSON number grammar."""


class DuplicateObjectKeyError(ValueError):
    """Signal an object whose keys do not form one unambiguous mapping."""


def reject_non_finite(token: str) -> None:
    raise NonFiniteNumberError(f"non-finite numeric token {token!r} is outside JSON")


def require_unique_object_keys(pairs: list[tuple[str, object]]) -> dict:
    """Build one JSON object after proving that every key is unique."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateObjectKeyError(
                f"JSON object key {key!r} appears more than once; "
                "each object key must be unique"
            )
        result[key] = value
    return result


def parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise NonFiniteNumberError(
            f"numeric token {token!r} exceeds the finite JSON domain"
        )
    return value


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open(encoding="utf-8") as handle:
        return json.load(
            handle,
            object_pairs_hook=require_unique_object_keys,
            parse_constant=reject_non_finite,
            parse_float=parse_finite_float,
        )


def sha256_digest(relative_path: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def canonical_json_digest(document: dict) -> str:
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def unique_ids(records: list[dict], label: str) -> set[str]:
    values = [record["id"] for record in records]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} identifiers contain duplicates")
    return set(values)


def validate() -> dict[str, int]:
    capabilities = load_json("specifications/capabilities.json")["requirements"]
    invariants = load_json("specifications/invariants.json")["rules"]
    scenarios = load_json("examples/scenarios.json")["scenarios"]
    forecast_document = load_json("forecasts/forecast-2026-Q3-r2.json")
    forecasts = forecast_document["predictions"]
    roles = load_json("acceptance/roles.json")["roles"]
    proof_classes = load_json("acceptance/proof-classes.json")["proof_classes"]
    receipts = load_json("receipts/open-receipts.json")["receipts"]
    bounded_caller = load_json("specifications/bounded-caller.json")
    operations = bounded_caller["operations"]
    probes_document = load_json("probes/catalog.json")
    probes = probes_document["probes"]
    coordination_horizon = load_json("coordination-horizon.json")
    future_reality = load_json(
        "simulations/future-reality-closure-v0.3.json"
    )
    governance_closure = load_json(
        "simulations/simulated-receipt-closure.v2.json"
    )
    receipt_vocabulary = load_json(
        "specifications/receipt-vocabulary-map.v1.json"
    )
    simulated_closures = future_reality["closures"]
    constellation = load_json("constellation.json")
    constellation_lock = load_json("constellation.lock.json")
    machine_node = load_json("machine-node.json")
    first_receipt = load_json("first-receipt.json")
    release_role = load_json("release/repository-role.json")

    requirement_ids = unique_ids(capabilities, "requirement")
    rule_ids = unique_ids(invariants, "rule")
    scenario_ids = unique_ids(scenarios, "scenario")
    role_ids = unique_ids(roles, "role")
    proof_class_ids = unique_ids(proof_classes, "proof class")
    receipt_ids = unique_ids(receipts, "receipt")
    orientation_receipt_ids = receipt_ids | {PROMOTION_RECEIPT_ID}
    operation_ids = unique_ids(operations, "operation")
    probe_ids = unique_ids(probes, "probe")
    closure_ids = unique_ids(simulated_closures, "simulated closure")
    closure_proof_class_by_id = {
        item["id"]: item["proof_class"] for item in simulated_closures
    }

    for requirement in capabilities:
        unknown_rules = set(requirement["rule_ids"]) - rule_ids
        if unknown_rules:
            raise ValueError(f"{requirement['id']} references unknown rules: {sorted(unknown_rules)}")

    for scenario in scenarios:
        if scenario["requirement_id"] not in requirement_ids:
            raise ValueError(f"{scenario['id']} references an unknown requirement")
        if scenario["rule_id"] not in rule_ids:
            raise ValueError(f"{scenario['id']} references an unknown rule")
        unknown_roles = set(scenario["acceptance_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{scenario['id']} references unknown roles: {sorted(unknown_roles)}")
        operation_id = scenario.get("operation_id")
        if operation_id is not None:
            if operation_id not in operation_ids:
                raise ValueError(
                    f"{scenario['id']} references unknown operation {operation_id}"
                )
            operation = next(
                item for item in operations if item["id"] == operation_id
            )
            if scenario.get("effect_class") != operation["effect_class"]:
                raise ValueError(
                    f"{scenario['id']} effect class differs from {operation_id}"
                )
    scenario_operation_ids = {
        item["operation_id"]
        for item in scenarios
        if "operation_id" in item
    }
    if scenario_operation_ids != operation_ids:
        raise ValueError(
            "specification-by-example scenarios must cover every bounded operation"
        )

    for forecast in forecasts:
        unknown_scenarios = set(forecast["scenario_ids"]) - scenario_ids
        if unknown_scenarios:
            raise ValueError(f"{forecast['id']} references unknown scenarios: {sorted(unknown_scenarios)}")
        probability = forecast["probability"]
        lower, upper = forecast["range"]
        if not (0 <= lower <= probability <= upper <= 1):
            raise ValueError(
                f"{forecast['id']} probability or range falls outside ordered "
                "[0, 1] bounds"
            )
        for field in (
            "probability_of",
            "horizon",
            "estimation_basis",
            "recalibration_trigger",
        ):
            value = (
                forecast_document[field]
                if field == "estimation_basis"
                else forecast[field]
            )
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{forecast['id']} requires a substantive {field}"
                )

    for proof_class in proof_classes:
        unknown_roles = set(proof_class["required_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{proof_class['id']} references unknown roles: {sorted(unknown_roles)}")
        if proof_class["simulated_closure_id"] not in closure_ids:
            raise ValueError(
                f"{proof_class['id']} references an unknown simulated closure"
            )

    for receipt in receipts:
        if receipt["proof_class"] not in proof_class_ids:
            raise ValueError(f"{receipt['id']} references an unknown proof class")
        unknown_roles = set(receipt["accountable_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{receipt['id']} references unknown roles: {sorted(unknown_roles)}")
        if receipt.get("status") != "open":
            raise ValueError(
                f"{receipt['id']} preserves open status for future observed closure"
            )
        simulation = receipt.get("simulation", {})
        observed = receipt.get("future_observed_closure", {})
        if (
            simulation.get("evidence_mode") != "simulated"
            or simulation.get("status") != "closed_in_future_reality"
            or simulation.get("closure_id") not in closure_ids
        ):
            raise ValueError(
                f"{receipt['id']} lacks a valid simulated future-reality closure"
            )
        if (
            closure_proof_class_by_id[simulation["closure_id"]]
            != receipt["proof_class"]
        ):
            raise ValueError(
                f"{receipt['id']} points to a closure for another proof class"
            )
        if (
            observed.get("evidence_mode") != "observed"
            or observed.get("status") != "open"
        ):
            raise ValueError(
                f"{receipt['id']} lacks a separate open observed successor"
            )

    effect_classes = {item["id"] for item in bounded_caller["effect_classes"]}
    expected_effect_classes = {
        "read",
        "narrow_idempotent_write",
        "approval_gated_broad_write",
    }
    if effect_classes != expected_effect_classes:
        raise ValueError(
            "bounded caller effect classes differ from the three-class contract"
        )
    operation_effect_classes = {item["effect_class"] for item in operations}
    if operation_effect_classes != expected_effect_classes:
        raise ValueError(
            "bounded caller operations do not exercise every effect class"
        )
    for operation in operations:
        if operation["input_schema"].get("additional_properties") is not False:
            raise ValueError(
                f"{operation['id']} input contract must reject undeclared fields"
            )
        if not operation["input_schema"].get("required"):
            raise ValueError(f"{operation['id']} requires explicit input fields")

    expected_veracity = set(probes_document["veracity_vocabulary"])
    required_veracity = {
        "verified",
        "source_supported",
        "source_specific",
        "draft_probe",
        "local_measurement_needed",
        "correction_needed",
        "hold_for_resilience_pass",
    }
    if expected_veracity != required_veracity:
        raise ValueError("Practitioner Probe veracity vocabulary is incomplete")
    for probe in probes:
        level_numbers = [item["level"] for item in probe["levels"]]
        if level_numbers != [1, 2, 3, 4, 5]:
            raise ValueError(
                f"{probe['id']} must contain ordered Levels 1 through 5"
            )
        if probe["veracity"]["status"] not in expected_veracity:
            raise ValueError(f"{probe['id']} uses an unknown veracity status")
        links = probe["evidence_links"]
        unknown_requirements = set(links["requirement_ids"]) - requirement_ids
        unknown_rules = set(links["rule_ids"]) - rule_ids
        unknown_scenarios = set(links["scenario_ids"]) - scenario_ids
        unknown_receipts = set(links["receipt_ids"]) - receipt_ids
        if any(
            (
                unknown_requirements,
                unknown_rules,
                unknown_scenarios,
                unknown_receipts,
            )
        ):
            raise ValueError(
                f"{probe['id']} has unknown evidence links: "
                f"requirements={sorted(unknown_requirements)}, "
                f"rules={sorted(unknown_rules)}, "
                f"scenarios={sorted(unknown_scenarios)}, "
                f"receipts={sorted(unknown_receipts)}"
            )

    canonical_successor = future_reality.get("canonical_execution_successor", {})
    canonical_future = governance_closure.get("future_reality", {})
    if (
        future_reality.get("evidence_mode") != "simulated"
        or future_reality.get("authority") != "advisory_design_only"
        or future_reality.get("artifact_role") != "program_design_simulation"
        or future_reality.get("design_status") != "advisory_design"
        or future_reality.get("simulation_id")
        != "DESIGN-FUTURE-REALITY-CLOSURE-001"
        or future_reality.get("design_future_reality_id")
        == canonical_future.get("future_reality_id")
    ):
        raise ValueError(
            "future-reality design must remain simulated, advisory, and "
            "distinct from the canonical executed simulation"
        )
    if (
        canonical_successor.get("closure_id")
        != governance_closure.get("closure_id")
        or canonical_successor.get("future_reality_id")
        != canonical_future.get("future_reality_id")
        or canonical_successor.get("digest") != CANONICAL_CLOSURE_DIGEST
        or canonical_successor.get("authority")
        != "definitive_within_selected_future_reality"
        or canonical_successor.get("production_authorization_effect") != "none"
    ):
        raise ValueError(
            "advisory design must identify the exact canonical executed successor"
        )
    closure_by_id = {item["id"]: item for item in simulated_closures}
    receipt_ids_by_class: dict[str, set[str]] = {
        proof_class_id: {
            item["id"]
            for item in receipts
            if item["proof_class"] == proof_class_id
        }
        for proof_class_id in proof_class_ids
    }
    for closure in simulated_closures:
        if closure["proof_class"] not in proof_class_ids:
            raise ValueError(
                f"{closure['id']} references an unknown proof class"
            )
        if closure.get("status") != "closed_in_simulation":
            raise ValueError(
                f"{closure['id']} must declare closed_in_simulation"
            )
        if not closure.get("probability_of"):
            raise ValueError(f"{closure['id']} must name its probability event")
        if not 0 <= closure.get("probability", -1) <= 1:
            raise ValueError(f"{closure['id']} probability falls outside [0, 1]")
        if set(closure["covered_receipt_ids"]) != receipt_ids_by_class[
            closure["proof_class"]
        ]:
            raise ValueError(
                f"{closure['id']} receipt coverage differs from its proof class"
            )
        observed = closure.get("future_observed_closure", {})
        if (
            observed.get("evidence_mode") != "observed"
            or observed.get("status") != "open"
        ):
            raise ValueError(
                f"{closure['id']} must preserve an open observed successor"
            )
        for decision in closure.get("synthetic_decisions", []):
            if decision["role"] not in role_ids:
                raise ValueError(
                    f"{closure['id']} references unknown synthetic decision role"
                )
        proof_class = next(
            item
            for item in proof_classes
            if item["id"] == closure["proof_class"]
        )
        decision_roles = {
            item["role"] for item in closure.get("synthetic_decisions", [])
        }
        missing_decision_roles = set(proof_class["required_roles"]) - decision_roles
        if missing_decision_roles:
            raise ValueError(
                f"{closure['id']} lacks simulated decisions for required roles: "
                f"{sorted(missing_decision_roles)}"
            )
    for proof_class in proof_classes:
        closure = closure_by_id[proof_class["simulated_closure_id"]]
        if closure["proof_class"] != proof_class["id"]:
            raise ValueError(
                f"{proof_class['id']} points to a closure for another class"
            )

    if (
        receipt_vocabulary.get("contract_id")
        != "RECEIPT-VOCABULARY-MAP-001"
        or receipt_vocabulary.get("version") != RECEIPT_VOCABULARY_RELEASE
    ):
        raise ValueError("receipt vocabulary contract identity differs")
    family_mappings = receipt_vocabulary["family_mappings"]
    expected_individual_families = {
        "configured_vendor",
        "migration_restore",
        "security_observability",
        "scientific_acceptance_support",
        "quality_acceptance_support",
        "regulatory_acceptance_support",
        "engineering_verification",
    }
    if {
        item["individual_receipt_family"] for item in family_mappings
    } != expected_individual_families:
        raise ValueError("receipt vocabulary omits an individual receipt family")
    governance_family_to_proof_class = {
        item["grouped_canonical_family"]: item["program_proof_class"]
        for item in family_mappings
        if item["grouped_canonical_family"] != "explicit_family_required"
    }
    if set(governance_family_to_proof_class.values()) != proof_class_ids:
        raise ValueError(
            "receipt vocabulary differs from the program proof-class registry"
        )
    engineering_mapping = next(
        item
        for item in family_mappings
        if item["individual_receipt_family"] == "engineering_verification"
    )
    if set(engineering_mapping["allowed_grouped_canonical_families"]) != set(
        governance_family_to_proof_class
    ):
        raise ValueError(
            "cross-cutting engineering verification must name every eligible "
            "canonical family and select none implicitly"
        )
    status_mappings = {
        (
            item["source_scope"],
            item["source_status"],
            item["target_scope"],
            item["target_status"],
        )
        for item in receipt_vocabulary["status_mappings"]
    }
    if status_mappings != {
        (
            "program individual receipt simulation link",
            "closed_in_future_reality",
            "canonical selected-future closure",
            "closed_in_simulation",
        ),
        (
            "future environment-observed individual receipt",
            "open",
            "canonical environment-observed aggregate state",
            "separate_unasserted_state",
        ),
    }:
        raise ValueError("receipt status vocabulary differs from the two-state map")
    projected_families = {
        item["family"] for item in governance_closure["receipt_closures"]
    }
    if projected_families != set(governance_family_to_proof_class):
        raise ValueError(
            "governance closure projection must contain exactly four families"
        )
    if {
        governance_family_to_proof_class[item]
        for item in projected_families
    } != proof_class_ids:
        raise ValueError(
            "governance closure projection differs from the proof-class registry"
        )
    if (
        governance_closure.get("evidence_mode") != "simulated"
        or governance_closure.get("closure_status")
        != "closed_in_simulation"
        or governance_closure.get("environment_observed_closure")
        != "separate_unasserted_state"
        or governance_closure.get("production_authorization_effect") != "none"
    ):
        raise ValueError(
            "governance closure projection collapses evidence or authority state"
        )
    if (
        governance_closure.get("closure_id")
        != "CLOSURE-SIM-SUBSTANTIVE-2028-V1"
        or canonical_future.get("future_reality_id")
        != "FUTURE-REALITY-LIMS-2028-001"
        or canonical_json_digest(governance_closure)
        != CANONICAL_CLOSURE_DIGEST
    ):
        raise ValueError(
            "program canonical closure differs from the released simulation closure"
        )
    projected_scenario_ids = {
        scenario_id
        for closure in governance_closure["receipt_closures"]
        for scenario_id in closure["scenario_ids"]
    }
    if (
        len(projected_scenario_ids) != 12
        or any(
            not scenario_id.startswith("SCENARIO-")
            for scenario_id in projected_scenario_ids
        )
    ):
        raise ValueError(
            "canonical closure must preserve its twelve executable simulation "
            "scenario identifiers; program design scenarios remain a distinct "
            "namespace"
        )
    if (
        release_role.get("repository_role") != "program_specification"
        or release_role.get("repository_release") != PROGRAM_RELEASE
        or release_role.get("release_state") != "candidate_pending_promotion"
        or release_role["canonical_closure"]["digest"]
        != CANONICAL_CLOSURE_DIGEST
        or release_role["canonical_closure"]["authority"]
        != "definitive_within_selected_future_reality"
        or release_role["canonical_closure"]["production_authorization_effect"]
        != "none"
        or release_role["advisory_design"]["future_reality_id"]
        != future_reality["design_future_reality_id"]
        or release_role["advisory_design"]["digest"]
        != sha256_digest("simulations/future-reality-closure-v0.3.json")
        or release_role["advisory_design"]["authority"]
        != "advisory_design_only"
        or release_role["contract_bindings"]["receipt_vocabulary_map"]["digest"]
        != sha256_digest("specifications/receipt-vocabulary-map.v1.json")
        or release_role["release_coordinates"]["candidate_commit"]
        != PENDING_COMMIT
        or release_role["release_coordinates"]["candidate_tree_digest"]
        != PENDING_TREE_DIGEST
        or release_role["release_coordinates"]["candidate_coordinate_status"]
        != "pending_release_promotion"
    ):
        raise ValueError("repository release role collapses design and execution")

    horizon_item_ids = {
        item["item_id"] for item in coordination_horizon["work_items"]
    }
    expected_horizon_item_ids = {
        "HORIZON-CONTRACTS",
        "HORIZON-VERTICAL-SLICE",
        "HORIZON-EXTENSIONS",
    }
    if horizon_item_ids != expected_horizon_item_ids:
        raise ValueError(
            "Coordination Horizon differs from the three-band program contract"
        )
    if not set(coordination_horizon["current_item_ids"]) <= horizon_item_ids:
        raise ValueError(
            "Coordination Horizon current items reference unknown work"
        )
    if (
        coordination_horizon["metadata"]["schema_version"]
        != GOVERNANCE_RELEASE
    ):
        raise ValueError("Coordination Horizon schema binding differs")

    repository_roles = {entry["role"] for entry in constellation["repositories"]}
    expected_roles = {"program", "actual", "simulation", "comparison", "governance"}
    if repository_roles != expected_roles:
        raise ValueError(
            "constellation repository roles differ from the five-part contract: "
            f"expected={sorted(expected_roles)}, actual={sorted(repository_roles)}"
        )

    if set(machine_node["open_receipts"]) != orientation_receipt_ids:
        raise ValueError(
            "Machine Node open receipts differ from the substantive receipt "
            "registry plus candidate-promotion receipt"
        )
    if (
        machine_node["schema_release"] != GOVERNANCE_RELEASE
        or machine_node["control_plane_profile"] != "0.3.0"
        or machine_node["repository_role"] != "program_specification"
    ):
        raise ValueError("Machine Node governance schema binding differs")
    if (
        machine_node["lifecycle_state"] != "settling"
        or machine_node["current_provenance"]["commit"] != PENDING_COMMIT
        or machine_node["current_provenance"]["digest"]
        != "sha256:" + ("0" * 64)
        or "seed_lineage" not in machine_node
    ):
        raise ValueError(
            "Machine Node must expose settling candidate provenance and seed lineage"
        )
    if (
        machine_node["coordination_horizon_id"]
        != coordination_horizon["horizon_id"]
        or machine_node["authority"]["mode"] != "orientation_only"
    ):
        raise ValueError("Machine Node orientation posture differs")
    if (
        machine_node["first_receipt_contract_id"]
        != first_receipt["first_receipt_id"]
        or first_receipt["machine_node_id"] != machine_node["machine_node_id"]
        or first_receipt["coordination_horizon_id"]
        != coordination_horizon["horizon_id"]
    ):
        raise ValueError("First receipt orientation coordinates differ")
    if (
        first_receipt["authority_posture"]["mode"] != "orientation_only"
        or set(first_receipt["open_receipts"]) != orientation_receipt_ids
    ):
        raise ValueError("First receipt authority or open-receipt posture differs")

    current_horizon_items = [
        item
        for item in coordination_horizon["work_items"]
        if item["item_id"] in coordination_horizon["current_item_ids"]
    ]
    promotion_horizon_items = [
        item
        for item in current_horizon_items
        if "promotion"
        in " ".join(
            str(item.get(field, ""))
            for field in ("item_id", "horizon_label", "desired_state")
        ).lower()
    ]
    if not any(
        item.get("state") == "settling" for item in promotion_horizon_items
    ):
        raise ValueError(
            "pending candidate provenance requires a current settling "
            "promotion item"
        )

    promotion_coordinates = release_role.get("promotion_coordinates", {})
    expected_promotion_roles = {
        "site_reading_governance",
        "program_specification",
        "enterprise_implementation",
        "simulated_final_state",
        "comparative_evidence",
    }
    if (
        promotion_coordinates.get("status")
        != "pending_cross_repository_settlement"
        or promotion_coordinates.get("open_receipt_id")
        != PROMOTION_RECEIPT_ID
        or set(promotion_coordinates.get("required_roles", []))
        != expected_promotion_roles
    ):
        raise ValueError(
            "release manifest promotion coordinates differ from the "
            "candidate-promotion receipt"
        )

    contract_paths = {
        "CALLER-CONTRACT-001": (
            "specifications/bounded-caller.json",
            "file",
        ),
        "LIMS-ELN-PRACTITIONER-PROBES-001": (
            "probes/catalog.json",
            "file",
        ),
        "LIMS-ELN-PROOF-CLASSES-001": (
            "acceptance/proof-classes.json",
            "file",
        ),
        "DESIGN-FUTURE-REALITY-CLOSURE-001": (
            "simulations/future-reality-closure-v0.3.json",
            "file",
        ),
        "SIMULATED-SUBSTANTIVE-CLOSURE-2028-V1": (
            "simulations/simulated-receipt-closure.v2.json",
            "canonical_json",
        ),
        "RECEIPT-VOCABULARY-MAP-001": (
            "specifications/receipt-vocabulary-map.v1.json",
            "file",
        ),
    }
    machine_contracts = {
        item["contract_id"]: item for item in machine_node["contracts"]
    }
    first_receipt_contracts = {
        item["contract_id"]: item for item in first_receipt["contract_state"]
    }
    if (
        set(machine_contracts) != set(contract_paths)
        or set(first_receipt_contracts) != set(contract_paths)
    ):
        raise ValueError("Machine Node or first receipt contract set differs")
    for contract_id, (path, digest_mode) in contract_paths.items():
        expected_digest = (
            canonical_json_digest(load_json(path))
            if digest_mode == "canonical_json"
            else sha256_digest(path)
        )
        if (
            machine_contracts[contract_id]["digest"] != expected_digest
            or first_receipt_contracts[contract_id]["digest"] != expected_digest
        ):
            raise ValueError(
                f"{contract_id} orientation digest differs from {path}"
            )

    for role, pattern in RELEASE_PATTERNS.items():
        release = constellation_lock[role]["release"]
        if pattern.fullmatch(release) is None:
            raise ValueError(
                f"{role} release {release!r} falls outside its protected tag family"
            )

    versioned_documents = {
        "specifications/capabilities.json": load_json(
            "specifications/capabilities.json"
        ),
        "specifications/invariants.json": load_json(
            "specifications/invariants.json"
        ),
        "specifications/bounded-caller.json": bounded_caller,
        "examples/scenarios.json": load_json("examples/scenarios.json"),
        "receipts/open-receipts.json": load_json("receipts/open-receipts.json"),
        "probes/catalog.json": probes_document,
        "simulations/future-reality-closure-v0.3.json": future_reality,
        "forecasts/forecast-2026-Q3-r2.json": forecast_document,
        "acceptance/roles.json": load_json("acceptance/roles.json"),
        "acceptance/proof-classes.json": load_json(
            "acceptance/proof-classes.json"
        ),
        "constellation.json": constellation,
    }
    for path, document in versioned_documents.items():
        if document.get("version") != PROGRAM_RELEASE:
            raise ValueError(
                f"{path} version differs from planned program release "
                f"{PROGRAM_RELEASE}"
            )
    if constellation_lock.get("constellation_version") != PROGRAM_RELEASE:
        raise ValueError(
            "constellation lock version differs from the planned program release"
        )
    if constellation_lock["specification"]["release"] != "spec-v0.3.0":
        raise ValueError(
            "specification lock release differs from planned spec-v0.3.0"
        )
    if constellation_lock["governance"]["release"] != "governance-v2.0.0":
        raise ValueError(
            "governance lock release differs from governance-v2.0.0"
        )
    if (
        constellation_lock["governance"].get("schema_version")
        != GOVERNANCE_RELEASE
        or constellation_lock["governance"].get("profile")
        != "Control Plane Profile 0.3.0"
    ):
        raise ValueError(
            "governance lock binding differs from Control Plane Profile 0.3.0"
        )
    if constellation_lock["comparison"]["receipt_schema"] != GOVERNANCE_RELEASE:
        raise ValueError(
            f"receipt schema differs from governance {GOVERNANCE_RELEASE}"
        )

    for role in RELEASE_PATTERNS:
        coordinate = constellation_lock[role]
        status = coordinate.get("coordinate_status")
        if status == "pending_release_commit":
            if (
                coordinate.get("commit") != PENDING_COMMIT
                or coordinate.get("digest") != PENDING_TREE_DIGEST
            ):
                raise ValueError(
                    f"{role} pending coordinate differs from the explicit "
                    "zero-placeholder contract"
                )
        elif status == "pinned":
            if (
                coordinate.get("commit") == PENDING_COMMIT
                or coordinate.get("digest") == PENDING_TREE_DIGEST
            ):
                raise ValueError(
                    f"{role} pinned coordinate requires observed commit and tree"
                )
        else:
            raise ValueError(
                f"{role} coordinate status must be pending_release_commit or pinned"
            )

    required_paths = [
        "README.md",
        "BRANCHING.md",
        "GOVERNANCE.md",
        "SECURITY.md",
        "constellation.lock.json",
        "coordination-horizon.json",
        "first-receipt.json",
        "release/repository-role.json",
        "specifications/bounded-caller.json",
        "specifications/receipt-vocabulary-map.v1.json",
        "probes/catalog.json",
        "simulations/future-reality-closure-v0.3.json",
        "simulations/simulated-receipt-closure.v2.json",
        ".github/workflows/validate.yml",
        ".github/workflows/branch-policy.yml",
        ".github/dependabot.yml",
        ".github/pull_request_template.md",
        "scripts/check_branch_flow.py",
        "tests/test_branch_flow.py",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    if missing:
        raise ValueError(f"required collaboration surfaces are absent: {missing}")

    return {
        "requirements": len(requirement_ids),
        "rules": len(rule_ids),
        "scenarios": len(scenario_ids),
        "operations": len(operation_ids),
        "probes": len(probe_ids),
        "simulated_closures": len(closure_ids),
        "governance_closure_families": len(projected_families),
        "receipt_vocabulary_mappings": len(family_mappings),
        "roles": len(role_ids),
        "proof_classes": len(proof_class_ids),
        "open_receipts": len(receipts),
        "promotion_receipts": 1,
        "repositories": len(repository_roles),
    }


if __name__ == "__main__":
    summary = validate()
    print(json.dumps({"status": "valid", **summary}, indent=2, sort_keys=True))
