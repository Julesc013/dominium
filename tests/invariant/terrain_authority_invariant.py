import argparse
import os
import re
import sys

from invariant_utils import is_override_active

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "ci")))
from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings


SCAN_ROOTS = (
    "engine",
    "game",
)

TERRAIN_HINTS = (
    "terrain",
    "sdf",
    "signed distance",
    "field_stack",
)

FORBIDDEN_TOKENS = (
    re.compile(r"\bmesh\b", re.IGNORECASE),
    re.compile(r"\bplanet\b", re.IGNORECASE),
    re.compile(r"\bstation\b", re.IGNORECASE),
)

EROSION_TOKENS = (
    re.compile(r"\berosion\b", re.IGNORECASE),
    re.compile(r"\bdecay\b", re.IGNORECASE),
    re.compile(r"\bregeneration\b", re.IGNORECASE),
)

TICK_TOKENS = (
    re.compile(r"\btick\b", re.IGNORECASE),
    re.compile(r"\bper_tick\b", re.IGNORECASE),
    re.compile(r"\bper-tick\b", re.IGNORECASE),
)

COLLISION_TOKENS = (
    re.compile(r"\bcollision\b", re.IGNORECASE),
    re.compile(r"\btruth\b", re.IGNORECASE),
)

PHI_TOKENS = (
    re.compile(r"\bphi\b", re.IGNORECASE),
    re.compile(r"\bsdf\b", re.IGNORECASE),
)


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def is_terrain_related(rel_path, stripped_text):
    rel_lower = rel_path.lower()
    for hint in TERRAIN_HINTS:
        if hint in rel_lower:
            return True
    for hint in TERRAIN_HINTS:
        if hint in stripped_text.lower():
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: terrain truth uses SDF + process-only overlays.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-TERRAIN-TRUTH-001"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    scanned = 0
    exts = [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"]
    for root in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for path in iter_files([abs_root], DEFAULT_EXCLUDES, exts):
            rel = repo_rel(repo_root, path)
            if rel.startswith("engine/tests/") or rel.startswith("game/tests/"):
                continue
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            if not is_terrain_related(rel, stripped):
                continue
            scanned += 1

            for token_re in FORBIDDEN_TOKENS:
                if token_re.search(stripped):
                    violations.append("{}: forbidden token {}".format(rel, token_re.pattern))

            if any(token.search(stripped) for token in EROSION_TOKENS) and any(
                token.search(stripped) for token in TICK_TOKENS
            ):
                violations.append("{}: erosion/decay/regeneration tied to ticks".format(rel))

            if any(token.search(stripped) for token in COLLISION_TOKENS):
                if not any(token.search(stripped) for token in PHI_TOKENS):
                    violations.append("{}: collision/truth without phi or SDF reference".format(rel))

    if violations:
        print("Terrain authority invariant violated:")
        for item in sorted(violations):
            print("  {}".format(item))
        return 1

    if scanned == 0:
        print("Terrain authority invariant OK (no terrain sources found).")
        return 0

    print("Terrain authority invariant OK. scanned={}".format(scanned))
    return 0


if __name__ == "__main__":
    sys.exit(main())
