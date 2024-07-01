#!/usr/bin/env bash
# shellcheck disable=SC1090,SC1091
# Common logging functionality for all odtp
# components using bash scripts.

# Prints an info to `stdout`.
function odtp::print_info() {
  odtp::internal::print "" "" "$@"
}

# Prints warning message to `stdout`.
# Each argument (`$@`) are output on separate lines.
function odtp::print_warning() {
  odtp::internal::print "" "WARN: " "$@" >&2
}

# Prints error message to `stdout`.
# Each argument (`$@`) are output on separate lines.
function odtp::print_error() {
  odtp::internal::print "" "ERROR: " "$@" >&2
}

# Print an error message and exit with `1`.
# Prints also a nice tracelog.
function odtp::die() {
  odtp::print_error "$@"
  # Trigger trace log.
  trap 'odtp::internal::errexit "$?" "$BASH_COMMAND"' EXIT
  exit 1
}

function odtp::internal::enable_errors() {
  set -e
  set -o pipefail
}

# shellcheck disable=SC2154,SC2086
function odtp::internal::print() {
  local flags="$1"
  local header="$2"
  shift 2

  local msg
  msg=$(printf '%b\n' "$@")
  msg="${msg//$'\n'/$'\n'   }"
  echo $flags -e "->   $header$msg"
}

# Trace functionality.
function odtp::internal::errexit() {
  local lasterr="$1"
  local bashCmd="$2"

  set +o xtrace
  set -e

  odtp::print_error "Error in ${BASH_SOURCE[1]}:${BASH_LINENO[0]}: ('$bashCmd' exited with status '$lasterr')"

  odtp::print_error "Call tree:"
  for ((i = 1; i < ${#FUNCNAME[@]} - 1; i++)); do
    odtp::print_error " $i: ${BASH_SOURCE[$i + 1]}:${BASH_LINENO[$i]} ${FUNCNAME[$i]}(...)"
  done

  exit 1
}
