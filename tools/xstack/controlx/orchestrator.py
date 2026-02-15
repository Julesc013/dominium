"""Deterministic ControlX orchestration for FAST/STRICT/FULL profiles."""

from __future__ import annotations

import json
import os
import time
from typing import Callable, Dict, List, Tuple

from tools.xstack.auditx import run_auditx_check
from tools.xstack.compatx.check import run_compatx_check
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.pack_contrib.parser import parse_contributions
from tools.xstack.pack_loader.dependency_resolver import resolve_packs
from tools.xstack.pack_loader.loader import load_pack_set
from tools.xstack.performx import run_performx_check
from tools.xstack.packagingx import build_dist_layout, run_lab_build_validation, validate_dist_layout
from tools.xstack.registry_compile.bundle_profile import load_bundle_profiles, resolve_bundle_selection, validate_bundle_file
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from tools.xstack.repox import run_repox_check
from tools.xstack.securex import run_securex_check
from tools.xstack.sessionx import boot_session_spec, create_session_spec
from tools.xstack.testx import run_testx_suite

from .types import RunContext
from .utils import ensure_dir, file_sha256, norm, now_utc_iso, read_json, write_json


StepFn = Callable[[RunContext], Dict[str, object]]


def _severity_rank(severity: str) -> int:
    token = str(severity or "").strip().lower()
    if token == "warn":
        return 0
    if token == "fail":
        return 1
    if token == "refusal":
        return 2
    return 9


def _sort_findings(findings: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return sorted(
        [
            {str(key): value for key, value in row.items()}
            for row in findings
            if isinstance(row, dict)
        ],
        key=lambda row: (
            _severity_rank(str(row.get("severity", ""))),
            str(row.get("code", "")),
            str(row.get("file_path", "")),
            int(row.get("line_number", 0) or 0),
            str(row.get("message", "")),
        ),
    )


def _status_from_findings(findings: List[Dict[str, object]]) -> str:
    severities = set(str(row.get("severity", "")) for row in findings)
    if "refusal" in severities:
        return "refusal"
    if "fail" in severities:
        return "fail"
    return "pass"


def _artifact_row(repo_root: str, path: str) -> Dict[str, str]:
    abs_path = path if os.path.isabs(path) else os.path.join(repo_root, path.replace("/", os.sep))
    rel = norm(os.path.relpath(abs_path, repo_root))
    if not os.path.isfile(abs_path):
        return {"path": rel, "sha256": ""}
    return {"path": rel, "sha256": file_sha256(abs_path)}


def _validate_json_file(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {}, "missing file"
    try:
        payload = read_json(abs_path)
    except Exception:
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid JSON object root"
    return payload, ""


def _step_pack(repo_root: RunContext) -> Dict[str, object]:
    loaded = load_pack_set(repo_root=repo_root.repo_root)
    findings: List[Dict[str, object]] = []
    if loaded.get("result") != "complete":
        for row in loaded.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.pack.load_failed")),
                    "message": str(row.get("message", "")),
                    "file_path": str(row.get("path", "")),
                }
            )
        return {
            "status": "refusal",
            "message": "pack validation refused",
            "findings": findings,
        }

    contrib = parse_contributions(repo_root=repo_root.repo_root, packs=loaded.get("packs") or [])
    if contrib.get("result") != "complete":
        for row in contrib.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.pack.contrib_failed")),
                    "message": str(row.get("message", "")),
                    "file_path": str(row.get("path", "")),
                }
            )
        return {
            "status": "refusal",
            "message": "pack contribution validation refused",
            "findings": findings,
        }

    rows = []
    for row in sorted(loaded.get("packs") or [], key=lambda item: str(item.get("pack_id", ""))):
        rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "category": str(row.get("category", "")),
                "version": str(row.get("version", "")),
                "dependency_count": len(row.get("dependencies") or []),
                "signature_status": str(row.get("signature_status", "")),
            }
        )
    out_path = os.path.join(repo_root.output_dir, "pack_list.json")
    write_json(
        out_path,
        {
            "result": "complete",
            "pack_count": int(loaded.get("pack_count", 0)),
            "contribution_count": int(contrib.get("contribution_count", 0)),
            "packs": rows,
        },
    )
    return {
        "status": "pass",
        "message": "pack validation passed (packs={}, contributions={})".format(
            int(loaded.get("pack_count", 0)),
            int(contrib.get("contribution_count", 0)),
        ),
        "findings": [],
        "artifacts": [norm(os.path.relpath(out_path, repo_root.repo_root))],
    }


def _step_bundle(context: RunContext) -> Dict[str, object]:
    listing = load_bundle_profiles(repo_root=context.repo_root, schema_repo_root=context.repo_root)
    findings: List[Dict[str, object]] = []
    if listing.get("result") != "complete":
        for row in listing.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.bundle_profile.invalid")),
                    "message": str(row.get("message", "")),
                    "file_path": str(row.get("path", "")),
                }
            )
        return {
            "status": "refusal",
            "message": "bundle validation refused",
            "findings": findings,
        }

    default_bundle_path = os.path.join(context.repo_root, "bundles", "bundle.base.lab", "bundle.json")
    validated = validate_bundle_file(repo_root=context.repo_root, bundle_file_path=default_bundle_path, schema_repo_root=context.repo_root)
    if validated.get("result") != "complete":
        for row in validated.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.bundle_profile.invalid")),
                    "message": str(row.get("message", "")),
                    "file_path": "bundles/bundle.base.lab/bundle.json",
                }
            )
        return {
            "status": "refusal",
            "message": "bundle.base.lab validation refused",
            "findings": findings,
        }

    artifact_path = "bundles/bundle.base.lab/bundle.json"
    return {
        "status": "pass",
        "message": "bundle validation passed (bundles={})".format(int(listing.get("bundle_count", 0))),
        "findings": [],
        "artifacts": [artifact_path],
    }


def _step_registry_compile(context: RunContext) -> Dict[str, object]:
    result = compile_bundle(
        repo_root=context.repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        use_cache=bool(context.cache_enabled),
    )
    if result.get("result") != "complete":
        findings = []
        for row in result.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.registry_compile.failed")),
                    "message": str(row.get("message", "")),
                    "file_path": str(row.get("path", "")),
                }
            )
        return {
            "status": "refusal",
            "message": "registry compile refused",
            "findings": findings,
        }

    artifact_paths = []
    for token in (
        "build/registries/domain.registry.json",
        "build/registries/law.registry.json",
        "build/registries/experience.registry.json",
        "build/registries/lens.registry.json",
        "build/registries/activation_policy.registry.json",
        "build/registries/budget_policy.registry.json",
        "build/registries/fidelity_policy.registry.json",
        "build/registries/astronomy.catalog.index.json",
        "build/registries/site.registry.index.json",
        "build/registries/ui.registry.json",
        "build/lockfile.json",
    ):
        abs_path = os.path.join(context.repo_root, token.replace("/", os.sep))
        if os.path.isfile(abs_path):
            artifact_paths.append(token)
    cache_hit = bool(result.get("cache_hit", False))
    return {
        "status": "pass",
        "message": "registry compile passed (cache_hit={})".format("true" if cache_hit else "false"),
        "findings": [],
        "artifacts": sorted(set(artifact_paths)),
        "details": {
            "cache_hit": cache_hit,
            "cache_key": str(result.get("cache_key", "")),
            "pack_lock_hash": str(result.get("pack_lock_hash", "")),
            "ordered_pack_ids": list(result.get("ordered_pack_ids") or []),
            "registry_hashes": dict(result.get("registry_hashes") or {}),
        },
    }


def _step_lockfile_validate(context: RunContext) -> Dict[str, object]:
    rel_path = "build/lockfile.json"
    payload, err = _validate_json_file(context.repo_root, rel_path)
    findings: List[Dict[str, object]] = []
    if err:
        findings.append(
            {
                "severity": "refusal",
                "code": "refuse.lockfile.unavailable",
                "message": "lockfile unavailable: {}".format(err),
                "file_path": rel_path,
            }
        )
        return {"status": "refusal", "message": "lockfile validation refused", "findings": findings}

    schema_check = validate_instance(
        repo_root=context.repo_root,
        schema_name="bundle_lockfile",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(schema_check.get("valid", False)):
        for row in schema_check.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.lockfile.schema_invalid")),
                    "message": str(row.get("message", "")),
                    "file_path": rel_path,
                }
            )

    lock_check = validate_lockfile_payload(payload)
    if lock_check.get("result") != "complete":
        for row in lock_check.get("errors", []):
            findings.append(
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.lockfile.invalid")),
                    "message": str(row.get("message", "")),
                    "file_path": rel_path,
                }
            )

    if context.profile in ("STRICT", "FULL") and not findings:
        loaded = load_pack_set(repo_root=context.repo_root)
        if loaded.get("result") != "complete":
            findings.append(
                {
                    "severity": "refusal",
                    "code": "refuse.lockfile.strict_pack_load_failed",
                    "message": "strict lockfile check could not load pack set",
                    "file_path": "packs",
                }
            )
        else:
            bundle = resolve_bundle_selection(
                bundle_id=str(payload.get("bundle_id", "")),
                packs=loaded.get("packs") or [],
                repo_root=context.repo_root,
                schema_repo_root=context.repo_root,
            )
            if bundle.get("result") != "complete":
                findings.append(
                    {
                        "severity": "refusal",
                        "code": "refuse.lockfile.strict_bundle_selection_failed",
                        "message": "strict lockfile check could not resolve bundle selection",
                        "file_path": "bundles",
                    }
                )
            else:
                resolved = resolve_packs(loaded.get("packs") or [], bundle_selection=list(bundle.get("selected_pack_ids") or []))
                if resolved.get("result") != "complete":
                    findings.append(
                        {
                            "severity": "refusal",
                            "code": "refuse.lockfile.strict_dependency_resolution_failed",
                            "message": "strict lockfile check could not resolve pack dependencies",
                            "file_path": "packs",
                        }
                    )
                else:
                    expected_rows = [
                        {
                            "pack_id": str(row.get("pack_id", "")),
                            "version": str(row.get("version", "")),
                            "canonical_hash": str((row.get("manifest") or {}).get("canonical_hash", "")),
                            "signature_status": str(row.get("signature_status", "")),
                        }
                        for row in (resolved.get("ordered_pack_list") or [])
                    ]
                    actual_rows = [
                        {
                            "pack_id": str(row.get("pack_id", "")),
                            "version": str(row.get("version", "")),
                            "canonical_hash": str(row.get("canonical_hash", "")),
                            "signature_status": str(row.get("signature_status", "")),
                        }
                        for row in (payload.get("resolved_packs") or [])
                        if isinstance(row, dict)
                    ]
                    if expected_rows != actual_rows:
                        findings.append(
                            {
                                "severity": "refusal",
                                "code": "refuse.lockfile.strict_bundle_mismatch",
                                "message": "lockfile resolved_packs do not match deterministic bundle composition",
                                "file_path": rel_path,
                            }
                        )

    ordered = _sort_findings(findings)
    status = _status_from_findings(ordered)
    if status != "pass":
        return {"status": status, "message": "lockfile validation completed with findings", "findings": ordered}
    return {
        "status": "pass",
        "message": "lockfile validation passed",
        "findings": [],
        "artifacts": [rel_path],
    }


def _step_repox(context: RunContext) -> Dict[str, object]:
    return run_repox_check(repo_root=context.repo_root, profile=context.profile)


def _step_auditx(context: RunContext) -> Dict[str, object]:
    return run_auditx_check(repo_root=context.repo_root, profile=context.profile)


def _step_testx(context: RunContext) -> Dict[str, object]:
    if context.skip_testx:
        return {
            "status": "pass",
            "message": "testx skipped by DOM_XSTACK_SKIP_TESTX",
            "findings": [],
        }
    result = run_testx_suite(
        repo_root=context.repo_root,
        profile=context.profile,
        shards=context.shards,
        shard_index=context.shard_index,
        cache_enabled=context.cache_enabled,
    )
    details_path = os.path.join(context.output_dir, "testx_results.json")
    write_json(
        details_path,
        {
            "selection": result.get("selection") or {},
            "tests": result.get("tests") or [],
            "status": result.get("status"),
            "message": result.get("message"),
        },
    )
    result["artifacts"] = [norm(os.path.relpath(details_path, context.repo_root))]
    return result


def _step_packaging_verify(context: RunContext) -> Dict[str, object]:
    smoke_out = "build/dist.smoke.{}".format(str(context.profile).strip().lower())
    build_result = build_dist_layout(
        repo_root=context.repo_root,
        bundle_id="bundle.base.lab",
        out_dir=smoke_out,
        use_cache=bool(context.cache_enabled),
    )
    if build_result.get("result") != "complete":
        return {
            "status": "refusal",
            "message": "deterministic packaging smoke refused",
            "findings": [
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "REFUSE_DIST_BUILD_FAILED")),
                    "message": str(row.get("message", "")),
                    "file_path": "dist",
                }
                for row in (build_result.get("errors") or [])
            ],
        }

    validate_result = validate_dist_layout(repo_root=context.repo_root, dist_root=smoke_out)
    if validate_result.get("result") != "complete":
        return {
            "status": "refusal",
            "message": "deterministic packaging validation refused",
            "findings": [
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "REFUSE_DIST_VALIDATE_FAILED")),
                    "message": str(row.get("message", "")),
                    "file_path": "dist",
                }
                for row in (validate_result.get("errors") or [])
            ],
        }

    details: Dict[str, object] = {
        "packaging_smoke_status": "pass",
        "packaging_smoke_out_dir": str(build_result.get("out_dir", "")),
        "packaging_content_hash": str(build_result.get("canonical_content_hash", "")),
        "packaging_manifest_hash": str(build_result.get("manifest_hash", "")),
        "pack_lock_hash": str(build_result.get("pack_lock_hash", "")),
        "registry_hashes": dict(build_result.get("registry_hashes") or {}),
        "lab_build_status": "pass",
        "composite_hash_anchor": "",
    }
    artifacts = sorted(
        set(
            path
            for path in (
                str(build_result.get("manifest_path", "")),
                str(build_result.get("lockfile_path", "")),
            )
            if path
        )
    )
    message = "packaging smoke passed (content_hash={})".format(str(build_result.get("canonical_content_hash", "")))

    if context.profile in ("STRICT", "FULL"):
        lab = run_lab_build_validation(
            repo_root=context.repo_root,
            bundle_id="bundle.base.lab",
            dist_a="build/dist.lab_validation.a",
            dist_b="build/dist.lab_validation.b",
            save_id="save.xstack.lab_validation.{}".format(str(context.profile).strip().lower()),
        )
        if lab.get("result") != "complete":
            return {
                "status": "refusal",
                "message": "lab build validation refused",
                "findings": [
                    {
                        "severity": "refusal",
                        "code": str(row.get("code", "REFUSE_LAB_BUILD_VALIDATION_FAILED")),
                        "message": str(row.get("message", "")),
                        "file_path": "build/dist.lab_validation",
                    }
                    for row in (lab.get("errors") or [])
                ],
            }
        details.update(
            {
                "lab_build_status": str(lab.get("lab_build_status", "pass")),
                "composite_hash_anchor": str(lab.get("composite_hash_anchor", "")),
                "pack_lock_hash": str(lab.get("pack_lock_hash", "")),
                "registry_hashes": dict(lab.get("registry_hashes") or {}),
                "lab_run_meta_path": str(lab.get("run_meta_path", "")),
                "lab_dist_hash": str(lab.get("dist_content_hash", "")),
            }
        )
        artifacts.extend(
            [
                "build/dist.lab_validation.a/manifest.json",
                "build/dist.lab_validation.b/manifest.json",
            ]
        )
        message = "packaging + lab build validation passed (composite_hash={})".format(
            str(lab.get("composite_hash_anchor", ""))
        )

    return {
        "status": "pass",
        "message": message,
        "findings": [],
        "artifacts": sorted(set(artifacts)),
        "details": details,
    }


def _step_performx(context: RunContext) -> Dict[str, object]:
    return run_performx_check(repo_root=context.repo_root, profile=context.profile)


def _step_securex(context: RunContext) -> Dict[str, object]:
    return run_securex_check(repo_root=context.repo_root, profile=context.profile)


def _step_session_spec_fixture(context: RunContext) -> Dict[str, object]:
    rel = "tools/xstack/testdata/session/session_spec.fixture.json"
    abs_path = os.path.join(context.repo_root, rel.replace("/", os.sep))
    payload, err = _validate_json_file(context.repo_root, rel)
    if err:
        return {
            "status": "refusal",
            "message": "session fixture validation refused",
            "findings": [
                {
                    "severity": "refusal",
                    "code": "refuse.session.fixture_missing",
                    "message": "session fixture is unavailable: {}".format(err),
                    "file_path": rel,
                }
            ],
        }
    validation = validate_instance(
        repo_root=context.repo_root,
        schema_name="session_spec",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(validation.get("valid", False)):
        return {
            "status": "refusal",
            "message": "session fixture failed schema validation",
            "findings": [
                {
                    "severity": "refusal",
                    "code": str(row.get("code", "refuse.session.fixture_invalid")),
                    "message": str(row.get("message", "")),
                    "file_path": rel,
                }
                for row in (validation.get("errors") or [])
            ],
        }
    if not os.path.isfile(abs_path):
        return {
            "status": "refusal",
            "message": "session fixture path is missing",
            "findings": [
                {
                    "severity": "refusal",
                    "code": "refuse.session.fixture_missing",
                    "message": "missing fixture file",
                    "file_path": rel,
                }
            ],
        }
    return {
        "status": "pass",
        "message": "session fixture validation passed",
        "findings": [],
        "artifacts": [rel],
    }


def _step_session_boot_smoke(context: RunContext) -> Dict[str, object]:
    save_id = "save.xstack.smoke.{}".format(str(context.profile).strip().lower())
    created = create_session_spec(
        repo_root=context.repo_root,
        save_id=save_id,
        bundle_id="bundle.base.lab",
        scenario_id="scenario.lab.galaxy_nav",
        mission_id="",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        rng_seed_string="seed.xstack.session.smoke",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.xstack.universe.smoke",
        universe_id="",
        entitlements=[
            "session.boot",
            "entitlement.camera_control",
            "entitlement.teleport",
            "entitlement.time_control",
            "entitlement.inspect",
            "lens.nondiegetic.access",
            "ui.window.lab.nav",
        ],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="observer",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        refusal_payload = created.get("refusal") or {}
        return {
            "status": "refusal",
            "message": "session create refused",
            "findings": [
                {
                    "severity": "refusal",
                    "code": str(refusal_payload.get("reason_code", "refuse.session.create_failed")),
                    "message": str(refusal_payload.get("message", "")),
                    "file_path": "saves/{}".format(save_id),
                }
            ],
        }

    session_rel = str(created.get("session_spec_path", ""))
    session_abs = os.path.join(context.repo_root, session_rel.replace("/", os.sep))
    booted = boot_session_spec(
        repo_root=context.repo_root,
        session_spec_path=session_abs,
        bundle_id="bundle.base.lab",
        compile_if_missing=False,
    )
    if booted.get("result") != "complete":
        refusal_payload = booted.get("refusal") or {}
        return {
            "status": "refusal",
            "message": "session boot refused",
            "findings": [
                {
                    "severity": "refusal",
                    "code": str(refusal_payload.get("reason_code", "refuse.session.boot_failed")),
                    "message": str(refusal_payload.get("message", "")),
                    "file_path": session_rel,
                }
            ],
        }
    return {
        "status": "pass",
        "message": "session boot/shutdown smoke passed (run_id={})".format(str(booted.get("run_id", ""))),
        "findings": [],
        "artifacts": sorted(
            set(
                str(path)
                for path in (
                    str(created.get("session_spec_path", "")),
                    str(created.get("universe_identity_path", "")),
                    str(created.get("universe_state_path", "")),
                    str(booted.get("run_meta_path", "")),
                )
                if str(path).strip()
            )
        ),
        "details": {
            "session_spec_hash": str(created.get("session_spec_hash", "")),
            "pack_lock_hash": str(created.get("pack_lock_hash", "")),
            "registry_hashes": dict(created.get("registry_hashes") or {}),
            "run_id": str(booted.get("run_id", "")),
            "deterministic_fields_hash": str(booted.get("deterministic_fields_hash", "")),
            "selected_lens_id": str(booted.get("selected_lens_id", "")),
            "perceived_model_hash": str(booted.get("perceived_model_hash", "")),
            "render_model_hash": str(booted.get("render_model_hash", "")),
        },
    }


def _step_definitions() -> List[Tuple[str, str, StepFn]]:
    return [
        ("01.compatx.check", "compatx", lambda ctx: run_compatx_check(repo_root=ctx.repo_root, profile=ctx.profile)),
        ("02.bundle.validate", "bundle_profile", _step_bundle),
        ("03.pack.validate", "pack_loader", _step_pack),
        ("04.registry.compile", "registry_compile", _step_registry_compile),
        ("05.lockfile.validate", "registry_compile", _step_lockfile_validate),
        ("06.session_spec.fixture.validate", "sessionx", _step_session_spec_fixture),
        ("07.session_boot.smoke", "sessionx", _step_session_boot_smoke),
        ("08.repox.scan", "repox", _step_repox),
        ("09.auditx.scan", "auditx", _step_auditx),
        ("10.testx.run", "testx", _step_testx),
        ("11.performx.check", "performx", _step_performx),
        ("12.securex.check", "securex", _step_securex),
        ("13.packaging.verify", "packagingx", _step_packaging_verify),
    ]


def _normalize_status(token: str) -> str:
    value = str(token or "").strip().lower()
    if value in ("pass", "fail", "refusal", "error"):
        return value
    return "error"


def _exit_code(step_rows: List[Dict[str, object]]) -> int:
    statuses = [str(row.get("status", "")) for row in step_rows]
    if "error" in statuses:
        return 3
    if "refusal" in statuses:
        return 2
    if "fail" in statuses:
        return 1
    return 0


def _result_token(exit_code: int) -> str:
    if exit_code == 0:
        return "pass"
    if exit_code == 1:
        return "fail"
    if exit_code == 2:
        return "refusal"
    return "error"


def _summary_lines(report: Dict[str, object]) -> List[str]:
    lines = []
    lines.append(
        "[xstack] profile={} cache={} shard={}/{}".format(
            str(report.get("profile", "")),
            str(report.get("cache", "")),
            int((report.get("shard") or {}).get("index", 0)),
            int((report.get("shard") or {}).get("count", 1)),
        )
    )
    for row in report.get("steps") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            "[xstack] step={} subsystem={} status={} message={}".format(
                str(row.get("step_id", "")),
                str(row.get("subsystem", "")),
                str(row.get("status", "")),
                str(row.get("message", "")),
            )
        )
    lines.append(
        "[xstack] result={} exit_code={} report={}".format(
            str(report.get("result", "")),
            int(report.get("exit_code", 3)),
            str(report.get("report_path", "")),
        )
    )
    lines.append(
        "[xstack] lab_build_status={} composite_hash_anchor={}".format(
            str(report.get("lab_build_status", "")),
            str(report.get("composite_hash_anchor", "")),
        )
    )
    return lines


def _lab_summary_from_steps(step_rows: List[Dict[str, object]]) -> Dict[str, object]:
    for row in step_rows:
        if str(row.get("step_id", "")) != "13.packaging.verify":
            continue
        details = row.get("details")
        if not isinstance(details, dict):
            break
        return {
            "lab_build_status": str(details.get("lab_build_status", "unknown")),
            "composite_hash_anchor": str(details.get("composite_hash_anchor", "")),
            "pack_lock_hash": str(details.get("pack_lock_hash", "")),
            "registry_hashes": dict(details.get("registry_hashes") or {}),
        }
    return {
        "lab_build_status": "unknown",
        "composite_hash_anchor": "",
        "pack_lock_hash": "",
        "registry_hashes": {},
    }


def run_profile(context: RunContext) -> Dict[str, object]:
    ensure_dir(context.output_dir)
    steps_dir = os.path.join(context.output_dir, "steps")
    ensure_dir(steps_dir)

    step_rows: List[Dict[str, object]] = []
    for step_id, subsystem, fn in _step_definitions():
        started = time.perf_counter()
        try:
            raw = fn(context)
        except Exception as exc:
            raw = {
                "status": "error",
                "message": "internal tool crash: {}".format(str(exc)),
                "findings": [
                    {
                        "severity": "refusal",
                        "code": "refuse.controlx.step_crash",
                        "message": "{} crashed".format(step_id),
                    }
                ],
            }
        duration_ms = int((time.perf_counter() - started) * 1000.0)

        findings = _sort_findings(list(raw.get("findings") or []))
        status = _normalize_status(raw.get("status", _status_from_findings(findings)))
        message = str(raw.get("message", "")).strip() or "{} completed".format(step_id)

        findings_path = os.path.join(steps_dir, "{}.findings.json".format(step_id.replace(".", "_")))
        write_json(
            findings_path,
            {
                "step_id": step_id,
                "subsystem": subsystem,
                "findings": findings,
            },
        )
        artifacts: List[Dict[str, str]] = [_artifact_row(context.repo_root, findings_path)]

        details = raw.get("details")
        if isinstance(details, dict):
            details_path = os.path.join(steps_dir, "{}.details.json".format(step_id.replace(".", "_")))
            write_json(details_path, details)
            artifacts.append(_artifact_row(context.repo_root, details_path))

        for item in sorted(set(str(path) for path in (raw.get("artifacts") or []) if str(path).strip())):
            artifacts.append(_artifact_row(context.repo_root, item))

        step_row = {
            "step_id": step_id,
            "subsystem": subsystem,
            "status": status,
            "duration_ms": duration_ms,
            "message": message,
            "findings_count": len(findings),
            "artifacts": sorted(
                artifacts,
                key=lambda row: (str(row.get("path", "")), str(row.get("sha256", ""))),
            ),
        }
        if isinstance(details, dict):
            step_row["details"] = details
        step_rows.append(step_row)

    exit_code = _exit_code(step_rows)
    result_token = _result_token(exit_code)
    report_path = os.path.join(context.output_dir, "report.json")
    lab_summary = _lab_summary_from_steps(step_rows)
    report = {
        "schema_version": "1.0.0",
        "generated_utc": now_utc_iso(),
        "profile": str(context.profile).upper(),
        "result": result_token,
        "exit_code": exit_code,
        "cache": "on" if context.cache_enabled else "off",
        "shard": {
            "count": int(context.shards),
            "index": int(context.shard_index),
        },
        "step_count": len(step_rows),
        "steps": step_rows,
        "report_path": norm(os.path.relpath(report_path, context.repo_root)),
        "lab_build_status": str(lab_summary.get("lab_build_status", "unknown")),
        "composite_hash_anchor": str(lab_summary.get("composite_hash_anchor", "")),
        "pack_lock_hash": str(lab_summary.get("pack_lock_hash", "")),
        "registry_hashes": dict(lab_summary.get("registry_hashes") or {}),
    }
    write_json(report_path, report)
    summary_path = os.path.join(context.output_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as handle:
        for line in _summary_lines(report):
            handle.write(line + "\n")

    report["summary_path"] = norm(os.path.relpath(summary_path, context.repo_root))
    report["summary_lines"] = _summary_lines(report)
    return report
