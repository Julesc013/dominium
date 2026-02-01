import argparse
import os
import re
import sys


AUTHORITATIVE_DIRS = (
    os.path.join("engine", "modules", "core"),
    os.path.join("engine", "modules", "sim"),
    os.path.join("engine", "modules", "world"),
    os.path.join("game", "core"),
    os.path.join("game", "rules"),
)

SKIP_DIRS = {
    ".git",
    ".vs",
    ".vscode",
    "build",
    "dist",
    "out",
    "legacy",
    "docs",
    "schema",
    "third_party",
    "external",
    "deps",
}

SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".inl", ".inc", ".ipp",
    ".m", ".mm",
}

RNG_SEED_CALL_RE = re.compile(r"\bd_rng_(seed|stream_seed|streams_seed)\s*\(")
RNG_SEED_ALLOWLIST = {
    "engine/modules/core/rng.c",
    "engine/modules/core/rng_streams.c",
    "engine/modules/core/rng_model.c",
}


def iter_files(root, repo_root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, repo_root).replace("\\", "/")
        parts = rel.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in SOURCE_EXTS:
                continue
            yield os.path.join(dirpath, filename)


def iter_code_lines(path):
    in_block = False
    in_string = None
    try:
        with open(path, "r", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                i = 0
                out = ""
                while i < len(line):
                    ch = line[i]
                    nxt = line[i:i + 2]
                    if in_block:
                        if nxt == "*/":
                            in_block = False
                            i += 2
                            continue
                        i += 1
                        continue
                    if in_string:
                        if ch == "\\":
                            i += 2
                            continue
                        if ch == in_string:
                            in_string = None
                        i += 1
                        continue
                    if nxt == "//":
                        break
                    if nxt == "/*":
                        in_block = True
                        i += 2
                        continue
                    if ch in ("'", '"'):
                        in_string = ch
                        i += 1
                        continue
                    out += ch
                    i += 1
                yield idx, out
    except IOError:
        return


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def require_tokens(path, tokens, label):
    text = read_text(path)
    missing = [token for token in tokens if token not in text]
    if missing:
        raise AssertionError("{} missing tokens: {}".format(label, ", ".join(missing)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Determinism hard-lock contract tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    rng_doc = os.path.join(repo_root, "docs", "architecture", "RNG_MODEL.md")
    reduction_doc = os.path.join(repo_root, "docs", "architecture", "REDUCTION_MODEL.md")
    float_doc = os.path.join(repo_root, "docs", "architecture", "FLOAT_POLICY.md")
    rng_header = os.path.join(repo_root, "engine", "include", "domino", "core", "rng_model.h")

    for path in (rng_doc, reduction_doc, float_doc, rng_header):
        if not os.path.isfile(path):
            raise AssertionError("missing required file: {}".format(path))

    require_tokens(rng_doc,
                   ["noise.stream.", "world seed", "domain_id", "process_id", "tick_index"],
                   "RNG_MODEL.md")
    require_tokens(reduction_doc,
                   ["dom_det_reduce", "dom_det_order_sort"],
                   "REDUCTION_MODEL.md")
    require_tokens(float_doc,
                   ["floating point", "authoritative", "client"],
                   "FLOAT_POLICY.md")
    require_tokens(rng_header,
                   ["d_rng_stream_name_valid", "D_DET_GUARD_RNG_STREAM_NAME"],
                   "rng_model.h")

    fab_path = os.path.join(repo_root, "game", "rules", "fab", "fab_interpreters.cpp")
    scale_path = os.path.join(repo_root, "game", "rules", "scale", "scale_collapse_expand.cpp")
    require_tokens(fab_path, ["noise.stream."], "fab_interpreters.cpp")
    require_tokens(scale_path, ["noise.stream."], "scale_collapse_expand.cpp")

    violations = []
    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root, repo_root):
            rel = os.path.relpath(path, repo_root).replace("\\", "/")
            if rel in RNG_SEED_ALLOWLIST:
                continue
            for idx, code in iter_code_lines(path):
                if RNG_SEED_CALL_RE.search(code):
                    violations.append("{}:{}: d_rng_seed usage".format(rel, idx))

    if violations:
        raise AssertionError("anonymous RNG seeding detected.\n" + "\n".join(violations))

    print("determinism hard-lock tests OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
