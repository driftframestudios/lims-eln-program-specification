from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_RELEASE = "0.2.0"
GOVERNANCE_RELEASE = "1.0.0"
PENDING_COMMIT = "0" * 40
PENDING_TREE_DIGEST = "git-tree-sha1:" + ("0" * 40)
RELEASE_PATTERNS = {
    "specification": re.compile(r"^spec-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "simulation": re.compile(r"^forecast-[0-9]{4}-Q[1-4]-r[1-9][0-9]*$"),
    "implementation": re.compile(r"^candidate-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "comparison": re.compile(r"^comparison-v[0-9]+\.[0-9]+\.[0-9]+$"),
    "governance": re.compile(r"^governance-v[0-9]+\.[0-9]+\.[0-9]+$"),
}


class NonFiniteNumberError(ValueError):
    """Signal a numeric token outside the JSON number grammar."""


def reject_non_finite(token: str) -> None:
    raise NonFiniteNumberError(f"non-finite numeric token {token!r} is outside JSON")


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
            parse_constant=reject_non_finite,
            parse_float=parse_finite_float,
        )


def unique_ids(records: list[dict], label: str) -> set[str]:
    values = [record["id"] for record in records]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} identifiers contain duplicates")
    return set(values)


def validate() -> dict[str, int]:
    capabilities = load_json("specifications/capabilities.json")["requirements"]
    invariants = load_json("specifications/invariants.json")["rules"]
    scenarios = load_json("examples/scenarios.json")["scenarios"]
    forecasts = load_json("forecasts/forecast-2026-Q3-r1.json")["predictions"]
    roles = load_json("acceptance/roles.json")["roles"]
    proof_classes = load_json("acceptance/proof-classes.json")["proof_classes"]
    receipts = load_json("receipts/open-receipts.json")["receipts"]
    constellation = load_json("constellation.json")
    constellation_lock = load_json("constellation.lock.json")
    machine_node = load_json("machine-node.json")

    requirement_ids = unique_ids(capabilities, "requirement")
    rule_ids = unique_ids(invariants, "rule")
    scenario_ids = unique_ids(scenarios, "scenario")
    role_ids = unique_ids(roles, "role")
    proof_class_ids = unique_ids(proof_classes, "proof class")
    unique_ids(receipts, "receipt")

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

    for proof_class in proof_classes:
        unknown_roles = set(proof_class["required_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{proof_class['id']} references unknown roles: {sorted(unknown_roles)}")

    for receipt in receipts:
        if receipt["proof_class"] not in proof_class_ids:
            raise ValueError(f"{receipt['id']} references an unknown proof class")
        unknown_roles = set(receipt["accountable_roles"]) - role_ids
        if unknown_roles:
            raise ValueError(f"{receipt['id']} references unknown roles: {sorted(unknown_roles)}")

    repository_roles = {entry["role"] for entry in constellation["repositories"]}
    expected_roles = {"program", "actual", "simulation", "comparison", "governance"}
    if repository_roles != expected_roles:
        raise ValueError(
            "constellation repository roles differ from the five-part contract: "
            f"expected={sorted(expected_roles)}, actual={sorted(repository_roles)}"
        )

    if set(machine_node["open_receipt_classes"]) != proof_class_ids:
        raise ValueError(
            "Machine Node proof classes differ from the acceptance registry"
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
        "examples/scenarios.json": load_json("examples/scenarios.json"),
        "receipts/open-receipts.json": load_json("receipts/open-receipts.json"),
        "acceptance/roles.json": load_json("acceptance/roles.json"),
        "acceptance/proof-classes.json": load_json(
            "acceptance/proof-classes.json"
        ),
        "constellation.json": constellation,
        "machine-node.json": machine_node,
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
    if constellation_lock["specification"]["release"] != "spec-v0.2.0":
        raise ValueError(
            "specification lock release differs from planned spec-v0.2.0"
        )
    if constellation_lock["governance"]["release"] != "governance-v1.0.0":
        raise ValueError(
            "governance lock release differs from governance-v1.0.0"
        )
    if constellation_lock["comparison"]["receipt_schema"] != GOVERNANCE_RELEASE:
        raise ValueError(
            f"receipt schema differs from governance {GOVERNANCE_RELEASE}"
        )

    for role in ("specification", "governance"):
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
        ".github/workflows/validate.yml",
        ".github/pull_request_template.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).exists()]
    if missing:
        raise ValueError(f"required collaboration surfaces are absent: {missing}")

    return {
        "requirements": len(requirement_ids),
        "rules": len(rule_ids),
        "scenarios": len(scenario_ids),
        "roles": len(role_ids),
        "proof_classes": len(proof_class_ids),
        "open_receipts": len(receipts),
        "repositories": len(repository_roles),
    }


if __name__ == "__main__":
    summary = validate()
    print(json.dumps({"status": "valid", **summary}, indent=2, sort_keys=True))
