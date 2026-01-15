# macOS PKG Templates (Plan S-6)

Design-only notes for downstream packagers:

1. Build a component package (payload):
   - root contains `Dominium.app` under `Applications/`
2. Build a product installer:
   - use `Distribution.xml` to describe choices and package references

Codesigning and notarization are handled by the packaging pipeline; this directory only provides declarative templates.

