cmake_minimum_required(VERSION 3.16)

add_executable(dominium_server
    main_server.c
    ${CMAKE_SOURCE_DIR}/game/law/authority/dom_server_authority.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/dom_server_protocol.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/dom_server_runtime.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_api.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_router.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_domain_index.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/dom_cross_shard_log.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/dom_global_id.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/dom_shard_lifecycle.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/domain_shard_mapper.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/task_splitter.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/message_bus.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_executor.cpp
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_hashing.cpp
    ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/integrity_checkpoints.cpp
    ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dom_checkpointing.cpp
    ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dispute_bundle.cpp
)
target_link_libraries(dominium_server PRIVATE
    app::runtime
    domino_engine
    dominium_game
    libs::contracts
)
target_include_directories(dominium_server PRIVATE
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${CMAKE_SOURCE_DIR}/runtime/network/server
    ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
    ${CMAKE_SOURCE_DIR}/runtime/storage/server
    ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
)
set_target_properties(dominium_server PROPERTIES
    OUTPUT_NAME "server"
    LINKER_LANGUAGE CXX
    C_STANDARD 17
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
target_include_directories(dominium_server PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)
add_executable(dom_server ALIAS dominium_server)
dom_register_product(server dominium_server)

if(WIN32)
    add_executable(server_app_win32 WIN32
        ${CMAKE_SOURCE_DIR}/runtime/platform/win32/server/server_app_win32.cpp
    )
    target_link_libraries(server_app_win32 PRIVATE
        libs::appcore
        runtime_platform_win32_ui
    )
    set_target_properties(server_app_win32 PROPERTIES
        OUTPUT_NAME "server_app_win32"
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    if(TARGET ui_bind_phase)
        add_dependencies(server_app_win32 ui_bind_phase)
    endif()
    if(MSVC)
        target_compile_options(server_app_win32 PRIVATE /W4 /WX)
    endif()
endif()

if(DOM_BUILD_TESTS)
    add_executable(dominium_server_shard_tests
        ${CMAKE_SOURCE_DIR}/tests/server/shard_api_tests.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_api.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_router.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_domain_index.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/domain_shard_mapper.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/task_splitter.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/message_bus.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_executor.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_hashing.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/integrity_checkpoints.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_shard_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/runtime/network/server
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
        ${CMAKE_SOURCE_DIR}/runtime/storage/server
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
    )
    target_link_libraries(dominium_server_shard_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_shard_tests PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_shard_api COMMAND dominium_server_shard_tests)

    add_executable(dominium_server_shard_routing_tests
        ${CMAKE_SOURCE_DIR}/tests/server/shard_routing_tests.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_api.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_router.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_domain_index.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/domain_shard_mapper.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/task_splitter.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/message_bus.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_executor.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_hashing.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/integrity_checkpoints.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_shard_routing_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/runtime/network/server
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
        ${CMAKE_SOURCE_DIR}/runtime/storage/server
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
    )
    target_link_libraries(dominium_server_shard_routing_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_shard_routing_tests PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_shard_routing COMMAND dominium_server_shard_routing_tests)

    add_executable(dominium_server_integrity_tests
        ${CMAKE_SOURCE_DIR}/tests/server/integrity_checkpoint_tests.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_api.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_router.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_domain_index.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/domain_shard_mapper.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/task_splitter.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/message_bus.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_executor.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_hashing.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/integrity_checkpoints.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_integrity_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/runtime/network/server
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
        ${CMAKE_SOURCE_DIR}/runtime/storage/server
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
    )
    target_link_libraries(dominium_server_integrity_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_integrity_tests PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_integrity COMMAND dominium_server_integrity_tests)

    add_executable(dominium_server_shard_regression_tests
        ${CMAKE_SOURCE_DIR}/tests/server/shard_regression_tests.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_api.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_router.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_domain_index.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/domain_shard_mapper.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/task_splitter.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/message_bus.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_executor.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_hashing.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/integrity_checkpoints.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_shard_regression_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/runtime/network/server
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
        ${CMAKE_SOURCE_DIR}/runtime/storage/server
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
        ${CMAKE_SOURCE_DIR}/engine
        ${CMAKE_SOURCE_DIR}/engine/kernel
    )
    target_compile_definitions(dominium_server_shard_regression_tests PRIVATE
        DOMINIUM_FIXTURES_DIR="${CMAKE_SOURCE_DIR}/tests/game/fixtures"
    )
    target_link_libraries(dominium_server_shard_regression_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_shard_regression_tests PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_shard_regression COMMAND dominium_server_shard_regression_tests)

    add_executable(dominium_server_domain_shard_partition_tests
        ${CMAKE_SOURCE_DIR}/tests/server/domain_shard_partition_tests.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_api.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_router.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_domain_index.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/domain_shard_mapper.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/task_splitter.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/message_bus.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_executor.cpp
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard/shard_hashing.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/integrity_checkpoints.cpp
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_domain_shard_partition_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/runtime/network/server
        ${CMAKE_SOURCE_DIR}/runtime/network/server/shard
        ${CMAKE_SOURCE_DIR}/runtime/storage/server
        ${CMAKE_SOURCE_DIR}/runtime/storage/server/persistence
    )
    target_link_libraries(dominium_server_domain_shard_partition_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_domain_shard_partition_tests PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_domain_shard_partition COMMAND dominium_server_domain_shard_partition_tests)
endif()
