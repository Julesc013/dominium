"""Deterministic XI-4 convergence execution helpers."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


CONVERGENCE_PLAN_REL = "data/refactor/convergence_plan.json"
CONVERGENCE_ACTIONS_REL = "data/refactor/convergence_actions.json"
CONVERGENCE_RISK_MAP_REL = "data/refactor/convergence_risk_map.json"
ARCHITECTURE_GRAPH_REL = "data/architecture/architecture_graph.json"
BUILD_GRAPH_REL = "data/audit/build_graph.json"

CONVERGENCE_EXECUTION_LOG_REL = "data/refactor/convergence_execution_log.json"
CONVERGENCE_EXECUTION_LOG_DOC_REL = "docs/refactor/CONVERGENCE_EXECUTION_LOG.md"
DEPRECATIONS_REL = "docs/refactor/DEPRECATIONS.md"
XI_4_FINAL_REL = "docs/audit/XI_4_FINAL.md"
QUARANTINE_DOC_DIR_REL = "docs/refactor"
QUARANTINE_DOC_PREFIX = "QUARANTINE_"

OUTPUT_REL_PATHS = {
    CONVERGENCE_EXECUTION_LOG_REL,
    CONVERGENCE_EXECUTION_LOG_DOC_REL,
    DEPRECATIONS_REL,
    XI_4_FINAL_REL,
}

REQUIRED_INPUTS = {
    "architecture_graph": ARCHITECTURE_GRAPH_REL,
    "build_graph": BUILD_GRAPH_REL,
    "convergence_actions": CONVERGENCE_ACTIONS_REL,
    "convergence_plan": CONVERGENCE_PLAN_REL,
    "convergence_risk_map": CONVERGENCE_RISK_MAP_REL,
}

DOC_REPORT_DATE = "2026-03-26"
SOURCE_LIKE_DIRS = {"Source", "Sources", "source", "src"}
TEST_PATH_PREFIXES = ("Testing/", "game/tests/", "tests/", "tools/xstack/testx/tests/")
AUTO_QUARANTINE_SYMBOLS = {"main", "sizeof", "stat", "winmain", "wwinmain"}
ACTION_KIND_ORDER = {"keep": 0, "merge": 1, "rewire": 2, "deprecate": 3, "quarantine": 4}
RISK_ORDER = {"HIGH": 0, "MED": 1, "LOW": 2}
CLUSTER_LIST_LIMIT = 20
DEPRECATION_LIST_LIMIT = 20
QUARANTINE_REASON_LIMIT = 8
EXECUTION_MODE = "conservative_preflight"

GATE_ROWS = (
    {
        "gate_id": "build_strict",
        "command": "cmake --build --preset verify --config Debug --target domino_engine dominium_game dominium_client",
        "phase": "phase_1_safe_merges",
        "status": "pass",
    },
    {
        "gate_id": "testx_targeted",
        "command": "python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable,test_deprecated_files_not_in_default_build,test_canonical_paths_used_for_core_concepts_smoke,test_convergence_execution_log_deterministic",
        "phase": "phase_1_safe_merges",
        "status": "pass",
    },
    {
        "gate_id": "validate_fast",
        "command": "python tools/validation/tool_run_validation.py --repo-root . --profile FAST",
        "phase": "phase_1_safe_merges",
        "status": "fail",
        "note": "repo-global validation failure: dist smoke client_descriptor returned non-zero inside ARCH-AUDIT disaster scan",
    },
    {
        "gate_id": "validate_strict",
        "command": "python tools/validation/tool_run_validation.py --repo-root . --profile STRICT",
        "phase": "phase_2_medium_risk_merges",
        "status": "fail",
        "note": "repo-global validation failure: ARCH-AUDIT disaster worktree cleanup under build/tmp/omega4_disaster_arch_audit failed",
    },
    {
        "gate_id": "omega_1_worldgen_lock",
        "command": "python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .",
        "phase": "phase_2_medium_risk_merges",
        "status": "pass",
    },
    {
        "gate_id": "omega_2_baseline_universe",
        "command": "python tools/mvp/tool_verify_baseline_universe.py --repo-root .",
        "phase": "phase_2_medium_risk_merges",
        "status": "pass",
    },
    {
        "gate_id": "omega_3_gameplay_loop",
        "command": "python tools/mvp/tool_verify_gameplay_loop.py --repo-root .",
        "phase": "phase_2_medium_risk_merges",
        "status": "pass",
    },
    {
        "gate_id": "omega_4_disaster_suite",
        "command": "python tools/mvp/tool_run_disaster_suite.py --repo-root .",
        "phase": "phase_2_medium_risk_merges",
        "status": "pass",
    },
)
EXECUTED_GATE_IDS = [str(row["gate_id"]) for row in GATE_ROWS]


class XiInputMissingError(RuntimeError):
    """Raised when the required XI inputs are missing."""

    def __init__(self, missing_paths: Sequence[str]):
        super().__init__("missing XI inputs")
        self.missing_paths = sorted({_norm_rel(path) for path in missing_paths if _token(path)})
        self.refusal_code = "refusal.xi.missing_inputs"
        self.remediation = "Run Ξ-0 through Ξ-3 first."


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, _norm_rel(rel_path).replace("/", os.sep))))


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _write_canonical_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload)))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = os.path.normpath(os.path.abspath(path))
    _ensure_parent(target)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _required_inputs(repo_root: str) -> dict[str, dict]:
    root = _repo_root(repo_root)
    missing = []
    payloads: dict[str, dict] = {}
    for key, rel_path in sorted(REQUIRED_INPUTS.items()):
        abs_path = _repo_abs(root, rel_path)
        if not os.path.isfile(abs_path):
            missing.append(rel_path)
            continue
        payload = _read_json(abs_path)
        if not payload:
            missing.append(rel_path)
            continue
        payloads[key] = payload
    if missing:
        raise XiInputMissingError(missing)
    return payloads


def _simple_symbol_name(symbol_name: object) -> str:
    token = _token(symbol_name)
    if not token:
        return ""
    token = token.split("::")[-1]
    token = token.split(".")[-1]
    return token


def _tests_only_path(path: object) -> bool:
    norm = _norm_rel(path)
    return any(norm.startswith(prefix) for prefix in TEST_PATH_PREFIXES)


def _source_like_path(path: object) -> bool:
    parts = [part for part in _norm_rel(path).split("/") if part]
    return any(part in SOURCE_LIKE_DIRS for part in parts)


def _quarantine_doc_name(cluster_id: object) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", _token(cluster_id))
    return "{}{}.md".format(QUARANTINE_DOC_PREFIX, safe or "unknown")


def _candidate_rows(cluster: Mapping[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    canonical = dict(cluster.get("canonical_candidate") or {})
    if canonical:
        canonical["disposition"] = "canonical"
        rows.append(canonical)
    for row in cluster.get("secondary_candidates") or []:
        if isinstance(row, dict):
            rows.append(dict(row))
    return rows


def _gate_result_for_ids(gate_ids: Sequence[str]) -> str:
    status_by_id = {str(row.get("gate_id", "")): str(row.get("status", "")).strip().lower() for row in GATE_ROWS}
    for gate_id in gate_ids:
        if status_by_id.get(str(gate_id), "pass") != "pass":
            return "fail"
    return "pass"


def _build_indexes(payloads: Mapping[str, dict]) -> dict[str, object]:
    actions = [dict(row) for row in list(dict(payloads.get("convergence_actions") or {}).get("actions") or []) if isinstance(row, dict)]
    clusters = [dict(row) for row in list(dict(payloads.get("convergence_plan") or {}).get("clusters") or []) if isinstance(row, dict)]
    build_targets = [dict(row) for row in list(dict(payloads.get("build_graph") or {}).get("targets") or []) if isinstance(row, dict)]
    architecture_modules = [dict(row) for row in list(dict(payloads.get("architecture_graph") or {}).get("modules") or []) if isinstance(row, dict)]

    cluster_by_id: dict[str, dict[str, object]] = {}
    for row in sorted(clusters, key=lambda item: (_token(item.get("cluster_id")), _token(item.get("symbol_name")))):
        cluster_id = _token(row.get("cluster_id"))
        if cluster_id:
            cluster_by_id[cluster_id] = row

    file_to_targets: defaultdict[str, set[str]] = defaultdict(set)
    file_to_products: defaultdict[str, set[str]] = defaultdict(set)
    for row in build_targets:
        target_id = _token(row.get("target_id"))
        product_id = _token(row.get("product_id"))
        for source in row.get("sources") or []:
            file_path = _norm_rel(source)
            if not file_path:
                continue
            if target_id:
                file_to_targets[file_path].add(target_id)
            if product_id:
                file_to_products[file_path].add(product_id)

    module_roots: dict[str, str] = {}
    for row in architecture_modules:
        module_id = _token(row.get("module_id"))
        module_root = _norm_rel(row.get("module_root"))
        if module_id and module_root:
            module_roots[module_id] = module_root

    return {
        "actions": sorted(
            actions,
            key=lambda item: (
                _token(item.get("action_id")),
                _token(item.get("cluster_id")),
                ACTION_KIND_ORDER.get(_token(item.get("kind")), 99),
                _norm_rel(item.get("secondary_file")),
            ),
        ),
        "cluster_by_id": cluster_by_id,
        "file_to_products": {key: sorted(values) for key, values in sorted(file_to_products.items())},
        "file_to_targets": {key: sorted(values) for key, values in sorted(file_to_targets.items())},
        "module_roots": module_roots,
    }


def _quarantine_reasons_for_action(action: Mapping[str, object], cluster: Mapping[str, object], indexes: Mapping[str, object]) -> list[str]:
    reasons: set[str] = set()
    symbol_name = _simple_symbol_name(action.get("symbol_name")).lower()
    canonical_file = _norm_rel(action.get("canonical_file"))
    secondary_file = _norm_rel(action.get("secondary_file"))
    file_to_targets = dict(indexes.get("file_to_targets") or {})
    canonical_targets = set(file_to_targets.get(canonical_file, []))
    secondary_targets = set(file_to_targets.get(secondary_file, []))

    if symbol_name in AUTO_QUARANTINE_SYMBOLS:
        reasons.add("builtin_or_entrypoint_collision")
    if symbol_name.endswith("main"):
        reasons.add("entrypoint_surface")
    if secondary_targets:
        reasons.add("secondary_file_active_in_default_build")
    if len(canonical_targets | secondary_targets) > 1:
        reasons.add("cross_product_surface")
    if bool(_tests_only_path(canonical_file)) != bool(_tests_only_path(secondary_file)):
        reasons.add("test_runtime_split")
    if canonical_file.startswith("tools/") != secondary_file.startswith("tools/"):
        reasons.add("cross_domain_helper_collision")
    if _source_like_path(canonical_file) or _source_like_path(secondary_file):
        reasons.add("source_like_surface")
    if os.path.splitext(canonical_file)[1].lower() != os.path.splitext(secondary_file)[1].lower():
        reasons.add("cross_language_surface")
    if canonical_file and secondary_file and canonical_file.rsplit("/", 1)[0] != secondary_file.rsplit("/", 1)[0]:
        reasons.add("file_scope_ambiguity")
    if _token(cluster.get("cluster_kind")).lower() == "near":
        reasons.add("near_duplicate_requires_review")
    if not reasons:
        reasons.add("no_safe_file_local_transform")
    return sorted(reasons)


def _entry_payload(action: Mapping[str, object], result: str, reason_tokens: Sequence[object], gate_ids: Sequence[str]) -> dict[str, object]:
    payload = {
        "action_id": _token(action.get("action_id")),
        "canonical_file": _norm_rel(action.get("canonical_file")),
        "cluster_id": _token(action.get("cluster_id")),
        "commits": [],
        "deterministic_fingerprint": "",
        "gates_run": [str(item) for item in gate_ids if _token(item)],
        "kind": _token(action.get("kind")),
        "risk_level": _token(action.get("risk_level")),
        "risk_reasons": sorted({_token(item) for item in action.get("risk_reasons") or [] if _token(item)}),
        "result": result,
        "result_reasons": sorted({_token(item) for item in reason_tokens if _token(item)}),
        "secondary_file": _norm_rel(action.get("secondary_file")),
        "symbol_name": _token(action.get("symbol_name")),
    }
    payload["gate_results"] = _gate_result_for_ids(payload["gates_run"])
    payload["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in payload.items() if key != "deterministic_fingerprint"})
    return payload


def _execution_entry(action: Mapping[str, object], cluster: Mapping[str, object], indexes: Mapping[str, object]) -> dict[str, object]:
    kind = _token(action.get("kind"))
    risk_level = _token(action.get("risk_level"))
    if kind == "keep":
        return _entry_payload(action, "applied", ["canonical_selection_recorded"], EXECUTED_GATE_IDS)
    if kind == "quarantine":
        return _entry_payload(action, "quarantined", ["planned_quarantine"], EXECUTED_GATE_IDS)
    if risk_level in {"MED", "HIGH"}:
        reasons = ["phase_boundary_deferred"]
        if risk_level == "MED":
            reasons.append("requires_medium_risk_batch_gate")
        else:
            reasons.append("requires_single_action_full_gate")
        return _entry_payload(action, "skipped", reasons, [])
    return _entry_payload(action, "quarantined", _quarantine_reasons_for_action(action, cluster, indexes), EXECUTED_GATE_IDS)


def _result_counts(entries: Sequence[Mapping[str, object]]) -> dict[str, int]:
    counter = Counter(_token(item.get("result")) for item in entries)
    return {key: int(counter.get(key, 0)) for key in ("applied", "quarantined", "skipped")}


def _nested_counts(entries: Sequence[Mapping[str, object]], outer_key: str) -> list[dict[str, object]]:
    grouped: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for row in entries:
        grouped[_token(row.get(outer_key))][_token(row.get("result"))] += 1
    out: list[dict[str, object]] = []
    for key in sorted(grouped, key=lambda item: (RISK_ORDER.get(item, 99), item)):
        counter = grouped[key]
        out.append(
            {
                outer_key: key,
                "applied": int(counter.get("applied", 0)),
                "quarantined": int(counter.get("quarantined", 0)),
                "skipped": int(counter.get("skipped", 0)),
            }
        )
    return out


def _cluster_sets(entries: Sequence[Mapping[str, object]]) -> dict[str, list[str]]:
    buckets: defaultdict[str, set[str]] = defaultdict(set)
    for row in entries:
        cluster_id = _token(row.get("cluster_id"))
        result = _token(row.get("result"))
        if cluster_id and result:
            buckets[result].add(cluster_id)
    return {key: sorted(values) for key, values in sorted(buckets.items())}


def _deprecation_rows(entries: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in entries:
        if _token(row.get("kind")) != "deprecate" or _token(row.get("result")) != "applied":
            continue
        rows.append(
            {
                "cluster_id": _token(row.get("cluster_id")),
                "canonical_file": _norm_rel(row.get("canonical_file")),
                "secondary_file": _norm_rel(row.get("secondary_file")),
                "symbol_name": _token(row.get("symbol_name")),
            }
        )
    return sorted(rows, key=lambda item: (item["secondary_file"], item["canonical_file"], item["cluster_id"]))


def _quarantine_packet(cluster: Mapping[str, object], cluster_actions: Sequence[Mapping[str, object]]) -> str:
    cluster_id = _token(cluster.get("cluster_id"))
    symbol_name = _token(cluster.get("symbol_name"))
    canonical = dict(cluster.get("canonical_candidate") or {})
    candidate_rows = _candidate_rows(cluster)
    competing_files = sorted({_norm_rel(row.get("file_path")) for row in candidate_rows if _norm_rel(row.get("file_path"))})
    tests = sorted({_token(cmd) for row in cluster_actions for cmd in (dict(row).get("required_tests") or []) if _token(cmd)})
    action_kinds = sorted(
        {_token(row.get("kind")) for row in cluster_actions if _token(row.get("kind")) and _token(row.get("kind")) != "keep"},
        key=lambda item: ACTION_KIND_ORDER.get(item, 99),
    )
    quarantine_reasons = sorted(
        {
            _token(reason)
            for row in cluster_actions
            for reason in (dict(row).get("result_reasons") or [])
            if _token(reason) and _token(reason) != "canonical_selection_recorded"
        }
    )

    lines = [
        "Status: Quarantine",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Stability: provisional",
        "Replacement Target: XI-4b manual review resolution",
        "",
        "# Quarantine Packet `{}`".format(cluster_id),
        "",
        "- Symbol: `{}`".format(symbol_name or "unknown"),
        "- Cluster Kind: `{}`".format(_token(cluster.get("cluster_kind")) or "unknown"),
        "- Cluster Resolution: `{}`".format(_token(cluster.get("cluster_resolution")) or "unknown"),
        "- Risk Level: `{}`".format(_token(cluster.get("risk_level")) or "unknown"),
        "- Canonical Candidate: `{}`".format(_norm_rel(canonical.get("file_path")) or "unknown"),
        "- Quarantine Reasons: `{}`".format(", ".join(quarantine_reasons[:QUARANTINE_REASON_LIMIT]) or "planned_quarantine"),
        "- Planned Action Kinds: `{}`".format(", ".join(action_kinds) or "quarantine"),
        "",
        "## Competing Files",
        "",
    ]
    for path in competing_files:
        lines.append("- `{}`".format(path))
    if not competing_files:
        lines.append("- none recorded")
    lines.extend(["", "## Scorecard", ""])
    for row in candidate_rows:
        lines.append(
            "- `{}` disposition=`{}` rank=`{}` total_score=`{}` risk=`{}`".format(
                _norm_rel(row.get("file_path")) or "unknown",
                _token(row.get("disposition")) or ("canonical" if _norm_rel(row.get("file_path")) == _norm_rel(canonical.get("file_path")) else "candidate"),
                int(row.get("candidate_rank", 0) or 0),
                round(float(row.get("total_score", 0.0) or 0.0), 2),
                _token(row.get("risk_level")) or _token(cluster.get("risk_level")) or "unknown",
            )
        )
    lines.extend(["", "## Usage Sites", ""])
    lines.append("- Build Targets: `{}`".format(", ".join(sorted({_token(item) for item in canonical.get("build_targets_using_file") or [] if _token(item)})) or "none"))
    lines.append("- Docs: `{}`".format(", ".join(sorted({_norm_rel(item) for item in canonical.get("docs_referencing_symbol") or [] if _token(item)})) or "none"))
    lines.extend(["", "## Tests Involved", ""])
    for command in tests:
        lines.append("- `{}`".format(command))
    if not tests:
        lines.append("- none recorded")
    lines.extend(["", "## Recommended Decision Options", ""])
    if "merge" in action_kinds:
        lines.append("- Review file-local deltas and port only unique behavior into the canonical file.")
    if "rewire" in action_kinds:
        lines.append("- Rewire call sites only after confirming the secondary file is not an active product entrypoint.")
    if "deprecate" in action_kinds:
        lines.append("- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.")
    lines.append("- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.")
    lines.append("")
    return "\n".join(lines)


def _build_snapshot(repo_root: str) -> dict[str, object]:
    payloads = _required_inputs(repo_root)
    indexes = _build_indexes(payloads)
    cluster_by_id = dict(indexes.get("cluster_by_id") or {})

    entries: list[dict[str, object]] = []
    cluster_actions: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for action in list(indexes.get("actions") or []):
        cluster_id = _token(action.get("cluster_id"))
        cluster = dict(cluster_by_id.get(cluster_id) or {})
        entry = _execution_entry(action, cluster, indexes)
        entries.append(entry)
        action_with_result = dict(action)
        action_with_result["result_reasons"] = list(entry.get("result_reasons") or [])
        cluster_actions[cluster_id].append(action_with_result)

    entries = sorted(
        entries,
        key=lambda row: (
            _token(row.get("action_id")),
            _token(row.get("cluster_id")),
            ACTION_KIND_ORDER.get(_token(row.get("kind")), 99),
            _norm_rel(row.get("secondary_file")),
        ),
    )
    cluster_sets = _cluster_sets(entries)
    deprecations = _deprecation_rows(entries)
    quarantine_cluster_ids = sorted(
        {
            _token(row.get("cluster_id"))
            for row in entries
            if _token(row.get("result")) == "quarantined" and _token(row.get("cluster_id"))
        }
    )
    quarantine_docs: dict[str, str] = {}
    for cluster_id in quarantine_cluster_ids:
        cluster = dict(cluster_by_id.get(cluster_id) or {"cluster_id": cluster_id})
        quarantine_docs[_norm_rel(os.path.join(QUARANTINE_DOC_DIR_REL, _quarantine_doc_name(cluster_id)))] = _quarantine_packet(
            cluster,
            cluster_actions.get(cluster_id, []),
        )

    execution_log = {
        "doc_date": DOC_REPORT_DATE,
        "execution_mode": EXECUTION_MODE,
        "gate_runs": [dict(row) for row in GATE_ROWS],
        "kind_result_counts": _nested_counts(entries, "kind"),
        "quarantined_cluster_count": int(len(quarantine_cluster_ids)),
        "report_id": "xi4.convergence_execution_log",
        "result_counts": _result_counts(entries),
        "risk_result_counts": _nested_counts(entries, "risk_level"),
        "entries": entries,
        "cluster_sets": cluster_sets,
        "deprecations": deprecations,
    }
    execution_log["entry_count"] = int(len(entries))
    execution_log["deterministic_fingerprint"] = canonical_sha256({key: value for key, value in execution_log.items() if key != "deterministic_fingerprint"})

    return {
        "convergence_execution_log": execution_log,
        "quarantine_docs": quarantine_docs,
    }


def render_convergence_execution_log(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("convergence_execution_log") or {})
    result_counts = dict(payload.get("result_counts") or {})
    cluster_sets = dict(payload.get("cluster_sets") or {})
    deprecations = list(payload.get("deprecations") or [])
    gate_rows = list(payload.get("gate_runs") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-4b bounded follow-up and XI-5 src removal execution",
        "",
        "# XI-4 Convergence Execution Log",
        "",
        "- Execution Mode: `{}`".format(_token(payload.get("execution_mode")) or EXECUTION_MODE),
        "- Execution Boundary: `record canonical selections, quarantine ambiguous clusters, defer code-changing merge/rewire work outside the bounded XI-4 slice`",
        "- Entry Count: `{}`".format(int(payload.get("entry_count", 0) or 0)),
        "- Applied Records: `{}`".format(int(result_counts.get("applied", 0) or 0)),
        "- Quarantined: `{}`".format(int(result_counts.get("quarantined", 0) or 0)),
        "- Skipped: `{}`".format(int(result_counts.get("skipped", 0) or 0)),
        "- Quarantined Clusters: `{}`".format(int(payload.get("quarantined_cluster_count", 0) or 0)),
        "- Deprecated Files Applied: `{}`".format(len(deprecations)),
        "",
        "## Gate Summary",
        "",
    ]
    for row in gate_rows:
        note = _token(row.get("note"))
        line = "- `{}` `{}` -> `{}`".format(_token(row.get("gate_id")), _token(row.get("command")), _token(row.get("status")) or "unknown")
        if note:
            line += " note=`{}`".format(note)
        lines.append(line)
    lines.extend(["", "## Applied Canonical Selections", ""])
    for cluster_id in list(cluster_sets.get("applied") or [])[:CLUSTER_LIST_LIMIT]:
        lines.append("- `{}`".format(cluster_id))
    if not list(cluster_sets.get("applied") or []):
        lines.append("- none")
    lines.extend(["", "## Quarantined Clusters", ""])
    for cluster_id in list(cluster_sets.get("quarantined") or [])[:CLUSTER_LIST_LIMIT]:
        lines.append("- `{}`".format(cluster_id))
    if len(list(cluster_sets.get("quarantined") or [])) > CLUSTER_LIST_LIMIT:
        lines.append("- ... see `docs/refactor/QUARANTINE_*.md` for the full packet set")
    if not list(cluster_sets.get("quarantined") or []):
        lines.append("- none")
    lines.extend(["", "## Deferred Clusters", ""])
    for cluster_id in list(cluster_sets.get("skipped") or [])[:CLUSTER_LIST_LIMIT]:
        lines.append("- `{}`".format(cluster_id))
    if len(list(cluster_sets.get("skipped") or [])) > CLUSTER_LIST_LIMIT:
        lines.append("- ... see `data/refactor/convergence_execution_log.json` for the full deferred set")
    if not list(cluster_sets.get("skipped") or []):
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_deprecations(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("convergence_execution_log") or {})
    deprecations = list(payload.get("deprecations") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Stability: provisional",
        "Future Series: XI-5 or later",
        "Replacement Target: final deprecation registry once convergence is complete",
        "",
        "# XI-4 Deprecations",
        "",
    ]
    if not deprecations:
        lines.extend(
            [
                "No file-level deprecations were applied in this XI-4 pass.",
                "",
                "Ambiguous merge/rewire/deprecate actions were quarantined or deferred instead of marking live files deprecated without proof.",
                "",
            ]
        )
        return "\n".join(lines)
    lines.append("Applied deprecations:")
    lines.append("")
    for row in deprecations[:DEPRECATION_LIST_LIMIT]:
        lines.append(
            "- `{}` -> `{}` symbol=`{}`".format(
                _norm_rel(row.get("secondary_file")),
                _norm_rel(row.get("canonical_file")),
                _token(row.get("symbol_name")) or "unknown",
            )
        )
    if len(deprecations) > DEPRECATION_LIST_LIMIT:
        lines.append("- ... see `data/refactor/convergence_execution_log.json` for the complete set")
    lines.append("")
    return "\n".join(lines)


def render_xi_4_final(snapshot: Mapping[str, object]) -> str:
    payload = dict(snapshot.get("convergence_execution_log") or {})
    result_counts = dict(payload.get("result_counts") or {})
    cluster_sets = dict(payload.get("cluster_sets") or {})
    gate_rows = list(payload.get("gate_runs") or [])
    deprecations = list(payload.get("deprecations") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(DOC_REPORT_DATE),
        "Stability: provisional",
        "Future Series: XI-5",
        "Replacement Target: XI-4b bounded execution follow-up",
        "",
        "# XI-4 Final Report",
        "",
        "## Outcome",
        "",
        "- Execution Mode: `{}`".format(_token(payload.get("execution_mode")) or EXECUTION_MODE),
        "- Execution Boundary: `record canonical selections, quarantine ambiguous clusters, defer bulk code-changing merge/rewire work until bounded XI-4 follow-up slices`",
        "- Applied Records: `{}`".format(int(result_counts.get("applied", 0) or 0)),
        "- Quarantined Actions: `{}`".format(int(result_counts.get("quarantined", 0) or 0)),
        "- Deferred Actions: `{}`".format(int(result_counts.get("skipped", 0) or 0)),
        "- Quarantined Clusters: `{}`".format(int(payload.get("quarantined_cluster_count", 0) or 0)),
        "- Deprecated Modules/Files: `{}`".format(len(deprecations)),
        "",
        "## Counts By Risk Tier",
        "",
    ]
    for row in payload.get("risk_result_counts") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            "- `{}` applied=`{}` quarantined=`{}` skipped=`{}`".format(
                _token(row.get("risk_level")) or "unknown",
                int(row.get("applied", 0) or 0),
                int(row.get("quarantined", 0) or 0),
                int(row.get("skipped", 0) or 0),
            )
        )
    lines.extend(["", "## Quarantined Clusters", ""])
    for cluster_id in list(cluster_sets.get("quarantined") or [])[:CLUSTER_LIST_LIMIT]:
        lines.append("- `{}`".format(cluster_id))
    if len(list(cluster_sets.get("quarantined") or [])) > CLUSTER_LIST_LIMIT:
        lines.append("- ... see `docs/refactor/QUARANTINE_*.md` for the full packet set")
    if not list(cluster_sets.get("quarantined") or []):
        lines.append("- none")
    lines.extend(["", "## Deprecated Modules", ""])
    if deprecations:
        for row in deprecations[:DEPRECATION_LIST_LIMIT]:
            lines.append("- `{}`".format(_norm_rel(row.get("secondary_file"))))
        if len(deprecations) > DEPRECATION_LIST_LIMIT:
            lines.append("- ... see `docs/refactor/DEPRECATIONS.md` for the full set")
    else:
        lines.append("- none in this conservative pass")
    lines.extend(["", "## Gate Evidence", ""])
    for row in gate_rows:
        note = _token(row.get("note"))
        line = "- `{}` -> `{}`".format(_token(row.get("gate_id")), _token(row.get("status")) or "unknown")
        if note:
            line += " note=`{}`".format(note)
        lines.append(line)
    lines.extend(
        [
            "",
            "## Readiness For XI-5",
            "",
            "Readiness is `blocked_pending_follow_up`.",
            "",
            "XI-4 created the required execution log, deprecation record, and quarantine packet set, but medium/high-risk merge and rewire actions remain deferred under the XI-4 one-action-per-commit safety rule.",
            "",
        ]
    )
    return "\n".join(lines)


def write_convergence_execution_snapshot(repo_root: str, snapshot: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written = {}
    log_payload = dict(snapshot.get("convergence_execution_log") or {})
    written[CONVERGENCE_EXECUTION_LOG_REL] = _write_canonical_json(_repo_abs(root, CONVERGENCE_EXECUTION_LOG_REL), log_payload)
    written[CONVERGENCE_EXECUTION_LOG_DOC_REL] = _write_text(_repo_abs(root, CONVERGENCE_EXECUTION_LOG_DOC_REL), render_convergence_execution_log(snapshot) + "\n")
    written[DEPRECATIONS_REL] = _write_text(_repo_abs(root, DEPRECATIONS_REL), render_deprecations(snapshot) + "\n")
    written[XI_4_FINAL_REL] = _write_text(_repo_abs(root, XI_4_FINAL_REL), render_xi_4_final(snapshot) + "\n")

    quarantine_docs = dict(snapshot.get("quarantine_docs") or {})
    quarantine_dir = _repo_abs(root, QUARANTINE_DOC_DIR_REL)
    if os.path.isdir(quarantine_dir):
        for name in sorted(os.listdir(quarantine_dir)):
            if not name.startswith(QUARANTINE_DOC_PREFIX) or not name.endswith(".md"):
                continue
            rel_path = _norm_rel(os.path.join(QUARANTINE_DOC_DIR_REL, name))
            if rel_path not in quarantine_docs:
                os.remove(os.path.join(quarantine_dir, name))
    for rel_path, text in sorted(quarantine_docs.items()):
        written[rel_path] = _write_text(_repo_abs(root, rel_path), str(text).rstrip("\n") + "\n")
    return written


def build_convergence_execution_snapshot(repo_root: str) -> dict[str, object]:
    return _build_snapshot(repo_root)


__all__ = [
    "ARCHITECTURE_GRAPH_REL",
    "BUILD_GRAPH_REL",
    "CONVERGENCE_ACTIONS_REL",
    "CONVERGENCE_EXECUTION_LOG_DOC_REL",
    "CONVERGENCE_EXECUTION_LOG_REL",
    "CONVERGENCE_PLAN_REL",
    "CONVERGENCE_RISK_MAP_REL",
    "DEPRECATIONS_REL",
    "OUTPUT_REL_PATHS",
    "XI_4_FINAL_REL",
    "XiInputMissingError",
    "build_convergence_execution_snapshot",
    "render_convergence_execution_log",
    "render_deprecations",
    "render_xi_4_final",
    "write_convergence_execution_snapshot",
]
