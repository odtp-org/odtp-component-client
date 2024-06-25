#!/bin/bash

#########################################################
# ODTP COMPONENT TEMPLATE
#########################################################

echo "STARTING ODTP COMPONENT"
sleep 2

## ODTP LOGGER in the background
if [[ -v ODTP_MONGO_SERVER && "${ODTP_LOGS_IN_DB:-}" == "TRUE" ]]; then
    echo "STARTING LOGGING IN 'ODTP_MONGO_SERVER'"
    python3 /odtp/odtp-component-client/logger.py >> /odtp/odtp-logs/odtpLoggerDebugging.txt 2>&1 &
else
    echo "'ODTP_MONGO_SERVER' does not exist or 'ODTP_LOGS_IN_DB' not set to 'TRUE'"
fi


############################################################################################
# USER APP
############################################################################################

bash /odtp/odtp-app/app.sh

############################################################################################
# END OF USER APP
############################################################################################

#########################################################
# TRANSFERRING INPUT TO OUTPUT 
#########################################################

if [[ "${TRANSFER_INPUT_TO_OUTPUT:-}" == "TRUE" ]]; then
    echo "COPYING INPUT FILES TO OUTPUT because 'TRANSFER_INPUT_TO_OUTPUT' is 'TRUE'"
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
if [[ "${ODTP_SAVE_SNAPSHOT:-}" = "TRUE" ]]; then
    cd /odtp/odtp-workdir
    zip -rq ../odtp-snapshot.zip ./*
    mv ../odtp-snapshot.zip odtp-snapshot.zip
fi

## Saving Snapshot in s3

if [[ -v ODTP_S3_SERVER && -v ODTP_MONGO_SERVER ]]; then
    echo "Uploading to ODTP_S3_SERVER because 'ODTP_S3_SERVER' and 'ODTP_MONGO_SERVER' are both set"
    python3 /odtp/odtp-component-client/s3uploader.py 2>&1 | tee /odtp/odtp-logs/odtpS3UploadedDebugging.txt  
else
    echo "Not uploading to S3 since either 'ODTP_S3_SERVER' or 'ODTP_MONGO_SERVER' is not specified"
fi

## Copying logs into output

if [[ "${ODTP_LOGS_AS_FILE:-}" == "TRUE" ]]; then
    echo "Writing log files to output since 'ODTP_LOGS_AS_FILE' is set to 'TRUE'"
    cp /odtp/odtp-logs/log.txt /odtp/odtp-output/log.txt
fi
