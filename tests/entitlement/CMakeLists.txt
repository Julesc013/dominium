add_executable(entitlement_mapping_tests
    entitlement_mapping_tests.c
)
target_link_libraries(entitlement_mapping_tests PRIVATE
    launcher_core
)
target_include_directories(entitlement_mapping_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
)
set_target_properties(entitlement_mapping_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME entitlement_mapping COMMAND entitlement_mapping_tests)
