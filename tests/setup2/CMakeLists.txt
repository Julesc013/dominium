cmake_minimum_required(VERSION 3.16)

add_executable(setup2_adapter_steam_tests
    test_adapter_steam.cpp
)
target_include_directories(setup2_adapter_steam_tests PRIVATE
    ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
)
target_link_libraries(setup2_adapter_steam_tests PRIVATE
    dsk_kernel
)
set_target_properties(setup2_adapter_steam_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_dependencies(setup2_adapter_steam_tests
    dominium-setup2
    dominium-setup2-steam
)
add_test(NAME setup2_adapter_steam
    COMMAND setup2_adapter_steam_tests
        $<TARGET_FILE:dominium-setup2>
        $<TARGET_FILE:dominium-setup2-steam>
        ${CMAKE_CURRENT_BINARY_DIR}/adapter_steam
)

add_executable(setup2_adapter_macos_pkg_tests
    test_adapter_macos_pkg.cpp
)
set_target_properties(setup2_adapter_macos_pkg_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_adapter_macos_pkg
    COMMAND setup2_adapter_macos_pkg_tests
        ${CMAKE_SOURCE_DIR}
)

add_executable(setup2_adapter_linux_wrappers_tests
    test_adapter_linux_wrappers.cpp
)
set_target_properties(setup2_adapter_linux_wrappers_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_adapter_linux_wrappers
    COMMAND setup2_adapter_linux_wrappers_tests
        ${CMAKE_SOURCE_DIR}
)

add_executable(setup2_adapter_wrapper_tests
    test_adapter_wrapper_scripts.cpp
)
set_target_properties(setup2_adapter_wrapper_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME setup2_adapter_wrapper_scripts
    COMMAND setup2_adapter_wrapper_tests
        ${CMAKE_SOURCE_DIR}
)

if(WIN32)
    add_executable(setup2_adapter_windows_tests
        test_adapter_windows_exe.cpp
    )
    target_include_directories(setup2_adapter_windows_tests PRIVATE
        ${CMAKE_SOURCE_DIR}/source/dominium/setup/kernel/include
    )
    target_link_libraries(setup2_adapter_windows_tests PRIVATE
        dsk_kernel
    )
    set_target_properties(setup2_adapter_windows_tests PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_dependencies(setup2_adapter_windows_tests
        dominium-setup2
        dominium-setup2-win-exe
    )
    add_test(NAME setup2_adapter_windows_exe
        COMMAND setup2_adapter_windows_tests
            $<TARGET_FILE:dominium-setup2>
            $<TARGET_FILE:dominium-setup2-win-exe>
            ${CMAKE_CURRENT_BINARY_DIR}/adapter_windows
    )
endif()
