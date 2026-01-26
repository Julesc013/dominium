import argparse
import os
import shutil
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_contains=None, cwd=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        cwd=cwd,
    )
    output = result.stdout
    ok = True
    if expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        ok = False
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                ok = False
                break
    return ok, output


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def prepare_root(base, name):
    root = os.path.join(base, name)
    ensure_clean_dir(root)
    os.makedirs(os.path.join(root, "data", "saves"))
    return root


def mix64(value):
    value &= 0xFFFFFFFFFFFFFFFF
    value ^= value >> 33
    value = (value * 0xFF51AFD7ED558CCD) & 0xFFFFFFFFFFFFFFFF
    value ^= value >> 33
    value = (value * 0xC4CEB9FE1A85EC53) & 0xFFFFFFFFFFFFFFFF
    value ^= value >> 33
    return value & 0xFFFFFFFFFFFFFFFF


def hash32(value):
    return mix64(value) & 0xFFFFFFFF


def pick_seed(kind):
    intent_id = 1
    for seed in range(1, 2048):
        rng_seed = mix64(seed ^ intent_id)
        roll = hash32(rng_seed ^ kind) & 0xFFFF
        if roll > 0:
            return seed
    return 1


def main():
    parser = argparse.ArgumentParser(description="SLICE-1 local physical interaction tests.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True

    seed = pick_seed(kind=2)
    base_cmd = (
        "new-world template=builtin.minimal_system seed={seed} "
        "policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free"
    ).format(seed=seed)
    fields_cmd = (
        "field-set field=support_capacity value=2;"
        "field-set field=surface_gradient value=1;"
        "field-set field=local_moisture value=2;"
        "field-set field=accessibility_cost value=0"
    )

    # Acting without survey should fail epistemically.
    cmd = "batch {base}; {fields}; collect".format(base=base_cmd, fields=fields_cmd)
    ok = ok and run_cmd(
        [args.client, cmd],
        expect_contains=["process=failed", "reason=epistemic"],
    )[0]

    # Survey refines subjective knowledge (before vs after).
    cmd = "batch {base}; {fields}; fields".format(base=base_cmd, fields=fields_cmd)
    ok_fields_before, out_before = run_cmd([args.client, cmd], expect_contains=["fields="])
    ok = ok and ok_fields_before
    if "subjective=unknown" not in out_before:
        sys.stderr.write("FAIL: expected subjective=unknown before survey\n")
        sys.stderr.write(out_before)
        ok = False

    cmd = "batch {base}; {fields}; survey; fields".format(base=base_cmd, fields=fields_cmd)
    ok_fields_after, out_after = run_cmd(
        [args.client, cmd],
        expect_contains=["process=ok process=survey_local_area", "fields="],
    )
    ok = ok and ok_fields_after
    if "subjective=unknown" in out_after:
        sys.stderr.write("FAIL: expected subjective values after survey\n")
        sys.stderr.write(out_after)
        ok = False
    if "known=1" not in out_after:
        sys.stderr.write("FAIL: expected known fields after survey\n")
        sys.stderr.write(out_after)
        ok = False

    # Collect succeeds after survey with sufficient fields.
    cmd = "batch {base}; {fields}; survey; collect".format(base=base_cmd, fields=fields_cmd)
    ok = ok and run_cmd(
        [args.client, cmd],
        expect_contains=["process=ok process=collect_local_material"],
    )[0]

    # Failure is causal and explainable; replay preserves events.
    fail_root = prepare_root(temp_root, "failure")
    fail_cmd = (
        "batch {base}; "
        "field-set field=support_capacity value=0.5;"
        "field-set field=surface_gradient value=1;"
        "field-set field=local_moisture value=2;"
        "field-set field=accessibility_cost value=0;"
        "survey; assemble; save path=data/saves/world.save"
    ).format(base=base_cmd)
    ok = ok and run_cmd(
        [args.client, fail_cmd],
        expect_contains=["process=failed", "reason=capacity", "save=ok"],
        cwd=fail_root,
    )[0]

    replay_cmd = "batch inspect-replay path=data/saves/world.save; events"
    ok = ok and run_cmd(
        [args.client, replay_cmd],
        expect_contains=["replay_inspect=ok", "client.process", "reason=capacity"],
        cwd=fail_root,
    )[0]

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
