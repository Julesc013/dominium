import argparse
import os
import sys
import tempfile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.lib.lib_stress_common import DEFAULT_LIB7_SEED, generate_lib_stress_scenario, run_lib_stress


_SCENARIO_CACHE: dict[tuple[str, str], dict] = {}
_REPORT_CACHE: dict[tuple[str, str], dict] = {}


def _projection(report: dict) -> dict:
    rounds = list(report.get("rounds") or [])
    if not rounds:
        raise RuntimeError("stress report missing rounds")
    return dict(dict(rounds[0]).get("projection") or {})


def _scenario(tmp_root: str, slash_mode: str) -> dict:
    key = (os.path.abspath(tmp_root), slash_mode)
    cached = _SCENARIO_CACHE.get(key)
    if cached is not None:
        return cached
    payload = generate_lib_stress_scenario(
        repo_root=REPO_ROOT_HINT,
        out_root=os.path.join(tmp_root, "scenario_{}".format(slash_mode)),
        seed=DEFAULT_LIB7_SEED,
        slash_mode=slash_mode,
    )
    _SCENARIO_CACHE[key] = payload
    return payload


def _report(tmp_root: str, slash_mode: str) -> dict:
    key = (os.path.abspath(tmp_root), slash_mode)
    cached = _REPORT_CACHE.get(key)
    if cached is not None:
        return cached
    payload = run_lib_stress(
        repo_root=REPO_ROOT_HINT,
        out_root=os.path.join(tmp_root, "run_{}".format(slash_mode)),
        seed=DEFAULT_LIB7_SEED,
        slash_mode=slash_mode,
    )
    _REPORT_CACHE[key] = payload
    return payload


def test_lib_stress_scenario_deterministic(tmp_root: str) -> None:
    scenario_a = _scenario(os.path.join(tmp_root, "scenario_a"), "forward")
    scenario_b = _scenario(os.path.join(tmp_root, "scenario_b"), "forward")
    if str(scenario_a.get("deterministic_fingerprint", "")).strip() != str(scenario_b.get("deterministic_fingerprint", "")).strip():
        raise RuntimeError("LIB-7 scenario fingerprint changed across repeated generation")


def test_export_import_roundtrip_hash_match(tmp_root: str) -> None:
    report = _report(tmp_root, "forward")
    projection = _projection(report)
    import_results = dict(projection.get("import_results") or {})
    bundle_verifications = dict(projection.get("bundle_verifications") or {})
    if not bool(report.get("assertions", {}).get("bundle_hash_stable", False)):
        raise RuntimeError("bundle hashes are not stable across repeated LIB-7 runs")
    if any(str(value).strip() != "complete" for value in import_results.values()):
        raise RuntimeError("expected all LIB-7 imports to complete")
    if any(str(dict(result).get("result", "")).strip() != "complete" for result in bundle_verifications.values()):
        raise RuntimeError("expected all LIB-7 bundle verifications to complete")


def test_provider_resolution_policies(tmp_root: str) -> None:
    report = _report(tmp_root, "forward")
    outcomes = dict(report.get("provider_resolution_outcomes") or {})
    strict = dict(outcomes.get("strict") or {})
    explicit = dict(outcomes.get("explicit") or {})
    anarchy = dict(outcomes.get("anarchy") or {})
    if str(strict.get("result", "")).strip() != "refused":
        raise RuntimeError("strict provider policy should refuse ambiguity")
    if str(strict.get("refusal_code", "")).strip() != "refusal.provides.ambiguous":
        raise RuntimeError("strict provider policy refusal code mismatch")
    if str(explicit.get("result", "")).strip() != "complete":
        raise RuntimeError("explicit provider policy should complete with a pinned selection")
    if str(anarchy.get("result", "")).strip() != "complete":
        raise RuntimeError("anarchy provider policy should deterministically complete")
    chosen_pack_id = str((list(anarchy.get("provides_resolutions") or [{}])[0]).get("chosen_pack_id", "")).strip()
    if chosen_pack_id != "fork.official.dominium.dem.primary.alt.demx":
        raise RuntimeError("anarchy provider policy selected an unexpected provider")


def test_strict_refuses_ambiguous_provides(tmp_root: str) -> None:
    report = _report(tmp_root, "forward")
    pack_outcomes = dict(report.get("pack_verification_outcomes") or {})
    launcher_outcomes = dict(report.get("launcher_outcomes") or {})
    ambiguous_pack = dict(pack_outcomes.get("ambiguous_strict") or {})
    strict_launcher = dict(launcher_outcomes.get("strict_ambiguous") or {})
    if "refusal.provides.ambiguous" not in list(ambiguous_pack.get("refusal_codes") or []):
        raise RuntimeError("strict ambiguous pack verification did not refuse ambiguity")
    if "refusal.provides.ambiguous" not in list(strict_launcher.get("refusal_codes") or []):
        raise RuntimeError("launcher strict ambiguity case did not surface the refusal code")


def test_save_read_only_fallback_logged(tmp_root: str) -> None:
    report = _report(tmp_root, "forward")
    launcher_outcomes = dict(report.get("launcher_outcomes") or {})
    save_outcomes = dict(report.get("save_outcomes") or {})
    launcher_read_only = dict(launcher_outcomes.get("read_only_save") or {})
    contract_mismatch = dict(save_outcomes.get("contract_mismatch_read_only") or {})
    if str(launcher_read_only.get("mode", "")).strip() != "inspect-only":
        raise RuntimeError("read-only launcher case did not degrade to inspect-only")
    if not bool(launcher_read_only.get("degrade_logged", False)):
        raise RuntimeError("read-only launcher case did not log degradation")
    if not bool(contract_mismatch.get("read_only_required", False)):
        raise RuntimeError("contract mismatch save case did not require read-only access")


def test_cross_platform_lib_hash_match(tmp_root: str) -> None:
    forward = _report(tmp_root, "forward")
    backward = _report(tmp_root, "backward")
    forward_projection = _projection(forward)
    backward_projection = _projection(backward)
    if dict(forward.get("bundle_hashes") or {}) != dict(backward.get("bundle_hashes") or {}):
        raise RuntimeError("bundle hashes changed across slash-mode variants")
    if str(dict(forward_projection).get("projection_hash", "")).strip() == str(dict(backward_projection).get("projection_hash", "")).strip():
        pass
    elif str((list(forward.get("projection_hashes") or [""])[0])).strip() != str((list(backward.get("projection_hashes") or [""])[0])).strip():
        raise RuntimeError("projection hash changed across slash-mode variants")


def main() -> int:
    parser = argparse.ArgumentParser(description="LIB-7 stress envelope tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    os.chdir(repo_root)

    with tempfile.TemporaryDirectory() as tmp_root:
        test_lib_stress_scenario_deterministic(tmp_root)
        test_export_import_roundtrip_hash_match(tmp_root)
        test_provider_resolution_policies(tmp_root)
        test_strict_refuses_ambiguous_provides(tmp_root)
        test_save_read_only_fallback_logged(tmp_root)
        test_cross_platform_lib_hash_match(tmp_root)

    print("LIB-7 stress envelope tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
