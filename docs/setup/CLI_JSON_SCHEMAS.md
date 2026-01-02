# Setup CLI JSON Schemas

All CLI JSON output uses stable key ordering and contains no timestamps in deterministic mode.

## Schema: `setup-cli-1`

```json
{
  "schema_version": "setup-cli-1",
  "command": "plan",
  "status": "ok|error",
  "status_code": 0,
  "artifacts": {
    "manifest": "path or empty",
    "request": "path or empty",
    "plan": "path or empty",
    "state": "path or empty",
    "audit": "path or empty",
    "journal": "path or empty",
    "txn_journal": "path or empty"
  },
  "digests": {
    "manifest": "0x...",
    "request": "0x...",
    "plan": "0x...",
    "state": "0x...",
    "audit": "0x..."
  },
  "details": {
    "error": {
      "domain": 0,
      "code": 0,
      "subcode": 0,
      "flags": 0,
      "msg_id": 0,
      "label": "ok"
    }
  }
}
```

## Notes
- `status_code` mirrors the CLI process exit code.
- `details` is command-specific and must remain deterministic.

## Command details
### plan / resolve / apply / resume / rollback / status
- `details.error`: stable error taxonomy fields.
- `details.plan`: plan summary with digests (when applicable).

### audit dump
- `details.audit`: parsed audit summary and selection evidence.

### state dump / verify
- `details.state`: installed state summary.
- Includes `state_version` and `migration_applied` when present.

### doctor
- `details.items`: per-artifact validation results.
- Each item has `kind`, `status`, and `detail`.

### explain-refusal
- `details.refusals`: list of refusal codes and stable labels.
