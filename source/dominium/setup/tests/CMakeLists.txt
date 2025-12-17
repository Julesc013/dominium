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

