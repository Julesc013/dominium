import argparse
import json
import os
import subprocess
import sys


def run_tool(repo_root, script_rel, args):
    script = os.path.join(repo_root, script_rel)
    cmd = [sys.executable, script] + args
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return json.loads(result.stdout.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Distribution maximal bundle tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    bundle_root = os.path.join("tests", "distribution", "fixtures", "packs_maximal")
    expected_ids = sorted([
        "org.dominium.core.units",
        "org.dominium.worldgen.minimal",
        "org.dominium.content.real.materials",
        "org.dominium.examples.simple_factory",
        "org.dominium.l10n.en_us",
    ])

    discover = run_tool(repo_root, "tools/distribution/pack_discover.py",
                        ["--repo-root", repo_root, "--root", bundle_root, "--format", "json"])
    pack_ids = sorted([p.get("pack_id") for p in discover.get("packs", []) if p.get("pack_id")])
    if pack_ids != expected_ids:
        print("max bundle: pack ids mismatch")
        return 1

    required_caps = [
        "cap.core.units",
        "cap.worldgen.minimal",
        "cap.content.materials.real",
        "cap.examples.simple_factory",
        "cap.l10n.en_us",
    ]
    compat = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", bundle_root, "--format", "json"] +
                      sum([["--require-capability", cap] for cap in required_caps], []))
    if not compat.get("ok"):
        print("max bundle: expected ok")
        return 1
    if compat.get("missing_capabilities"):
        print("max bundle: missing capabilities")
        return 1

    print("distribution maximal bundle OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
