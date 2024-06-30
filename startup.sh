#!/usr/bin/env bash

set -e
set -u
set -o pipefail

source "/odtp/odtp-component-client/src/shell/log.sh"
source "/odtp/odtp-component-client/src/shell/traceback.sh"

odtp::print_info "setting up log files for the component"
touch /odtp/odtp-logs/log.txt
touch /odtp/odtp-logs/odtpS3UploadedDebugging.txt

odtp::print_info "starting the odtp client app"
bash /odtp/odtp-component-client/odtp-app.sh 2>&1 | tee /odtp/odtp-logs/log.txt

# this comment is needed by the python logger to catch the end of the log
echo "--- ODTP COMPONENT ENDING ---" >>/odtp/odtp-logs/log.txt

# Leaving some time for logging to catch up
sleep 10

# Zip logs
zip -r /odtp/odtp-output/odtp-logs.zip odtp-logs
