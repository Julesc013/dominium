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
    parser = argparse.ArgumentParser(description="Blueprint refusal determinism checks.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    repo_root = os.path.abspath(args.repo_root)
    data_root = os.path.join(temp_root, "data")
    saves_dir = os.path.join(data_root, "saves")

    ok = True
    ok = ok and require(os.path.isfile(client_path), "client binary missing")
    if not ok:
        return 1

    ensure_clean_dir(data_root)
    os.makedirs(saves_dir, exist_ok=True)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root
    env["DOM_INSTALL_ROOT"] = repo_root

    ok, out = run_cmd(
        [client_path, "create-world template=world.template.exploration_baseline seed=43 policy.debug="],
        cwd=repo_root,
        env=env,
    )
    if not ok:
        sys.stderr.write(out)
        return 1

    save_files = [name for name in os.listdir(saves_dir) if name.endswith(".save")]
    ok = require(bool(save_files), "create-world produced no save")
    if not ok:
        return 1

    canonical_save = os.path.join(saves_dir, "world.save")
    shutil.copy2(os.path.join(saves_dir, save_files[0]), canonical_save)
    save_rel = os.path.join("saves", "world.save")

    preview_cmd = [client_path, "batch load path={}; blueprint.preview type=org.dominium.unknown; refusal".format(save_rel)]
    place_cmd = [client_path, "batch load path={}; blueprint.place type=org.dominium.unknown; refusal".format(save_rel)]

    ok, preview_out_a = run_cmd(preview_cmd, cwd=data_root, env=env)
    ok = ok and require(ok, "blueprint.preview refusal command failed")
    ok, preview_out_b = run_cmd(preview_cmd, cwd=data_root, env=env)
    ok = ok and require(ok, "blueprint.preview refusal repeat failed")
    ok = ok and require(preview_out_a == preview_out_b, "blueprint.preview refusal is non-deterministic")
    ok = ok and require("refusal_code=" in preview_out_a, "blueprint.preview refusal_code missing")
    ok = ok and require("refusal_detail=" in preview_out_a, "blueprint.preview refusal_detail missing")
    ok = ok and require("refusal_code=none" not in preview_out_a, "blueprint.preview refusal_code must not be none")

    ok, place_out_a = run_cmd(place_cmd, cwd=data_root, env=env)
    ok = ok and require(ok, "blueprint.place refusal command failed")
    ok, place_out_b = run_cmd(place_cmd, cwd=data_root, env=env)
    ok = ok and require(ok, "blueprint.place refusal repeat failed")
    ok = ok and require(place_out_a == place_out_b, "blueprint.place refusal is non-deterministic")
    ok = ok and require("refusal_code=" in place_out_a, "blueprint.place refusal_code missing")
    ok = ok and require("refusal_detail=" in place_out_a, "blueprint.place refusal_detail missing")
    ok = ok and require("refusal_code=none" not in place_out_a, "blueprint.place refusal_code must not be none")

    if not ok:
        return 1

    print("blueprint_refusal=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
