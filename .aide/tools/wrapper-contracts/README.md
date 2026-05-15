# AIDE Wrapper Contracts

This directory records reviewed or provisional command contracts for wrapping
existing Dominium validators through the AIDE control plane.

Wrapper contracts are preservation-first planning artifacts. They do not delete,
rename, move, retire, migrate, or execute legacy tools. They define the command
surface, inputs, outputs, side effects, timeout expectations, and review gates
that must be proved before a future executable adapter is enabled.

Dominium keeps legacy validator names such as XStack, AuditX, RepoX, TestX, and
BuildX-like surfaces until wrappers prove a safer long-term interface. AIDE wraps
before renaming so future agents can inventory, classify, adapt, migrate, and
retire old names with evidence instead of guessing from convenience or path
shape.
