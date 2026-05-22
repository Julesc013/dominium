#!/usr/bin/env python3
"""Apply the CANON-SPINE-NEW structural routing pass.

The tool is intentionally mechanical:
- read tracked files with git ls-files;
- map duplicate wrapper/sprawl paths to canonical source-spine paths;
- use git mv for tracked file moves;
- optionally rewrite exact path and import references after moves;
- write JSON/Markdown evidence.

It does not interpret file contents or mutate product identity fields.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "dominium.canon_spine_new.v1"


BAD_SEGMENTS = {
    "appshell",
    "appcore",
    "domain-data",
    "schemas",
    "registries",
    "capabilities",
    "instances",
    "saves",
    "ui_shared",
    "ui_bind",
    "validator",
    "validate",
    "validation",
    "__pycache__",
}


PREFIX_ROUTES: list[tuple[str, str, str]] = [
    ("artifacts/", "archive/generated/artifacts/", "generated artifact retention"),
    ("engine/tests/", "tests/engine/", "engine tests belong under tests"),
    ("engine/platform/", "runtime/platform/", "platform adapters belong under runtime"),
    ("engine/render/", "runtime/render/", "render adapters belong under runtime"),
    ("engine/store/", "runtime/storage/", "storage belongs under runtime"),
    ("engine/install/", "runtime/package/", "install/package runtime service"),
    ("engine/import/", "tools/import/", "import tooling"),
    ("engine/export/", "tools/export/", "export tooling"),
    ("engine/modules/execution/", "engine/execution/", "deterministic execution substrate"),
    ("engine/modules/replay/", "engine/replay/", "deterministic replay substrate"),
    ("engine/modules/input/", "runtime/input/", "input runtime service"),
    ("engine/modules/audio/", "runtime/audio/", "audio runtime service"),
    ("engine/modules/io/", "runtime/storage/io/", "runtime storage IO"),
    ("engine/modules/net/", "runtime/network/", "network runtime service"),
    ("engine/modules/compat/", "runtime/capability/compatibility/", "compatibility runtime capability service"),
    ("engine/modules/caps/", "runtime/capability/", "runtime capability service"),
    ("engine/modules/state/", "engine/state/", "deterministic state substrate"),
    ("engine/modules/struct/", "game/domain/structure/", "structure domain mechanics"),
    ("engine/modules/sys/", "runtime/platform/system/", "runtime system platform service"),
    ("engine/modules/system/", "runtime/platform/system/", "runtime system platform service"),
    ("engine/modules/trans/", "game/domain/transport/", "transport domain mechanics"),
    ("engine/modules/tui/", "runtime/projection/text/", "runtime TUI service"),
    ("engine/modules/ui/", "runtime/ui/service/", "runtime UI service"),
    ("engine/modules/ups/", "game/domain/systems/ups/", "UPS systems domain mechanics"),
    ("engine/modules/vehicle/", "game/domain/mobility/vehicle/", "vehicle mobility mechanics"),
    ("engine/modules/view/", "runtime/ui/view/", "runtime view service"),
    ("engine/modules/world/", "game/world/", "game world mechanics"),
    ("engine/modules/core/graph/", "engine/state/graph/", "deterministic graph state"),
    ("engine/modules/core/", "engine/kernel/", "deterministic kernel substrate"),
    ("engine/modules/ecs/", "engine/state/ecs/", "deterministic state storage"),
    ("engine/modules/sim/", "game/domain/simulation/", "simulation meaning belongs under game domain"),
    ("engine/modules/policy/", "game/rule/policy/", "game policy/rule implementation"),
    ("engine/modules/mod/", "runtime/package/mod/", "runtime package/mod service"),
    ("engine/modules/content/", "runtime/package/content/", "runtime content/package service"),
    ("engine/modules/build/", "game/domain/build/", "build domain mechanics"),
    ("engine/modules/agent/", "game/domain/agent/", "agent domain mechanics"),
    ("engine/modules/ai/", "game/domain/ai/", "AI domain mechanics"),
    ("engine/modules/decor/", "game/domain/decor/", "decor domain mechanics"),
    ("engine/modules/econ/", "game/domain/economy/", "economy domain mechanics"),
    ("engine/modules/env/", "game/domain/environment/", "environment domain mechanics"),
    ("engine/modules/hydro/", "game/domain/hydrology/", "hydrology domain mechanics"),
    ("engine/modules/job/", "game/domain/job/", "job domain mechanics"),
    ("engine/modules/res/", "game/domain/resource/", "resource domain mechanics"),
    ("engine/modules/research/", "game/domain/research/", "research domain mechanics"),
    ("engine/modules/scale/", "game/domain/scale/", "scale domain mechanics"),
    ("game/tests/", "tests/game/", "game tests belong under tests"),
    ("game/domains/", "game/domain/", "singular game domain code plane"),
    ("game/core/law/", "game/law/", "game law code plane"),
    ("game/core/execution/", "game/rule/execution/", "game execution rule code"),
    ("game/core/orchestration/", "game/rule/orchestration/", "game orchestration rules"),
    ("game/core/session/", "runtime/shell/session/", "session runtime shell"),
    ("game/core/", "game/rule/", "game rule code plane"),
    ("game/content/", "content/domains/game/", "authored game content"),
    ("game/mods/runtime/", "runtime/package/mod/", "mod runtime service"),
    ("game/mods/mods/examples/", "content/examples/modding/", "mod examples"),
    ("runtime/appshell/", "runtime/shell/", "canonical shell runtime"),
    ("runtime/app/", "runtime/shell/lifecycle/", "shell lifecycle runtime"),
    ("runtime/shell/appcore/ui_bind/", "tools/codegen/ui/bind/", "UI binding codegen"),
    ("runtime/shell/appcore/repox/", "tools/repo/repox/appcore/", "RepoX tooling"),
    ("runtime/shell/appcore/validate/", "tools/validators/shell/", "shell validators"),
    ("runtime/shell/appcore/command/", "runtime/shell/command/", "shell commands"),
    ("runtime/shell/appcore/discover/", "runtime/shell/discover/", "shell discovery"),
    ("runtime/shell/appcore/invoke/", "runtime/shell/invoke/", "shell invocation"),
    ("runtime/shell/appcore/output/", "runtime/shell/output/", "shell output"),
    ("runtime/shell/appcore/profile/", "runtime/shell/profile/", "shell profile binding"),
    ("apps/client/render/", "runtime/render/backend/", "client render runtime"),
    ("apps/client/ui/", "runtime/ui/client/", "client UI runtime"),
    ("apps/client/gui/", "runtime/platform/win32/client/", "client platform adapter"),
    ("apps/client/shell/", "runtime/shell/client/", "client shell binding"),
    ("apps/launcher/gui/", "runtime/platform/win32/launcher/", "launcher platform adapter"),
    ("apps/setup/gui/", "runtime/platform/win32/setup/", "setup platform adapter"),
    ("apps/server/gui/", "runtime/platform/win32/server/", "server platform adapter"),
    ("apps/server/runtime/", "runtime/shell/server/", "server shell runtime"),
    ("apps/launcher/core/", "apps/launcher/lifecycle/", "thin launcher lifecycle"),
    ("apps/setup/core/", "apps/setup/lifecycle/", "thin setup lifecycle"),
    ("tools/ui_shared/ui_codegen/", "tools/codegen/ui/", "UI codegen"),
    ("tools/ui_shared/ui_ir/", "runtime/view/ir/", "UI IR runtime model"),
    ("tools/ui_shared/dui/", "runtime/ui/control/dui/", "shared UI runtime"),
    ("tools/ui_shared/include/", "runtime/include/", "shared UI headers"),
    ("tools/ui_bind/", "tools/codegen/ui/bind/", "UI binding codegen"),
    ("tools/dist/", "tools/release/dist/", "release distribution tooling"),
    ("tools/distribution/", "tools/package/distribution/", "package distribution tooling"),
    ("tools/package/launcher/ui/", "tools/codegen/ui/launcher/", "launcher UI codegen inputs"),
    ("tools/package/setup/ui/", "tools/codegen/ui/setup/", "setup UI codegen inputs"),
    ("tools/ui_index/", "tools/codegen/ui/index/", "UI codegen index"),
    ("tools/ui_editor/", "apps/workbench/module/ui/editor/", "Workbench UI editor"),
    ("tools/tool_editor/", "apps/workbench/module/tooling/editor/", "Workbench tooling editor"),
    ("tools/world_editor/", "apps/workbench/module/world/editor/", "Workbench world editor"),
    ("tools/world_edit/", "apps/workbench/module/world/editor/", "Workbench world editor"),
    ("tools/game_edit/", "apps/workbench/module/game/editor/", "Workbench game editor"),
    ("tools/pack_editor/", "apps/workbench/module/pack/editor/", "Workbench pack editor"),
    ("tools/item_editor/", "apps/workbench/module/domain/item/", "Workbench item editor"),
    ("tools/policy_editor/", "apps/workbench/module/policy/editor/", "Workbench policy editor"),
    ("tools/process_editor/", "apps/workbench/module/process/editor/", "Workbench process editor"),
    ("tools/save_edit/", "apps/workbench/module/save/editor/", "Workbench save editor"),
    ("tools/save_inspector/", "apps/workbench/module/save/inspector/", "Workbench save inspector"),
    ("tools/replay_viewer/", "apps/workbench/module/replay/viewer/", "Workbench replay viewer"),
    ("tools/replay_analyzer/", "apps/workbench/module/replay/analyzer/", "Workbench replay analyzer"),
    ("tools/ui_preview_host/common/", "apps/workbench/module/ui/preview/service/", "Workbench UI preview service"),
    ("tools/ui_preview_host/", "apps/workbench/module/ui/preview/", "Workbench UI preview"),
    ("tools/universe_editor/", "apps/workbench/module/domain/universe/", "Workbench universe editor"),
    ("tools/blueprint_editor/", "apps/workbench/module/schema/blueprint/", "Workbench blueprint editor"),
    ("tools/editor_gui/", "apps/workbench/module/ui/preview/native/", "Workbench native preview host"),
    ("tools/struct_editor/", "apps/workbench/module/schema/structure/", "Workbench structure editor"),
    ("tools/tech_editor/", "apps/workbench/module/domain/technology/", "Workbench technology editor"),
    ("tools/transport_editor/", "apps/workbench/module/domain/transport/", "Workbench transport editor"),
    ("tools/appshell/", "tools/validators/shell/", "shell validation and replay tooling"),
    ("tools/validator/", "tools/validators/", "validator consolidation"),
    ("tools/validation/", "tools/validators/validation/", "validation tooling consolidation"),
    ("tools/validate/", "tools/validators/", "validator consolidation"),
    ("tools/xstack/auditx/", "tools/xstack/auditx/", "XStack AuditX family"),
    ("tools/xstack/compatx/", "tools/xstack/compatx/", "XStack CompatX family"),
    ("tools/xstack/controlx/", "tools/xstack/controlx/", "XStack ControlX family"),
    ("tools/xstack/securex/", "tools/xstack/securex/", "XStack SecureX family"),
    ("tools/xstack/performx/", "tools/xstack/performx/", "XStack PerformX family"),
    ("tools/network/", "tools/validators/network/", "network validators"),
    ("tools/geo/", "tools/validators/domain/geology/", "geology domain validators"),
    ("tools/geology/", "tools/validators/domain/geology/", "geology domain validators"),
    ("tools/physics/", "tools/validators/domain/physics/", "physics domain validators"),
    ("tools/libraries/", "tools/package/libraries/", "library package tooling"),
    ("tools/repo/repox/appcore/", "tools/repo/repox/shell/", "RepoX shell tooling"),
    ("tools/xstack/testdata/registries/", "tools/xstack/testdata/registry/", "singular XStack test registry data"),
    ("tools/validators/validation/", "tools/validators/suite/", "validator suite tooling"),
    ("docs/validation/", "docs/testing/validation/", "validation docs under testing"),
    ("contracts/schemas/", "contracts/schema/", "singular contract schema category"),
    ("contracts/schema/appshell/", "contracts/schema/runtime/shell/", "shell schema ownership"),
    ("contracts/schema/capabilities/", "contracts/schema/capability/", "singular capability schema ownership"),
    ("contracts/schema/registries/", "contracts/schema/registry/", "singular registry schema ownership"),
    ("contracts/schema/validation/", "contracts/schema/validation/", "validator schema ownership"),
    ("contracts/registries/", "contracts/registry/", "singular contract registry category"),
    ("contracts/capabilities/", "contracts/capability/", "singular contract capability category"),
    ("contracts/bundles/", "contracts/package/bundles/", "contract package bundle rules"),
    (
        "contracts/packs/",
        "contracts/package/",
        "package contract/law material; authored pack payloads belong under content/packs",
    ),
    ("contracts/instances/", "contracts/instance/", "singular contract instance category"),
    ("contracts/saves/", "contracts/save/", "singular contract save category"),
    ("contracts/projections/", "contracts/projection/", "singular contract projection category"),
    ("contracts/protocols/", "contracts/protocol/", "singular contract protocol category"),
    ("contracts/locks/", "contracts/lock/", "singular contract lock category"),
    ("content/domain-data/", "content/domains/", "canonical content domains"),
    ("content/data/defaults/", "content/defaults/", "content defaults"),
    ("content/data/world/", "content/domains/world/", "world domain content"),
    ("content/data/archive/", "archive/historical/content/", "historical content data"),
    ("content/data/audit/", "archive/generated/audit/", "generated audit evidence"),
    ("content/data/analysis/", "archive/generated/analysis/", "generated analysis evidence"),
    ("content/data/perf/", "archive/generated/performance/", "generated performance evidence"),
    ("content/data/release/", "archive/generated/release/", "generated release evidence"),
    ("content/data/repo/", "archive/generated/repo/", "generated repo evidence"),
    ("content/data/restructure/", "archive/generated/restructure/", "generated restructure evidence"),
    ("content/data/refactor/", "archive/generated/refactor/", "generated refactor evidence"),
    ("content/data/xstack/", "archive/generated/xstack/", "generated XStack evidence"),
    ("content/data/blueprint/", "archive/generated/blueprint/", "generated blueprint evidence"),
    ("content/data/architecture/", "archive/generated/architecture/", "generated architecture evidence"),
    ("content/data/agents/", "archive/generated/agents/", "generated agent evidence"),
    ("content/data/governance/", "contracts/governance/", "governance data contracts"),
    ("content/data/planning/", "contracts/planning/", "planning machine data"),
    ("content/data/session_templates/", "content/templates/session/", "session templates"),
    ("docs/appshell/", "docs/runtime/shell/", "runtime shell docs"),
    ("docs/app/", "docs/apps/", "application docs"),
    ("docs/compat/", "docs/compatibility/", "compatibility docs"),
    ("docs/dev/", "docs/development/", "development docs"),
    ("docs/diag/", "docs/runtime/diagnostics/", "diagnostics docs"),
    ("docs/geo/", "docs/domains/geology/", "geology docs"),
    ("docs/chemistry/", "docs/domains/chemistry/", "chemistry docs"),
    ("docs/physics/", "docs/domains/physics/", "physics docs"),
    ("docs/fluid/", "docs/domains/fluids/", "fluid docs"),
    ("docs/thermal/", "docs/domains/thermal/", "thermal docs"),
    ("docs/net/", "docs/runtime/network/", "network docs"),
    ("docs/render/", "docs/runtime/render/", "render docs"),
    ("docs/platform/", "docs/runtime/platform/", "platform docs"),
    ("docs/tools/", "docs/development/tools/", "tool docs"),
]


SPECIAL_FILES = {
    "runtime/shell/appcore/CMakeLists.txt": ("runtime/shell/CMakeLists.txt", "shell CMake owner"),
    "tools/appshell/tool_generate_command_docs.py": ("tools/codegen/shell/tool_generate_command_docs.py", "shell command documentation codegen"),
}


@dataclass(frozen=True)
class Route:
    source: str
    target: str
    reason: str
    action: str


def run(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=repo, text=True, capture_output=True, check=check)


def git_ls_files(repo: Path) -> list[str]:
    result = run(repo, ["git", "ls-files"])
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def route_apps_client_core(path: str) -> Route | None:
    prefix = "apps/client/core/"
    if not path.startswith(prefix):
        return None
    rel = path[len(prefix) :]
    name = Path(rel).name
    if name.startswith("client_command"):
        target = "apps/client/command/" + rel
        reason = "client product command registration"
    elif name.startswith("client_models"):
        target = "apps/client/model/" + rel
        reason = "client product model binding"
    else:
        target = "apps/client/session/" + rel
        reason = "client product session binding"
    return Route(path, target, reason, "move")


def route_pycache(path: str) -> Route | None:
    if "/__pycache__/" in path or path.startswith("__pycache__/"):
        return Route(path, "archive/generated/pycache/" + path, "tracked Python cache evidence", "move")
    return None


def route_path(path: str) -> Route | None:
    if path in SPECIAL_FILES:
        target, reason = SPECIAL_FILES[path]
        return Route(path, target, reason, "move")
    special = route_pycache(path) or route_apps_client_core(path)
    if special:
        return special
    for old, new, reason in PREFIX_ROUTES:
        if path.startswith(old):
            return Route(path, new + path[len(old) :], reason, "move")
    return None


def collect_routes(paths: Iterable[str]) -> list[Route]:
    routes: list[Route] = []
    for path in paths:
        route = route_path(path)
        if route and route.source != route.target:
            routes.append(route)
    return sorted(routes, key=lambda item: item.source)


def resolve_collisions(routes: list[Route], tracked: set[str]) -> tuple[list[Route], list[dict[str, str]]]:
    seen: dict[str, str] = {}
    resolved: list[Route] = []
    collisions: list[dict[str, str]] = []
    for route in routes:
        target = route.target
        collides_with = None
        if target in tracked and target != route.source:
            collides_with = target
        if target in seen and seen[target] != route.source:
            collides_with = seen[target]
        if collides_with:
            quarantine = "archive/quarantine/canon-spine/" + route.source
            collisions.append({
                "source": route.source,
                "intended_target": target,
                "collision": collides_with,
                "rerouted_target": quarantine,
            })
            route = Route(route.source, quarantine, route.reason + "; collision quarantined", "move_quarantine")
            target = route.target
        seen[target] = route.source
        resolved.append(route)
    return resolved, collisions


def replacement_pairs(routes: list[Route]) -> list[tuple[bytes, bytes, str]]:
    pairs: list[tuple[bytes, bytes, str]] = []
    prefix_pairs: list[tuple[str, str, str]] = []
    for old, new, reason in PREFIX_ROUTES:
        prefix_pairs.append((old, new, reason))
    for old, (new, reason) in SPECIAL_FILES.items():
        prefix_pairs.append((old, new, reason))
    for route in routes:
        if route.source.startswith("apps/client/core/") or route.action == "move_quarantine":
            prefix_pairs.append((route.source, route.target, route.reason))
    # Longest first avoids replacing a parent prefix before a more specific child.
    for old, new, _reason in sorted(prefix_pairs, key=lambda item: len(item[0]), reverse=True):
        pairs.append((old.encode("utf-8"), new.encode("utf-8"), "slash path"))
        pairs.append((old.replace("/", "\\").encode("utf-8"), new.replace("/", "\\").encode("utf-8"), "backslash path"))
    dotted = {
        "runtime.appshell": "runtime.shell",
        "runtime.app": "runtime.shell.lifecycle",
        "runtime.shell.appcore": "runtime.shell",
        "apps.client.render": "runtime.render.backend",
        "apps.client.ui": "runtime.ui.client",
        "apps.server.runtime": "runtime.shell.server",
        "tools.ui_shared": "runtime.ui",
        "tools.ui_bind": "tools.codegen.ui.bind",
        "tools.auditx": "tools.xstack.auditx",
        "tools.compatx": "tools.xstack.compatx",
        "tools.controlx": "tools.xstack.controlx",
        "tools.securex": "tools.xstack.securex",
        "tools.performx": "tools.xstack.performx",
        "game.domains": "game.domain",
        "contracts.schemas": "contracts.schema",
        "contracts.registries": "contracts.registry",
        "contracts.capabilities": "contracts.capability",
        "contracts.projections": "contracts.projection",
        "contracts.protocols": "contracts.protocol",
    }
    for old, new in dotted.items():
        pairs.append((old.encode("utf-8"), new.encode("utf-8"), "python/module path"))
    return pairs


def rewrite_text(repo: Path, routes: list[Route]) -> dict[str, object]:
    paths = git_ls_files(repo)
    pairs = replacement_pairs(routes)
    changed: list[dict[str, object]] = []
    skipped_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".aps", ".exe", ".dll", ".pdb", ".lib", ".obj", ".pyc"}
    for rel in paths:
        suffix = Path(rel).suffix.lower()
        if suffix in skipped_suffixes:
            continue
        full = repo / rel
        try:
            data = full.read_bytes()
        except OSError:
            continue
        new_data = data
        replacements = 0
        kinds: set[str] = set()
        for old, new, kind in pairs:
            count = new_data.count(old)
            if count:
                new_data = new_data.replace(old, new)
                replacements += count
                kinds.add(kind)
        if replacements:
            full.write_bytes(new_data)
            changed.append({"path": rel, "replacements": replacements, "kinds": sorted(kinds)})
    return {
        "files_changed": len(changed),
        "replacement_count": sum(int(item["replacements"]) for item in changed),
        "files": changed,
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def apply_moves(repo: Path, routes: list[Route]) -> dict[str, object]:
    applied: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []
    for route in routes:
        source = repo / route.source
        target = repo / route.target
        if not source.exists():
            failed.append({"source": route.source, "target": route.target, "error": "source_missing"})
            continue
        ensure_parent(target)
        result = run(repo, ["git", "mv", route.source, route.target], check=False)
        if result.returncode == 0:
            applied.append({"source": route.source, "target": route.target, "reason": route.reason, "action": route.action})
        else:
            failed.append({
                "source": route.source,
                "target": route.target,
                "error": (result.stderr or result.stdout).strip(),
            })
    return {"applied": applied, "failed": failed}


def segment_findings(paths: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        for segment in path.split("/")[:-1]:
            if segment in BAD_SEGMENTS:
                counts[segment] = counts.get(segment, 0) + 1
    return dict(sorted(counts.items()))


def write_reports(args: argparse.Namespace, payload: dict[str, object]) -> None:
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.md_out:
        out = Path(args.md_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        summary = payload["summary"]  # type: ignore[index]
        lines = [
            "# CANON-SPINE-NEW Report",
            "",
            f"Mode: `{payload['mode']}`",
            f"Status: `{payload['status']}`",
            "",
            "## Summary",
            "",
            f"- Candidate routes: {summary['candidate_routes']}",  # type: ignore[index]
            f"- Applied moves: {summary.get('applied_moves', 0)}",  # type: ignore[union-attr]
            f"- Failed moves: {summary.get('failed_moves', 0)}",  # type: ignore[union-attr]
            f"- Collision reroutes: {summary['collision_reroutes']}",  # type: ignore[index]
            f"- Text files changed: {summary.get('text_files_changed', 0)}",  # type: ignore[union-attr]
            f"- Text replacements: {summary.get('text_replacements', 0)}",  # type: ignore[union-attr]
            "",
            "## Top Route Reasons",
            "",
        ]
        reasons = payload.get("reason_counts", {})
        if isinstance(reasons, dict):
            for reason, count in sorted(reasons.items(), key=lambda item: (-int(item[1]), item[0]))[:40]:
                lines.append(f"- {reason}: {count}")
        lines.extend(["", "## Remaining Forbidden Segment Counts", ""])
        segs = payload.get("post_segment_findings", payload.get("pre_segment_findings", {}))
        if isinstance(segs, dict) and segs:
            for segment, count in segs.items():
                lines.append(f"- `{segment}`: {count}")
        else:
            lines.append("- none detected by this tool")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rewrite-text", action="store_true")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    paths = git_ls_files(repo)
    tracked = set(paths)
    routes, collisions = resolve_collisions(collect_routes(paths), tracked)
    reason_counts: dict[str, int] = {}
    for route in routes:
        reason_counts[route.reason] = reason_counts.get(route.reason, 0) + 1

    move_result: dict[str, object] = {"applied": [], "failed": []}
    rewrite_result: dict[str, object] = {"files_changed": 0, "replacement_count": 0, "files": []}
    mode = "dry_run"
    if args.apply:
        mode = "apply"
        move_result = apply_moves(repo, routes)
        if args.rewrite_text:
            rewrite_result = rewrite_text(repo, routes)

    post_paths = git_ls_files(repo) if args.apply else paths
    status = "PASS" if not move_result.get("failed") else "PARTIAL"
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "status": status,
        "summary": {
            "candidate_routes": len(routes),
            "collision_reroutes": len(collisions),
            "applied_moves": len(move_result.get("applied", [])),
            "failed_moves": len(move_result.get("failed", [])),
            "text_files_changed": rewrite_result.get("files_changed", 0),
            "text_replacements": rewrite_result.get("replacement_count", 0),
        },
        "reason_counts": reason_counts,
        "collisions": collisions,
        "routes": [route.__dict__ for route in routes],
        "move_result": move_result,
        "rewrite_result": rewrite_result,
        "pre_segment_findings": segment_findings(paths),
        "post_segment_findings": segment_findings(post_paths),
    }
    write_reports(args, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if status in {"PASS", "PARTIAL"} else 1


if __name__ == "__main__":
    sys.exit(main())
