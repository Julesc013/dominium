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
    parser = argparse.ArgumentParser(description="CONTENTLIB fixture scenario tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    fixtures_root = os.path.join("tests", "fixtures", "contentlib")
    empty_root = os.path.join(fixtures_root, "empty_root")
    core_units_root = os.path.join(fixtures_root, "core_units")
    core_all_root = os.path.join(fixtures_root, "core_all")

    # No packs installed.
    discover_empty = run_tool(repo_root, "tools/distribution/pack_discover.py",
                              ["--repo-root", repo_root, "--root", empty_root, "--format", "json"])
    if discover_empty.get("packs"):
        print("fixture empty: expected no packs")
        return 1
    compat_empty = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                            ["--repo-root", repo_root, "--root", empty_root, "--format", "json"])
    if not compat_empty.get("ok"):
        print("fixture empty: expected ok")
        return 1

    # Only core.units.
    discover_units = run_tool(repo_root, "tools/distribution/pack_discover.py",
                              ["--repo-root", repo_root, "--root", core_units_root, "--format", "json"])
    pack_ids = sorted([p.get("pack_id") for p in discover_units.get("packs", []) if p.get("pack_id")])
    if pack_ids != ["org.dominium.core.units"]:
        print("fixture core_units: unexpected pack list")
        return 1
    compat_units = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                            ["--repo-root", repo_root, "--root", core_units_root,
                             "--require-capability", "org.dominium.core.units",
                             "--format", "json"])
    if not compat_units.get("ok"):
        print("fixture core_units: expected ok")
        return 1
    compat_missing = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                              ["--repo-root", repo_root, "--root", core_units_root,
                               "--require-capability", "org.dominium.core.parts",
                               "--format", "json"])
    refusal = compat_missing.get("refusal", {})
    if compat_missing.get("ok") or refusal.get("code") != "REFUSE_CAPABILITY_MISSING":
        print("fixture core_units: expected capability refusal")
        return 1

    # All core.* packs.
    discover_all = run_tool(repo_root, "tools/distribution/pack_discover.py",
                            ["--repo-root", repo_root, "--root", core_all_root, "--format", "json"])
    expected_all = sorted([
        "org.dominium.core.units",
        "org.dominium.core.interfaces",
        "org.dominium.core.materials.basic",
        "org.dominium.core.parts.basic",
        "org.dominium.core.processes.basic",
        "org.dominium.core.standards.basic",
    ])
    pack_ids_all = sorted([p.get("pack_id") for p in discover_all.get("packs", []) if p.get("pack_id")])
    if pack_ids_all != expected_all:
        print("fixture core_all: unexpected pack list")
        return 1

    require_caps = [
        "org.dominium.core.units",
        "org.dominium.core.interfaces",
        "org.dominium.core.materials",
        "org.dominium.core.parts",
        "org.dominium.core.processes",
        "org.dominium.core.standards",
    ]
    compat_all = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                          ["--repo-root", repo_root, "--root", core_all_root, "--format", "json"] +
                          sum([["--require-capability", cap] for cap in require_caps], []))
    if not compat_all.get("ok") or compat_all.get("missing_capabilities"):
        print("fixture core_all: expected ok")
        return 1

    # Deterministic discovery output.
    discover_all_again = run_tool(repo_root, "tools/distribution/pack_discover.py",
                                  ["--repo-root", repo_root, "--root", core_all_root, "--format", "json"])
    if discover_all_again != discover_all:
        print("fixture core_all: discovery output not deterministic")
        return 1

    print("CONTENTLIB fixture scenarios OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
