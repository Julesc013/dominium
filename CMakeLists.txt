cmake_minimum_required(VERSION 3.16)
project(dominium LANGUAGES C CXX)

set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Public include root
set(DOMINIUM_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_subdirectory(source/domino/system)
add_subdirectory(source/domino/render)
add_subdirectory(source/domino/sim)
add_subdirectory(source/domino/mod)

add_subdirectory(source/dominium/rules)
add_subdirectory(source/dominium/product/launcher)
add_subdirectory(source/dominium/product/setup)
add_subdirectory(source/dominium/product/game)

add_subdirectory(tools)
add_subdirectory(tests)
