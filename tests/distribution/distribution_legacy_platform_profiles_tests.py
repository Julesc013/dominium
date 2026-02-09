import argparse
import json
import os
import subprocess
import sys


EXPECTED_PLATFORM_TUPLES = {
    ("win9x", "x86_32", "abi:win9x:mingw-legacy"),
    ("win16", "x86_16", "abi:win16:watcom-16"),
    ("dos", "x86_16", "abi:dos:watcom"),
    ("dos", "x86_32", "abi:dos:djgpp"),
}

LEGACY_PROFILE_FILES = (
    "profile.runtime_min.win9x.json",
    "profile.runtime_min.win16.json",
    "profile.runtime_min.dos.json",
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


def _check_platform_registry(repo_root):
    path = os.path.join(repo_root, "data", "registries", "platform_registry.json")
    payload = _load_json(path)
    record = payload.get("record", {})
    entries = record.get("platforms", [])
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = (
            str(entry.get("platform", "")).strip(),
            str(entry.get("arch", "")).strip(),
            str(entry.get("abi_id", "")).strip(),
        )
        if key in EXPECTED_PLATFORM_TUPLES:
            seen.add(key)
            extensions = entry.get("extensions", {})
            compression = (extensions.get("compression_support") or {}).get("required") or []
            if "deflate" not in compression:
                raise AssertionError("legacy platform tuple missing deflate requirement: {}".format("/".join(key)))
            modes = extensions.get("supported_modes") or []
            mode_set = sorted(set([str(v) for v in modes]))
            if mode_set != ["cli", "tui"]:
                raise AssertionError("legacy platform tuple must declare cli/tui support: {}".format("/".join(key)))
            if str(extensions.get("support_status", "")).strip() != "declared_not_built":
                raise AssertionError("legacy platform tuple missing declared_not_built status: {}".format("/".join(key)))
    missing = sorted(["{}/{}/{}".format(*item) for item in EXPECTED_PLATFORM_TUPLES - seen])
    if missing:
        raise AssertionError("missing legacy platform tuples: {}".format(", ".join(missing)))


def _check_legacy_profiles(repo_root):
    profile_dir = os.path.join(repo_root, "data", "profiles")
    empty_root = os.path.join("tests", "distribution", "fixtures", "empty_root")
    for filename in LEGACY_PROFILE_FILES:
        path = os.path.join(profile_dir, filename)
        payload = _load_json(path)
        if payload.get("schema_id") != "dominium.schema.distribution.profile":
            raise AssertionError("legacy profile schema mismatch: {}".format(filename))
        record = payload.get("record", {})
        profile_id = str(record.get("profile_id", "")).strip()
        if ".runtime_min." not in profile_id:
            raise AssertionError("unexpected legacy profile id {}".format(profile_id))
        required_caps = []
        for entry in record.get("requires_capabilities") or []:
            if isinstance(entry, dict):
                cap_id = entry.get("capability_id")
                if isinstance(cap_id, str):
                    required_caps.append(cap_id)
        cmd_args = ["--repo-root", repo_root, "--root", empty_root, "--format", "json"]
        for cap_id in required_caps:
            cmd_args += ["--require-capability", cap_id]
        rc, out = _run_json(repo_root, os.path.join("tools", "distribution", "compat_dry_run.py"), cmd_args)
        if rc != 2:
            raise AssertionError("legacy profile compatibility refusal must be deterministic for {}".format(filename))
        refusal = out.get("refusal", {})
        if refusal.get("code") != "REFUSE_CAPABILITY_MISSING":
            raise AssertionError("legacy profile refusal code mismatch for {}".format(filename))


def _check_stub_manifests(repo_root):
    root = os.path.join(repo_root, "tests", "distribution", "fixtures", "legacy_platform_pkg_manifests")
    expected = ("win9x_runtime_stub.pkg_manifest.json", "win16_runtime_stub.pkg_manifest.json", "dos_runtime_stub.pkg_manifest.json")
    for name in expected:
        payload = _load_json(os.path.join(root, name))
        extensions = payload.get("extensions", {})
        if extensions.get("install_scope") != "optional":
            raise AssertionError("legacy stub install_scope must be optional: {}".format(name))
        refusal_codes = extensions.get("refusal_codes") or []
        if "REFUSE_PLATFORM_UNSUPPORTED" not in refusal_codes:
            raise AssertionError("legacy stub refusal code missing: {}".format(name))


def main():
    parser = argparse.ArgumentParser(description="Legacy platform profile and refusal tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    _check_platform_registry(repo_root)
    _check_legacy_profiles(repo_root)
    _check_stub_manifests(repo_root)
    print("distribution legacy platform profiles OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
