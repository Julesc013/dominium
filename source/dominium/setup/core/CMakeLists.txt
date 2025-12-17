cmake_minimum_required(VERSION 3.16)

add_library(dsu_core STATIC
    src/dsu_callbacks.c
    src/dsu_config.c
    src/dsu_ctx.c
    src/dsu_execute.c
    src/fs/dsu_fs.c
    src/fs/dsu_fs_stdio.c
    src/fs/dsu_platform_iface.c
    src/log/dsu_log.c
    src/manifest/dsu_manifest.c
    src/plan/dsu_plan.c
    src/resolve/dsu_resolve.c
    src/state/dsu_state.c
    src/txn/dsu_journal.c
    src/util/dsu_util_blob.c
    src/util/dsu_util_digest.c
    src/util/dsu_util_filefmt.c
    src/util/dsu_util_hash.c
    src/util/dsu_util_le.c
    src/util/dsu_util_mem.c
    src/util/dsu_util_sha256.c
    src/util/dsu_util_sort.c
    src/util/dsu_util_str.c
    src/util/dsu_util_tlv.c
)

target_include_directories(dsu_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(dsu_core PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
