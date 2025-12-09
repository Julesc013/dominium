cmake_minimum_required(VERSION 3.16)

if(NOT UNIX OR APPLE)
    return()
endif()

option(DOMINIUM_BUILD_DEB "Build Debian package" ON)
option(DOMINIUM_BUILD_RPM "Build RPM package" ON)
option(DOMINIUM_BUILD_RUN "Build self-extracting .run installer" ON)

set(DOMINIUM_VERSION "1.0.0" CACHE STRING "Dominium product version for Linux packaging")
set(DOMINIUM_DIST_DIR "${CMAKE_BINARY_DIR}/dist" CACHE PATH "Staging directory with dominium binaries/data")
set(DOMINIUM_INSTALLER_DIR "${CMAKE_BINARY_DIR}/dist/installers/linux" CACHE PATH "Output directory for Linux installers")
set(DOMINIUM_DEB_DEPENDS "libc6, libstdc++6" CACHE STRING "Debian dependencies")
set(DOMINIUM_DEB_MAINTAINER "Dominium Team <support@dominium.invalid>" CACHE STRING "Debian maintainer field")
set(DOMINIUM_RPM_REQUIRES "libstdc++" CACHE STRING "RPM Requires line")
set(DOMINIUM_RPM_RELEASE "1" CACHE STRING "RPM Release field")

find_program(DPKG_DEB_EXECUTABLE dpkg-deb)
find_program(RPMBUILD_EXECUTABLE rpmbuild)
find_program(BASH_EXECUTABLE bash)

file(MAKE_DIRECTORY "${DOMINIUM_INSTALLER_DIR}")

# Configure static templates
set(VERSION "${DOMINIUM_VERSION}")
set(MAINTAINER "${DOMINIUM_DEB_MAINTAINER}")
set(DEPENDS "${DOMINIUM_DEB_DEPENDS}")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/deb/DEBIAN/control.in"
    "${CMAKE_CURRENT_BINARY_DIR}/deb/control"
    @ONLY
)

set(RELEASE "${DOMINIUM_RPM_RELEASE}")
set(REQUIRES "${DOMINIUM_RPM_REQUIRES}")
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/rpm/dominium.spec.in"
    "${CMAKE_CURRENT_BINARY_DIR}/rpm/dominium.spec"
    @ONLY
)

if(DOMINIUM_BUILD_DEB)
    if(NOT DPKG_DEB_EXECUTABLE)
        message(WARNING "dpkg-deb not found; dominium_deb target disabled")
    else()
        set(_deb_root "${DOMINIUM_INSTALLER_DIR}/deb/dominium_${DOMINIUM_VERSION}_amd64")
        set(_deb_pkg "${DOMINIUM_INSTALLER_DIR}/dominium_${DOMINIUM_VERSION}_amd64.deb")

        add_custom_command(
            OUTPUT "${_deb_pkg}"
            COMMAND "${CMAKE_COMMAND}" -E rm -rf "${_deb_root}"
            COMMAND "${CMAKE_COMMAND}" -E make_directory "${_deb_root}/DEBIAN"
            COMMAND "${CMAKE_COMMAND}" -E make_directory "${_deb_root}/opt/dominium"
            COMMAND "${CMAKE_COMMAND}" -E copy_directory "${DOMINIUM_DIST_DIR}/" "${_deb_root}/opt/dominium"
            COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_CURRENT_BINARY_DIR}/deb/control" "${_deb_root}/DEBIAN/control"
            COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_CURRENT_SOURCE_DIR}/deb/DEBIAN/postinst" "${_deb_root}/DEBIAN/postinst"
            COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_CURRENT_SOURCE_DIR}/deb/DEBIAN/prerm" "${_deb_root}/DEBIAN/prerm"
            COMMAND "${CMAKE_COMMAND}" -E copy "${CMAKE_CURRENT_SOURCE_DIR}/deb/DEBIAN/postrm" "${_deb_root}/DEBIAN/postrm"
            COMMAND "${CMAKE_COMMAND}" -E chmod 0755 "${_deb_root}/DEBIAN/postinst" "${_deb_root}/DEBIAN/prerm" "${_deb_root}/DEBIAN/postrm"
            COMMAND "${DPKG_DEB_EXECUTABLE}" --build "${_deb_root}" "${_deb_pkg}"
            DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/deb/control"
            COMMENT "dpkg-deb -> ${_deb_pkg}"
        )

        add_custom_target(dominium_deb
            DEPENDS "${_deb_pkg}"
        )
    endif()
endif()

if(DOMINIUM_BUILD_RPM)
    if(NOT RPMBUILD_EXECUTABLE)
        message(WARNING "rpmbuild not found; dominium_rpm target disabled")
    else()
        set(_rpm_top "${DOMINIUM_INSTALLER_DIR}/rpm")
        set(_rpm_pkg "${DOMINIUM_INSTALLER_DIR}/dominium-${DOMINIUM_VERSION}-${DOMINIUM_RPM_RELEASE}.x86_64.rpm")

        add_custom_command(
            OUTPUT "${_rpm_pkg}"
            COMMAND "${CMAKE_COMMAND}" -E rm -rf "${_rpm_top}"
            COMMAND "${CMAKE_COMMAND}" -E make_directory "${_rpm_top}/SOURCES"
            COMMAND "${CMAKE_COMMAND}" -E make_directory "${_rpm_top}/BUILD"
            COMMAND "${CMAKE_COMMAND}" -E make_directory "${_rpm_top}/RPMS"
            COMMAND "${CMAKE_COMMAND}" -E copy_directory "${DOMINIUM_DIST_DIR}/" "${_rpm_top}/SOURCES/dominium"
            COMMAND "${RPMBUILD_EXECUTABLE}" -bb
                --define "_topdir ${_rpm_top}"
                --define "_sourcedir ${_rpm_top}/SOURCES"
                --define "_rpmdir ${DOMINIUM_INSTALLER_DIR}"
                --define "_srcrpmdir ${DOMINIUM_INSTALLER_DIR}"
                --define "_builddir ${_rpm_top}/BUILD"
                --define "_buildrootdir ${_rpm_top}/BUILDROOT"
                --define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm"
                "${CMAKE_CURRENT_BINARY_DIR}/rpm/dominium.spec"
            DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/rpm/dominium.spec"
            COMMENT "rpmbuild -> ${_rpm_pkg}"
        )

        add_custom_target(dominium_rpm
            DEPENDS "${_rpm_pkg}"
        )
    endif()
endif()

if(DOMINIUM_BUILD_RUN)
    if(NOT BASH_EXECUTABLE)
        message(WARNING "bash not found; dominium_run target disabled")
    else()
        set(_run_path "${DOMINIUM_INSTALLER_DIR}/Dominium-${DOMINIUM_VERSION}.run")
        add_custom_command(
            OUTPUT "${_run_path}"
            COMMAND "${CMAKE_COMMAND}" -E env
                DIST_DIR="${DOMINIUM_DIST_DIR}"
                VERSION="${DOMINIUM_VERSION}"
                OUT_DIR="${DOMINIUM_INSTALLER_DIR}"
                STUB_TEMPLATE="${CMAKE_CURRENT_SOURCE_DIR}/dominium-installer.sh.in"
                "${BASH_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/build_run.sh"
            DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/build_run.sh" "${CMAKE_CURRENT_SOURCE_DIR}/dominium-installer.sh.in"
            COMMENT "Building Dominium self-extracting .run"
        )

        add_custom_target(dominium_run
            DEPENDS "${_run_path}"
        )
    endif()
endif()
