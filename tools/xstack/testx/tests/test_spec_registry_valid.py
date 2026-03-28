"""STRICT test: SPEC-1 registries and optional default pack load deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.specs.registry_valid"
TEST_TAGS = ["strict", "specs", "registry"]


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from specs import (
        compliance_check_rows_by_id,
        load_spec_sheet_rows,
        spec_sheet_rows_by_id,
        spec_type_rows_by_id,
        tolerance_policy_rows_by_id,
    )

    spec_type_registry = _read_json(repo_root, "data/registries/spec_type_registry.json")
    tolerance_registry = _read_json(repo_root, "data/registries/tolerance_policy_registry.json")
    compliance_registry = _read_json(repo_root, "data/registries/compliance_check_registry.json")
    if (not spec_type_registry) or (not tolerance_registry) or (not compliance_registry):
        return {"status": "fail", "message": "required SpecSheet registries are missing or unreadable"}

    spec_type_rows = spec_type_rows_by_id(spec_type_registry)
    tolerance_rows = tolerance_policy_rows_by_id(tolerance_registry)
    compliance_rows = compliance_check_rows_by_id(compliance_registry)

    required_spec_types = {
        "spec.track",
        "spec.road",
        "spec.tunnel",
        "spec.bridge",
        "spec.vehicle_interface",
        "spec.docking_interface",
    }
    required_tolerances = {"tol.default", "tol.strict", "tol.relaxed"}
    required_checks = {
        "check.geometry.clearance",
        "check.geometry.curvature_limit",
        "check.structure.load_rating_stub",
        "check.interface.compatibility",
        "check.operation.max_speed_policy",
    }
    if not required_spec_types.issubset(set(spec_type_rows.keys())):
        return {"status": "fail", "message": "spec_type_registry missing required baseline spec types"}
    if not required_tolerances.issubset(set(tolerance_rows.keys())):
        return {"status": "fail", "message": "tolerance_policy_registry missing required baseline policies"}
    if not required_checks.issubset(set(compliance_rows.keys())):
        return {"status": "fail", "message": "compliance_check_registry missing required baseline checks"}

    pack_payloads = []
    default_pack_rel = "packs/specs/specs.default.realistic.m1/data/spec_sheets.json"
    default_pack_abs = os.path.join(repo_root, default_pack_rel.replace("/", os.sep))
    if os.path.isfile(default_pack_abs):
        default_pack_payload = _read_json(repo_root, default_pack_rel)
        pack_payloads.append(
            {
                "pack_id": "specs.default.realistic.m1",
                "spec_sheets": list(default_pack_payload.get("spec_sheets") or []),
                "payload": dict(default_pack_payload),
            }
        )

    rows, errors = load_spec_sheet_rows(
        inline_rows=[],
        pack_payloads=pack_payloads,
        spec_type_registry=spec_type_registry,
        tolerance_policy_registry=tolerance_registry,
        compliance_check_registry=compliance_registry,
    )
    if errors:
        first = dict(errors[0] if errors else {})
        return {
            "status": "fail",
            "message": "spec sheet load failed: {}".format(str(first.get("message", "unknown"))),
        }

    row_map = spec_sheet_rows_by_id(rows)
    if pack_payloads:
        required_specs = {
            "spec.track.standard_gauge.v1",
            "spec.track.narrow_gauge_example.v1",
            "spec.road.basic_lane_width.v1",
            "spec.tunnel.basic_clearance.v1",
        }
        if not required_specs.issubset(set(row_map.keys())):
            return {"status": "fail", "message": "optional default spec pack missing baseline spec sheet entries"}

    return {"status": "pass", "message": "SpecSheet registries validated and optional pack loads deterministically"}

