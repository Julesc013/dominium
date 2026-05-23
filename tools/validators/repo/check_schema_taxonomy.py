#!/usr/bin/env python3
"""Validate the high-signal contracts/schema taxonomy routes.

This is a narrow structure validator for the residual schema cleanup pass. It
does not try to prove every schema is semantically final; it blocks the retired
active buckets and flat schema prefixes that now have canonical routes.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


RETIRED_SCHEMA_DIRS = {
    "agents": "contracts/schema/game/agents",
    "authority": "contracts/schema/repo/authority",
    "economy": "contracts/schema/game/economy",
    "law": "contracts/schema/game/law",
    "life": "contracts/schema/game/life",
    "session": "contracts/schema/runtime/session",
    "time": "contracts/schema/runtime/time",
    "ui": "contracts/schema/runtime/ui",
    "world": "contracts/schema/game/world",
    "worldgen": "contracts/schema/game/worldgen",
}

RETIRED_FLAT_PREFIXES = {
    "agent": "contracts/schema/game/agents",
    "animal.": "contracts/schema/game/agents",
    "authority": "contracts/schema/repo/authority",
    "civilization": "contracts/schema/domain/civilization",
    "control": "contracts/schema/runtime/control",
    "controller": "contracts/schema/runtime/control",
    "core_": "contracts/schema/runtime/engine/core",
    "fluid": "contracts/schema/domain/fluids",
    "geo_": "contracts/schema/domain/geology",
    "geology.": "contracts/schema/domain/geology",
    "geometry_": "contracts/schema/domain/geology",
    "law": "contracts/schema/game/law",
    "net_": "contracts/schema/runtime/network",
    "network": "contracts/schema/domain/network",
    "render": "contracts/schema/runtime/render",
    "renderable": "contracts/schema/runtime/render",
    "server_": "contracts/schema/runtime/server",
    "server_protocol": "contracts/schema/runtime/server",
    "session": "contracts/schema/runtime/session",
    "sync_policy": "contracts/schema/runtime/time",
    "temporal_domain": "contracts/schema/runtime/time",
    "terrain.": "contracts/schema/domain/geology",
    "tick_t": "contracts/schema/runtime/time",
    "time": "contracts/schema/runtime/time",
    "topology": "contracts/schema/domain/geology",
    "tui_": "contracts/schema/runtime/ui",
    "ui_": "contracts/schema/runtime/ui",
    "world_definition": "contracts/schema/game/world",
    "worldgen": "contracts/schema/game/worldgen",
}


def _configure_stdio():
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdio()


def utc_now():
    return _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def posix(path):
    return str(path).replace("\\", "/")


def git_files(repo_root):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def add(findings, severity, path, code, message, target=""):
    findings.append(
        {
            "severity": severity,
            "path": path,
            "code": code,
            "message": message,
            "target": target,
        }
    )


def build_report(repo_root, max_findings):
    tracked = git_files(repo_root)
    findings = []

    for path in tracked:
        if not path.startswith("contracts/schema/"):
            continue
        tail = path[len("contracts/schema/") :]
        first = tail.split("/", 1)[0]
        if first in RETIRED_SCHEMA_DIRS:
            add(
                findings,
                "blocker",
                path,
                "retired_schema_bucket",
                "retired contracts/schema bucket remains active",
                RETIRED_SCHEMA_DIRS[first],
            )
            continue
        if "/" in tail:
            continue
        for prefix, target in sorted(RETIRED_FLAT_PREFIXES.items()):
            if tail.startswith(prefix):
                add(
                    findings,
                    "blocker",
                    path,
                    "retired_flat_schema_prefix",
                    "flat schema file has a canonical taxonomy route",
                    target,
                )
                break

    unique = {}
    for item in findings:
        key = (item["severity"], item["path"], item["code"], item["target"])
        unique[key] = item
    findings = sorted(unique.values(), key=lambda item: (item["severity"], item["path"], item["code"]))
    blocker_count = sum(1 for item in findings if item["severity"] == "blocker")
    return {
        "schema_version": "dominium.repo.schema_taxonomy.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS",
        "blocker_count": blocker_count,
        "finding_count": len(findings),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate routed contracts/schema taxonomy.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail on blockers.")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("schema taxonomy: {0}".format(report["status"]))
        for item in report["findings"]:
            record = dict(item)
            record["target_text"] = " -> {0}".format(item["target"]) if item.get("target") else ""
            print("{severity} {path}: {code}: {message}{target_text}".format(**record))

    if args.strict and report["blocker_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
