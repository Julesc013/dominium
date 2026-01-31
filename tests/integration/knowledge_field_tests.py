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
        sys.stderr.write("FAIL: expected exit {} for {}\\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\\n".format(token, cmd))
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
        sys.stderr.write("FAIL: {}\\n".format(message))
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Knowledge T18 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "knowledge")

    fixtures = [
        "survey_baseline.knowledge",
        "apprenticeship_loop.knowledge",
        "certification_spike.knowledge",
        "decay_stress.knowledge",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "knowledge tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "knowledge fixtures missing")

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
                "DOMINIUM_KNOWLEDGE_VALIDATE_V1",
                "provider_chain=artifacts->skills->programs->events",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "survey_baseline.knowledge")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--artifact",
            "knowledge.artifact.geology_core",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_KNOWLEDGE_INSPECT_V1",
            "entity=artifact",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "artifact_id",
            "subject_domain_id",
            "claim_count",
            "evidence_count",
            "confidence_q16",
            "uncertainty_q16",
            "decay_rate_q16",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "artifact inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--skill",
            "knowledge.skill.mining",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_KNOWLEDGE_INSPECT_V1",
            "entity=skill",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "profile_id",
            "skill_domain_id",
            "variance_reduction_q16",
            "failure_bias_reduction_q16",
            "decay_rate_q16",
            "process_ref_count",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "skill inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--program",
            "knowledge.program.basic_mining",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_KNOWLEDGE_INSPECT_V1",
            "entity=program",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "program_id",
            "curriculum_id",
            "duration_ticks",
            "energy_cost_q48",
            "resource_cost_q48",
            "output_skill_id",
            "accreditation_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "program inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--event",
            "knowledge.event.practice_1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_KNOWLEDGE_INSPECT_V1",
            "entity=event",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "event_id",
            "process_type",
            "artifact_id",
            "skill_id",
            "delta_confidence_q16",
            "delta_uncertainty_q16",
            "delta_variance_q16",
            "delta_bias_q16",
            "event_tick",
            "flags",
        ):
            ok = ok and require(key in data, "event inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "knowledge.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_KNOWLEDGE_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "artifact_count",
            "skill_count",
            "program_count",
            "event_count",
            "confidence_avg_q16",
            "variance_reduction_avg_q16",
            "failure_bias_reduction_avg_q16",
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
            "knowledge.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_KNOWLEDGE_RESOLVE_V1",
            "provider_chain=artifacts->skills->programs->events",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "artifact_count",
            "skill_count",
            "program_count",
            "event_count",
            "event_applied_count",
            "confidence_avg_q16",
            "variance_reduction_avg_q16",
            "failure_bias_reduction_avg_q16",
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
            "knowledge.region.primary",
            "--tick",
            "3",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_KNOWLEDGE_RESOLVE_V1"],
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
            "knowledge.region.primary",
        ],
        expect_contains=["DOMINIUM_KNOWLEDGE_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
