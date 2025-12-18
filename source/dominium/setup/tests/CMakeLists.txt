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

add_executable(dsu_cli_test
    dsu_cli_test.c
)

target_include_directories(dsu_cli_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../core/include
)

target_link_libraries(dsu_cli_test
    PRIVATE dsu_core
)

add_dependencies(dsu_cli_test
    dominium-setup
)

set_target_properties(dsu_cli_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

add_test(NAME dsu_cli_test COMMAND dsu_cli_test $<TARGET_FILE:dominium-setup> ${CMAKE_CURRENT_SOURCE_DIR})
set_tests_properties(dsu_cli_test PROPERTIES
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

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

find_program(DOMINIUM_PYTHON NAMES python3 python)
if(DOMINIUM_PYTHON)
    set(_dom_repo_root "${CMAKE_CURRENT_SOURCE_DIR}/../../../../")
    set(_dom_packaging_test "${_dom_repo_root}/scripts/packaging/tests/packaging_validation_test.py")
    set(_dom_manifest_template "${_dom_repo_root}/assets/setup/manifests/product.template.json")

    add_test(
        NAME dsu_packaging_validation_test
        COMMAND
            ${DOMINIUM_PYTHON}
            ${_dom_packaging_test}
            --build-dir ${CMAKE_BINARY_DIR}
            --version 0.1.0
            --manifest-template ${_dom_manifest_template}
    )

    set_tests_properties(dsu_packaging_validation_test PROPERTIES
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        ENVIRONMENT "SOURCE_DATE_EPOCH=946684800"
    )
endif()
