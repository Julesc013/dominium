Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-5 UX polish and archive matrix

# DIST Platform Matrix Report

- result: `complete`
- channel_id: `mock`
- contexts: `tty, gui, headless`
- deterministic_fingerprint: `7efb1baccdfe7c517c2a61b6c7be37f249029546b581edded4d5a80c61e15669`

## Matrix Summary

- `win64` `platform.winnt` source=`built` failures=`0` fingerprint=`46c8b86e17368bc26b6e9aea90fc2a975dd6ada5793ddf59d25d076a10223442`

## Product Runtime Checks

### win64

- `client` descriptor=`0` compat_cli=`0` selected=`cli` capability_match=`True`
- `engine` descriptor=`0` compat_cli=`0` selected=`cli` capability_match=`True`
- `game` descriptor=`0` compat_cli=`0` selected=`cli` capability_match=`True`
- `launcher` descriptor=`0` compat_cli=`0` selected=`cli` capability_match=`True`
- `server` descriptor=`0` compat_cli=`0` selected=`cli` capability_match=`True`
- `setup` descriptor=`0` compat_cli=`0` selected=`cli` capability_match=`True`

## Simulated Context Selection

- `win64` `client` `gui` expected=`cli` selected=`cli` passed=`True`
- `win64` `client` `headless` expected=`cli` selected=`cli` passed=`True`
- `win64` `client` `tty` expected=`tui` selected=`tui` passed=`True`
- `win64` `engine` `gui` expected=`cli` selected=`cli` passed=`True`
- `win64` `engine` `headless` expected=`cli` selected=`cli` passed=`True`
- `win64` `engine` `tty` expected=`cli` selected=`cli` passed=`True`
- `win64` `game` `gui` expected=`cli` selected=`cli` passed=`True`
- `win64` `game` `headless` expected=`cli` selected=`cli` passed=`True`
- `win64` `game` `tty` expected=`tui` selected=`tui` passed=`True`
- `win64` `launcher` `gui` expected=`cli` selected=`cli` passed=`True`
- `win64` `launcher` `headless` expected=`cli` selected=`cli` passed=`True`
- `win64` `launcher` `tty` expected=`tui` selected=`tui` passed=`True`
- `win64` `server` `gui` expected=`cli` selected=`cli` passed=`True`
- `win64` `server` `headless` expected=`cli` selected=`cli` passed=`True`
- `win64` `server` `tty` expected=`tui` selected=`tui` passed=`True`
- `win64` `setup` `gui` expected=`cli` selected=`cli` passed=`True`
- `win64` `setup` `headless` expected=`cli` selected=`cli` passed=`True`
- `win64` `setup` `tty` expected=`tui` selected=`tui` passed=`True`

## Forced Fallback Checks

- `win64` `client` context=`tty` requested=`rendered` expected=`tui` selected=`tui` degrade_logged=`True` passed=`True`
- `win64` `engine` context=`tty` requested=`tui` expected=`tui` selected=`tui` degrade_logged=`False` passed=`True`
- `win64` `game` context=`tty` requested=`tui` expected=`tui` selected=`tui` degrade_logged=`False` passed=`True`
- `win64` `launcher` context=`tty` requested=`os_native` expected=`tui` selected=`tui` degrade_logged=`True` passed=`True`
- `win64` `server` context=`tty` requested=`tui` expected=`tui` selected=`tui` degrade_logged=`False` passed=`True`
- `win64` `setup` context=`tty` requested=`os_native` expected=`tui` selected=`tui` degrade_logged=`True` passed=`True`

## Failures

- none
