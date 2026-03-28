Status: DERIVED
Last Reviewed: 2026-03-28
Stability: provisional
Future Series: XI
Replacement Target: XI-5a-v3 final execution report

# XI-4z Fix3 Final

- selected option preserved: `C`
- dangerous shadow roots for Xi-5a-v3: `src/`, `app/src/`
- approved dangerous-shadow rows: `542`
- promoted package initializers: `src/client/interaction/__init__.py, src/lib/store/__init__.py`
- deferred rows for Xi-5b/Xi-5c: `253`
- reserved package protections inherited: `platform, time`

Xi-5a should no longer attempt the full mixed `src/source` surface. It should execute only the dangerous shadow-root slice using the v4 lock and leave later source-pocket normalization to subsequent Xi-5 phases.
