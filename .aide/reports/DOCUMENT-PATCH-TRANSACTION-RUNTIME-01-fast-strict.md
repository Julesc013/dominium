# Fast Strict Test Tier Result

- status: `FAIL`
- mode: `fast_strict`
- repo root: `C:\Inbox\Git Repos\dominium`
- started: `2026-05-21T16:26:31Z`
- completed: `2026-05-21T16:26:32Z`
- elapsed seconds: `0.953`
- selected tiers: `T0, T1, T2`

## Commands

| ID | Tier | Required | Status | Seconds |
| --- | --- | --- | --- | ---: |
| `t0.git_diff_check` | `T0` | `true` | `pass` | `0.14` |
| `t0.staged_generated_output_check` | `T0` | `true` | `pass` | `0.094` |
| `t0.changed_json_parse` | `T0` | `true` | `fail` | `0.719` |

## Findings

### t0.changed_json_parse

- status: `fail`
- returncode: `1`

```text
JSON parse failures:
contracts/conformance/conformance_suite.schema.json: Invalid \escape: line 8 column 63 (char 502)
contracts/service/service_descriptor.schema.json: Invalid \escape: line 8 column 68 (char 686)
```


## Not Run

10 command(s) were outside the selected mode.
