add_executable(distribution_single_package_tests
    distribution_single_package_tests.c
)
target_include_directories(distribution_single_package_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
)
target_link_libraries(distribution_single_package_tests PRIVATE
    libs::contracts
)
set_target_properties(distribution_single_package_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME distribution_single_package COMMAND distribution_single_package_tests)
