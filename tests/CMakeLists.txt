cmake_minimum_required(VERSION 3.15)

option(DOM_BUILD_TESTS "Build Dominium tests" ON)
if(NOT DOM_BUILD_TESTS)
    return()
endif()

enable_testing()

add_executable(dom_test_dynarray unit/test_dynarray.c)
target_include_directories(dom_test_dynarray PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/source/core
    ${CMAKE_SOURCE_DIR}/source/core/base
)
target_link_libraries(dom_test_dynarray PRIVATE dom_core)
add_test(NAME dom_test_dynarray COMMAND dom_test_dynarray)

add_executable(dom_test_platform integration/test_platform_probe.c)
target_include_directories(dom_test_platform PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/source/core
    ${CMAKE_SOURCE_DIR}/source/core/base
)
target_link_libraries(dom_test_platform PRIVATE dom_core dom_platform dom_app_mode)
add_test(NAME dom_test_platform COMMAND dom_test_platform)
