import os


MARKERS = ("TODO", "FIXME", "PLACEHOLDER")
STUB_TOKEN = "_stub"


def should_skip_dir(rel_path):
    parts = rel_path.split(os.sep)
    return parts[0] in {".git", ".vs", "build", "out", "dist", "tmp", "updates"}


def scan_file(path):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                up = line.upper()
                for marker in MARKERS:
                    if marker in up:
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
