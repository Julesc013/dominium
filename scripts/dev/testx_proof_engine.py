#!/usr/bin/env python3
"""Structured TestX suite runner with manifest-driven selection."""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

from env_tools_lib import canonical_workspace_id, canonicalize_env_for_workspace


DEFAULT_REGISTRY_REL = os.path.join("data", "registries", "testx_suites.json")
DEFAULT_MANIFEST_REL = os.path.join("docs", "audit", "proof_manifest.json")
DEFAULT_SUMMARY_JSON_REL = os.path.join("docs", "audit", "testx", "TESTX_SUMMARY.json")
DEFAULT_SUMMARY_MD_REL = os.path.join("docs", "audit", "testx", "TESTX_SUMMARY.md")
DEFAULT_RUN_META_REL = os.path.join("docs", "audit", "testx", "TESTX_RUN_META.json")


def _norm(path):
    return os.path.normpath(path)


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def _write_json(path, payload):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_markdown(path, suite_id, summary):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("Status: DERIVED\n")
        handle.write("Last Reviewed: {}\n".format(datetime.utcnow().strftime("%Y-%m-%d")))
        handle.write("Supersedes: none\n")
        handle.write("Superseded By: none\n\n")
        handle.write("# TestX Suite Summary\n\n")
        handle.write("- suite_id: `{}`\n".format(suite_id))
        handle.write("- result: `{}`\n".format("pass" if summary.get("returncode", 1) == 0 else "fail"))
        handle.write("- selected_tests: `{}`\n".format(summary.get("selected_test_count", 0)))
        tags = ", ".join(summary.get("required_test_tags", []))
        handle.write("- required_test_tags: `{}`\n".format(tags))
        if summary.get("warnings"):
            handle.write("- warnings:\n")
            for item in summary.get("warnings", []):
                handle.write("  - `{}`\n".format(item))


def load_suite_registry(repo_root, registry_rel=DEFAULT_REGISTRY_REL):
    path = _norm(os.path.join(repo_root, registry_rel))
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return None, "refuse.invalid_suite_registry"
    record = payload.get("record")
    if not isinstance(record, dict):
        return None, "refuse.invalid_suite_registry_record"
    suites = record.get("suites")
    if not isinstance(suites, list):
        return None, "refuse.invalid_suite_registry_suites"
    index = {}
    for entry in suites:
        if not isinstance(entry, dict):
            continue
        suite_id = str(entry.get("suite_id", "")).strip()
        if not suite_id:
            continue
        index[suite_id] = entry
    if not index:
        return None, "refuse.empty_suite_registry"
    return {
        "path": path,
        "schema_id": str(payload.get("schema_id", "")).strip(),
        "record": record,
        "index": index,
    }, ""


def load_proof_manifest(repo_root, manifest_rel=DEFAULT_MANIFEST_REL):
    path = _norm(os.path.join(repo_root, manifest_rel))
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return None
    return payload


def _normalized_tags(raw_values):
    out = set()
    if not isinstance(raw_values, list):
        return out
    for item in raw_values:
        token = str(item).strip()
        if token:
            out.add(token)
    return out


def _unique_sorted(values):
    return sorted(set(values))


def select_tests_for_suite(suite_id, suite_record, manifest_payload):
    extensions = suite_record.get("extensions") or {}
    tests_by_tag = extensions.get("tests_by_tag") if isinstance(extensions.get("tests_by_tag"), dict) else {}
    default_tests = extensions.get("default_tests") if isinstance(extensions.get("default_tests"), list) else []
    required_tests = extensions.get("required_tests") if isinstance(extensions.get("required_tests"), list) else []

    suite_tags = _normalized_tags(suite_record.get("test_tags"))
    manifest_tags = set()
    manifest_used = False
    if isinstance(manifest_payload, dict):
        manifest_tags = _normalized_tags(manifest_payload.get("required_test_tags"))
        manifest_used = bool(manifest_tags)

    active_tags = set(suite_tags)
    if suite_id == "testx_fast" and manifest_tags:
        active_tags = set(manifest_tags)
    elif manifest_tags:
        active_tags.update(manifest_tags)

    selected = set(str(item).strip() for item in default_tests if str(item).strip())
    selected.update(str(item).strip() for item in required_tests if str(item).strip())

    for tag in sorted(active_tags):
        values = tests_by_tag.get(tag)
        if not isinstance(values, list):
            continue
        selected.update(str(item).strip() for item in values if str(item).strip())

    selected_tests = _unique_sorted([item for item in selected if item])
    return {
        "manifest_used": manifest_used,
        "required_test_tags": _unique_sorted(active_tags),
        "selected_tests": selected_tests,
        "required_tests": _unique_sorted(required_tests),
        "run_all_tests": bool(extensions.get("run_all_tests", False)),
    }


def _run_command(command, repo_root, env):
    return subprocess.run(
        command,
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def _list_ctest_tests(build_dir, config, repo_root, env):
    cmd = ["ctest", "-N", "--test-dir", build_dir]
    if config:
        cmd.extend(["-C", config])
    result = _run_command(cmd, repo_root, env)
    if result.returncode != 0:
        return [], result
    names = []
    pattern = re.compile(r"^\s*Test\s+#\d+:\s+(.+?)\s*$")
    for line in (result.stdout or "").splitlines():
        match = pattern.match(line)
        if match:
            names.append(match.group(1).strip())
    return _unique_sorted(names), result


def _ctest_regex_for_tests(names):
    escaped = [r"({})".format(re.escape(name)) for name in names]
    return r"^({})$".format("|".join(escaped))


def _ensure_required_tests_exist(required, all_tests):
    all_set = set(all_tests)
    missing = [name for name in required if name not in all_set]
    return _unique_sorted(missing)


def run_suite(repo_root, suite_id, suite, build_dir, config, selection, env):
    all_tests, list_result = _list_ctest_tests(build_dir, config, repo_root, env)
    if list_result.returncode != 0:
        return {
            "returncode": int(list_result.returncode),
            "output": list_result.stdout or "",
            "all_tests": [],
            "executed_command": list_result.args if isinstance(list_result.args, list) else [],
            "missing_required_tests": selection.get("required_tests", []),
        }

    missing_required = _ensure_required_tests_exist(selection.get("required_tests", []), all_tests)
    if missing_required:
        return {
            "returncode": 2,
            "output": "refuse.required_tests_missing: {}".format(",".join(missing_required)),
            "all_tests": all_tests,
            "executed_command": [],
            "missing_required_tests": missing_required,
        }

    run_all = selection.get("run_all_tests", False)
    selected_tests = selection.get("selected_tests", [])
    if not run_all and not selected_tests:
        run_all = True

    command = ["ctest", "--output-on-failure", "--test-dir", build_dir]
    if config:
        command.extend(["-C", config])
    if not run_all:
        command.extend(["-R", _ctest_regex_for_tests(selected_tests)])
    result = _run_command(command, repo_root, env)

    executed = all_tests if run_all else [name for name in selected_tests if name in set(all_tests)]
    return {
        "returncode": int(result.returncode),
        "output": result.stdout or "",
        "all_tests": all_tests,
        "executed_tests": _unique_sorted(executed),
        "executed_command": command,
        "missing_required_tests": missing_required,
    }


def _resolve_repo_root(value):
    if value:
        return _norm(os.path.abspath(value))
    return _norm(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _summary_paths(repo_root, summary_json_rel, summary_md_rel, run_meta_rel):
    return (
        _norm(os.path.join(repo_root, summary_json_rel)),
        _norm(os.path.join(repo_root, summary_md_rel)),
        _norm(os.path.join(repo_root, run_meta_rel)),
    )


def _canonical_summary_payload(registry, suite_id, selection, run_result):
    warnings = []
    if run_result.get("missing_required_tests"):
        warnings.append("required_tests_missing")

    return {
        "artifact_class": "CANONICAL",
        "registry_id": str(registry["record"].get("registry_id", "")).strip(),
        "registry_version": str(registry["record"].get("registry_version", "")).strip(),
        "returncode": int(run_result.get("returncode", 1)),
        "selected_test_count": len(selection.get("selected_tests", [])),
        "selected_tests": _unique_sorted(selection.get("selected_tests", [])),
        "suite_id": suite_id,
        "suite_passed": bool(int(run_result.get("returncode", 1)) == 0),
        "warnings": _unique_sorted(warnings),
        "required_test_tags": _unique_sorted(selection.get("required_test_tags", [])),
        "executed_tests": _unique_sorted(run_result.get("executed_tests", [])),
    }


def _run_meta_payload(suite_id, duration_ms, run_result):
    return {
        "artifact_class": "RUN_META",
        "duration_ms": int(duration_ms),
        "generated_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "returncode": int(run_result.get("returncode", 1)),
        "status": "DERIVED",
        "suite_id": suite_id,
    }


def main():
    parser = argparse.ArgumentParser(description="Manifest-aware TestX suite runner.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--suite", required=True)
    parser.add_argument("--build-dir", default="")
    parser.add_argument("--config", default="Debug")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_REL)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST_REL)
    parser.add_argument("--summary-json", default=DEFAULT_SUMMARY_JSON_REL)
    parser.add_argument("--summary-md", default=DEFAULT_SUMMARY_MD_REL)
    parser.add_argument("--run-meta-json", default=DEFAULT_RUN_META_REL)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = _resolve_repo_root(args.repo_root)
    ws_id = os.environ.get("DOM_WS_ID", "") or canonical_workspace_id(repo_root, env=os.environ)
    env, ws_dirs = canonicalize_env_for_workspace(dict(os.environ), repo_root, ws_id=ws_id)

    registry, refusal = load_suite_registry(repo_root, registry_rel=args.registry)
    if registry is None:
        print(json.dumps({"result": "refused", "refusal_code": refusal}, indent=2, sort_keys=True))
        return 2

    suite = registry["index"].get(args.suite)
    if suite is None:
        print(json.dumps({"result": "refused", "refusal_code": "refuse.unknown_suite"}, indent=2, sort_keys=True))
        return 2

    manifest = load_proof_manifest(repo_root, manifest_rel=args.manifest)
    selection = select_tests_for_suite(args.suite, suite, manifest)

    build_dir = args.build_dir.strip()
    if not build_dir:
        build_dir = ws_dirs.get("build_verify", os.path.join(repo_root, "out", "build", "vs2026", "verify"))
    if not os.path.isabs(build_dir):
        build_dir = _norm(os.path.join(repo_root, build_dir))

    start = time.time()
    if args.dry_run:
        run_result = {
            "returncode": 0,
            "executed_tests": selection.get("selected_tests", []),
            "missing_required_tests": [],
        }
    else:
        run_result = run_suite(repo_root, args.suite, suite, build_dir, args.config, selection, env)
    duration_ms = int((time.time() - start) * 1000.0)

    summary_payload = _canonical_summary_payload(registry, args.suite, selection, run_result)
    summary_json_path, summary_md_path, run_meta_path = _summary_paths(
        repo_root,
        args.summary_json,
        args.summary_md,
        args.run_meta_json,
    )
    _write_json(summary_json_path, summary_payload)
    _write_markdown(summary_md_path, args.suite, summary_payload)
    _write_json(run_meta_path, _run_meta_payload(args.suite, duration_ms, run_result))

    print(
        json.dumps(
            {
                "result": "suite_complete",
                "suite_id": args.suite,
                "returncode": int(run_result.get("returncode", 1)),
                "selected_tests": summary_payload.get("selected_tests", []),
                "required_test_tags": summary_payload.get("required_test_tags", []),
                "summary_json": os.path.relpath(summary_json_path, repo_root).replace("\\", "/"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return int(run_result.get("returncode", 1))


if __name__ == "__main__":
    raise SystemExit(main())
