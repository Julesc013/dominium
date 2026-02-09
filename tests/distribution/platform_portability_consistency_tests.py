import argparse
import json
import os
import subprocess
import sys
import tempfile


CANONICAL_PLATFORM_IDS = {
    "winnt",
    "win9x",
    "win16",
    "dos",
    "macosx",
    "macclassic",
    "linux",
    "android",
    "ios",
    "web",
}
FORBIDDEN_ALIASES = {"win", "windows", "mac", "osx"}


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _run_json(repo_root, cwd, rel_script, args):
    script = os.path.join(repo_root, rel_script)
    cmd = [sys.executable, script] + args
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        check=False,
    )
    payload = {}
    text = proc.stdout.strip()
    if text:
        payload = json.loads(text)
    return proc.returncode, payload, proc.stderr.strip()


def _run_plain(repo_root, cwd, rel_script, args):
    script = os.path.join(repo_root, rel_script)
    cmd = [sys.executable, script] + args
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        check=False,
    )


def _check_platform_registry(repo_root):
    path = os.path.join(repo_root, "data", "registries", "platform_registry.json")
    payload = _load_json(path)
    record = payload.get("record", {})
    entries = record.get("platforms", [])
    platforms = set()
    for entry in entries:
        platform = str(entry.get("platform", "")).strip()
        if not platform:
            continue
        if platform in FORBIDDEN_ALIASES:
            raise AssertionError("forbidden platform alias in registry: {}".format(platform))
        if platform not in CANONICAL_PLATFORM_IDS:
            raise AssertionError("non-canonical platform in registry: {}".format(platform))
        platforms.add(platform)
    missing = sorted(CANONICAL_PLATFORM_IDS - platforms)
    if missing:
        raise AssertionError("missing canonical platform declarations: {}".format(", ".join(missing)))


def _check_dist_aliases(repo_root):
    roots = [
        os.path.join(repo_root, "dist", "pkg"),
        os.path.join(repo_root, "dist", "sys"),
        os.path.join(repo_root, "dist", "sym"),
        os.path.join(repo_root, "dist", "meta"),
        os.path.join(repo_root, "dist", "wrap"),
        os.path.join(repo_root, "dist", "redist"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            abs_path = os.path.join(root, name)
            if not os.path.isdir(abs_path):
                continue
            name_norm = name.strip().lower()
            if name_norm in FORBIDDEN_ALIASES:
                rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                raise AssertionError("forbidden dist platform alias directory: {}".format(rel))


def _check_portable_help(repo_root):
    with tempfile.TemporaryDirectory(prefix="dominium_portable_cwd_") as work:
        setup_help = _run_plain(repo_root, work, os.path.join("tools", "setup", "setup_cli.py"), ["--help"])
        if setup_help.returncode != 0:
            raise AssertionError("setup --help failed from random cwd")
        launcher_help = _run_plain(repo_root, work, os.path.join("tools", "launcher", "launcher_cli.py"), ["--help"])
        if launcher_help.returncode != 0:
            raise AssertionError("launcher --help failed from random cwd")


def _check_refusal_codes(repo_root):
    with tempfile.TemporaryDirectory(prefix="dominium_portable_refusal_") as work:
        rc, payload, _stderr = _run_json(
            repo_root,
            work,
            os.path.join("tools", "setup", "setup_cli.py"),
            ["detect"],
        )
        if rc != 3:
            raise AssertionError("setup detect without install-root must refuse")
        refusal = payload.get("refusal", {})
        if refusal.get("code") != "REFUSE_INVALID_INTENT":
            raise AssertionError("setup detect refusal code mismatch")

        rc, payload, _stderr = _run_json(
            repo_root,
            work,
            os.path.join("tools", "launcher", "launcher_cli.py"),
            [
                "--deterministic",
                "preflight",
                "--install-manifest",
                "missing.install.manifest.json",
                "--instance-manifest",
                "missing.instance.manifest.json",
            ],
        )
        if rc != 3:
            raise AssertionError("launcher preflight with missing manifests must refuse")
        refusal = payload.get("compat_report", {}).get("refusal", {})
        if refusal.get("code") != "REFUSE_INVALID_INTENT":
            raise AssertionError("launcher missing manifest refusal code mismatch")


def main():
    parser = argparse.ArgumentParser(description="Platform/canonical portability consistency tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    _check_platform_registry(repo_root)
    _check_dist_aliases(repo_root)
    _check_portable_help(repo_root)
    _check_refusal_codes(repo_root)

    print("platform portability consistency OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
