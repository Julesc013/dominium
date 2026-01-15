#!/bin/sh
set -e

STATE_PATH="${DSK_STATE_PATH:-/var/lib/dominium/installed_state.tlv}"
JOURNAL_PATH="${DSK_JOURNAL_PATH:-/var/lib/dominium/job_journal.tlv}"

if [ -f "${STATE_PATH}" ]; then
  rm -f "${STATE_PATH}"
fi
if [ -f "${JOURNAL_PATH}" ]; then
  rm -f "${JOURNAL_PATH}"
fi
