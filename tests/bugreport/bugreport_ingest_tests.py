import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


INGEST_CLI = os.path.join("tools", "bugreport", "ingest.py")


def run_cli(args):
    result = subprocess.run(
        [sys.executable, INGEST_CLI] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    payload = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except ValueError:
            payload = {"raw": result.stdout}
    return result.returncode, payload, result.stdout


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_ingest_success(tmp_root):
    out_root = os.path.join(tmp_root, "bugreports")
    code, payload, output = run_cli([
        "--deterministic",
        "--bugreport-id", "bugreport.sample.001",
        "--clip-path", "clips/session001.mp4",
        "--timestamp", "00:00:05-00:00:17",
        "--expected", "camera observer mode refused without entitlement",
        "--observed", "camera observer mode was accepted",
        "--build-identity", "{\"product\":\"client\",\"build_kind\":\"dev\",\"gbn\":\"none\"}",
        "--capability", "ui.camera.mode.observer",
        "--pack", "org.dominium.core.units",
        "--repro-step", "launch client",
        "--repro-step", "run camera.set_mode observer",
        "--status", "open",
        "--out-root", out_root,
    ])
    require(code == 0, "ingest failed: {}".format(output))
    require(payload.get("result") == "ok", "ingest result not ok")
    created_path = payload.get("path", "")
    require(created_path.endswith("bugreport.sample.001.json"), "unexpected output path")
    require(os.path.isfile(created_path), "output file missing")

    report = load_json(created_path)
    require(report.get("schema_id") == "dominium.schema.bugreport_observation", "schema_id mismatch")
    require(report.get("schema_version") == "1.0.0", "schema_version mismatch")
    record = report.get("record", {})
    require(record.get("created_at") == "2000-01-01T00:00:00Z", "deterministic timestamp mismatch")
    require(record.get("clip_path") == "clips/session001.mp4", "clip_path mismatch")
    require(record.get("status") == "open", "status mismatch")
    require(record.get("capability_set") == ["ui.camera.mode.observer"], "capability_set mismatch")


def test_ingest_requires_media(tmp_root):
    out_root = os.path.join(tmp_root, "bugreports_missing_media")
    code, _payload, output = run_cli([
        "--deterministic",
        "--bugreport-id", "bugreport.sample.002",
        "--expected", "expected behavior",
        "--observed", "observed behavior",
        "--build-identity", "{\"product\":\"client\"}",
        "--out-root", out_root,
    ])
    require(code != 0, "ingest should fail when clip/voice is missing")
    require("clip-path or voice-note-path is required" in output, "missing media refusal message")


def main():
    parser = argparse.ArgumentParser(description="Bugreport ingest tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))

    with tempfile.TemporaryDirectory() as tmp_root:
        test_ingest_success(tmp_root)
        test_ingest_requires_media(tmp_root)

    print("bugreport_ingest_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
