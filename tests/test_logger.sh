#!/usr/bin/env bash
# Test script for the python script 'logger.py' that is called form odtp-app.sh:

PWDDIR=$(pwd)
bash "$PWDDIR/tests/helpers/write_log_file_for_streaming.sh" &
python3 "$PWDDIR/logger.py" "$PWDDIR/log.txt" "--dryrun"

