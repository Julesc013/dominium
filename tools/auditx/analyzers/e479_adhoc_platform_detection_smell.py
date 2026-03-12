"""E479 ad hoc platform detection smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding


ANALYZER_ID = "E479_ADHOC_PLATFORM_DETECTION_SMELL"
TARGET_EXTENSIONS = {".py"}
SCAN_ROOTS = (
    "src/appshell",
    "src/client",
    "src/server",
    "tools/launcher",
    "tools/setup",
)
ALLOWED_PATHS = {
    "src/platform/platform_probe.py",
    "src/platform/platform_caps_probe.py",
    "src/platform/platform_window.py",
}
TOKENS = (
    "sys.platform",
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "GetConsoleWindow",
    "ctypes.windll",
    "AppKit",
    "__CFBundleIdentifier",
    "TERM_PROGRAM",
    'find_spec("curses")',
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    root = os.path.normpath(os.path.abspath(repo_root))
    for scan_root in SCAN_ROOTS:
        abs_root = os.path.join(root, scan_root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for dirpath, _dirnames, filenames in os.walk(abs_root):
            for filename in sorted(filenames):
                rel_path = _norm(os.path.relpath(os.path.join(dirpath, filename), root))
                if rel_path in ALLOWED_PATHS:
                    continue
                if os.path.splitext(filename)[1].lower() not in TARGET_EXTENSIONS:
                    continue
                text = _read_text(os.path.join(root, rel_path.replace("/", os.sep)))
                for token in TOKENS:
                    if token not in text:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="platform.adhoc_detection_smell",
                            severity="RISK",
                            confidence=0.97,
                            file_path=rel_path,
                            evidence=[
                                "token={}".format(token),
                                "platform detection heuristics must be centralized in src/platform/platform_probe.py",
                            ],
                            suggested_classification="TODO-BLOCKED",
                            recommended_action="ROUTE_THROUGH_PLATFORM_PROBE",
                            related_invariants=["INV-UI-MODE-SELECTION-USES-PROBE"],
                            related_paths=[rel_path, "src/platform/platform_probe.py"],
                        )
                    )
    return findings
