# Remaining Risks

- Git index writes are blocked by filesystem permission in the current sandbox, so this repair could not be committed here.
- The worktree still contains a large generated `.aide/**` evidence set from Q52/Q53/DCHECK and this repair.
- Full eval has been timeout-prone; treat it as deferred unless rerun with an explicit longer budget.
- XStack integration is registry/contract level only. Legacy wrappers remain disabled until a future task proves safe execution one wrapper at a time.
- Existing tool and root inventories still contain many unknown classifications; this is expected pending future classifier and wrapper work.
