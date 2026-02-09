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


def check_refusal(client_path, env, command, refusal_code):
    ok_a, out_a = run_cmd([client_path, command], env=env, expect_code=3)
    ok_b, out_b = run_cmd([client_path, command], env=env, expect_code=3)
    ok = ok_a and ok_b
    ok = ok and require(refusal_code in out_a, "{} missing refusal {}".format(command, refusal_code))
    ok = ok and require(out_a == out_b, "{} refusal path non-deterministic".format(command))
    return ok


def main():
    parser = argparse.ArgumentParser(description="Canonical client refusal code determinism checks.")
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
    ok = ok and check_refusal(client_path, env, "client.world.modify", "REFUSE_CAPABILITY_MISSING")
    ok = ok and check_refusal(client_path, env, "client.server.list", "REFUSE_CAPABILITY_MISSING")
    ok = ok and check_refusal(client_path, env, "client.options.network.set", "REFUSE_CAPABILITY_MISSING")
    ok = ok and check_refusal(client_path, env, "client.menu.select.multiplayer", "REFUSE_CAPABILITY_MISSING")
    ok = ok and check_refusal(client_path, env, "client.unknown.command", "REFUSE_UNAVAILABLE")

    if not ok:
        return 1
    print("client_refusal_codes=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
