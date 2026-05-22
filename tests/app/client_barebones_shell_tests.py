#!/usr/bin/env python3
"""Tests for BAREBONES-CLIENT-SHELL-01."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "contract" / "client" / "fixtures"
APP_DESCRIPTOR = ROOT / "tests" / "contract" / "app" / "fixtures" / "valid_client_barebones_descriptor.json"
COMMAND_SURFACE = ROOT / "contracts" / "command" / "command_surface.contract.toml"
DIAGNOSTICS = ROOT / "contracts" / "diagnostics" / "diagnostic_code.registry.json"
REFUSALS = ROOT / "contracts" / "refusal" / "refusal_code.registry.json"
CLIENT_MAIN = ROOT / "apps" / "client" / "main_client.c"

REQUIRED_COMMANDS = {
    "dominium.client.status.v1",
    "dominium.client.diag.v1",
    "dominium.client.verify.v1",
}

REQUIRED_DIAGNOSTICS = {
    "DOM-CLIENT-BAREBONES-OK",
    "DOM-CLIENT-OPTIONAL-CONTENT-MISSING",
    "DOM-CLIENT-RENDERED-UNAVAILABLE",
    "DOM-CLIENT-GAMEPLAY-UNAVAILABLE",
    "DOM-CLIENT-WORLD-RUNTIME-UNAVAILABLE",
    "DOM-CLIENT-PACKAGE-RUNTIME-UNAVAILABLE",
    "DOM-CLIENT-PROVIDER-RUNTIME-UNAVAILABLE",
    "DOM-CLIENT-MODULE-LOADER-UNAVAILABLE",
    "DOM-CLIENT-MODE-UNSUPPORTED",
}

REQUIRED_REFUSALS = {
    "dominium.refusal.client.rendered_unavailable",
    "dominium.refusal.client.gameplay_unavailable",
    "dominium.refusal.client.world_runtime_unavailable",
    "dominium.refusal.client.package_runtime_unavailable",
    "dominium.refusal.client.provider_runtime_unavailable",
    "dominium.refusal.client.module_loader_unavailable",
    "dominium.refusal.client.mode_unsupported",
}

REQUIRED_UNAVAILABLE = {
    "dominium.client.rendered_shell",
    "dominium.client.gameplay",
    "dominium.client.world_runtime",
    "dominium.client.package_runtime",
    "dominium.client.provider_runtime",
    "dominium.client.module_loader",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_false_claims(data: dict, path: Path) -> None:
    support = data.get("support_claims", {})
    runtime = data.get("runtime_support", {})
    forbidden_support = [
        "playable_gameplay",
        "rendered_shell",
        "package_runtime",
        "provider_runtime",
        "module_loader",
        "world_runtime",
        "release_supported",
    ]
    for key in forbidden_support:
        assert support.get(key) is False, f"{path}: support_claims.{key} must be false"
    for key, value in runtime.items():
        if key.endswith("_implemented") or key.endswith("_broad"):
            assert value is False, f"{path}: runtime_support.{key} must be false"


def assert_no_required_optional_content(data: dict, path: Path) -> None:
    for item in data.get("missing_optional_content", []):
        assert item.get("required") is False, f"{path}: optional content cannot be required"


def assert_unavailable_explicit(data: dict, path: Path) -> None:
    unavailable = {item.get("capability_id") for item in data.get("unavailable_capabilities", [])}
    if data.get("status") != "refused":
        assert REQUIRED_UNAVAILABLE.issubset(unavailable), f"{path}: missing explicit unavailable capabilities"
    for item in data.get("unavailable_capabilities", []):
        assert item.get("status") == "unavailable", f"{path}: unavailable status missing"
        assert item.get("expected") is True, f"{path}: unavailable capability must be expected"
        assert item.get("diagnostic_ref"), f"{path}: unavailable capability missing diagnostic"
        assert item.get("refusal_ref"), f"{path}: unavailable capability missing refusal"


def test_valid_barebones_fixtures() -> None:
    for name in (
        "valid_client_barebones_status.json",
        "valid_client_barebones_diag.json",
        "refusal_client_rendered_unavailable.json",
        "refusal_client_gameplay_unavailable.json",
    ):
        path = FIXTURE_DIR / name
        data = load_json(path)
        assert data["schema_id"] == "dominium.client.barebones_result"
        assert data["product_id"] == "dominium.client"
        assert "dominium.product.mode.cli" in data["available_capabilities"]
        assert "dominium.product.mode.headless" in data["available_capabilities"]
        assert_false_claims(data, path)
        assert_no_required_optional_content(data, path)
        assert_unavailable_explicit(data, path)


def test_negative_fixtures_fail_expected_policy() -> None:
    gameplay = load_json(FIXTURE_DIR / "invalid_client_claims_gameplay_without_evidence.json")
    assert gameplay["support_claims"]["playable_gameplay"] is True
    assert "claims_gameplay_without_evidence" in gameplay["expected_failures"]

    optional_pack = load_json(FIXTURE_DIR / "invalid_client_requires_optional_pack_for_status.json")
    assert any(item.get("kind") == "packs" and item.get("required") is True for item in optional_pack["missing_optional_content"])
    assert "requires_optional_pack_for_status" in optional_pack["expected_failures"]


def test_client_descriptor_is_no_content_floor() -> None:
    data = load_json(APP_DESCRIPTOR)
    assert data["app_id"] == "dominium.client"
    assert data["default_packs"] == []
    assert data["enabled_modules"] == []
    assert data["provider_preferences"] == []
    floor = data["barebones_floor"]
    for key, value in floor.items():
        if key.endswith("_required"):
            assert value is False, f"barebones_floor.{key} must be false"
    assert set(data["unavailable_capabilities"]) == REQUIRED_UNAVAILABLE


def test_contract_registries_have_client_entries() -> None:
    command_text = COMMAND_SURFACE.read_text(encoding="utf-8")
    for command_id in REQUIRED_COMMANDS:
        assert command_id in command_text

    diagnostics = load_json(DIAGNOSTICS)
    diagnostic_codes = {item["code"] for item in diagnostics["codes"]}
    assert REQUIRED_DIAGNOSTICS.issubset(diagnostic_codes)

    refusals = load_json(REFUSALS)
    refusal_codes = {item["code"] for item in refusals["codes"]}
    assert REQUIRED_REFUSALS.issubset(refusal_codes)


def test_client_entrypoint_exposes_barebones_flags() -> None:
    text = CLIENT_MAIN.read_text(encoding="utf-8")
    for token in ("--help", "--version", "--status", "--diag", "--verify"):
        assert token in text
    for token in (
        "client_barebones=",
        "optional_packs_required=false",
        "unavailable_capability=dominium.client.rendered_shell",
        "support_claim_playable=false",
        "support_claim_rendered=false",
    ):
        assert token in text


if __name__ == "__main__":
    test_valid_barebones_fixtures()
    test_negative_fixtures_fail_expected_policy()
    test_client_descriptor_is_no_content_floor()
    test_contract_registries_have_client_entries()
    test_client_entrypoint_exposes_barebones_flags()
    print("Client barebones shell tests OK.")
