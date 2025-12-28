#!/bin/sh
set -e

if [ "$#" -ne 3 ]; then
  echo "Usage: make_sfx.sh <installer.exe> <payload.dsuarch> <out.exe>"
  exit 1
fi

python - "$1" "$2" "$3" <<'PY'
import struct
import sys

exe_path, arc_path, out_path = sys.argv[1:4]
with open(exe_path, "rb") as f:
    exe = f.read()
with open(arc_path, "rb") as f:
    arc = f.read()
footer = b"DSUX" + struct.pack("<II", len(exe), len(arc))
with open(out_path, "wb") as f:
    f.write(exe)
    f.write(arc)
    f.write(footer)
PY

echo "SFX built: $3"
