#!/usr/bin/env bash
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
preset="${1:-debug}"
log_dir="$root/dist/release/setup_release_gate"
log_dir_rel="dist/release/setup_release_gate"

mkdir -p "$log_dir"

build_log="$log_dir/build.log"
maint_log="$log_dir/maintenance.log"
unit_log="$log_dir/unit_tests.log"
parity_log="$log_dir/parity_lock.log"
gold_log="$log_dir/gold_master.log"
conf_log="$log_dir/conformance.log"
adapter_log="$log_dir/adapter_checks.log"
pack_log="$log_dir/packaging_checks.log"
frontend_log="$log_dir/frontend_purity.log"

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
frontend_status="pass"

> "$build_log"
if ! run_cmd "cmake --build --preset ${preset} --target dominium-setup setup_kernel_tests setup_services_fs_tests setup_services_platform_tests setup_kernel_services_tests setup_splat_tests setup_plan_tests setup_apply_tests setup_cli_golden_tests setup_parity_lock_tests setup_gold_master_tests setup_conformance_runner setup_conformance_repeat_tests setup_adapter_steam_tests setup_adapter_macos_pkg_tests setup_adapter_linux_wrappers_tests setup_adapter_wrapper_tests setup_adapter_windows_tests setup-adapters" "$build_log"; then
    build_status="fail"
fi

> "$maint_log"
if ! run_cmd "scripts/setup/maintenance_checks.sh" "$maint_log"; then
    maint_status="fail"
fi

> "$frontend_log"
if ! run_cmd "scripts/setup2/check_frontend_purity.sh" "$frontend_log"; then
    frontend_status="fail"
fi

> "$unit_log"
if ! run_cmd "ctest --preset ${preset} -L setup -LE setup_adapters -E \"setup_conformance|setup_parity_lock_|setup_gold_master_\" --output-on-failure" "$unit_log"; then
    unit_status="fail"
fi

> "$parity_log"
if ! run_cmd "ctest --preset ${preset} -R setup_parity_lock_ --output-on-failure" "$parity_log"; then
    parity_status="fail"
fi

> "$gold_log"
if ! run_cmd "ctest --preset ${preset} -R setup_gold_master_ --output-on-failure" "$gold_log"; then
    gold_status="fail"
fi

> "$conf_log"
if ! run_cmd "ctest --preset ${preset} -R setup_conformance --output-on-failure" "$conf_log"; then
    conf_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup_conformance_repeat --output-on-failure" "$conf_log"; then
    conf_status="fail"
fi

> "$adapter_log"
if ! run_cmd "ctest --preset ${preset} -R setup_adapter_steam --output-on-failure" "$adapter_log"; then
    adapter_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup_adapter_windows_exe --output-on-failure" "$adapter_log"; then
    adapter_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup_adapter_macos_gui_export --output-on-failure" "$adapter_log"; then
    adapter_status="fail"
fi

> "$pack_log"
if ! run_cmd "ctest --preset ${preset} -R setup_adapter_wrapper_scripts --output-on-failure" "$pack_log"; then
    pack_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup_adapter_macos_pkg --output-on-failure" "$pack_log"; then
    pack_status="fail"
fi
if ! run_cmd "ctest --preset ${preset} -R setup_adapter_linux_wrappers --output-on-failure" "$pack_log"; then
    pack_status="fail"
fi

overall="pass"
if [ "$build_status" != "pass" ] || \
   [ "$maint_status" != "pass" ] || \
   [ "$frontend_status" != "pass" ] || \
   [ "$unit_status" != "pass" ] || \
   [ "$parity_status" != "pass" ] || \
   [ "$gold_status" != "pass" ] || \
   [ "$conf_status" != "pass" ] || \
   [ "$adapter_status" != "pass" ] || \
   [ "$pack_status" != "pass" ]; then
    overall="fail"
fi

summary="$root/dist/release/setup_release_gate_summary.json"
cat > "$summary" <<EOF
{
  "schema_version":"setup-release-gate-1",
  "log_dir":"${log_dir_rel}",
  "stages":[
    {"name":"build","status":"${build_status}","log":"${log_dir_rel}/build.log"},
    {"name":"maintenance_checks","status":"${maint_status}","log":"${log_dir_rel}/maintenance.log"},
    {"name":"frontend_purity","status":"${frontend_status}","log":"${log_dir_rel}/frontend_purity.log"},
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
