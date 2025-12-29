cmake_minimum_required(VERSION 3.16)

add_library(dss_services STATIC
    src/services/dss_error.cpp
    src/services/dss_services.cpp
    src/fs/dss_fs_iface.cpp
    src/fs/dss_fs_real.cpp
    src/fs/dss_fs_fake.cpp
    src/proc/dss_proc_iface.cpp
    src/proc/dss_proc_real.cpp
    src/proc/dss_proc_fake.cpp
    src/hash/dss_hash_iface.cpp
    src/hash/dss_hash_real.cpp
    src/hash/dss_hash_fake.cpp
    src/archive/dss_archive_iface.cpp
    src/archive/dss_archive_real.cpp
    src/archive/dss_archive_fake.cpp
    src/perms/dss_perms_iface.cpp
    src/perms/dss_perms_real.cpp
    src/perms/dss_perms_fake.cpp
    src/platform/dss_platform_real.cpp
    src/platform/dss_platform_fake.cpp
    src/registry_win/dss_registry_win_iface.cpp
    src/registry_win/dss_registry_win_real.cpp
    src/registry_win/dss_registry_win_fake.cpp
    src/pkgmgr_linux/dss_pkgmgr_linux_iface.cpp
    src/pkgmgr_linux/dss_pkgmgr_linux_real.cpp
    src/pkgmgr_linux/dss_pkgmgr_linux_fake.cpp
    src/codesign_macos/dss_codesign_macos_iface.cpp
    src/codesign_macos/dss_codesign_macos_real.cpp
    src/codesign_macos/dss_codesign_macos_fake.cpp
)

target_include_directories(dss_services PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)

target_include_directories(dss_services PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/util
)

target_link_libraries(dss_services
    PRIVATE
        dsu_core
)

set_target_properties(dss_services PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_library(setup_services_impl_platform STATIC
    platform/dsu_platform_iface.c
)

target_include_directories(setup_services_impl_platform PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/fs
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/util
)

target_link_libraries(setup_services_impl_platform
    PRIVATE
        setup_kernel
)

set_target_properties(setup_services_impl_platform PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_library(setup_services_impl_null STATIC
    null/dsu_platform_iface_null.c
)

target_include_directories(setup_services_impl_null PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/fs
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/core/src/util
)

target_link_libraries(setup_services_impl_null
    PRIVATE
        setup_kernel
)

set_target_properties(setup_services_impl_null PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
