# MOVE-BULK-08 Shim Debt

No temporary shims were created by MOVE-BULK-08. No MOVE-BULK apply batches after Batch A ran, so planned Batch E/F/G shims were not created.

| Shim Path | State | Retirement Task |
| --- | --- | --- |
| `compat/shims/__init__.py` | deferred_with_root | MOVE-BULK-04-GATE then MOVE-BULK-04-APPLY-AUTHORITY-POLICY if authorized |
| `compat/shims/common.py` | deferred_with_root | MOVE-BULK-04-GATE then MOVE-BULK-04-APPLY-AUTHORITY-POLICY if authorized |
| `tool_ui_bind.cmd` | valid_temporary | root wrapper retirement review after documented workflow replacement |
| `tool_ui_doc_annotate.cmd` | valid_temporary | root wrapper retirement review after documented workflow replacement |
| `tool_ui_validate.cmd` | valid_temporary | root wrapper retirement review after documented workflow replacement |
