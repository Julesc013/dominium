import argparse
import os
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout or ""
    if expect_code is not None and result.returncode != expect_code:
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


def parse_kv(output):
    data = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="History T22 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "history")

    fixtures = [
        "founding_memory.history",
        "mythic_war.history",
        "forgotten_reform.history",
        "rediscovered_ruins.history",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "history tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "history fixtures missing")

    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, _output = run_cmd(
            [
                tool_path,
                "validate",
                "--fixture",
                fixture_path,
            ],
            expect_contains=[
                "DOMINIUM_HISTORY_VALIDATE_V1",
                "provider_chain=sources->events->epochs->nodes->edges->graphs",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "founding_memory.history")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--source",
            "history.source.archive_founding",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=source"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "source_id",
            "source_type",
            "source_event_id",
            "confidence_q16",
            "flags",
        ):
            ok = ok and require(key in data, "source inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--event",
            "history.event.founding_discovery",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=event"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "event_id",
            "event_role",
            "category",
            "source_count",
            "confidence_q16",
            "flags",
        ):
            ok = ok and require(key in data, "event inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--epoch",
            "history.epoch.settlement",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=epoch"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "epoch_id",
            "epoch_type",
            "start_tick",
            "end_tick",
        ):
            ok = ok and require(key in data, "epoch inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--graph",
            "civ.graph.primary",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=graph"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "graph_id",
            "node_count",
            "edge_count",
            "trust_weight_avg_q16",
        ):
            ok = ok and require(key in data, "graph inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--node",
            "civ.node.archive",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=node"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("institution_ref_id" in data, "node inspect missing institution_ref_id")

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--edge",
            "civ.edge.settlement_coop",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=edge"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require("edge_type" in data, "edge inspect missing edge_type")

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "history.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_INSPECT_V1", "entity=region"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "source_count",
            "event_count",
            "epoch_count",
            "graph_count",
            "node_count",
            "edge_count",
            "flags",
        ):
            ok = ok and require(key in data, "region inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "history.region.primary",
            "--tick",
            "200",
            "--delta",
            "2",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_RESOLVE_V1"],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "source_count",
            "event_count",
            "epoch_count",
            "flags",
            "ok",
            "resolve_hash",
        ):
            ok = ok and require(key in data, "resolve missing {}".format(key))
        resolve_hash = data.get("resolve_hash")

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "history.region.primary",
            "--tick",
            "200",
            "--delta",
            "2",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_RESOLVE_V1"],
    )
    ok = ok and success
    if success and resolve_hash is not None:
        repeat_hash = parse_kv(output).get("resolve_hash")
        ok = ok and require(repeat_hash == resolve_hash, "determinism hash mismatch")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            base_fixture,
            "--region",
            "history.region.primary",
        ],
        expect_contains=["DOMINIUM_HISTORY_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    flag_forgotten = 1 << 2
    flag_myth = 1 << 4
    flag_archaeology = 1 << 5

    myth_fixture = os.path.join(fixture_root, "mythic_war.history")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            myth_fixture,
            "--region",
            "history.region.primary",
            "--tick",
            "500",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_myth, "myth fixture missing myth flag")

    forgotten_fixture = os.path.join(fixture_root, "forgotten_reform.history")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            forgotten_fixture,
            "--region",
            "history.region.primary",
            "--tick",
            "700",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_forgotten, "forgotten fixture missing forgotten flag")

    rediscovery_fixture = os.path.join(fixture_root, "rediscovered_ruins.history")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            rediscovery_fixture,
            "--region",
            "history.region.primary",
            "--tick",
            "800",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_HISTORY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_archaeology, "rediscovery fixture missing archaeology flag")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
