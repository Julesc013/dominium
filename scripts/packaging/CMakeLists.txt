cmake_minimum_required(VERSION 3.15)

file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Configure POSIX scripts
if (UNIX)
    if (APPLE)
        set(DOM_LAUNCHER_PLATFORM "MACOSX")
        set(DOM_LAUNCHER_BINARY   "dom_launcher")
        set(DOM_SETUP_BINARY      "dom_setup")
    else()
        set(DOM_LAUNCHER_PLATFORM "POSIX")
        set(DOM_LAUNCHER_BINARY   "dom_launcher")
        set(DOM_SETUP_BINARY      "dom_setup")
    endif()

    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/dominium.sh.in
        ${CMAKE_BINARY_DIR}/bin/dominium
        @ONLY
    )
    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/setup.sh.in
        ${CMAKE_BINARY_DIR}/bin/setup
        @ONLY
    )
    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/dom-client.sh.in
        ${CMAKE_BINARY_DIR}/bin/dom-client
        @ONLY
    )
    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/dom-server.sh.in
        ${CMAKE_BINARY_DIR}/bin/dom-server
        @ONLY
    )

    install(PROGRAMS
        ${CMAKE_BINARY_DIR}/bin/dominium
        ${CMAKE_BINARY_DIR}/bin/setup
        ${CMAKE_BINARY_DIR}/bin/dom-client
        ${CMAKE_BINARY_DIR}/bin/dom-server
        DESTINATION bin
    )
endif()

# Configure Windows scripts
if (WIN32)
    set(DOM_LAUNCHER_BINARY "dom_launcher.exe")
    set(DOM_SETUP_BINARY    "dom_setup.exe")

    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/dominium.cmd.in
        ${CMAKE_BINARY_DIR}/bin/dominium.cmd
        @ONLY
    )
    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/setup.cmd.in
        ${CMAKE_BINARY_DIR}/bin/setup.cmd
        @ONLY
    )
    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/dom-client.cmd.in
        ${CMAKE_BINARY_DIR}/bin/dom-client.cmd
        @ONLY
    )
    configure_file(
        ${CMAKE_SOURCE_DIR}/packaging/scripts/dom-server.cmd.in
        ${CMAKE_BINARY_DIR}/bin/dom-server.cmd
        @ONLY
    )

    install(PROGRAMS
        ${CMAKE_BINARY_DIR}/bin/dominium.cmd
        ${CMAKE_BINARY_DIR}/bin/setup.cmd
        ${CMAKE_BINARY_DIR}/bin/dom-client.cmd
        ${CMAKE_BINARY_DIR}/bin/dom-server.cmd
        DESTINATION bin
    )
endif()

if (WIN32)
    add_subdirectory(windows)
endif()

if (APPLE)
    add_subdirectory(macos)
endif()

if (UNIX AND NOT APPLE)
    add_subdirectory(linux)
endif()
