import argparse
import json
import os
import subprocess
import sys


PREALPHA_PACK_IDS = (
    "org.dominium.content.worldgen.placeholder",
    "org.dominium.content.terrain.placeholder",
    "org.dominium.content.institutions.placeholder",
    "org.dominium.content.resources.placeholder",
)

RUNTIME_ROOTS = (
    "engine",
    "game",
    "client",
    "server",
    "launcher",
    "setup",
    "libs",
    "tools",
)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _run_json(repo_root, rel_script, args):
    script = os.path.join(repo_root, rel_script)
    cmd = [sys.executable, script] + args
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
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
    return proc.returncode, payload


def _check_pack_markers(repo_root):
    for pack_id in PREALPHA_PACK_IDS:
        manifest_path = os.path.join(repo_root, "data", "packs", pack_id, "pack_manifest.json")
        payload = _load_json(manifest_path)
        record = payload.get("record", {})
        tags = set([str(value) for value in (record.get("pack_tags") or [])])
        if "pack.maturity.prealpha" not in tags:
            raise AssertionError("prealpha tag missing for {}".format(pack_id))
        if "pack.stability.disposable" not in tags:
            raise AssertionError("disposable tag missing for {}".format(pack_id))
        extensions = record.get("extensions", {})
        if str(extensions.get("maturity", "")).strip() != "prealpha":
            raise AssertionError("extension maturity mismatch for {}".format(pack_id))
        if str(extensions.get("stability", "")).strip() != "disposable":
            raise AssertionError("extension stability mismatch for {}".format(pack_id))


def _check_runtime_no_pack_literals(repo_root):
    for root in RUNTIME_ROOTS:
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, _dirs, files in os.walk(abs_root):
            rel_dir = os.path.relpath(dirpath, repo_root).replace("\\", "/")
            if rel_dir.startswith("tests/"):
                continue
            for name in files:
                _, ext = os.path.splitext(name.lower())
                if ext not in (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".py"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, "r", encoding="utf-8", errors="replace") as handle:
                    text = handle.read()
                for pack_id in PREALPHA_PACK_IDS:
                    if pack_id in text:
                        rel = os.path.relpath(path, repo_root).replace("\\", "/")
                        raise AssertionError("runtime file references prealpha pack id {} in {}".format(pack_id, rel))


def _check_pack_replacement_flow(repo_root):
    cap_id = "org.dominium.content.worldgen.placeholder"
    roots = (
        os.path.join("tests", "distribution", "fixtures", "packs_prealpha_a"),
        os.path.join("tests", "distribution", "fixtures", "packs_prealpha_b"),
    )
    for root in roots:
        rc, payload = _run_json(
            repo_root,
            os.path.join("tools", "distribution", "compat_dry_run.py"),
            [
                "--repo-root",
                repo_root,
                "--root",
                root,
                "--require-capability",
                cap_id,
                "--format",
                "json",
            ],
        )
        if rc != 0 or not payload.get("ok"):
            raise AssertionError("prealpha replacement root must satisfy capability: {}".format(root))

    rc, payload = _run_json(
        repo_root,
        os.path.join("tools", "distribution", "compat_dry_run.py"),
        [
            "--repo-root",
            repo_root,
            "--root",
            os.path.join("tests", "distribution", "fixtures", "empty_root"),
            "--require-capability",
            cap_id,
            "--format",
            "json",
        ],
    )
    if rc != 2:
        raise AssertionError("missing prealpha pack capability must refuse deterministically")
    refusal = payload.get("refusal", {})
    if refusal.get("code") != "REFUSE_CAPABILITY_MISSING":
        raise AssertionError("missing prealpha pack refusal code mismatch")


def main():
    parser = argparse.ArgumentParser(description="Pre-alpha content pack policy tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    _check_pack_markers(repo_root)
    _check_runtime_no_pack_literals(repo_root)
    _check_pack_replacement_flow(repo_root)
    print("distribution prealpha pack policy OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
