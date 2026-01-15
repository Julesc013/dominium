#!/bin/sh
set -e

STATE_PATH="${DSK_STATE_PATH:-/var/lib/dominium/installed_state.tlv}"
JOURNAL_PATH="${DSK_JOURNAL_PATH:-/var/lib/dominium/job_journal.tlv}"

dominium-setup status --journal "${JOURNAL_PATH}" || true
dominium-setup verify --state "${STATE_PATH}" --format txt || true
