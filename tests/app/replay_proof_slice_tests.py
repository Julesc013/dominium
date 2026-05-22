import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from tools.validators.contracts.check_replay_proof import (  # noqa: E402
    COMMAND_ID,
    VALID_PROOF_HASH_REL,
    VALID_VERIFICATION_REL,
    canonical_file_hash,
    load_json,
    proof_material_hash,
    validate_all,
)


def _assert(condition, message, violations):
    if not condition:
        violations.append(message)


def test_replay_proof_fixture_chain_passes(violations):
    result = validate_all(REPO_ROOT, include_fixtures=True, include_inventory=False)
    _assert(result["status"] == "pass", "replay proof validator did not pass", violations)
    _assert(result["summary"]["errors"] == 0, "replay proof validator reported errors", violations)
    _assert(result["fixtures"]["invalid_fixtures"] == 8, "expected negative fixture count changed", violations)


def test_proof_hash_is_deterministic(violations):
    proof_hash = load_json(REPO_ROOT / VALID_PROOF_HASH_REL)
    first = proof_material_hash(REPO_ROOT, proof_hash)
    second = proof_material_hash(REPO_ROOT, proof_hash)
    _assert(first == second, "proof material hash is not stable", violations)
    _assert(first == proof_hash["value"], "proof material hash does not match fixture", violations)


def test_verification_result_matches_proof_hash(violations):
    proof_hash = load_json(REPO_ROOT / VALID_PROOF_HASH_REL)
    verification = load_json(REPO_ROOT / VALID_VERIFICATION_REL)
    _assert(verification["command_ref"] == COMMAND_ID, "verification target command changed", violations)
    _assert(verification["status"] == "pass", "verification status changed", violations)
    _assert(verification["expected_hash"] == proof_hash["value"], "verification expected hash mismatch", violations)
    _assert(verification["observed_hash"] == proof_hash["value"], "verification observed hash mismatch", violations)
    _assert(verification["runtime_replay_implemented"] is False, "verification claims runtime replay support", violations)


def test_package_mount_result_hash_is_stable(violations):
    first = canonical_file_hash(REPO_ROOT, "tests/contract/package/fixtures/valid_package_mount_result.json")
    second = canonical_file_hash(REPO_ROOT, "tests/contract/package/fixtures/valid_package_mount_result.json")
    _assert(first == second, "package mount result canonical hash is not stable", violations)


def main():
    violations = []
    test_replay_proof_fixture_chain_passes(violations)
    test_proof_hash_is_deterministic(violations)
    test_verification_result_matches_proof_hash(violations)
    test_package_mount_result_hash_is_stable(violations)
    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Replay proof slice tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
