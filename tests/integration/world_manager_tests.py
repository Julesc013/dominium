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
    parser = argparse.ArgumentParser(description="Canonical world manager bridge tests.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    data_root = os.path.join(temp_root, "data")
    saves_dir = os.path.join(data_root, "saves")
    ensure_clean_dir(data_root)
    os.makedirs(saves_dir, exist_ok=True)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root

    cap_env = dict(env)
    cap_env["DOM_CLIENT_CAPABILITIES"] = "ui.blueprint.place"

    ok = True

    create_cmd = (
        "client.world.create template=builtin.minimal_system seed=777 "
        "path=saves/world_manager_bridge.save"
    )
    ok_create, out_create = run_cmd([client_path, create_cmd], env=cap_env, cwd=data_root, expect_code=0)
    ok = ok and ok_create
    ok = ok and require("world_create=ok" in out_create, "world create bridge did not succeed")
    ok = ok and require("world_save=ok" in out_create, "world create bridge did not save")

    ok_inspect, out_inspect = run_cmd([client_path, "client.world.inspect"], env=cap_env, cwd=data_root, expect_code=0)
    ok = ok and ok_inspect
    ok = ok and require("world_status" in out_inspect or "world=" in out_inspect, "world inspect bridge output missing")

    no_cap_env = dict(env)
    ok_modify, out_modify = run_cmd([client_path, "client.world.modify"], env=no_cap_env, cwd=data_root, expect_code=3)
    ok = ok and ok_modify
    ok = ok and require("REFUSE_CAPABILITY_MISSING" in out_modify, "world.modify must enforce capability")

    ok_delete, out_delete = run_cmd([client_path, "client.world.delete"], env=no_cap_env, cwd=data_root, expect_code=3)
    ok = ok and ok_delete
    ok = ok and require("REFUSE_CAPABILITY_MISSING" in out_delete, "world.delete must enforce capability")

    if not ok:
        return 1
    print("world_manager=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
