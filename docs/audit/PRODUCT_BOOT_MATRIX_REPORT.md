Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: regenerated product boot matrix report for release

# Product Boot Matrix Report

Fingerprint: `def0eb6b78ee0c7bbfbed23c7e34747456bb82df2f515bcbdbbc15cc0a4e5d05`

## Summary

- result: `complete`
- products: `7`
- command runs: `49`
- mode runs: `42`
- ipc runs: `5`
- failures: `0`

## Command Surface

| Product | Invocation | Command | Exit | Result | Install Mode | Selected Mode |
| --- | --- | --- | --- | --- | --- | --- |
| `client` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `client` | `installed` | `help` | `0` | `pass` | `` | `` |
| `client` | `installed` | `compat-status` | `0` | `complete` | `installed` | `tui` |
| `client` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `client` | `portable` | `help` | `0` | `pass` | `` | `` |
| `client` | `portable` | `compat-status` | `0` | `complete` | `portable` | `tui` |
| `client` | `portable` | `validate` | `0` | `complete` | `` | `` |
| `engine` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `engine` | `installed` | `help` | `0` | `pass` | `` | `` |
| `engine` | `installed` | `compat-status` | `0` | `complete` | `installed` | `cli` |
| `engine` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `engine` | `portable` | `help` | `0` | `pass` | `` | `` |
| `engine` | `portable` | `compat-status` | `0` | `complete` | `portable` | `cli` |
| `engine` | `portable` | `validate` | `0` | `complete` | `` | `` |
| `game` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `game` | `installed` | `help` | `0` | `pass` | `` | `` |
| `game` | `installed` | `compat-status` | `0` | `complete` | `installed` | `tui` |
| `game` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `game` | `portable` | `help` | `0` | `pass` | `` | `` |
| `game` | `portable` | `compat-status` | `0` | `complete` | `portable` | `tui` |
| `game` | `portable` | `validate` | `0` | `complete` | `` | `` |
| `launcher` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `launcher` | `installed` | `help` | `0` | `pass` | `` | `` |
| `launcher` | `installed` | `compat-status` | `0` | `complete` | `installed` | `tui` |
| `launcher` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `launcher` | `portable` | `help` | `0` | `pass` | `` | `` |
| `launcher` | `portable` | `compat-status` | `0` | `complete` | `portable` | `tui` |
| `launcher` | `portable` | `validate` | `0` | `complete` | `` | `` |
| `server` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `server` | `installed` | `help` | `0` | `pass` | `` | `` |
| `server` | `installed` | `compat-status` | `0` | `complete` | `installed` | `tui` |
| `server` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `server` | `portable` | `help` | `0` | `pass` | `` | `` |
| `server` | `portable` | `compat-status` | `0` | `complete` | `portable` | `tui` |
| `server` | `portable` | `validate` | `0` | `complete` | `` | `` |
| `setup` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `setup` | `installed` | `help` | `0` | `pass` | `` | `` |
| `setup` | `installed` | `compat-status` | `0` | `complete` | `installed` | `tui` |
| `setup` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `setup` | `portable` | `help` | `0` | `pass` | `` | `` |
| `setup` | `portable` | `compat-status` | `0` | `complete` | `portable` | `tui` |
| `setup` | `portable` | `validate` | `0` | `complete` | `` | `` |
| `tool.attach_console_stub` | `installed` | `descriptor` | `0` | `complete` | `` | `` |
| `tool.attach_console_stub` | `installed` | `help` | `0` | `pass` | `` | `` |
| `tool.attach_console_stub` | `installed` | `compat-status` | `0` | `complete` | `installed` | `tui` |
| `tool.attach_console_stub` | `portable` | `descriptor` | `0` | `complete` | `` | `` |
| `tool.attach_console_stub` | `portable` | `help` | `0` | `pass` | `` | `` |
| `tool.attach_console_stub` | `portable` | `compat-status` | `0` | `complete` | `portable` | `tui` |
| `tool.attach_console_stub` | `portable` | `validate` | `0` | `complete` | `` | `` |

## Mode Assertions

| Product | Invocation | Scenario | Expected | Observed | Compat | Degrade | Pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `client` | `installed` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `client` | `installed` | `gui` | `rendered` | `rendered` | `compat.full` | `0` | `yes` |
| `client` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `client` | `portable` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `client` | `portable` | `gui` | `rendered` | `rendered` | `compat.full` | `0` | `yes` |
| `client` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `engine` | `installed` | `tty` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `engine` | `installed` | `gui` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `engine` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `engine` | `portable` | `tty` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `engine` | `portable` | `gui` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `engine` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `game` | `installed` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `game` | `installed` | `gui` | `cli` | `cli` | `compat.degraded` | `1` | `yes` |
| `game` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `game` | `portable` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `game` | `portable` | `gui` | `cli` | `cli` | `compat.degraded` | `1` | `yes` |
| `game` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `launcher` | `installed` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `launcher` | `installed` | `gui` | `cli` | `cli` | `compat.degraded` | `2` | `yes` |
| `launcher` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `launcher` | `portable` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `launcher` | `portable` | `gui` | `cli` | `cli` | `compat.degraded` | `2` | `yes` |
| `launcher` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `server` | `installed` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `server` | `installed` | `gui` | `cli` | `cli` | `compat.degraded` | `1` | `yes` |
| `server` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `server` | `portable` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `server` | `portable` | `gui` | `cli` | `cli` | `compat.degraded` | `1` | `yes` |
| `server` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `setup` | `installed` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `setup` | `installed` | `gui` | `cli` | `cli` | `compat.degraded` | `2` | `yes` |
| `setup` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `setup` | `portable` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `setup` | `portable` | `gui` | `cli` | `cli` | `compat.degraded` | `2` | `yes` |
| `setup` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `tool.attach_console_stub` | `installed` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `tool.attach_console_stub` | `installed` | `gui` | `cli` | `cli` | `compat.degraded` | `1` | `yes` |
| `tool.attach_console_stub` | `installed` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |
| `tool.attach_console_stub` | `portable` | `tty` | `tui` | `tui` | `compat.full` | `0` | `yes` |
| `tool.attach_console_stub` | `portable` | `gui` | `cli` | `cli` | `compat.degraded` | `1` | `yes` |
| `tool.attach_console_stub` | `portable` | `headless` | `cli` | `cli` | `compat.full` | `0` | `yes` |

## IPC Assertions

| Product | Result | Compat | Endpoint Count | Pass |
| --- | --- | --- | --- | --- |
| `client` | `complete` | `` | `0` | `yes` |
| `launcher` | `complete` | `` | `0` | `yes` |
| `server` | `complete` | `` | `0` | `yes` |
| `setup` | `complete` | `` | `0` | `yes` |
| `tool.attach_console_stub` | `complete` | `` | `0` | `yes` |

## Failures

- none
