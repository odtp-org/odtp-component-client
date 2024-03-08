#!/bin/bash
echo "RUNNING THE APP"
touch /odtp/odtp-logs/log.txt
touch /odtp/odtp-logs/odtpLoggerDebugging.txt
touch /odtp/odtp-logs/odtpS3UploadedDebugging.txt 

bash /odtp/odtp-client/odtp-app.sh 2>&1 | tee /odtp/odtp-logs/log.txt

echo "--- ODTP COMPONENT ENDING ---" >> /odtp/odtp-logs/log.txt

# Leaving some time for logging to catch up
sleep 10

# Zip logs
zip -r /odtp/odtp-output/odtp-logs.zip odtp-logs