# Replacement Protocol Contract Fixtures

These fixtures prove `tools/validators/repo/check_replacement_packet.py`.

The valid fixtures are synthetic packets only. They do not perform a real
replacement and do not claim runtime conformance beyond the fixture proof.

The invalid fixtures intentionally exercise hard rules:

- old surface must be known;
- public replacements need proof;
- rollback is required for active replacements;
- stable artifact breaks need migration or refusal behavior.
