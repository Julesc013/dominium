cmake_minimum_required(VERSION 3.16)

add_executable(dsu_core_smoke_test
    dsu_core_smoke_test.c
)

target_include_directories(dsu_core_smoke_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_core_smoke_test
    PRIVATE dsu_core
)

set_target_properties(dsu_core_smoke_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_core_smoke_test COMMAND dsu_core_smoke_test)

add_executable(dsu_manifest_test
    dsu_manifest_test.c
)

target_include_directories(dsu_manifest_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_manifest_test
    PRIVATE dsu_core
)

set_target_properties(dsu_manifest_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_manifest_test COMMAND dsu_manifest_test)

add_executable(dsu_resolve_test
    dsu_resolve_test.c
)

target_include_directories(dsu_resolve_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_resolve_test
    PRIVATE dsu_core
)

set_target_properties(dsu_resolve_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_resolve_test COMMAND dsu_resolve_test)

add_executable(dsu_txn_test
    dsu_txn_test.c
)

target_include_directories(dsu_txn_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_txn_test
    PRIVATE dsu_core
)

set_target_properties(dsu_txn_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_txn_test COMMAND dsu_txn_test)

if(WIN32)
    add_executable(dsu_adapter_smoke_test
        dsu_adapter_smoke_test.c
    )

    target_include_directories(dsu_adapter_smoke_test PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
    )

    target_link_libraries(dsu_adapter_smoke_test
        PRIVATE dsu_core
    )

    add_dependencies(dsu_adapter_smoke_test
        dominium-setup-win
        dominium-setup-steam
    )

    set_target_properties(dsu_adapter_smoke_test PROPERTIES
        C_STANDARD 90
        C_STANDARD_REQUIRED ON
        C_EXTENSIONS OFF
    )

    add_test(NAME dsu_adapter_smoke_test COMMAND dsu_adapter_smoke_test)
endif()
