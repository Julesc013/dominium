import argparse
import hashlib
import json
import os
import subprocess
import sys
import time


def _run_json(repo_root, rel_script, args):
    script = os.path.join(repo_root, rel_script)
    cmd = [sys.executable, script] + args
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
        check=False,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000.0)
    payload = {}
    text = proc.stdout.strip()
    if text:
        payload = json.loads(text)
    return proc.returncode, payload, elapsed_ms


def _digest_payload(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Distribution determinism and performance baseline tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    lockfile_a = os.path.join("tests", "distribution", "fixtures", "lockfiles", "lockfile_a.json")
    lockfile_b = os.path.join("tests", "distribution", "fixtures", "lockfiles", "lockfile_b.json")
    rc_a, out_a, ms_a = _run_json(
        repo_root,
        os.path.join("tools", "distribution", "lockfile_inspect.py"),
        ["--input", lockfile_a, "--format", "json"],
    )
    rc_b, out_b, ms_b = _run_json(
        repo_root,
        os.path.join("tools", "distribution", "lockfile_inspect.py"),
        ["--input", lockfile_b, "--format", "json"],
    )
    if rc_a != 0 or rc_b != 0:
        print("determinism baseline: lockfile inspection failed")
        return 1
    if out_a != out_b:
        print("determinism baseline: lockfile output mismatch")
        return 1

    caps = [
        "cap.core.units",
        "cap.worldgen.minimal",
        "cap.content.materials.real",
        "cap.examples.simple_factory",
        "cap.l10n.en_us",
    ]
    args_order_a = ["--repo-root", repo_root, "--root", os.path.join("tests", "distribution", "fixtures", "packs_maximal"), "--format", "json"]
    for cap_id in caps:
        args_order_a += ["--require-capability", cap_id]
    rc_ca, out_ca, ms_ca = _run_json(repo_root, os.path.join("tools", "distribution", "compat_dry_run.py"), args_order_a)
    if rc_ca != 0 or not out_ca.get("ok"):
        print("determinism baseline: capability order A failed")
        return 1

    args_order_b = ["--repo-root", repo_root, "--root", os.path.join("tests", "distribution", "fixtures", "packs_maximal"), "--format", "json"]
    for cap_id in reversed(caps):
        args_order_b += ["--require-capability", cap_id]
    rc_cb, out_cb, ms_cb = _run_json(repo_root, os.path.join("tools", "distribution", "compat_dry_run.py"), args_order_b)
    if rc_cb != 0 or not out_cb.get("ok"):
        print("determinism baseline: capability order B failed")
        return 1
    if _digest_payload(out_ca) != _digest_payload(out_cb):
        print("determinism baseline: capability order digest mismatch")
        return 1

    perf_out = {
        "result": "ok",
        "probes": {
            "lockfile_inspect_a_ms": ms_a,
            "lockfile_inspect_b_ms": ms_b,
            "compat_order_a_ms": ms_ca,
            "compat_order_b_ms": ms_cb,
        },
        "determinism": {
            "lockfile_digest": _digest_payload(out_a),
            "compat_digest": _digest_payload(out_ca),
        },
    }
    perf_dir = os.path.join(repo_root, "tmp", "perf")
    os.makedirs(perf_dir, exist_ok=True)
    perf_path = os.path.join(perf_dir, "distribution_baseline.json")
    with open(perf_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(perf_out, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("distribution determinism/performance baseline OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
