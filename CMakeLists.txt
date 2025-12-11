cmake_minimum_required(VERSION 3.16)
project(DominiumDomino LANGUAGES C CXX)

set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 98)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(DOMINIUM_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(DominiumBundleRuntime)

option(DOMINIUM_STATIC_GNU_RUNTIME "Link libgcc/libstdc++ statically on MinGW/MSYS" ON)
if(DOMINIUM_STATIC_GNU_RUNTIME AND (MINGW OR MSYS))
    add_link_options(-static-libgcc -static-libstdc++)
endif()

set(DOMINIUM_RUNTIME_SEARCH_DIRS "")
if(WIN32 AND (MINGW OR MSYS))
    get_filename_component(_dom_toolchain_bindir "${CMAKE_C_COMPILER}" DIRECTORY)
    list(APPEND DOMINIUM_RUNTIME_SEARCH_DIRS "${_dom_toolchain_bindir}")
    if(CMAKE_PREFIX_PATH)
        list(APPEND DOMINIUM_RUNTIME_SEARCH_DIRS ${CMAKE_PREFIX_PATH})
    endif()
endif()

option(DOMINIUM_ENABLE_PACKAGING "Enable packaging helper targets" OFF)

add_subdirectory(source/domino)
add_subdirectory(source/dominium)
add_subdirectory(source/tests)

if(DOMINIUM_ENABLE_PACKAGING)
    add_subdirectory(scripts/packaging)
endif()

set(CPACK_PACKAGE_NAME "dominium")
set(CPACK_PACKAGE_VENDOR "Dominium")
set(CPACK_PACKAGE_CONTACT "support@dominium.invalid")
set(CPACK_PACKAGE_VERSION "0.1.0")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_SECTION "games")
set(CPACK_RPM_PACKAGE_LICENSE "MIT")
set(CPACK_RPM_PACKAGE_URL "https://example.com/dominium")
include(CPack)
