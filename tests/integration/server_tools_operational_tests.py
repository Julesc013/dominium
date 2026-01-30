import argparse
import glob
import json
import os
import shutil
import subprocess
import sys


SERVER_LOG_HEADER = "{\"schema\":\"server_log_v1\"}"
SERVER_REPLAY_HEADER = "DOMINIUM_REPLAY_V1"


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None, env=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
    )
    output = result.stdout or ""
    if expect_nonzero:
        if result.returncode == 0:
            sys.stderr.write("FAIL: expected non-zero exit for {}\n".format(cmd))
            sys.stderr.write(output)
            return False, output
    elif expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False, output
    return True, output


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\n\r") for line in handle]


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True)
    parser.add_argument("--tools", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    server_path = os.path.abspath(args.server)
    tools_path = os.path.abspath(args.tools)
    temp_root = os.path.abspath(args.temp_root)

    ok = True
    ok = ok and require(os.path.isfile(server_path), "server binary missing")
    ok = ok and require(os.path.isfile(tools_path), "tools binary missing")
    if not ok:
        return 1

    ensure_clean_dir(temp_root)
    data_root = os.path.join(temp_root, "data_root")
    instance_id = "11111111-1111-1111-1111-111111111111"

    headless_cmd = [
        server_path,
        "--headless",
        "--data-root",
        data_root,
        "--instance-id",
        instance_id,
        "--ticks",
        "12",
        "--checkpoint-interval",
        "5",
        "--health-interval",
        "4",
        "--log-max-bytes",
        "400",
        "--log-rotate-max",
        "5",
    ]
    ok = ok and run_cmd(headless_cmd, expect_code=0)[0]

    log_path = os.path.join(data_root, "logs", "server", instance_id, "server.log")
    replay_path = os.path.join(data_root, "replays", instance_id, "server.replay")
    compat_path = os.path.join(data_root, "compat", instance_id, "compat_report.json")

    ok = ok and require(os.path.isfile(log_path), "server log missing")
    if ok:
        log_dir = os.path.dirname(log_path)
        log_files = sorted(path for path in glob.glob(os.path.join(log_dir, "server.log*"))
                           if os.path.isfile(path))
        ok = ok and require(len(log_files) > 1, "log rotation missing")
        all_lines = []
        for log_file in log_files:
            lines = read_lines(log_file)
            ok = ok and require(lines, "server log empty: {}".format(log_file))
            ok = ok and require(lines[0].strip() == SERVER_LOG_HEADER,
                                "log header mismatch: {}".format(log_file))
            all_lines.extend(lines)
        ok = ok and require(any("\"event\":\"start\"" in line for line in all_lines),
                            "log missing start event")
        ok = ok and require(any("\"event\":\"shutdown\"" in line for line in all_lines),
                            "log missing shutdown event")
        ok = ok and require(any("REFUSE_INVALID_INTENT" in line for line in all_lines),
                            "log missing health refusal")

    ok = ok and require(os.path.isfile(replay_path), "replay missing")
    if ok:
        replay_lines = read_lines(replay_path)
        ok = ok and require(replay_lines, "replay file empty")
        ok = ok and require(replay_lines[0].strip() == SERVER_REPLAY_HEADER,
                            "replay header mismatch")
        ok = ok and require(any("event=server.start" in line for line in replay_lines),
                            "replay missing start event")
        ok = ok and require(any("event=server.shutdown" in line for line in replay_lines),
                            "replay missing shutdown event")

    ok = ok and require(os.path.isfile(compat_path), "compat_report missing")
    if ok:
        with open(compat_path, "r", encoding="utf-8", errors="replace") as handle:
            payload = json.load(handle)
        required_keys = [
            "context",
            "install_id",
            "instance_id",
            "runtime_id",
            "capability_baseline",
            "required_capabilities",
            "provided_capabilities",
            "missing_capabilities",
            "compatibility_mode",
            "refusal_codes",
            "mitigation_hints",
            "timestamp",
            "extensions",
        ]
        for key in required_keys:
            ok = ok and require(key in payload, "compat_report missing {}".format(key))
        ok = ok and require(payload.get("context") == "run", "compat_report context mismatch")

    replay_cmd = [
        server_path,
        "--replay",
        replay_path,
        "--replay-step",
        "0",
        "--data-root",
        data_root,
        "--instance-id",
        instance_id,
    ]
    ok = ok and run_cmd(replay_cmd, expect_code=0,
                        expect_contains=["replay_event=", "replay_events="])[0]

    inspect_cmd = [
        server_path,
        "--inspect",
        "--format",
        "json",
        "--data-root",
        data_root,
        "--instance-id",
        instance_id,
    ]
    ok = ok and run_cmd(inspect_cmd, expect_code=0,
                        expect_contains=["\"core_info\"", "\"topology\""])[0]

    validate_cmd = [
        server_path,
        "--validate",
        "--data-root",
        data_root,
        "--instance-id",
        instance_id,
    ]
    ok = ok and run_cmd(validate_cmd, expect_code=0,
                        expect_contains=["validate_status=ok", "compat_status=ok"])[0]

    refuse_cmd = [
        server_path,
        "--validate",
        "--data-root",
        data_root,
        "--instance-id",
        instance_id,
        "--expect-engine-version=9.9.9",
    ]
    ok = ok and run_cmd(refuse_cmd, expect_nonzero=True,
                        expect_contains=["engine_version mismatch"])[0]

    tools_replay_cmd = [
        tools_path,
        "replay",
        "--input",
        replay_path,
    ]
    ok = ok and run_cmd(tools_replay_cmd, expect_code=0,
                        expect_contains=["replay_path=", "events="])[0]

    tools_inspect_cmd = [
        tools_path,
        "--format",
        "json",
        "inspect",
    ]
    ok = ok and run_cmd(tools_inspect_cmd, expect_code=0,
                        expect_contains=["\"core_info\"", "\"topology\""])[0]

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
