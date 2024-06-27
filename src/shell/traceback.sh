#!/usr/bin/env bash
# shellcheck disable=SC1090,SC1091
#
# Adds traceback functionality to your script.
# From: https://gist.github.com/Asher256/4c68119705ffa11adb7446f297a7beae

DIR_TEMP="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
. "$DIR_TEMP/log.sh"
unset DIR_TEMP

# Provide an error handler whenever a command exits nonzero
trap 'odtp::internal::errexit "${?}" "$BASH_COMMAND"' ERR

# Propagate ERR trap handler functions, expansions and subshells
set -o errtrace
set -o functrace
