cmake_minimum_required(VERSION 3.16)
project(dominium LANGUAGES C CXX)

set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Public include root
set(DOMINIUM_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

option(DOMINIUM_ENABLE_PACKAGING "Enable packaging helper targets" OFF)

# Core source trees
add_subdirectory(source/domino)
add_subdirectory(source/dominium)
add_subdirectory(tools)
add_subdirectory(tests)

if(DOMINIUM_ENABLE_PACKAGING)
    add_subdirectory(scripts/packaging)
endif()
