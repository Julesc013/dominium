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


def main():
    parser = argparse.ArgumentParser(description="SLICE-2 coordination and infrastructure tests.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)

    ok = True
    root = prepare_root(temp_root, "coordination")

    base_cmd = (
        "new-world template=builtin.minimal_system seed=11 "
        "policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free"
    )
    setup_cmd = (
        "network-create id=1 type=logistics; "
        "network-node network=1 id=100 capacity=1 stored=0 min=1; "
        "network-node network=1 id=200 capacity=1 stored=0 min=1; "
        "network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0; "
        "agent-add id=1 caps=logistics resource=100 dest=200; "
        "agent-add id=2 caps=survey; "
        "goal-add agent=1 type=stabilize; "
        "goal-add agent=2 type=survey"
    )

    cmd = (
        "batch {base}; {setup}; "
        "delegate delegator=2 delegatee=1 goal=1; "
        "simulate; "
        "authority-grant granter=2 grantee=1 authority=infra; "
        "simulate; "
        "save path=data/saves/slice2.save; "
        "events"
    ).format(base=base_cmd, setup=setup_cmd)

    ok_run, out = run_cmd(
        [args.client, cmd],
        expect_contains=[
            "delegation=ok",
            "authority_grant=ok",
            "simulate=ok",
            "event=client.agent.plan",
            "reason=insufficient_authority",
            "event=client.network.fail",
            "reason=threshold",
            "world_save=ok",
        ],
        cwd=root,
    )
    ok = ok and ok_run

    if "event=client.agent.command agent_id=1" not in out:
        sys.stderr.write("FAIL: missing agent 1 command in output\n")
        sys.stderr.write(out)
        ok = False
    if "event=client.agent.command agent_id=2" not in out:
        sys.stderr.write("FAIL: missing agent 2 command in output\n")
        sys.stderr.write(out)
        ok = False

    replay_cmd = "batch inspect-replay path=data/saves/slice2.save; events"
    ok = ok and run_cmd(
        [args.client, replay_cmd],
        expect_contains=[
            "replay_inspect=ok",
            "event=client.network.fail",
            "reason=threshold",
        ],
        cwd=root,
    )[0]

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
