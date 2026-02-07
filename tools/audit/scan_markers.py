import os
from datetime import date


MARKERS = ("TODO", "FIXME", "PLACEHOLDER")
STUB_TOKEN = "_stub"


def should_skip_dir(rel_path):
    parts = rel_path.split(os.sep)
    if parts[0] in {".git", ".vs", "build", "out", "dist", "tmp", "updates"}:
        return True
    if rel_path.startswith(os.path.join("docs", "archive")):
        return True
    return False


def is_historical_doc(path):
    norm = path.replace("\\", "/")
    if not norm.startswith("docs/"):
        return False
    if not norm.lower().endswith((".md", ".txt")):
        return False
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
                if line.lower().startswith("status:"):
                    return line.split(":", 1)[1].strip().lower() == "historical"
    except OSError:
        return False
    return False


def scan_file(path):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                up = line.upper()
                for marker in MARKERS:
                    if marker in up:
                        low = line.lower()
                        if "docs/archive/" in low or "docs\\archive\\" in low:
                            continue
                        findings.append((marker, i, line.rstrip()))
    except OSError:
        pass
    return findings


def main():
    root = "."
    stub_files = []
    marker_hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            rel = ""
        if rel and should_skip_dir(rel):
            dirnames[:] = []
            continue
        for name in filenames:
            path = os.path.join(rel, name) if rel else name
            if STUB_TOKEN in name:
                stub_files.append(path.replace("\\", "/"))
            if not name.lower().endswith((".c", ".cpp", ".h", ".md", ".py", ".txt")):
                continue
            if is_historical_doc(path):
                continue
            for marker, line_no, line in scan_file(path):
                marker_hits.append(
                    {
                        "path": path.replace("\\", "/"),
                        "marker": marker,
                        "line": line_no,
                        "text": line,
                    }
                )

    os.makedirs("docs/audit", exist_ok=True)
    with open("docs/audit/MARKER_SCAN.txt", "w", encoding="utf-8") as f:
        f.write("Status: DERIVED\n")
        f.write("Last Reviewed: {}\n".format(date.today().isoformat()))
        f.write("Supersedes: none\n")
        f.write("Superseded By: none\n\n")
        f.write(
            "Note: This document may reference archived or historical files\n"
            "for descriptive purposes only. Such references do not confer\n"
            "authority and are not normative.\n\n"
        )
        f.write("STUB FILES\n")
        for p in sorted(stub_files):
            f.write(p + "\n")
        f.write("\nMARKERS\n")
        for hit in marker_hits:
            f.write(
                "{path}:{line} [{marker}] {text}\n".format(**hit)
            )


if __name__ == "__main__":
    main()
