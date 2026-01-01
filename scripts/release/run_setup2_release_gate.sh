#!/usr/bin/env bash
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
preset="${1:-debug}"
log_dir="$root/dist/release/setup2_release_gate"
log_dir_rel="dist/release/setup2_release_gate"

mkdir -p "$log_dir"

build_log="$log_dir/build.log"
maint_log="$log_dir/maintenance.log"
unit_log="$log_dir/unit_tests.log"
parity_log="$log_dir/parity_lock.log"
gold_log="$log_dir/gold_master.log"
conf_log="$log_dir/conformance.log"
adapter_log="$log_dir/adapter_checks.log"
pack_log="$log_dir/packaging_checks.log"

run_cmd() {
    local cmd="$1"
    local log="$2"
    echo ">> ${cmd}" >> "$log"
    (cd "$root" && bash -c "$cmd") >> "$log" 2>&1
    return $?
}

build_status="pass"
maint_status="pass"
unit_status="pass"
parity_status="pass"
gold_status="pass"
conf_status="pass"
adapter_status="pass"
pack_status="pass"

> "$build_log"
if ! run_cmd "cmake --build --preset ${preset} --target dominium-setup2 setup2_kernel_tests setup2_services_fs_tests setup2_services_platform_tests setup2_kernel_services_tests setup2_splat_tests setup2_plan_tests setup2_apply_tests setup2_cli_golden_tests setup2_parity_lock_tests setup2_gold_master_tests setup2_conformance_runner setup2_conformance_repeat_tests setup2_adapter_steam_tests setup2_adapter_macos_pkg_tests setup2_adapter_linux_wrappers_tests setup2_adapter_wrapper_tests setup2_adapter_windows_tests setup2-adapters" "$build_log"; then
    build_status="fail"
fi

> "$maint_log"
if ! run_cmd "scripts/setup2/maintenance_checks.sh" "$maint_log"; then
    maint_status="fail"
fi

> "$unit_log"
if ! run_cmd "ctest --preset ${preset} -L setup2 -LE setup2_adapters -E \"setup2_conformance|setup2_parity_lock_|setup2_gold_master_\" --output-on-failure" "$unit_log"; then
    unit_status="fail"
fi

> "$parity_log"
if ! run_cmd "ctest --preset ${preset} -R setup2_parity_lock_ --output-on-failure" "$parity_log"; then
    parity_status="fail"
fi

> "$gold_log"
if ! run_cmd "ctest --preset ${preset} -R setup2_gold_master_ --output-on-failure" "$gold_log"; then
    gold_status="fail"
fi

> "$conf_log"
if ! run_cmd "ctest --preset ${preset} -R setup2_conformance --output-on-failure" "$conf_log"; then
    conf_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup2_conformance_repeat --output-on-failure" "$conf_log"; then
    conf_status="fail"
fi

> "$adapter_log"
if ! run_cmd "ctest --preset ${preset} -R setup2_adapter_steam --output-on-failure" "$adapter_log"; then
    adapter_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup2_adapter_windows_exe --output-on-failure" "$adapter_log"; then
    adapter_status="fail"
fi

> "$pack_log"
if ! run_cmd "ctest --preset ${preset} -R setup2_adapter_wrapper_scripts --output-on-failure" "$pack_log"; then
    pack_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup2_adapter_macos_pkg --output-on-failure" "$pack_log"; then
    pack_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup2_adapter_linux_wrappers --output-on-failure" "$pack_log"; then
    pack_status="fail"
fi

overall="pass"
if [ "$build_status" != "pass" ] || \
   [ "$maint_status" != "pass" ] || \
   [ "$unit_status" != "pass" ] || \
   [ "$parity_status" != "pass" ] || \
   [ "$gold_status" != "pass" ] || \
   [ "$conf_status" != "pass" ] || \
   [ "$adapter_status" != "pass" ] || \
   [ "$pack_status" != "pass" ]; then
    overall="fail"
fi

summary="$root/dist/release/setup2_release_gate_summary.json"
cat > "$summary" <<EOF
{
  "schema_version":"setup2-release-gate-1",
  "log_dir":"${log_dir_rel}",
  "stages":[
    {"name":"build","status":"${build_status}","log":"${log_dir_rel}/build.log"},
    {"name":"maintenance_checks","status":"${maint_status}","log":"${log_dir_rel}/maintenance.log"},
    {"name":"unit_tests","status":"${unit_status}","log":"${log_dir_rel}/unit_tests.log"},
    {"name":"parity_lock","status":"${parity_status}","log":"${log_dir_rel}/parity_lock.log"},
    {"name":"gold_master","status":"${gold_status}","log":"${log_dir_rel}/gold_master.log"},
    {"name":"conformance","status":"${conf_status}","log":"${log_dir_rel}/conformance.log"},
    {"name":"adapter_checks","status":"${adapter_status}","log":"${log_dir_rel}/adapter_checks.log"},
    {"name":"packaging_checks","status":"${pack_status}","log":"${log_dir_rel}/packaging_checks.log"}
  ],
  "overall":"${overall}"
}
EOF

if [ "$overall" != "pass" ]; then
    exit 1
fi
