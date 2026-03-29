cmake_minimum_required(VERSION 3.16)

add_library(dsu_core STATIC
    dsu_callbacks.c
    dsu_config.c
    dsu_ctx.c
    dsu_execute.c
    invocation/dsu_invocation.c
    fs/dsu_fs.c
    fs/dsu_fs_stdio.c
    platform_iface/dsu_platform_iface.c
    log/dsu_log.c
    job/dsu_job.c
    manifest/dsu_manifest.c
    plan/dsu_plan.c
    report/dsu_report.c
    resolve/dsu_resolve.c
    state/dsu_state_s5.c
    txn/dsu_journal.c
    txn/dsu_txn.c
    util/dsu_util_archive.c
    util/dsu_util_blob.c
    util/dsu_util_digest.c
    util/dsu_util_filefmt.c
    util/dsu_util_hash.c
    util/dsu_util_le.c
    util/dsu_util_mem.c
    util/dsu_util_sha256.c
    util/dsu_util_sort.c
    util/dsu_util_str.c
    util/dsu_util_tlv.c
)

target_include_directories(dsu_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${PROJECT_SOURCE_DIR}/include
)

target_link_libraries(dsu_core
    PRIVATE
        core_tlv
        core_audit
        core_util
        core_err
        core_job
        core_log
)

set_target_properties(dsu_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_library(setup_kernel ALIAS dsu_core)
