#!/usr/bin/env bash
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
log_dir="$root/dist/release_gate"
log_dir_rel="dist/release_gate"

mkdir -p "$log_dir"

build_log="$log_dir/build.log"
setup_log="$log_dir/setup_tests.log"
launcher_log="$log_dir/launcher_smoke.log"
packaging_log="$log_dir/packaging_validation.log"

run_cmd() {
    local cmd="$1"
    local log="$2"
    echo ">> ${cmd}" >> "$log"
    (cd "$root" && bash -c "$cmd") >> "$log" 2>&1
    return $?
}

build_status="pass"
setup_status="pass"
launcher_status="pass"
packaging_status="pass"

> "$build_log"
if ! run_cmd "cmake --build --preset debug" "$build_log"; then
    build_status="fail"
fi

> "$setup_log"
if ! run_cmd "ctest --preset debug -R dsu_ -E dsu_packaging_validation_test --output-on-failure" "$setup_log"; then
    setup_status="fail"
fi
if ! run_cmd "ctest --preset debug -R test_ --output-on-failure" "$setup_log"; then
    setup_status="fail"
fi

> "$launcher_log"
if ! run_cmd "ctest --preset debug -R dominium_launcher_state_smoke_tests --output-on-failure" "$launcher_log"; then
    launcher_status="fail"
fi
if ! run_cmd "ctest --preset debug -R dominium_launcher_ui_smoke_tests --output-on-failure" "$launcher_log"; then
    launcher_status="fail"
fi
if ! run_cmd "ctest --preset debug -R dominium_launcher_tui_smoke_tests --output-on-failure" "$launcher_log"; then
    launcher_status="fail"
fi

> "$packaging_log"
if ! run_cmd "ctest --preset debug -R dsu_packaging_validation_test --output-on-failure" "$packaging_log"; then
    packaging_status="fail"
fi

overall="pass"
if [ "$build_status" != "pass" ] || \
   [ "$setup_status" != "pass" ] || \
   [ "$launcher_status" != "pass" ] || \
   [ "$packaging_status" != "pass" ]; then
    overall="fail"
fi

summary="$log_dir/release_gate_summary.json"
cat > "$summary" <<EOF
{
  "schema_version": 1,
  "log_dir": "${log_dir_rel}",
  "stages": [
    {"name":"build","status":"${build_status}","log":"${log_dir_rel}/build.log"},
    {"name":"setup_tests","status":"${setup_status}","log":"${log_dir_rel}/setup_tests.log"},
    {"name":"launcher_smoke","status":"${launcher_status}","log":"${log_dir_rel}/launcher_smoke.log"},
    {"name":"packaging_validation","status":"${packaging_status}","log":"${log_dir_rel}/packaging_validation.log"}
  ],
  "overall":"${overall}"
}
EOF

if [ "$overall" != "pass" ]; then
    exit 1
fi
