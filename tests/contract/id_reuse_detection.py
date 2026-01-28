import argparse
import os
import re
import sys
from typing import Dict, Iterable, List, Optional, Tuple


SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*(\S+)")


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def iter_schema_files(schema_root: str) -> Iterable[str]:
    for dirpath, _dirnames, filenames in os.walk(schema_root):
        for name in filenames:
            if name.endswith(".schema"):
                yield os.path.join(dirpath, name)


def first_schema_id(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                match = SCHEMA_ID_RE.match(line)
                if match:
                    return match.group(1)
    except OSError:
        return None
    return None


def parse_refusal_block(text: str) -> List[Tuple[int, str, str]]:
    start = text.find("```refusal-codes")
    if start == -1:
        return []
    start = text.find("\n", start)
    end = text.find("```", start + 1)
    if end == -1:
        return []
    rows: List[Tuple[int, str, str]] = []
    for raw_line in text[start:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",", 2)]
        if len(parts) < 2:
            continue
        try:
            code_id = int(parts[0])
        except ValueError:
            continue
        code = parts[1]
        meaning = parts[2] if len(parts) > 2 else ""
        rows.append((code_id, code, meaning))
    return rows


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="ID reuse and collision checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    schema_root = os.path.join(repo_root, "schema")
    refusal_doc = os.path.join(repo_root, "docs", "architecture", "REFUSAL_SEMANTICS.md")

    if not os.path.isdir(schema_root):
        print("missing schema directory: {}".format(schema_root))
        return 1
    if not os.path.isfile(refusal_doc):
        print("missing refusal semantics doc: {}".format(refusal_doc))
        return 1

    violations: List[str] = []

    # Schema ID uniqueness.
    schema_ids: Dict[str, str] = {}
    for path in iter_schema_files(schema_root):
        schema_id = first_schema_id(path)
        if not schema_id:
            violations.append("missing schema_id in {}".format(repo_rel(repo_root, path)))
            continue
        rel_path = repo_rel(repo_root, path)
        previous = schema_ids.get(schema_id)
        if previous and previous != rel_path:
            violations.append(
                "schema_id reused: {} in {} and {}".format(schema_id, previous, rel_path)
            )
        else:
            schema_ids[schema_id] = rel_path

    # Refusal code uniqueness.
    refusal_rows = parse_refusal_block(load_text(refusal_doc))
    if not refusal_rows:
        violations.append("missing refusal-codes block in docs/architecture/REFUSAL_SEMANTICS.md")
    else:
        code_ids: Dict[int, str] = {}
        code_tokens: Dict[str, int] = {}
        for code_id, code, _meaning in refusal_rows:
            prev_code = code_ids.get(code_id)
            if prev_code and prev_code != code:
                violations.append(
                    "refusal code_id reused with different token: {} -> {} vs {}".format(
                        code_id, prev_code, code
                    )
                )
            else:
                code_ids[code_id] = code

            prev_id = code_tokens.get(code)
            if prev_id and prev_id != code_id:
                violations.append(
                    "refusal token reused with different code_id: {} -> {} vs {}".format(
                        code, prev_id, code_id
                    )
                )
            else:
                code_tokens[code] = code_id

    # Cross-class reuse detection.
    schema_id_set = set(schema_ids.keys())
    refusal_token_set = {code for _code_id, code, _meaning in refusal_rows}
    collisions = sorted(schema_id_set.intersection(refusal_token_set))
    for token in collisions:
        violations.append(
            "identifier reused across classes (schema_id and refusal token): {}".format(token)
        )

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("ID reuse detection OK. schema_ids={} refusal_codes={}".format(
        len(schema_ids), len(refusal_rows)
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
