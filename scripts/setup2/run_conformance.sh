#!/usr/bin/env bash
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
preset="${1:-debug}"
log_dir="$root/dist/setup2/conformance"
log="$log_dir/conformance.log"
build_dir="$root/build/$preset"
summary_src="$build_dir/source/tests/setup2_conformance/conformance_summary.json"
summary_dst="$log_dir/conformance_summary.json"

mkdir -p "$log_dir"

echo ">> ctest --preset ${preset} -R setup2_conformance --output-on-failure" > "$log"
(cd "$root" && ctest --preset "$preset" -R setup2_conformance --output-on-failure) >> "$log" 2>&1
if [ -f "$summary_src" ]; then
  cp "$summary_src" "$summary_dst"
fi
exit $?
