cmake_minimum_required(VERSION 3.15)

add_executable(dom_tests
    tests_runner.c
)

target_include_directories(dom_tests
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
)

target_link_libraries(dom_tests
    PRIVATE
        dom_engine
)

if(TARGET dom_setup_lib)
    add_executable(dom_manifest_tests
        manifest_io_test.cpp
    )
    target_link_libraries(dom_manifest_tests PRIVATE dom_setup_lib)
    target_include_directories(dom_manifest_tests PRIVATE ${CMAKE_SOURCE_DIR}/setup/include)

    add_executable(dom_setup_flow_test
        setup_flow_test.cpp
    )
    target_link_libraries(dom_setup_flow_test PRIVATE dom_setup_lib)
    target_include_directories(dom_setup_flow_test PRIVATE ${CMAKE_SOURCE_DIR}/setup/include)
endif()

if(TARGET dom_launcher_lib)
    add_executable(dom_launcher_tests
        launcher_discovery_test.cpp
    )
    target_link_libraries(dom_launcher_tests PRIVATE dom_launcher_lib dom_setup_lib)
    target_include_directories(dom_launcher_tests PRIVATE ${CMAKE_SOURCE_DIR}/launcher/include ${CMAKE_SOURCE_DIR}/setup/include)
endif()
