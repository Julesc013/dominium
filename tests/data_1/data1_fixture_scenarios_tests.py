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


def require_ok(output, label):
    if not output.get("ok"):
        print("{}: expected ok".format(label))
        return False
    return True


def require_refusal(output, code, label):
    refusal = output.get("refusal", {})
    if output.get("ok") or refusal.get("code") != code:
        print("{}: expected refusal {}".format(label, code))
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="DATA-1 fixture scenario tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    fixtures_root = os.path.join("tests", "fixtures", "data_1")

    ok = True

    materials_only = os.path.join(fixtures_root, "materials_only")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", materials_only,
                       "--require-capability", "org.dominium.core.materials.extended",
                       "--format", "json"])
    ok = require_ok(output, "materials_only") and ok

    parts_only = os.path.join(fixtures_root, "parts_only")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", parts_only,
                       "--require-capability", "org.dominium.core.parts.extended",
                       "--format", "json"])
    ok = require_ok(output, "parts_only") and ok
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", parts_only,
                       "--require-capability", "org.dominium.core.materials.extended",
                       "--format", "json"])
    ok = require_refusal(output, "REFUSE_CAPABILITY_MISSING", "parts_only_missing_materials") and ok

    parts_with_materials = os.path.join(fixtures_root, "parts_with_materials")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", parts_with_materials,
                       "--require-capability", "org.dominium.core.parts.extended",
                       "--require-capability", "org.dominium.core.materials.extended",
                       "--format", "json"])
    ok = require_ok(output, "parts_with_materials") and ok

    processes_only = os.path.join(fixtures_root, "processes_only")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", processes_only,
                       "--require-capability", "org.dominium.core.processes.extended",
                       "--format", "json"])
    ok = require_ok(output, "processes_only") and ok
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", processes_only,
                       "--require-capability", "org.dominium.core.standards.extended",
                       "--format", "json"])
    ok = require_refusal(output, "REFUSE_CAPABILITY_MISSING", "processes_only_missing_standards") and ok

    processes_with_deps = os.path.join(fixtures_root, "processes_with_deps")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", processes_with_deps,
                       "--require-capability", "org.dominium.core.processes.extended",
                       "--require-capability", "org.dominium.core.standards.extended",
                       "--require-capability", "org.dominium.core.instruments.extended",
                       "--format", "json"])
    ok = require_ok(output, "processes_with_deps") and ok

    assemblies_only = os.path.join(fixtures_root, "assemblies_only")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", assemblies_only,
                       "--require-capability", "org.dominium.core.assemblies.extended",
                       "--format", "json"])
    ok = require_ok(output, "assemblies_only") and ok
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", assemblies_only,
                       "--require-capability", "org.dominium.core.parts.extended",
                       "--format", "json"])
    ok = require_refusal(output, "REFUSE_CAPABILITY_MISSING", "assemblies_only_missing_parts") and ok

    assemblies_with_deps = os.path.join(fixtures_root, "assemblies_with_deps")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", assemblies_with_deps,
                       "--require-capability", "org.dominium.core.assemblies.extended",
                       "--require-capability", "org.dominium.core.parts.extended",
                       "--require-capability", "org.dominium.core.processes.extended",
                       "--require-capability", "org.dominium.core.standards.extended",
                       "--require-capability", "org.dominium.core.instruments.extended",
                       "--require-capability", "org.dominium.core.materials.extended",
                       "--format", "json"])
    ok = require_ok(output, "assemblies_with_deps") and ok

    quality_only = os.path.join(fixtures_root, "quality_only")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", quality_only,
                       "--require-capability", "org.dominium.core.quality.extended",
                       "--format", "json"])
    ok = require_ok(output, "quality_only") and ok
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", quality_only,
                       "--require-capability", "org.dominium.core.processes.extended",
                       "--format", "json"])
    ok = require_refusal(output, "REFUSE_CAPABILITY_MISSING", "quality_only_missing_processes") and ok

    full_extended = os.path.join(fixtures_root, "full_extended")
    output = run_tool(repo_root, "tools/distribution/compat_dry_run.py",
                      ["--repo-root", repo_root, "--root", full_extended,
                       "--require-capability", "org.dominium.core.materials.extended",
                       "--require-capability", "org.dominium.core.parts.extended",
                       "--require-capability", "org.dominium.core.interfaces.extended",
                       "--require-capability", "org.dominium.core.assemblies.extended",
                       "--require-capability", "org.dominium.core.processes.extended",
                       "--require-capability", "org.dominium.core.quality.extended",
                       "--require-capability", "org.dominium.core.standards.extended",
                       "--require-capability", "org.dominium.core.instruments.extended",
                       "--require-capability", "org.dominium.core.hazards.extended",
                       "--format", "json"])
    ok = require_ok(output, "full_extended") and ok

    discover_a = run_tool(repo_root, "tools/distribution/pack_discover.py",
                          ["--repo-root", repo_root, "--root", full_extended, "--format", "json"])
    discover_b = run_tool(repo_root, "tools/distribution/pack_discover.py",
                          ["--repo-root", repo_root, "--root", full_extended, "--format", "json"])
    if discover_a != discover_b:
        print("full_extended: discovery output not deterministic")
        ok = False

    print("DATA-1 fixture scenarios OK." if ok else "DATA-1 fixture scenarios FAILED.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
