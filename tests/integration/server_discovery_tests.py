import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, env=None, cwd=None, expect_code=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env,
        cwd=cwd,
    )
    output = result.stdout or ""
    if expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    return True, output


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Server discovery provider determinism and refusal checks.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    data_root = os.path.join(temp_root, "data")
    ensure_clean_dir(data_root)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root

    ok = True

    ok_a, out_a = run_cmd([client_path, "client.server.connect"], env=env, expect_code=3)
    ok_b, out_b = run_cmd([client_path, "client.server.connect"], env=env, expect_code=3)
    ok = ok and ok_a and ok_b
    ok = ok and require("REFUSE_CAPABILITY_MISSING" in out_a, "connect without capabilities must refuse by capability")
    ok = ok and require(out_a == out_b, "connect refusal must be deterministic")

    obs_env = dict(env)
    obs_env["DOM_CLIENT_CAPABILITIES"] = "tool.observation.stream"

    ok_c, out_c = run_cmd([client_path, "client.server.list"], env=obs_env, expect_code=3)
    ok_d, out_d = run_cmd([client_path, "client.server.list"], env=obs_env, expect_code=3)
    ok = ok and ok_c and ok_d
    ok = ok and require("REFUSE_UNAVAILABLE" in out_c, "provider-backed list should refuse with unavailable code")
    ok = ok and require(out_c == out_d, "list refusal must be deterministic")

    if not ok:
        return 1
    print("server_discovery=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
