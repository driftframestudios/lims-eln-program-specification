from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def unique_ids(records: list[dict], label: str) -> set[str]:
    values = [record["id"] for record in records]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} identifiers remain unique")
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
            raise ValueError(f"{forecast['id']} probability range is ordered and bounded")

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
        raise ValueError("constellation repository roles match the five-part contract")

    if set(machine_node["open_receipt_classes"]) != proof_class_ids:
        raise ValueError("Machine Node proof classes match the acceptance registry")

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
        raise ValueError(f"required collaboration surfaces are present: {missing}")

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

