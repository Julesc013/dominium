import json
import os


SCENARIO_HEADER = "DOMINIUM_SCENARIO_V1"
ALLOWED_STATUSES = {"UNSUPPORTED", "PARTIAL", "COMPLETE"}


def read_text_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\r\n") for line in handle]


def first_content_line(path):
    for line in read_text_lines(path):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith(";"):
            continue
        return stripped
    return ""


def load_json(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return json.load(handle)


def parse_refusal_codes(refusal_path):
    codes = {}
    lines = read_text_lines(refusal_path)
    in_block = False
    for line in lines:
        stripped = line.strip()
        if stripped == "```refusal-codes":
            in_block = True
            continue
        if in_block and stripped == "```":
            break
        if not in_block:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        parts = [p.strip() for p in stripped.split(",", 2)]
        if len(parts) < 2:
            continue
        code_token = parts[1]
        codes[code_token] = parts[0]
    return codes


def is_reverse_dns(value):
    if not value or not isinstance(value, str):
        return False
    if not value.isascii():
        return False
    candidate = value.lower()
    if candidate != value:
        return False
    parts = candidate.split(".")
    if len(parts) < 2:
        return False
    for part in parts:
        if not part:
            return False
        if part[0] == "-" or part[-1] == "-":
            return False
        for ch in part:
            if ch.isalnum():
                continue
            if ch == "-":
                continue
            return False
    return True


def ensure_sorted(values):
    return values == sorted(values)


def ensure_unique(values):
    return len(values) == len(set(values))


def list_level_dirs(repo_root):
    base = os.path.join(repo_root, "tests", "coverage")
    return [
        ("c_a_abiotic", "C-A"),
        ("c_b_life_simple", "C-B"),
        ("c_c_animals", "C-C"),
        ("c_d_proto_culture", "C-D"),
        ("c_e_symbolic_knowledge", "C-E"),
        ("c_f_civilization", "C-F"),
        ("c_g_collapse", "C-G"),
        ("c_h_speculative", "C-H"),
    ]


def coverage_paths(repo_root, level_dir):
    base = os.path.join(repo_root, "tests", "coverage", level_dir)
    return {
        "dir": base,
        "coverage": os.path.join(base, "coverage.json"),
        "scenario": os.path.join(base, "scenario.scenario"),
        "fixtures": os.path.join(base, "fixtures"),
        "cap_present": os.path.join(base, "fixtures", "capabilities_present.json"),
        "cap_missing": os.path.join(base, "fixtures", "capabilities_missing.json"),
        "proc_present": os.path.join(base, "fixtures", "process_families_present.json"),
        "proc_missing": os.path.join(base, "fixtures", "process_families_missing.json"),
    }
