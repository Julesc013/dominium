"""Deterministic documentation inventory and canon reconciliation helpers."""

from __future__ import annotations

import os
import sys
from collections import Counter
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


DOC_INVENTORY_JSON_REL = "data/audit/doc_inventory.json"
DOC_INDEX_MD_REL = "docs/audit/DOC_INDEX.md"
CANON_MAP_MD_REL = "docs/audit/CANON_MAP.md"
DOC_DRIFT_MATRIX_MD_REL = "docs/audit/DOC_DRIFT_MATRIX.md"
DOC_GAPS_MD_REL = "docs/audit/DOC_GAPS.md"
REPO_REVIEW_3_FINAL_MD_REL = "docs/audit/REPO_REVIEW_3_FINAL.md"

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".xstack_cache",
    "build",
    "dist",
    "node_modules",
}
SKIP_PREFIXES = ("docs/audit/auditx/",)
DOC_EXTENSIONS = {".md", ".rst", ".tex"}
ROOT_DOC_PATHS = {
    "AGENTS.md",
    "CHANGELOG.md",
    "CODE_CHANGE_JUSTIFICATION.md",
    "CONTRIBUTING.md",
    "DOMINIUM.md",
    "GOVERNANCE.md",
    "LICENSE.md",
    "MODDING.md",
    "README.md",
    "SECURITY.md",
    "data/CONTENT_AUDIT.md",
    "bundles/README.md",
}
CURRENT_SCOPE_KEYWORDS = {
    "appshell",
    "authority",
    "bundle",
    "capability",
    "canon",
    "compat",
    "contract",
    "determinism",
    "diag",
    "distribution",
    "earth",
    "epoch",
    "field",
    "geo",
    "illumination",
    "instance",
    "ipc",
    "law",
    "lens",
    "lib",
    "logic",
    "mode",
    "mvp",
    "negotiation",
    "orbit",
    "overlay",
    "pack",
    "platform",
    "process",
    "proof",
    "projection",
    "replay",
    "renderer",
    "save",
    "scope freeze",
    "server",
    "shell",
    "smoke",
    "sol",
    "stability",
    "stress",
    "supervisor",
    "tick",
    "time anchor",
    "tui",
    "ui",
    "universe",
    "validation",
    "worldgen",
    "xstack",
}
EXCLUDED_SCOPE_KEYWORDS = {
    "agent",
    "alchemy",
    "campaign",
    "chemistry",
    "civilization",
    "combat",
    "crafting",
    "ecology",
    "economy",
    "erosion",
    "inventory",
    "institutions",
    "molecule",
    "n-body",
    "narrative",
    "periodic table",
    "stellar lifecycle",
    "supernova",
    "tectonic",
    "vehicle",
    "vegetation",
}
PILLAR_RULES = {
    "Ontology: Assemblies/Fields/Processes/Agents/Law": ("assembly", "field", "law", "ontology", "process", "authority", "agent"),
    "Determinism: fixed-point, RNG streams, replay": ("determinism", "rng", "replay", "proof", "anchor", "fixed-point", "hash"),
    "Epistemics: Truth/Perceived/Render separation": ("epistemic", "truth", "perceived", "render", "renderer", "lens"),
    "Profiles: LawProfile/PhysicsProfile/etc.": ("profile", "lawprofile", "physicsprofile", "experienceprofile", "parameterbundle"),
    "GEO: topology/metric/projection/overlays": ("geo", "topology", "metric", "projection", "overlay", "spatial"),
    "LOGIC: signals/state machines/compile": ("logic", "signal", "state machine", "compile", "protocol"),
    "SYS/PROC: capsules, stabilization, drift": ("capsule", "stabilization", "drift", "system", "process"),
    "CAP-NEG: negotiation + degrade ladders": ("cap-neg", "negotiation", "handshake", "degrade", "descriptor"),
    "PACK-COMPAT: compat manifests, offline verification": ("pack", "compat", "manifest", "verification", "lock"),
    "LIB: installs/instances/saves, CAS": ("install", "instance", "save", "content-address", "cas", "bundle"),
    "APPSHELL: CLI/TUI/IPC/supervisor": ("appshell", "cli", "tui", "ipc", "supervisor", "launcher", "setup"),
    "DIAG: repro bundles": ("diag", "repro", "bundle", "forensics", "probe"),
    "RELEASE/DIST: manifests, packaging": ("release", "distribution", "dist", "package", "platform", "setup"),
}
TOPIC_RULES = {
    "appshell": ("appshell", "cli", "tui", "ipc", "supervisor", "launcher", "setup"),
    "build": ("build", "toolchain", "cmake", "preset"),
    "canon": ("canon", "constitution", "glossary", "binding"),
    "compat": ("compat", "compatx", "migration", "descriptor", "handshake"),
    "determinism": ("determinism", "deterministic", "rng", "replay", "proof", "fixed-point"),
    "diag": ("diag", "repro", "forensics", "audit"),
    "distribution": ("dist", "distribution", "release", "packaging", "installer"),
    "earth": ("earth", "hydrology", "climate", "terrain", "albedo"),
    "epistemics": ("epistemic", "lens", "truth", "perceived", "render"),
    "galaxy": ("galaxy", "milky way", "stellar", "metallicity", "radiation"),
    "geo": ("geo", "topology", "metric", "projection", "overlay", "spatial"),
    "logic": ("logic", "signal", "state machine", "compile", "trace"),
    "meta": ("stability", "contract", "schema", "canon", "scope freeze"),
    "pack": ("pack", "manifest", "compat", "lock", "bundle"),
    "platform": ("windows", "macos", "linux", "platform", "renderer"),
    "release": ("release", "dist", "scope freeze", "mvp"),
    "server": ("server", "authority", "session", "loopback"),
    "sol": ("sol", "orbit", "illumination", "moon", "ephemeris"),
    "time": ("time", "tick", "epoch", "anchor"),
    "validation": ("repox", "auditx", "testx", "compatx", "performx", "validation"),
    "worldgen": ("worldgen", "refinement", "mw", "galaxy", "earth"),
    "xstack": ("xstack", "repox", "auditx", "testx", "compatx"),
}
SUPERSESSION_OVERRIDES = {
    "docs/GLOSSARY.md": {"alignment_status": "superseded", "replacement_doc": "docs/canon/glossary_v1.md", "reason": "duplicate glossary surface is no longer binding; canon glossary v1 wins"},
    "docs/CAPABILITY_STAGES.md": {"alignment_status": "superseded", "replacement_doc": "docs/architecture/CAPABILITY_ONLY_CANON.md", "reason": "legacy capability staging summary already points to the current canonical document"},
    "docs/TESTX_STAGE_MATRIX.md": {"alignment_status": "superseded", "replacement_doc": "tests/testx/CAPABILITY_MATRIX.yaml", "reason": "matrix ownership moved into the generated TestX capability matrix artifact"},
    "docs/app/UI_MODES.md": {"alignment_status": "contradictory", "replacement_doc": "docs/appshell/APPSHELL_CONSTITUTION.md", "reason": "mode-selection order conflicts with the frozen v0.0.0 AppShell contract"},
    "docs/architecture/DIRECTORY_STRUCTURE.md": {"alignment_status": "contradictory", "replacement_doc": "docs/audit/REPO_TREE_INDEX.md", "reason": "top-level layout no longer matches the real repository inventory"},
}
PARTIAL_OVERRIDES = {
    "docs/ARCHITECTURE.md": "root architecture summary still describes boundaries, but does not reflect the current `src/` + `tools/` repository organization or current canon precedence",
    "docs/STATUS_NOW.md": "snapshot sections predate the final MVP scope freeze and need release-era updates",
    "docs/XSTACK.md": "governance overview is useful, but its implementation pointers and ownership language need reconciliation with the current tool layout",
    "docs/app/PRODUCT_BOUNDARIES.md": "product responsibilities remain mostly correct, but capability negotiation, AppShell, and standalone guarantees need alignment with current release docs",
    "docs/architecture/ARCH_REPO_LAYOUT.md": "ownership intent remains useful, but the concrete top-level layout is stale relative to the real repository tree",
}
GAP_ROWS = (
    {"priority": "high", "topic": "virtual paths", "suggested_doc": "docs/lib/VIRTUAL_PATH_LAYER.md", "reason": "REPO-REVIEW-2 found wide direct-path usage and there is no single current doctrine for the virtual path layer."},
    {"priority": "high", "topic": "standalone product guarantees", "suggested_doc": "docs/release/STANDALONE_PRODUCT_GUARANTEES.md", "reason": "setup guarantees exist, but there is no single current release doc for client/server/launcher/setup standalone guarantees."},
    {"priority": "medium", "topic": "platform matrix", "suggested_doc": "docs/release/PLATFORM_MATRIX.md", "reason": "cross-platform gate outputs exist, but there is no stable release-facing platform support matrix."},
    {"priority": "medium", "topic": "validation unification", "suggested_doc": "docs/validation/VALIDATION_UNIFICATION.md", "reason": "RepoX, AuditX, TestX, CompatX, and ARCH-AUDIT surfaces are documented in fragments rather than one convergence doc."},
    {"priority": "medium", "topic": "user-facing UI mode selection", "suggested_doc": "docs/app/UI_MODE_SELECTION.md", "reason": "the old UI mode summary is contradictory and the current mode order only appears indirectly in AppShell and release-freeze docs."},
)
DRIFT_RULES = (
    {"kind": "duplicate_spec", "severity": "high", "paths": ("docs/GLOSSARY.md", "docs/canon/glossary_v1.md"), "message": "duplicate glossary surfaces exist; only the canon glossary v1 is binding."},
    {"kind": "conflicting_definition", "severity": "high", "paths": ("docs/app/UI_MODES.md", "docs/appshell/APPSHELL_CONSTITUTION.md", "docs/release/FROZEN_INVARIANTS_v0_0_0.md"), "message": "UI mode selection rules diverge between the older app doc and the frozen AppShell order."},
    {"kind": "conflicting_definition", "severity": "high", "paths": ("docs/architecture/DIRECTORY_STRUCTURE.md", "docs/architecture/ARCH_REPO_LAYOUT.md", "docs/audit/REPO_TREE_INDEX.md"), "message": "layout docs still describe top-level product directories that no longer match the actual repository tree."},
    {"kind": "duplicate_spec", "severity": "medium", "paths": ("docs/ARCHITECTURE.md", "docs/architecture/ARCH0_CONSTITUTION.md", "docs/canon/constitution_v1.md"), "message": "root architecture summary overlaps with binding constitutional docs and can drift if treated as equivalent authority."},
    {"kind": "duplicate_spec", "severity": "medium", "paths": ("docs/XSTACK.md", "docs/audit/VALIDATION_STACK_MAP.md"), "message": "XStack governance is documented both as a narrative overview and as a generated current-state validation surface map."},
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _token(value: object) -> str:
    return str(value or "").strip()


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, rel_path.replace("/", os.sep))))


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _iter_doc_paths(repo_root: str) -> list[str]:
    rows: list[str] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        rel_dir = _norm(os.path.relpath(dirpath, repo_root))
        if rel_dir == ".":
            rel_dir = ""
        dirnames[:] = sorted(
            [
                name
                for name in dirnames
                if name not in SKIP_DIR_NAMES
                and not any(_norm(os.path.join(rel_dir, name)).startswith(prefix) for prefix in SKIP_PREFIXES)
            ]
        )
        if any(rel_dir.startswith(prefix.rstrip("/")) for prefix in SKIP_PREFIXES):
            dirnames[:] = []
            continue
        for name in sorted(filenames):
            rel_path = _norm(os.path.join(rel_dir, name)) if rel_dir else _norm(name)
            if any(rel_path.startswith(prefix) for prefix in SKIP_PREFIXES):
                continue
            _, ext = os.path.splitext(rel_path)
            if ext.lower() not in DOC_EXTENSIONS:
                continue
            if rel_path.startswith("docs/") or rel_path in ROOT_DOC_PATHS or "/docs/" in rel_path:
                rows.append(rel_path)
    return sorted(set(rows))


def _parse_header(text: str) -> dict[str, str]:
    header: dict[str, str] = {}
    for line in text.splitlines()[:20]:
        if not line.strip():
            if header:
                break
            continue
        if ":" not in line:
            if header:
                break
            continue
        key, value = line.split(":", 1)
        token = _token(key)
        if token:
            header[token.lower()] = _token(value)
    return header


def _title_from_text(rel_path: str, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return os.path.splitext(os.path.basename(rel_path))[0]


def _detected_topics(rel_path: str, title: str, text: str) -> list[str]:
    lowered = " ".join((_norm(rel_path), title, text[:4000])).lower()
    return sorted({topic for topic, tokens in TOPIC_RULES.items() if any(token in lowered for token in tokens)})


def _pillar_rows(rel_path: str, title: str, text: str) -> list[str]:
    lowered = " ".join((_norm(rel_path), title, text[:4000])).lower()
    rows = [pillar for pillar, tokens in PILLAR_RULES.items() if any(token in lowered for token in tokens)]
    return rows or ["RELEASE/DIST: manifests, packaging"]


def _header_superseded_by(header: Mapping[str, object]) -> str:
    token = _token(header.get("superseded by"))
    if token.lower() == "none":
        return ""
    return token


def _classify_alignment(rel_path: str, title: str, text: str, header: Mapping[str, object]) -> tuple[str, str, str]:
    rel_norm = _norm(rel_path)
    if rel_norm in SUPERSESSION_OVERRIDES:
        row = dict(SUPERSESSION_OVERRIDES[rel_norm])
        return _token(row.get("alignment_status")), _token(row.get("replacement_doc")), _token(row.get("reason"))
    explicit_replacement = _header_superseded_by(header)
    if explicit_replacement:
        return "superseded", explicit_replacement, "document already declares an explicit replacement path"
    if rel_norm in PARTIAL_OVERRIDES:
        return "partially_aligned", "", _token(PARTIAL_OVERRIDES[rel_norm])
    lowered = " ".join((rel_norm, title, text[:4000])).lower()
    if rel_norm.startswith(("docs/archive/", "data/archive/")):
        return "legacy_reference_only", "", "archived surface retained only for historical reference"
    if rel_norm.startswith(("docs/guides/", "docs/specs/", "docs/post_canon/", "docs/impact/", "docs/roadmap/", "docs/ci/")):
        return "legacy_reference_only", "", "guide/spec backlog surface is not part of the current binding canon set"
    if any(token in lowered for token in EXCLUDED_SCOPE_KEYWORDS):
        return "legacy_reference_only", "", "document describes excluded or future domain scope for v0.0.0"
    if rel_norm.startswith("docs/canon/"):
        return "aligned", "", "binding canon surface"
    if rel_norm.startswith(("docs/release/", "docs/mvp/", "docs/meta/", "docs/time/", "docs/sol/", "docs/worldgen/", "docs/geo/", "docs/logic/", "docs/appshell/", "docs/packs/", "docs/server/", "docs/contracts/", "docs/compat/", "docs/net/", "docs/client/", "docs/universe/")):
        return "aligned", "", "document aligns to implemented constitutional pillars or release gates"
    if rel_norm.startswith("docs/audit/"):
        return "aligned", "", "derived audit artifact aligned to current implemented state"
    if rel_norm.startswith(("docs/app/", "docs/build/", "docs/distribution/", "docs/reality/")):
        return "aligned", "", "document covers active app, build, distribution, or runtime surfaces"
    if rel_norm.startswith("docs/architecture/"):
        if any(token in lowered for token in CURRENT_SCOPE_KEYWORDS):
            return "aligned", "", "architecture document covers current constitutional scope"
        return "legacy_reference_only", "", "architecture document is outside the frozen MVP scope or not tied to current implementation"
    if rel_norm.startswith("docs/"):
        return "partially_aligned", "", "documentation surface exists, but current canon ownership is not explicit"
    return "legacy_reference_only", "", "external or supplemental documentation surface retained for reference"


def _stability_class(alignment_status: str) -> tuple[str, str, str]:
    if alignment_status == "aligned":
        return "provisional", "DOC-CONVERGENCE", "canon-aligned documentation set for convergence and release preparation"
    if alignment_status == "partially_aligned":
        return "provisional", "DOC-CONVERGENCE", "patched document aligned to current canon ownership and release scope"
    if alignment_status == "superseded":
        return "provisional", "DOC-CONVERGENCE", "explicit replacement document listed in the supersession header"
    if alignment_status == "contradictory":
        return "provisional", "DOC-CONVERGENCE", "replacement canonical document listed in the supersession header"
    return "provisional", "DOC-ARCHIVE", "legacy reference surface retained without current binding authority"


def _inventory_entry(repo_root: str, rel_path: str) -> dict:
    text = _read_text(_repo_abs(repo_root, rel_path))
    header = _parse_header(text)
    title = _title_from_text(rel_path, text)
    topics = _detected_topics(rel_path, title, text)
    pillars = _pillar_rows(rel_path, title, text)
    alignment_status, replacement_doc, reason = _classify_alignment(rel_path, title, text, header)
    stability_class, future_series, replacement_target = _stability_class(alignment_status)
    superseded_by = replacement_doc or _header_superseded_by(header)
    payload = {
        "path": _norm(rel_path),
        "title": title,
        "detected_topics": topics,
        "last_modified": _token(header.get("last reviewed")),
        "pillars": pillars,
        "alignment_status": alignment_status,
        "stability_class": stability_class,
        "future_series": future_series,
        "replacement_target": replacement_target,
        "replacement_doc": superseded_by,
        "status_header_present": bool(_token(header.get("status"))),
        "stability_header_present": bool(_token(header.get("stability"))),
        "superseded_header_present": bool(superseded_by),
        "patch_note_present": "## patch note" in text.lower() or "## patch notes" in text.lower(),
        "reason": reason,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _summary(entries: list[dict]) -> dict:
    status_counter = Counter()
    pillar_counter = Counter()
    for row in entries:
        status_counter[_token(row.get("alignment_status"))] += 1
        for pillar in list(row.get("pillars") or []):
            pillar_counter[_token(pillar)] += 1
    return {
        "by_alignment_status": dict(sorted(status_counter.items())),
        "by_pillar": dict(sorted(pillar_counter.items())),
        "stability_header_missing_count": sum(1 for row in entries if not bool(row.get("stability_header_present"))),
        "superseded_without_replacement_count": sum(
            1
            for row in entries
            if _token(row.get("alignment_status")) in {"superseded", "contradictory"} and not bool(row.get("superseded_header_present"))
        ),
    }


def _drift_rows(repo_root: str) -> list[dict]:
    rows = []
    for row in DRIFT_RULES:
        if not all(os.path.isfile(_repo_abs(repo_root, path)) for path in row["paths"]):
            continue
        rows.append(dict(row))
    return rows


def _gap_rows(repo_root: str) -> list[dict]:
    del repo_root
    return [dict(row) for row in GAP_ROWS]


def build_doc_inventory(repo_root: str) -> dict:
    root = _repo_root(repo_root)
    entries = [_inventory_entry(root, rel_path) for rel_path in _iter_doc_paths(root)]
    entries = sorted(entries, key=lambda item: (str(item.get("path", "")), str(item.get("title", ""))))
    payload = {
        "inventory_id": "doc.inventory.v1",
        "result": "complete",
        "entry_count": len(entries),
        "entries": entries,
        "summary": _summary(entries),
        "drift_rows": _drift_rows(root),
        "gap_rows": _gap_rows(root),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def load_json_if_present(repo_root: str, rel_path: str) -> dict:
    path = _repo_abs(_repo_root(repo_root), rel_path)
    if not os.path.isfile(path):
        return {}
    try:
        import json

        payload = json.loads(_read_text(path))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_or_run_doc_inventory(repo_root: str, *, prefer_cached: bool = True) -> dict:
    root = _repo_root(repo_root)
    if prefer_cached:
        payload = load_json_if_present(root, DOC_INVENTORY_JSON_REL)
        if payload and _token(payload.get("inventory_id")) == "doc.inventory.v1":
            return payload
    return build_doc_inventory(root)


def missing_stability_header_entries(report: Mapping[str, object] | None) -> list[dict]:
    rows = []
    for row in list(dict(report or {}).get("entries") or []):
        item = dict(row or {})
        if bool(item.get("stability_header_present")):
            continue
        rows.append({"path": _token(item.get("path")), "alignment_status": _token(item.get("alignment_status")), "stability_class": _token(item.get("stability_class"))})
    return sorted(rows, key=lambda item: item["path"])


def superseded_without_replacement_entries(report: Mapping[str, object] | None) -> list[dict]:
    rows = []
    for row in list(dict(report or {}).get("entries") or []):
        item = dict(row or {})
        if _token(item.get("alignment_status")) not in {"superseded", "contradictory"}:
            continue
        if bool(item.get("superseded_header_present")):
            continue
        rows.append({"path": _token(item.get("path")), "alignment_status": _token(item.get("alignment_status"))})
    return sorted(rows, key=lambda item: item["path"])


def contradictory_doc_header_issues(report: Mapping[str, object] | None) -> list[dict]:
    rows = []
    for row in list(dict(report or {}).get("entries") or []):
        item = dict(row or {})
        if _token(item.get("alignment_status")) != "contradictory":
            continue
        missing_headers = []
        if not bool(item.get("status_header_present")):
            missing_headers.append("status")
        if not bool(item.get("superseded_header_present")):
            missing_headers.append("replacement")
        if not bool(item.get("stability_header_present")):
            missing_headers.append("stability")
        if not missing_headers:
            continue
        rows.append(
            {
                "path": _token(item.get("path")),
                "replacement_doc": _token(item.get("replacement_doc")),
                "missing_headers": missing_headers,
            }
        )
    return sorted(rows, key=lambda item: item["path"])


def _render_doc_index(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.",
        "",
        "# Doc Index",
        "",
        "Source: `tools/review/tool_doc_inventory.py`",
        "",
        "| Path | Title | Topics | Last Reviewed |",
        "| --- | --- | --- | --- |",
    ]
    for row in list(dict(report).get("entries") or []):
        item = dict(row or {})
        lines.append(
            "| `{}` | {} | `{}` | `{}` |".format(
                _token(item.get("path")),
                _token(item.get("title")),
                "`, `".join(list(item.get("detected_topics") or [])),
                _token(item.get("last_modified")) or "-",
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_canon_map(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.",
        "",
        "# Canon Map",
        "",
        "Source: `tools/review/tool_doc_inventory.py`",
        "",
        "| Path | Pillars | Alignment | Stability | Replacement Doc |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in list(dict(report).get("entries") or []):
        item = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(item.get("path")),
                "`, `".join(list(item.get("pillars") or [])),
                _token(item.get("alignment_status")),
                _token(item.get("stability_class")),
                _token(item.get("replacement_doc")) or "-",
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_drift_matrix(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.",
        "",
        "# Doc Drift Matrix",
        "",
        "Source: `tools/review/tool_doc_inventory.py`",
        "",
        "## Conflicting Definitions And Duplicate Specs",
        "",
    ]
    for row in list(dict(report).get("drift_rows") or []):
        item = dict(row or {})
        lines.append("- `{}` `{}`: {} [{}]".format(_token(item.get("severity")), _token(item.get("kind")), _token(item.get("message")), ", ".join("`{}`".format(path) for path in list(item.get("paths") or []))))
    lines.extend(["", "## Missing Docs Required For v0.0.0", ""])
    for row in list(dict(report).get("gap_rows") or []):
        item = dict(row or {})
        lines.append("- `{}` `{}` -> `{}`: {}".format(_token(item.get("priority")), _token(item.get("topic")), _token(item.get("suggested_doc")), _token(item.get("reason"))))
    lines.append("")
    return "\n".join(lines)


def _render_doc_gaps(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.",
        "",
        "# Doc Gaps",
        "",
        "Source: `tools/review/tool_doc_inventory.py`",
        "",
    ]
    for row in list(dict(report).get("gap_rows") or []):
        item = dict(row or {})
        lines.append("- `{}` `{}`: create `{}` because {}".format(_token(item.get("priority")), _token(item.get("topic")), _token(item.get("suggested_doc")), _token(item.get("reason"))))
    lines.append("")
    return "\n".join(lines)


def _render_final_report(report: Mapping[str, object]) -> str:
    summary = dict(dict(report).get("summary") or {})
    contradictions = [dict(row or {}) for row in list(dict(report).get("drift_rows") or []) if _token(dict(row or {}).get("severity")) == "high"][:5]
    gaps = [dict(row or {}) for row in list(dict(report).get("gap_rows") or [])][:5]
    lines = [
        "Status: DERIVED",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: Canon-aligned documentation set tracked by REPO-REVIEW-3.",
        "",
        "# Repo Review 3 Final",
        "",
        "Source: `tools/review/tool_doc_inventory.py`",
        "",
        "## Alignment Status Counts",
        "",
    ]
    for key, value in dict(summary.get("by_alignment_status") or {}).items():
        lines.append("- `{}`: `{}`".format(_token(key), int(value or 0)))
    lines.extend(["", "## Top Contradictions", ""])
    for row in contradictions:
        lines.append("- `{}` [{}]".format(_token(row.get("message")), ", ".join("`{}`".format(path) for path in list(row.get("paths") or []))))
    lines.extend(["", "## Top Missing Docs", ""])
    for row in gaps:
        lines.append("- `{}` `{}` -> `{}`".format(_token(row.get("priority")), _token(row.get("topic")), _token(row.get("suggested_doc"))))
    lines.extend(["", "## Readiness", "", "- Entrypoint unification: ready with doc supersession map in place.", "- Validation unification: partially ready; canonical gap remains tracked in `docs/audit/DOC_GAPS.md`.", ""])
    return "\n".join(lines)


def render_report_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        DOC_INDEX_MD_REL: _render_doc_index(report),
        CANON_MAP_MD_REL: _render_canon_map(report),
        DOC_DRIFT_MATRIX_MD_REL: _render_drift_matrix(report),
        DOC_GAPS_MD_REL: _render_doc_gaps(report),
        REPO_REVIEW_3_FINAL_MD_REL: _render_final_report(report),
    }


def write_doc_inventory_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    abs_inventory_path = _repo_abs(root, DOC_INVENTORY_JSON_REL)
    os.makedirs(os.path.dirname(abs_inventory_path), exist_ok=True)
    with open(abs_inventory_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(report)))
        handle.write("\n")
    written = {DOC_INVENTORY_JSON_REL: abs_inventory_path}
    for rel_path, text in render_report_bundle(report).items():
        abs_path = _repo_abs(root, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = abs_path
    return dict(sorted(written.items()))


__all__ = [
    "CANON_MAP_MD_REL",
    "DOC_DRIFT_MATRIX_MD_REL",
    "DOC_GAPS_MD_REL",
    "DOC_INDEX_MD_REL",
    "DOC_INVENTORY_JSON_REL",
    "REPO_REVIEW_3_FINAL_MD_REL",
    "build_doc_inventory",
    "contradictory_doc_header_issues",
    "load_json_if_present",
    "load_or_run_doc_inventory",
    "missing_stability_header_entries",
    "render_report_bundle",
    "superseded_without_replacement_entries",
    "write_doc_inventory_outputs",
]
