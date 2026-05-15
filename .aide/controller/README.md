# AIDE Outcome Controller

The AIDE outcome controller is advisory metadata only. It reads local AIDE
evidence such as verification, golden-task, token, review, and context reports
and writes deterministic recommendations under `.aide/controller/`.

It must not mutate prompts, policies, routes, provider settings, runtime
behavior, source files, GitHub settings, releases, tags, or workflows.

Provider calls, model calls, network calls, raw prompt storage, and raw response
storage remain disabled.
