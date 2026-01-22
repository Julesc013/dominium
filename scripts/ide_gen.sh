#!/usr/bin/env sh
set -eu

if [ "$#" -eq 0 ]; then
  echo "usage: ide_gen.sh <preset> [preset...]" >&2
  exit 2
fi

for preset in "$@"; do
  echo "[ide_gen] configure ${preset}"
  cmake --preset "${preset}"
  manifest="ide/manifests/${preset}.projection.json"
  if [ -f "${manifest}" ]; then
    echo "[ide_gen] manifest: ${manifest}"
  else
    echo "[ide_gen] manifest missing: ${manifest}"
  fi
done
