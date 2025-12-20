# Dominium packaging entrypoints (Plan S-8)
#
# These targets produce distribution artifacts from already-built outputs.
# They do not download dependencies and must not perform network calls.

PY ?= python3

# Build directory must contain built targets (dominium-setup, dominium-launcher, dominium_game).
BUILD_DIR ?= build/base-msys2

# Artifact/product version used for naming.
VERSION ?= 0.1.0
MANIFEST_TEMPLATE ?= assets/setup/manifests/product.template.json

DIST_DIR ?= dist
ARTIFACT_DIR ?= $(DIST_DIR)/artifacts/dominium-$(VERSION)

# Set REPRODUCIBLE=1 and SOURCE_DATE_EPOCH=<unix epoch seconds> for strict mode.
REPRODUCIBLE ?= 0

ifeq ($(REPRODUCIBLE),1)
REPRO_FLAG := --reproducible
else
REPRO_FLAG :=
endif

.PHONY: package-portable package-windows package-macos package-linux package-steam
.PHONY: assemble-artifact

assemble-artifact:
	$(PY) scripts/packaging/pipeline.py assemble --build-dir $(BUILD_DIR) --out $(ARTIFACT_DIR) --version $(VERSION) --manifest-template $(MANIFEST_TEMPLATE) $(REPRO_FLAG)

package-portable: assemble-artifact
	$(PY) scripts/packaging/pipeline.py portable --artifact $(ARTIFACT_DIR) --out $(DIST_DIR)/portable --version $(VERSION) $(REPRO_FLAG)

package-windows: assemble-artifact
	$(PY) scripts/packaging/pipeline.py windows --artifact $(ARTIFACT_DIR) --out $(DIST_DIR)/windows --version $(VERSION) --bootstrapper $(REPRO_FLAG)

package-macos: assemble-artifact
	$(PY) scripts/packaging/pipeline.py macos --artifact $(ARTIFACT_DIR) --out $(DIST_DIR)/macos --version $(VERSION) $(REPRO_FLAG)

package-linux: assemble-artifact
	$(PY) scripts/packaging/pipeline.py linux --artifact $(ARTIFACT_DIR) --out $(DIST_DIR)/linux --version $(VERSION) --build-deb --build-rpm $(REPRO_FLAG)

package-steam: assemble-artifact
	$(PY) scripts/packaging/pipeline.py steam --artifact $(ARTIFACT_DIR) --out $(DIST_DIR)/steam --version $(VERSION) $(REPRO_FLAG)
