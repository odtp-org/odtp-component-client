#!/usr/bin/env bash
set -e
set -u
set -o pipefail

source "/odtp/odtp-component-client/src/shell/log.sh"
source "/odtp/odtp-component-client/src/shell/traceback.sh"

# You would use in `app.sh`:
# ```shell
# . "/odtp/odtp-component-client/src/shell/log.sh"
# . "/odtp/odtp-component-client/src/shell/traceback.sh"
# ```

function run_app() {
 
    odtp::print_info "Starting app. In case app is persistent. Logging may stop here."
    bash /odtp/odtp-app/app.sh

    exit_code="$?"

    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "App 'app.sh' failed with exit code '$exit_code'."
    fi

    return 0
}

function start_logger() {

    if [[ -v ODTP_MONGO_SERVER && "${ODTP_LOGS_IN_DB:-}" == "TRUE" ]]; then

        odtp::print_info "starting python logger in the background."
        python3 /odtp/odtp-component-client/logger.py >> /odtp/odtp-logs/odtpLoggerDebugging.txt 2>&1 &

    else
        odtp::print_info "Logging to mongo db disabled"
    fi

    return 0
}

function transfer_input_to_output() {

    if [ "${TRANSFER_INPUT_TO_OUTPUT:-}" == "TRUE" ]; then

        odtp::print_info "copy inputs to the output directory"
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

    odtp::print_info "move to output directory"
    cd /odtp/odtp-output

    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "'cd /odtp/odtp-output' failed with exit code '$exit_code'."
    fi
    
    odtp::print_info "zip output directory"
    zip -rq ../odtp-output.zip ./*

    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "'zip -rq ../odtp-output.zip ./*' failed with exit code '$exit_code'."
    fi
     
    odtp::print_info "move zipped output file"
    mv ../odtp-output.zip odtp-output.zip

    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "'mv ../odtp-output.zip odtp-output.zip' failed with exit code '$exit_code'."
    fi
     
    return 0

}

function compress_workdir () {

    if [[ "${ODTP_SAVE_SNAPSHOT:-}" = "TRUE" ]]; then

        odtp::print_info "move into working directory"
        cd /odtp/odtp-workdir

        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'cd /odtp/odtp-workdir' failed with exit code '$exit_code'."
        fi
          
        odtp::print_info "zip workdir into a snapshot"
        zip -rq ../odtp-snapshot.zip ./*

        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'zip -rq ../odtp-snapshot.zip ./*' failed with exit code '$exit_code'."
        fi
      
        odtp::print_info "Move snapshot one directory up"
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
        odtp::print_info "Uploading the outputs to S3"
        python3 /odtp/odtp-component-client/s3uploader.py 2>&1 | tee /odtp/odtp-logs/odtpS3UploadedDebugging.txt

        if [ "$exit_code" -ne 0 ]; then
            odtp::print_error \
                "'python3 /odtp/odtp-component-client/s3uploader.py 2>&1 | tee /odtp/odtp-logs/odtpS3UploadedDebugging.txt' failed with '$exit_code'."
        fi       
    else
        odtp::print_info "Output uploading is skipped if component runs outside of odtp infrastructure"
    fi

    return 0

}

function move_logs_to_output () {

    odtp::print_info "Copying the logs to the output directory"
    cp /odtp/odtp-logs/log.txt /odtp/odtp-output/log.txt

    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "copying log files to output failed with '$exit_code'."
    fi

    return 0

}

function main() {
    odtp::print_info "Starting odtp component."

    # preprocessing for running the app

    # Some strange sleep to workaround what? ... we dont know
    sleep 2

    start_logger

    # this runs the app

    run_app

    # post processing after running the app

    # this will only be done if app is not a persistent component:
    # starting a process that does not end

    transfer_input_to_output
    compress_output
    compress_workdir
    upload_snapshot
    move_logs_to_output
}

main "$@"
