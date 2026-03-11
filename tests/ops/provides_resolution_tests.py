import argparse
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.lib.provides import (
    REFUSAL_PROVIDES_AMBIGUOUS,
    REFUSAL_PROVIDES_EXPLICIT_REQUIRED,
    RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
    RESOLUTION_POLICY_EXPLICIT_REQUIRED,
    RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
    canonicalize_provides_resolution,
    resolve_providers,
)


def _declaration(pack_id: str, provides_id: str, priority: int) -> dict:
    return {
        "pack_id": pack_id,
        "provides_id": provides_id,
        "provides_type": "dataset",
        "priority": priority,
        "extensions": {},
    }


def test_two_providers_strict_refuses() -> None:
    result = resolve_providers(
        instance_id="instance.test.strict",
        required_provides_ids=["provides.earth.dem.v1"],
        provider_declarations=[
            _declaration("mod.alpha.earth_dem", "provides.earth.dem.v1", 10),
            _declaration("fork.official.dominium.earth.alt.demx", "provides.earth.dem.v1", 5),
        ],
        resolution_policy_id=RESOLUTION_POLICY_STRICT_REFUSE_AMBIGUOUS,
    )
    if result.get("result") != "refused":
        raise RuntimeError("strict policy should refuse ambiguous providers")
    if result.get("refusal_code") != REFUSAL_PROVIDES_AMBIGUOUS:
        raise RuntimeError("strict policy refusal code mismatch: %s" % result)


def test_anarchy_selects_deterministically() -> None:
    args = {
        "instance_id": "instance.test.anarchy",
        "required_provides_ids": ["provides.earth.dem.v1"],
        "provider_declarations": [
            _declaration("mod.zed.earth_dem", "provides.earth.dem.v1", 10),
            _declaration("mod.alpha.earth_dem", "provides.earth.dem.v1", 10),
        ],
        "resolution_policy_id": RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
    }
    first = resolve_providers(**args)
    second = resolve_providers(
        instance_id=args["instance_id"],
        required_provides_ids=list(reversed(args["required_provides_ids"])),
        provider_declarations=list(reversed(args["provider_declarations"])),
        resolution_policy_id=args["resolution_policy_id"],
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        raise RuntimeError("anarchy resolution should complete deterministically")
    first_rows = list(first.get("provides_resolutions") or [])
    second_rows = list(second.get("provides_resolutions") or [])
    if first_rows != second_rows:
        raise RuntimeError("deterministic provider selection drifted")
    if str(first_rows[0].get("chosen_pack_id", "")) != "mod.alpha.earth_dem":
        raise RuntimeError("deterministic lowest-pack-id policy chose the wrong provider")


def test_explicit_resolution_required_policy() -> None:
    refused = resolve_providers(
        instance_id="instance.test.explicit",
        required_provides_ids=["provides.earth.dem.v1"],
        provider_declarations=[
            _declaration("mod.alpha.earth_dem", "provides.earth.dem.v1", 1),
            _declaration("mod.beta.earth_dem", "provides.earth.dem.v1", 2),
        ],
        resolution_policy_id=RESOLUTION_POLICY_EXPLICIT_REQUIRED,
    )
    if refused.get("result") != "refused":
        raise RuntimeError("explicit-required policy should refuse without a chosen provider")
    if refused.get("refusal_code") != REFUSAL_PROVIDES_EXPLICIT_REQUIRED:
        raise RuntimeError("explicit-required refusal code mismatch: %s" % refused)
    accepted = resolve_providers(
        instance_id="instance.test.explicit",
        required_provides_ids=["provides.earth.dem.v1"],
        provider_declarations=[
            _declaration("mod.alpha.earth_dem", "provides.earth.dem.v1", 1),
            _declaration("mod.beta.earth_dem", "provides.earth.dem.v1", 2),
        ],
        explicit_resolutions=[
            {
                "instance_id": "instance.test.explicit",
                "provides_id": "provides.earth.dem.v1",
                "chosen_pack_id": "mod.beta.earth_dem",
                "resolution_policy_id": RESOLUTION_POLICY_EXPLICIT_REQUIRED,
                "extensions": {},
            }
        ],
        resolution_policy_id=RESOLUTION_POLICY_EXPLICIT_REQUIRED,
    )
    chosen = list(accepted.get("provides_resolutions") or [])
    if accepted.get("result") != "complete" or not chosen:
        raise RuntimeError("explicit provider selection should succeed")
    if str(chosen[0].get("chosen_pack_id", "")) != "mod.beta.earth_dem":
        raise RuntimeError("explicit provider selection was not preserved")


def test_resolution_record_hash_stable() -> None:
    payload_a = canonicalize_provides_resolution(
        {
            "instance_id": "instance.test.hash",
            "provides_id": "provides.earth.dem.v1",
            "chosen_pack_id": "mod.alpha.earth_dem",
            "resolution_policy_id": RESOLUTION_POLICY_EXPLICIT_REQUIRED,
            "extensions": {"note": "stable"},
        }
    )
    payload_b = canonicalize_provides_resolution(
        {
            "resolution_policy_id": RESOLUTION_POLICY_EXPLICIT_REQUIRED,
            "chosen_pack_id": "mod.alpha.earth_dem",
            "instance_id": "instance.test.hash",
            "provides_id": "provides.earth.dem.v1",
            "extensions": {"note": "stable"},
        }
    )
    if payload_a.get("deterministic_fingerprint") != payload_b.get("deterministic_fingerprint"):
        raise RuntimeError("resolution record fingerprint is not stable")


def test_cross_platform_provider_resolution_match() -> None:
    windows_order = [
        _declaration("fork.official.dominium.earth.alt.demx", "provides.earth.dem.v1", 0),
        _declaration("mod.alpha.earth_dem", "provides.earth.dem.v1", 0),
    ]
    posix_order = list(reversed(windows_order))
    windows_like = resolve_providers(
        instance_id="instance.test.cross_platform",
        required_provides_ids=["provides.earth.dem.v1"],
        provider_declarations=windows_order,
        resolution_policy_id=RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
    )
    posix_like = resolve_providers(
        instance_id="instance.test.cross_platform",
        required_provides_ids=["provides.earth.dem.v1"],
        provider_declarations=posix_order,
        resolution_policy_id=RESOLUTION_POLICY_DETERMINISTIC_LOWEST_PACK_ID,
    )
    if list(windows_like.get("provides_resolutions") or []) != list(posix_like.get("provides_resolutions") or []):
        raise RuntimeError("provider resolution changed across ordering/platform variants")


def main() -> int:
    parser = argparse.ArgumentParser(description="LIB-5 provides resolution tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    os.chdir(os.path.abspath(args.repo_root))
    test_two_providers_strict_refuses()
    test_anarchy_selects_deterministically()
    test_explicit_resolution_required_policy()
    test_resolution_record_hash_stable()
    test_cross_platform_provider_resolution_match()
    print("provides resolution tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
