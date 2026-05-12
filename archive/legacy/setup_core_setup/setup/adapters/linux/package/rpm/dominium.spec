Name:           dominium
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Dominium setup bundle

License:        MIT
URL:            https://example.com/dominium
BuildArch:      @ARCH@
Requires:       @REQUIRES@

%description
Dominium payloads and Setup Core frontends. Installation and removal are
performed by Setup Core to preserve parity across platforms.

%prep
%setup -T -c -a 0

%build
# Prebuilt binaries only.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/dominium/artifact_root
cp -a %{_sourcedir}/dominium/artifact_root/. %{buildroot}/opt/dominium/artifact_root/

%post
if [ -x /opt/dominium/artifact_root/setup/dominium-setup ]; then
    cd /opt/dominium/artifact_root
    /opt/dominium/artifact_root/setup/dominium-setup --deterministic 1 export-invocation --manifest setup/manifests/product.dsumanifest --op install --scope system --ui-mode cli --frontend-id rpm --out /tmp/dominium_install.dsuinv || true
    /opt/dominium/artifact_root/setup/dominium-setup --deterministic 1 plan --manifest setup/manifests/product.dsumanifest --invocation /tmp/dominium_install.dsuinv --out /tmp/dominium_install.dsuplan || true
    /opt/dominium/artifact_root/setup/dominium-setup --deterministic 1 apply --plan /tmp/dominium_install.dsuplan || true
fi
if [ -x /opt/dominium/artifact_root/setup/dominium-setup-linux ] && [ -f /opt/dominium/.dsu/installed_state.dsustate ]; then
    /opt/dominium/artifact_root/setup/dominium-setup-linux platform-register --state /opt/dominium/.dsu/installed_state.dsustate --deterministic || true
fi

%preun
if [ $1 -eq 0 ] && [ -x /opt/dominium/artifact_root/setup/dominium-setup-linux ] && [ -f /opt/dominium/.dsu/installed_state.dsustate ]; then
    /opt/dominium/artifact_root/setup/dominium-setup-linux platform-unregister --state /opt/dominium/.dsu/installed_state.dsustate --deterministic || true
fi
if [ $1 -eq 0 ] && [ -x /opt/dominium/artifact_root/setup/dominium-setup ] && [ -f /opt/dominium/.dsu/installed_state.dsustate ]; then
    cd /opt/dominium/artifact_root
    /opt/dominium/artifact_root/setup/dominium-setup --deterministic 1 export-invocation --manifest setup/manifests/product.dsumanifest --state /opt/dominium/.dsu/installed_state.dsustate --op uninstall --scope system --ui-mode cli --frontend-id rpm --out /tmp/dominium_uninstall.dsuinv || true
    /opt/dominium/artifact_root/setup/dominium-setup --deterministic 1 plan --manifest setup/manifests/product.dsumanifest --state /opt/dominium/.dsu/installed_state.dsustate --invocation /tmp/dominium_uninstall.dsuinv --out /tmp/dominium_uninstall.dsuplan || true
    /opt/dominium/artifact_root/setup/dominium-setup --deterministic 1 apply --plan /tmp/dominium_uninstall.dsuplan || true
fi

%files
/opt/dominium
