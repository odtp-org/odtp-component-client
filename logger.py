#!/usr/bin/env python

from pymongo import MongoClient, errors
from bson import ObjectId
from datetime import datetime, timezone
import os
import sys
import time
import json
import argparse
import datetime
from pathlib import Path


ODTP_MONGO_DB = "odtp"
LOGS_COLLECTION = "logs"
STEPS_COLLECTION = "steps"
RESULTS_COLLECTION = "results"
OUTPUT_COLLECTION = "outputs"
LOG_WATCH_PATH = "/odtp/odtp-logs/log.txt"
LOG_WATCH_INTERVAL = 5
ODTP_DB_LOG_PAGESIZE = 500

class MongoManager(object):
    def __init__(self):
        self.mongodb_url = os.getenv("ODTP_MONGO_SERVER")
        self.client = MongoClient(mongodb_url)
        self.db = self.client[ODTP_MONGO_DB]
        self.step_id = os.getenv("ODTP_STEP_ID")
        self.logs_collection = self.db[LOGS_COLLECTION]

    def __add_logs_to_mongodb(self, log_page):
        log_entry = __format_log_entry(log_page)
        log_ids = self.logs_collection.insert_many(log_entry).inserted_ids
        return log_ids

    def __format_logs(self, log_page):
        log_entry = {
            "stepRef": self.step_id,
            "timestamp": datetime.now(timezone.utc),
            "logstring": log_page,
        }
        return log_entry

    def add_output(self, step_id, output_data):
        output_collection = self.db[OUTPUTS_COLLECTION]
        output_data["stepRef"] = step_id

        # TODO: Make its own function. Taking out user_id
        #output_data["access_control"]["authorized_users"] = user_id

        output_id = output_collection.insert_one(output_data).inserted_id

        # Update steps with execution reference
        self.db.steps.update_one(
            {"_id": ObjectId(step_id)},  # Specify the document to update
            {"$set": {"output": output_id}}  # Use $set to replace the value of a field
        )

        return output_id

    def update_result(self, result_id, output_id):
        results_collection = self.db[RESULTS_COLLECTION]
        results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$push": {"output": output_id}}
        )

        results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )

    def __close(self):
        self.client.close()


class LogReader:
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_position = 0

    def read_from_last_position(self):
        """read as long as there is something to read
        from a streaming log output"""
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


def process_logs():
    """
    Observe bash logs and write them to the mongo db
    """
    try:
        db_manager = MongoManager()
    except Exception as e:
        sys.exit(f"Mongo manager failed to load: Exception {e} occurred.")
    log_reader = LogReader(LOG_WATCH_PATH)
    pagesize = ODTP_DB_LOG_PAGESIZE

    # Active until it finds "--- ODTP COMPONENT ENDING ---"
    ending_detected = False
    log_page_list = []
    while ending_detected == False:
        # take breaks between reading the log file
        time.sleep(LOG_WATCH_INTERVAL)
        log_read_batch = log_reader.read_from_last_position()
        cond_page_not_full = len(log_page_list) + len(log_read_batch) <= pagesize
        cond_ending_detected = "--- ODTP COMPONENT ENDING ---" in log_batch
        cond_continue_reading = cond_page_not_full or cond_ending_detected
        if not cond_continue_reading:
            log_page_list.extend(log_batch)
        else:
            log_page = json.dumps(log_batch)
            db_manager.__add_logs_to_mongodb(log_page)
        if cond_ending_detected:
            break


if __name__ == '__main__':
    # this script is called from inside the odtp client and logs to the
    # mongodb during the execution of bashscripts
    time.sleep(0.2)
    process_logs()
