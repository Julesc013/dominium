#!/usr/bin/env python3
"""
CI smoke checks for the launcher CLI selection paths.

Goals (PROMPT L-8):
- Exercise `--ui=native|dgfx|null` parsing without launching the full GUI.
- Exercise `--gfx=soft|null` selection for whichever backends are compiled in.
- Preserve stdout/stderr + generated audit TLVs for inspection.

This script is intentionally best-effort in discovery:
- It parses `--print-caps` output to determine which backends exist.
- It only runs combinations that are present in the registry.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


LAUNCHER_BASENAME_WIN = "dominium-launcher.exe"
LAUNCHER_BASENAME_POSIX = "dominium-launcher"


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _is_exe_file(path: str) -> bool:
    return os.path.isfile(path) and os.access(path, os.X_OK)


def _find_launcher(build_dir: str) -> str:
    build_dir = os.path.abspath(build_dir)

    direct = [
        os.path.join(build_dir, LAUNCHER_BASENAME_WIN),
        os.path.join(build_dir, LAUNCHER_BASENAME_POSIX),
        os.path.join(build_dir, "Debug", LAUNCHER_BASENAME_WIN),
        os.path.join(build_dir, "Release", LAUNCHER_BASENAME_WIN),
    ]
    for p in direct:
        if _is_exe_file(p):
            return p

    matches: List[str] = []
    for root, _dirs, files in os.walk(build_dir):
        for name in files:
            if name in (LAUNCHER_BASENAME_WIN, LAUNCHER_BASENAME_POSIX):
                p = os.path.join(root, name)
                if _is_exe_file(p):
                    matches.append(p)

    if not matches:
        raise SystemExit("launcher binary not found under: %s" % build_dir)

    matches.sort(key=lambda p: (len(_norm(p)), _norm(p)))
    return matches[0]


@dataclass
class CapsInfo:
    by_subsystem: Dict[str, List[str]]


def _find_backends(caps: CapsInfo, name_hints: Tuple[str, ...]) -> List[str]:
    # Prefer exact key matches (case-insensitive), then substring matches.
    hints = [h.lower() for h in name_hints if h]
    for k, v in caps.by_subsystem.items():
        if k.lower() in hints:
            return v
    for k, v in caps.by_subsystem.items():
        kl = k.lower()
        for h in hints:
            if h and (kl.endswith(h) or h in kl):
                return v
    return []


def _parse_print_caps(text: str) -> CapsInfo:
    by: Dict[str, List[str]] = {}

    subsys_re = re.compile(r"^subsystem\s+(\d+)(?:\s+\(([^)]+)\))?\s*$")
    backend_re = re.compile(r"^\s*-\s+([^\s]+)\s+det=")

    current = ""
    for line in text.splitlines():
        m = subsys_re.match(line.strip("\r\n"))
        if m:
            current = (m.group(2) or m.group(1) or "").strip()
            if current:
                by.setdefault(current.upper(), [])
            continue
        m = backend_re.match(line.strip("\r\n"))
        if m and current:
            by[current.upper()].append(m.group(1))
    for k in by:
        by[k] = sorted(set(by[k]))
    return CapsInfo(by_subsystem=by)


def _run_one(launcher: str, args: List[str], cwd: str, out_base: str) -> None:
    cmd = [launcher] + args
    out_path = os.path.join(cwd, out_base + ".out.txt")
    err_path = os.path.join(cwd, out_base + ".err.txt")

    with open(out_path, "wb") as out_f, open(err_path, "wb") as err_f:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=out_f, stderr=err_f)
        rc = p.wait()

    if rc != 0:
        raise SystemExit("launcher smoke failed (rc=%d): %s" % (rc, " ".join(cmd)))


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Run launcher CLI smoke matrix (ui/gfx selection).")
    ap.add_argument("--build-dir", required=True, help="CMake build directory containing dominium-launcher")
    ap.add_argument("--out-dir", default="", help="Output directory (default: <build-dir>/ci_artifacts/launcher_cli_smoke)")
    args = ap.parse_args(argv)

    launcher = _find_launcher(args.build_dir)
    build_dir = os.path.abspath(args.build_dir)
    out_dir = os.path.abspath(args.out_dir) if args.out_dir else os.path.join(build_dir, "ci_artifacts", "launcher_cli_smoke")
    os.makedirs(out_dir, exist_ok=True)

    # Discover compiled-in backends via --print-caps.
    caps_cmd = [launcher, "--print-caps"]
    try:
        caps_out = subprocess.check_output(caps_cmd, cwd=out_dir, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write("launcher --print-caps failed:\n")
        sys.stderr.write(exc.output.decode("utf-8", errors="replace"))
        return 2

    caps_text = caps_out.decode("utf-8", errors="replace")
    with open(os.path.join(out_dir, "print_caps.txt"), "wb") as f:
        f.write(caps_out)

    caps = _parse_print_caps(caps_text)
    gfx_list = _find_backends(caps, ("gfx", "dgfx"))
    ui_list = _find_backends(caps, ("ui", "dui"))
    gfx_avail: Set[str] = set([b.lower() for b in gfx_list])
    ui_avail: Set[str] = set([b.lower() for b in ui_list])

    gfx_wanted = [b for b in ("soft", "null") if b in gfx_avail]
    if not gfx_wanted:
        raise SystemExit("No supported gfx backends found in caps (expected soft and/or null).")

    ui_wanted: List[Tuple[str, List[str]]] = []
    # Always exercise --ui=native parsing path (no override); expected to select something.
    ui_wanted.append(("native", ["--ui=native"]))
    if "dgfx" in ui_avail:
        ui_wanted.append(("dgfx", ["--ui=dgfx"]))
    if "null" in ui_avail:
        ui_wanted.append(("null", ["--ui=null"]))

    for gfx in gfx_wanted:
        for ui_name, ui_args in ui_wanted:
            base = "print_selection_ui-%s_gfx-%s" % (ui_name, gfx)
            _run_one(launcher, ["--print-selection", "--gfx=%s" % gfx] + ui_args, out_dir, base)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
