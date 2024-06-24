#!/usr/bin/env bash
set -e
set -u
set -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
. "$DIR/src/shell/log.sh"
. "$DIR/src/shell/traceback.sh"
unset DIR

# You would use in `app.sh`:
# ```shell
# . "/odtp/odtp-component-client/src/shell/log.sh"
# . "/odtp/odtp-component-client/src/shell/traceback.sh"
# ```

function run_app() {
    bash odtp/odtp-app/app.sh
    exit_code="$?"

    if [ "$exit_code" -ne 0 ]; then
        odtp::print_error \
            "App 'app.sh' failed with exit code '$exit_code'."
    fi

    return 0

}

function main() {

    #########################################################
    # ODTP COMPONENT TEMPLATE
    #########################################################

    odtp::print_error "Starting odtp component."
    sleep 2

    run_app

    ## ODTP LOGGER in the background
    if [ -v ODTP_MONGO_SERVER ]; then
        odtp::print_error "Starting logging in mongo server."
        python3 /odtp/odtp-component-client/logger.py \
            >>/odtp/odtp-logs/odtpLoggerDebugging.txt 2>&1 &
    else
        echo "Env. variable 'ODTP_MONGO_SERVER' does not exist. "
    fi

    ############################################################################################
    # USER APP
    ############################################################################################

    bash odtp/odtp-app/app.sh ||
        odtp::print_error "Failed to run 'app.sh'."

    ############################################################################################
    # END OF USER APP
    #########################################################
    # TRANSFERRING INPUT TO OUTPUT
    #########################################################

    if [ "${TRANSFER_INPUT_TO_OUTPUT:-}" == "TRUE" ]; then
        odtp::print_error \
            "Copying input files '/odpt/odtp-input' to '/odtp/odpt-output'."
        cp -r /odtp/odtp-input/* /odtp/odtp-output
    fi

    #########################################################
    # COMPRESS THE OUTPUT FOLDER GENERATED
    #########################################################

    #  Take output and export it
    cd /odtp/odtp-output
    zip -rq ../odtp-output.zip ./*
    mv ../odtp-output.zip odtp-output.zip

    #########################################################
    # ODTP SNAPSHOT CREATION
    #########################################################

    # Take snapshot of workdir
    if [ "${ODTP_SAVE_SNAPSHOT:-}" = "TRUE" ]; then
        cd /odtp/odtp-workdir
        zip -rq ../odtp-snapshot.zip ./*
        mv ../odtp-snapshot.zip odtp-snapshot.zip
    fi

    ## Saving Snapshot in s3

    if [[ -v ODTP_S3_SERVER && -v ODTP_MONGO_SERVER ]]; then
        odtp::print_error "Uploading output to '$ODTP_S3_SERVER'."

        python3 /odtp/odtp-component-client/s3uploader.py 2>&1 |
            tee /odtp/odtp-logs/odtpS3UploadedDebugging.txt
    else
        odtp::print_error "Env. variable 'ODTP_S3_SERVER' does not exist."
    fi

}

main "$@"
