#!/usr/bin/env bash
set -e
set -u
set -o pipefail

. "/odtp/odtp-component-client/src/shell/log.sh"
. "/odtp/odtp-component-client/src/shell/traceback.sh"

# You would use in `app.sh`:
# ```shell
# . "/odtp/odtp-component-client/src/shell/log.sh"
# . "/odtp/odtp-component-client/src/shell/traceback.sh"
# ```

# Runs app.sh script
function run_app() {
    odtp::print_info "Starting app. In case app is persistent. Logging may stop here. Find logs in 'odtp/odtp-logs'"
    bash /odtp/odtp-app/app.sh
    exit_code="$?"
    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "App 'app.sh' failed with exit code '$exit_code'."
    fi
    return 0
}

# start logging
function start_logger() {
## ODTP LOGGER in the background
    if [[ -v ODTP_MONGO_SERVER && "${ODTP_LOGS_IN_DB:-}" == "TRUE" ]]; then
        odtp::print_info "STARTING python logger in the background."
        # as command is started in the background there will be no exit code available for it
        python3 /odtp/odtp-component-client/logger.py >> /odtp/odtp-logs/odtpLoggerDebugging.txt 2>&1 &
    else
        odtp::print_info "Logging to mongo db disabled"
    fi
    return 0
}

# transfer input to output to s3
function transfer_input_to_output() {
    if [ "${TRANSFER_INPUT_TO_OUTPUT:-}" == "TRUE" ]; then
        odtp::print_info \
            "Copying input files '/odpt/odtp-input' to '/odtp/odpt-output'."
        cp -r /odtp/odtp-input/* /odtp/odtp-output
        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "Coping input to output failed with exit code '$exit_code'."
        fi        
    fi
    return 0
}

#  Take output and export it
function compress_output () {
    odtp::print_info "cd into '/odtp/odtp-output'"
    cd /odtp/odtp-output
    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "'cd /odtp/odtp-output' failed with exit code '$exit_code'."
    fi    
    odtp::print_info "'zip -rq ../odtp-output.zip ./*'"
    zip -rq ../odtp-output.zip ./*
    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "'zip -rq ../odtp-output.zip ./*' failed with exit code '$exit_code'."
    fi      
    odtp::print_info "cd into 'mv ../odtp-output.zip odtp-output.zip'"
    mv ../odtp-output.zip odtp-output.zip
    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "'mv ../odtp-output.zip odtp-output.zip' failed with exit code '$exit_code'."
    fi      
    return 0
}

function compress_workdir () {
    if [[ "${ODTP_SAVE_SNAPSHOT:-}" = "TRUE" ]]; then
        odtp::print_info "'cd /odtp/odtp-workdir'"
        cd /odtp/odtp-workdir
        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'cd /odtp/odtp-workdir' failed with exit code '$exit_code'."
        fi          
        odtp::print_info "'zip -rq ../odtp-snapshot.zip ./*'"
        zip -rq ../odtp-snapshot.zip ./*
        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'zip -rq ../odtp-snapshot.zip ./*' failed with exit code '$exit_code'."
        fi          
        odtp::print_info "'mv ../odtp-snapshot.zip odtp-snapshot.zip'"
        mv ../odtp-snapshot.zip odtp-snapshot.zip
        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'mv ../odtp-snapshot.zip odtp-snapshot.zip' failed with exit code '$exit_code'."
        fi         
    fi 
    return 0  
}

function upload_snapshot () {
    if [[ -v ODTP_S3_SERVER && -v ODTP_MONGO_SERVER ]]; then
        odtp::print_info "Uploading to ODTP_S3_SERVER because 'ODTP_S3_SERVER' and 'ODTP_MONGO_SERVER' are both set"
        python3 /odtp/odtp-component-client/s3uploader.py 2>&1 | tee /odtp/odtp-logs/odtpS3UploadedDebugging.txt
        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'python3 /odtp/odtp-component-client/s3uploader.py 2>&1 | tee /odtp/odtp-logs/odtpS3UploadedDebugging.txt' failed with '$exit_code'."
        fi          
    else
        odtp::print_info "Not uploading to S3 since either 'ODTP_S3_SERVER' or 'ODTP_MONGO_SERVER' is not specified"
    fi 
    return 0
}

function move_logs_to_output () {
    if [[ "${ODTP_LOGS_AS_FILE:-}" == "TRUE" ]]; then
        odtp::print_info "Writing log files to output since 'ODTP_LOGS_AS_FILE' is set to 'TRUE'"
        cp /odtp/odtp-logs/log.txt /odtp/odtp-output/log.txt
        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "copying log files to output failed with '$exit_code'."
        fi         
    fi 
    return 0
}


function main() {
    odtp::print_info "Starting odtp component."
    sleep 2
    start_logger
    run_app
    transfer_input_to_output
    compress_output
    compress_workdir
    upload_snapshot
    move_logs_to_output
}

main "$@"
