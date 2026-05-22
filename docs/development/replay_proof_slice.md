Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: REPLAY-PROOF-SLICE-01

# Replay Proof Slice Development Notes

Use this slice to validate the narrow command-level replay/proof surface:

```powershell
python -m py_compile tools/validators/contracts/check_replay_proof.py
python tools/validators/contracts/check_replay_proof.py --repo-root . --strict
python tools/validators/contracts/check_replay_proof.py --repo-root . --fixtures
py -3 tests/app/replay_proof_slice_tests.py
```

The validator checks replay/proof schemas, fixture refs, command refs, diagnostic/refusal bindings, evidence refs, canonical hashes, and unsupported runtime claims.

The hash policy is intentionally small:

```text
canonical JSON
sorted keys
UTF-8 bytes
compact separators
sha256
```

Do not add runtime replay, package runtime, game replay, save replay, renderer integration, native GUI integration, or Workbench shell behavior while maintaining this slice.

If a future command wants replay proof, add a new fixture chain and typed diagnostics/refusals rather than weakening the package mount proof.
