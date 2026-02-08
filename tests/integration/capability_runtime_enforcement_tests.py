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


def create_world(client_path, repo_root, data_root, env, seed, save_rel, debug_csv, interaction_csv, camera_csv):
    command = (
        "create-world template=world.template.exploration_baseline seed={} path={} "
        "policy.debug={} policy.interaction={} policy.camera={}"
    ).format(seed, save_rel, debug_csv, interaction_csv, camera_csv)
    return run_cmd([client_path, command], cwd=data_root, env=env)


def main():
    parser = argparse.ArgumentParser(description="Runtime capability/entitlement enforcement checks.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    client_path = os.path.abspath(args.client)
    temp_root = os.path.abspath(args.temp_root)
    repo_root = os.path.abspath(args.repo_root)
    data_root = os.path.join(temp_root, "data")
    saves_dir = os.path.join(data_root, "saves")
    replays_dir = os.path.join(data_root, "replays")

    ok = True
    ok = ok and require(os.path.isfile(client_path), "client binary missing")
    if not ok:
        return 1

    ensure_clean_dir(data_root)
    os.makedirs(saves_dir, exist_ok=True)
    os.makedirs(replays_dir, exist_ok=True)

    env = dict(os.environ)
    env["DOM_DATA_ROOT"] = data_root
    env["DOM_INSTANCE_ROOT"] = data_root
    env["DOM_INSTALL_ROOT"] = repo_root

    full_camera_policy = "camera.first_person,camera.third_person,camera.free,camera.memory,camera.observer"
    limited_camera_policy = "camera.first_person,camera.third_person,camera.free,camera.observer"

    no_caps_save = os.path.join("saves", "caps_none.save")
    ok, out = create_world(
        client_path,
        repo_root,
        data_root,
        env,
        301,
        no_caps_save,
        "",
        "policy.interaction.remove",
        full_camera_policy,
    )
    ok = ok and require(ok, "create-world without capabilities failed")
    if not ok:
        sys.stderr.write(out)
        return 1

    memory_save = os.path.join("saves", "caps_no_memory.save")
    ok, out = create_world(
        client_path,
        repo_root,
        data_root,
        env,
        303,
        memory_save,
        "",
        "policy.interaction.place",
        limited_camera_policy,
    )
    ok = ok and require(ok, "create-world without memory camera capability failed")
    if not ok:
        sys.stderr.write(out)
        return 1

    ok, observer_refuse_a = run_cmd(
        [client_path, "batch load path={}; camera.set_mode observer; refusal".format(no_caps_save)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "observer refusal command failed")
    ok = ok and require("refusal_code=WD-REFUSAL-SCHEMA" in observer_refuse_a, "observer refusal missing schema code")
    ok = ok and require("CAMERA_REFUSE_ENTITLEMENT" in observer_refuse_a, "observer refusal missing entitlement detail")
    if not ok:
        return 1

    ok, observer_refuse_b = run_cmd(
        [client_path, "batch load path={}; camera.set_mode observer; refusal".format(no_caps_save)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "observer refusal repeat command failed")
    ok = ok and require(observer_refuse_a == observer_refuse_b, "observer entitlement refusal is non-deterministic")
    if not ok:
        return 1

    ok, memory_allow_a = run_cmd(
        [client_path, "batch load path={}; camera.set_mode memory; refusal".format(no_caps_save)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "memory capability allow command failed")
    ok = ok and require("camera_set=ok" in memory_allow_a, "memory mode was not accepted when capability is present")
    ok = ok and require("CAMERA_REFUSE_POLICY" not in memory_allow_a, "memory mode unexpectedly refused by capability policy")
    if not ok:
        return 1

    ok, memory_allow_b = run_cmd(
        [client_path, "batch load path={}; camera.set_mode memory; refusal".format(no_caps_save)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "memory capability allow repeat command failed")
    ok = ok and require(memory_allow_a == memory_allow_b, "memory capability allow path is non-deterministic")
    if not ok:
        return 1

    ok, memory_refuse_out = run_cmd(
        [client_path, "batch load path={}; camera.set_mode memory; refusal".format(memory_save)],
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "memory capability refusal command failed")
    ok = ok and require("CAMERA_REFUSE_POLICY" in memory_refuse_out, "memory mode refusal did not use capability policy code")
    if not ok:
        return 1

    blueprint_cmd = [client_path, "batch load path={}; blueprint.preview type=org.dominium.unknown; refusal".format(no_caps_save)]
    ok, blueprint_refuse_a = run_cmd(
        blueprint_cmd,
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "blueprint refusal command failed")
    ok = ok and require("refusal_code=WD-REFUSAL-SCHEMA" in blueprint_refuse_a, "blueprint refusal missing schema code")
    ok = ok and require(
        ("BLUEPRINT_REFUSE_CAPABILITY" in blueprint_refuse_a) or ("interaction place blocked" in blueprint_refuse_a),
        "blueprint refusal missing expected detail",
    )
    if not ok:
        sys.stderr.write(blueprint_refuse_a)
        return 1

    ok, blueprint_refuse_b = run_cmd(
        blueprint_cmd,
        cwd=data_root,
        env=env,
    )
    ok = ok and require(ok, "blueprint refusal repeat command failed")
    ok = ok and require(blueprint_refuse_a == blueprint_refuse_b, "blueprint refusal path is non-deterministic")
    if not ok:
        return 1

    print("capability_runtime_enforcement=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
