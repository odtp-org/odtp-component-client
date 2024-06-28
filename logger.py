#!/usr/bin/env python

from pymongo import MongoClient, errors
from bson import ObjectId
from datetime import datetime, timezone
import os
import time
import json


class MongoManager:
    def __init__(self, mongodbUrl, db_name):
        self.client = MongoClient(mongodbUrl)
        self.db = self.client[db_name]
    
    def add_logs(self, log_data_list):
        logs_collection = self.db["logs"]

        log_ids = logs_collection.insert_many(log_data_list).inserted_ids

        return log_ids

    def __update_timestamp(self, step_id, field):
        steps_collection = self.db["steps"]
        steps_collection.update_one(
            {"_id": ObjectId(step_id)},
            {"$set": {field: datetime.now(timezone.utc)}}
        )

    def __close(self):
        self.client.close()


class LogReader:
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_position = 0

    def read_from_last_position(self):
        lines = []
        with open(self.log_file, 'r') as f:
            # Move to the last read position
            f.seek(self.last_position)

            # Read the remaining lines from the log file
            for line in f:
                lines.append(line.strip())

            # Update the last read position
            self.last_position = f.tell()

        return lines


def main(delay=2):
    ### Create Entry
    MONGO_URL = os.getenv("ODTP_MONGO_SERVER")
    step_id = os.getenv("ODTP_STEP_ID")
    db_name = "odtp"

    dbManager = MongoManager(MONGO_URL, db_name)
    dbManager.update_timestamp(step_id, "start_timestamp")
    dbManager.close()
    
    log_reader = LogReader('/odtp/odtp-logs/log.txt')

    # Active until it finds "--- ODTP COMPONENT ENDING ---"
    ending_detected = False
    while ending_detected == False:
        logs = log_reader.read_from_last_position()
        
        newLogList = []
        for log in logs:
            newLogEntry= {
            "stepRef": step_id,
            "timestamp": datetime.now(timezone.utc),
            "logstring": log}

            newLogList.append(newLogEntry)


        dbManager = MongoManager(MONGO_URL, db_name)
        _ = dbManager.add_logs(newLogList)
        dbManager.close()

        time.sleep(0.2)

        # TODO: Improve this
        if log == "--- ODTP COMPONENT ENDING ---":
            dbManager = MongoManager(MONGO_URL, db_name)
            dbManager.update_timestamp(step_id, "end_timestamp")
            dbManager.close()

            ending_detected = True

        #time.sleep(delay)


if __name__ == '__main__':
    # this script is called from inside the odtp client and logs to the
    # mongodb during the execution of bashscripts
    __main(delay=0.5)

