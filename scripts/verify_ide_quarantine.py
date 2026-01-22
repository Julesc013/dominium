import argparse
import fnmatch
import os
import sys

IDE_FILE_EXTS = {
    ".sln",
    ".vcxproj",
    ".vcproj",
    ".dsp",
    ".dsw",
    ".pbxproj",
    ".mcp",
}
IDE_DIR_SUFFIXES = {
    ".xcodeproj",
    ".xcworkspace",
}
STATE_DIR_NAMES = {
    ".vs",
    "DerivedData",
    ".xcuserdata",
    ".xcuserdatad",
}
STATE_FILE_PATTERNS = [
    "*.suo",
    "*.user",
    "*.opensdf",
    "*.sdf",
    "*.VC.db",
    "*.VC.VC.opendb",
    "*.sln.docstates",
]


def norm_rel(path, root):
    rel = os.path.relpath(path, root)
    return rel.replace("\\", "/")


def is_allowed_projection_path(rel_path):
    rel_path = rel_path.replace("\\", "/")
    if rel_path.startswith("ide/"):
        return True
    allow_patterns = [
        "setup/**/package/**/vs/**",
        "setup/**/xcode/**",
    ]
    for pattern in allow_patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def is_allowed_state_path(rel_path):
    rel_path = rel_path.replace("\\", "/")
    if rel_path.startswith("ide/"):
        return True
    if "/" not in rel_path:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Verify IDE file quarantine rules.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations = []

    for root, dirs, files in os.walk(repo_root):
        if os.path.basename(root) == ".git":
            dirs[:] = []
            continue

        rel_root = norm_rel(root, repo_root)
        for d in list(dirs):
            rel_dir = norm_rel(os.path.join(root, d), repo_root)
            if d in STATE_DIR_NAMES:
                if d == ".vs":
                    if rel_dir != ".vs" and not rel_dir.startswith("ide/"):
                        violations.append((rel_dir, "IDE state dir outside root or /ide"))
                else:
                    if not rel_dir.startswith("ide/"):
                        violations.append((rel_dir, "IDE state dir outside /ide"))
                continue
            for suffix in IDE_DIR_SUFFIXES:
                if d.endswith(suffix):
                    if not is_allowed_projection_path(rel_dir):
                        violations.append((rel_dir, "IDE project dir outside /ide or packaging inputs"))
                    break

        for f in files:
            rel_file = norm_rel(os.path.join(root, f), repo_root)
            _, ext = os.path.splitext(f)
            if ext in IDE_FILE_EXTS:
                if not is_allowed_projection_path(rel_file):
                    violations.append((rel_file, "IDE project file outside /ide or packaging inputs"))
                continue
            if any(fnmatch.fnmatch(f, pat) for pat in STATE_FILE_PATTERNS):
                if not is_allowed_state_path(rel_file):
                    violations.append((rel_file, "IDE state file outside root or /ide"))
                continue
            if f == "project.pbxproj":
                if not is_allowed_projection_path(rel_file):
                    violations.append((rel_file, "Xcode project file outside /ide or packaging inputs"))

    if violations:
        for path, msg in violations:
            sys.stderr.write(f"{path}:1: {msg}\n")
        return 1

    print("IDE quarantine OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
