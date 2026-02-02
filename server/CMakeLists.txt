cmake_minimum_required(VERSION 3.16)

add_executable(dominium_server
    app/main_server.c
    authority/dom_server_authority.cpp
    net/dom_server_protocol.cpp
    net/dom_server_runtime.cpp
    shard/shard_api.cpp
    shard/shard_router.cpp
    shard/shard_domain_index.cpp
    shard/dom_cross_shard_log.cpp
    shard/dom_global_id.cpp
    shard/dom_shard_lifecycle.cpp
    shard/domain_shard_mapper.cpp
    shard/task_splitter.cpp
    shard/message_bus.cpp
    shard/shard_executor.cpp
    shard/shard_hashing.cpp
    persistence/integrity_checkpoints.cpp
    persistence/dom_checkpointing.cpp
    persistence/dispute_bundle.cpp
)
target_link_libraries(dominium_server PRIVATE
    app::runtime
    domino_engine
    dominium_game
    libs::contracts
)
target_include_directories(dominium_server PRIVATE
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
)
set_target_properties(dominium_server PROPERTIES
    OUTPUT_NAME "server"
    LINKER_LANGUAGE CXX
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
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
        gui/server_app_win32.cpp
    )
    target_link_libraries(server_app_win32 PRIVATE
        libs::appcore
        shared_ui::win32
    )
    set_target_properties(server_app_win32 PROPERTIES
        OUTPUT_NAME "server_app_win32"
        CXX_STANDARD 98
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
        tests/shard_api_tests.cpp
        shard/shard_api.cpp
        shard/shard_router.cpp
        shard/shard_domain_index.cpp
        shard/domain_shard_mapper.cpp
        shard/task_splitter.cpp
        shard/message_bus.cpp
        shard/shard_executor.cpp
        shard/shard_hashing.cpp
        persistence/integrity_checkpoints.cpp
        persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_shard_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_link_libraries(dominium_server_shard_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_shard_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_shard_api COMMAND dominium_server_shard_tests)

    add_executable(dominium_server_shard_routing_tests
        tests/shard_routing_tests.cpp
        shard/shard_api.cpp
        shard/shard_router.cpp
        shard/shard_domain_index.cpp
        shard/domain_shard_mapper.cpp
        shard/task_splitter.cpp
        shard/message_bus.cpp
        shard/shard_executor.cpp
        shard/shard_hashing.cpp
        persistence/integrity_checkpoints.cpp
        persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_shard_routing_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_link_libraries(dominium_server_shard_routing_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_shard_routing_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_shard_routing COMMAND dominium_server_shard_routing_tests)

    add_executable(dominium_server_integrity_tests
        tests/integrity_checkpoint_tests.cpp
        shard/shard_api.cpp
        shard/shard_router.cpp
        shard/shard_domain_index.cpp
        shard/domain_shard_mapper.cpp
        shard/task_splitter.cpp
        shard/message_bus.cpp
        shard/shard_executor.cpp
        shard/shard_hashing.cpp
        persistence/integrity_checkpoints.cpp
        persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_integrity_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_link_libraries(dominium_server_integrity_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_integrity_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_integrity COMMAND dominium_server_integrity_tests)

    add_executable(dominium_server_shard_regression_tests
        tests/shard_regression_tests.cpp
        shard/shard_api.cpp
        shard/shard_router.cpp
        shard/shard_domain_index.cpp
        shard/domain_shard_mapper.cpp
        shard/task_splitter.cpp
        shard/message_bus.cpp
        shard/shard_executor.cpp
        shard/shard_hashing.cpp
        persistence/integrity_checkpoints.cpp
        persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_shard_regression_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_SOURCE_DIR}/engine/modules
    )
    target_compile_definitions(dominium_server_shard_regression_tests PRIVATE
        DOMINIUM_FIXTURES_DIR="${CMAKE_SOURCE_DIR}/game/tests/fixtures"
    )
    target_link_libraries(dominium_server_shard_regression_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_shard_regression_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_shard_regression COMMAND dominium_server_shard_regression_tests)

    add_executable(dominium_server_domain_shard_partition_tests
        tests/domain_shard_partition_tests.cpp
        shard/shard_api.cpp
        shard/shard_router.cpp
        shard/shard_domain_index.cpp
        shard/domain_shard_mapper.cpp
        shard/task_splitter.cpp
        shard/message_bus.cpp
        shard/shard_executor.cpp
        shard/shard_hashing.cpp
        persistence/integrity_checkpoints.cpp
        persistence/dispute_bundle.cpp
    )
    target_include_directories(dominium_server_domain_shard_partition_tests PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_link_libraries(dominium_server_domain_shard_partition_tests PRIVATE
        domino_engine
        dominium_game
    )
    set_target_properties(dominium_server_domain_shard_partition_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_test(NAME dominium_server_domain_shard_partition COMMAND dominium_server_domain_shard_partition_tests)
endif()
