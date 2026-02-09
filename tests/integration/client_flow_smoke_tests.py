import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, cwd=None, env=None, expect_code=0):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        cwd=cwd,
        env=env,
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
    parser = argparse.ArgumentParser(description="Client flow smoke checks for canonical command bridge.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    data_root = os.path.join(temp_root, "data")
    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root

    ok = True
    ensure_clean_dir(data_root)
    os.makedirs(os.path.join(data_root, "saves"), exist_ok=True)
    os.makedirs(os.path.join(data_root, "replays"), exist_ok=True)

    ok_help, out_help = run_cmd([client_path, "--help"], env=env)
    ok = ok and ok_help
    ok = ok and require("commands:" in out_help, "help missing commands section")
    ok = ok and require("client.*" in out_help, "help missing canonical client namespace hint")

    ok_boot, out_boot = run_cmd([client_path, "client.boot.start"], env=env)
    ok = ok and ok_boot
    ok = ok and require("result=ok command=client.boot.start" in out_boot, "boot start synthetic path missing")

    ok_menu, out_menu = run_cmd([client_path, "client.menu.open"], env=env)
    ok = ok and ok_menu
    ok = ok and require("result=ok command=client.menu.open" in out_menu, "menu open synthetic path missing")

    ok_about, out_about = run_cmd([client_path, "client.about.show"], env=env)
    ok = ok and ok_about
    ok = ok and require("result=ok command=client.about.show" in out_about, "about synthetic path missing")

    ok_multi, out_multi = run_cmd(
        [client_path, "client.menu.select.multiplayer"],
        env=env,
        expect_code=3,
    )
    ok = ok and ok_multi
    ok = ok and require("REFUSE_CAPABILITY_MISSING" in out_multi, "multiplayer refusal must be capability-gated")

    ok_opts, out_opts = run_cmd([client_path, "client.options.get"], env=env)
    ok = ok and ok_opts
    ok = ok and require("client_settings=ok" in out_opts, "options get must bridge to settings")

    obs_env = dict(env)
    obs_env["DOM_CLIENT_CAPABILITIES"] = "tool.observation.stream"
    ok_srv, out_srv = run_cmd([client_path, "client.server.list"], env=obs_env, expect_code=3)
    ok = ok and ok_srv
    ok = ok and require("REFUSE_UNAVAILABLE" in out_srv, "server list should refuse deterministically when provider unavailable")

    if not ok:
        return 1
    print("client_flow_smoke=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
