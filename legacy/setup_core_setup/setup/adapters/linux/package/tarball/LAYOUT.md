# Portable Tarball Layout (Plan S-6)

Design-only layout for a portable Linux distribution:

```
dominium/
  bin/
    dominium-setup-linux
    dominium-launcher
  manifests/
    dominium.dsumf
  payloads/
    *.dsuarchive
    *.dsublob
  .dsu/
    installed_state.dsustate
```

Invocation examples:

- install: `./bin/dominium-setup-linux install --plan ./manifests/dominium.dsuplan --deterministic`
- register: `./bin/dominium-setup-linux platform-register --state ./.dsu/installed_state.dsustate --deterministic`

