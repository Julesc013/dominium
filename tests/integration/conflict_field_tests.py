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
    parser = argparse.ArgumentParser(description="Conflict T21 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "conflict")

    fixtures = [
        "local_sabotage.conflict",
        "siege_campaign.conflict",
        "resistance_cell.conflict",
        "planetary_war.conflict",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "conflict tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "conflict fixtures missing")

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
                "DOMINIUM_CONFLICT_VALIDATE_V1",
                "provider_chain=records->sides->events->forces->engagements->outcomes->occupations->resistance->morale->weapons",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "local_sabotage.conflict")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--record",
            "conflict.record.local_sabotage",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_CONFLICT_INSPECT_V1",
            "entity=record",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "conflict_id",
            "status",
            "side_count",
            "event_count",
            "region_id",
            "flags",
            "meta.status",
            "budget.used",
        ):
            ok = ok and require(key in data, "record inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--side",
            "conflict.side.blue",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=side"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "side_id",
            "conflict_id",
            "force_count",
            "readiness_level_q16",
            "flags",
        ):
            ok = ok and require(key in data, "side inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--event",
            "conflict.event.sabotage",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=event"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "event_id",
            "event_type",
            "scheduled_tick",
            "participant_count",
            "flags",
        ):
            ok = ok and require(key in data, "event inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--force",
            "conflict.force.blue",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=force"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "force_id",
            "force_type",
            "capacity_q48",
            "readiness_q16",
            "morale_q16",
        ):
            ok = ok and require(key in data, "force inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--engagement",
            "conflict.engagement.bridge",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=engagement"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "engagement_id",
            "resolution_tick",
            "logistics_count",
            "flags",
        ):
            ok = ok and require(key in data, "engagement inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--outcome",
            "conflict.outcome.bridge",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=outcome"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "outcome_id",
            "casualty_count",
            "flags",
        ):
            ok = ok and require(key in data, "outcome inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--occupation",
            "conflict.occupation.bridge",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=occupation"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "occupation_id",
            "legitimacy_support_q16",
            "status",
            "flags",
        ):
            ok = ok and require(key in data, "occupation inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--resistance",
            "conflict.resistance.bridge",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=resistance"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "resistance_id",
            "trigger_reason",
            "flags",
        ):
            ok = ok and require(key in data, "resistance inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--morale",
            "conflict.morale.blue",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=morale"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "morale_id",
            "morale_level_q16",
            "decay_rate_q16",
            "flags",
        ):
            ok = ok and require(key in data, "morale inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--weapon",
            "conflict.weapon.sabotage",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=weapon"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "weapon_id",
            "range_q16",
            "rate_q16",
            "effectiveness_q16",
            "reliability_q16",
            "energy_cost_q48",
            "flags",
        ):
            ok = ok and require(key in data, "weapon inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "conflict.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_INSPECT_V1", "entity=region"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "conflict_count",
            "side_count",
            "event_count",
            "force_count",
            "engagement_count",
            "outcome_count",
            "occupation_count",
            "resistance_count",
            "morale_count",
            "weapon_count",
            "readiness_avg_q16",
            "morale_avg_q16",
            "legitimacy_avg_q16",
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
            "conflict.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_CONFLICT_RESOLVE_V1",
            "provider_chain=records->sides->events->forces->engagements->outcomes->occupations->resistance->morale->weapons",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "conflict_count",
            "side_count",
            "event_count",
            "event_applied_count",
            "outcome_applied_count",
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
            "conflict.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_RESOLVE_V1"],
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
            "conflict.region.primary",
        ],
        expect_contains=["DOMINIUM_CONFLICT_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    flag_shortage = 1 << 2
    flag_low_morale = 1 << 3
    flag_illegitimate = 1 << 4
    flag_resistance = 1 << 5

    siege_fixture = os.path.join(fixture_root, "siege_campaign.conflict")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            siege_fixture,
            "--region",
            "conflict.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_shortage, "siege fixture missing shortage flag")

    resistance_fixture = os.path.join(fixture_root, "resistance_cell.conflict")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            resistance_fixture,
            "--region",
            "conflict.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_illegitimate, "resistance fixture missing illegitimate flag")
        ok = ok and require(flags & flag_resistance, "resistance fixture missing resistance flag")

    planetary_fixture = os.path.join(fixture_root, "planetary_war.conflict")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            planetary_fixture,
            "--region",
            "conflict.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_CONFLICT_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        flags = int(parse_kv(output).get("flags", "0"))
        ok = ok and require(flags & flag_low_morale, "planetary fixture missing low morale flag")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
