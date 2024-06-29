#!/usr/bin/env python

#from pymongo import MongoClient, errors
#from bson import ObjectId
from datetime import datetime, timezone
import os
import time
import json
import argparse
import datetime
from pathlib import Path


ODTP_MONGO_DB = "odtp"
LOGS_COLLECTION = "logs"
LOG_WATCH_PATH = "/odtp/odtp-logs/log.txt"
LOG_WATCH_INTERVAL = 5
ODTP_DB_LOG_PAGESIZE = 500

class MongoManager(object):
    def __init__(self):
        self.mongodb_url = os.getenv(ODTP_MONGO_SERVER)
        self.__check_db_connection()
        self.client = MongoClient(mongodb_url)
        self.db = self.client[ODTP_MONGO_DB]
        self.step_id = os.getenv(ODTP_STEP_ID)
        self.logs_collection = self.db["logs"]
        self.steps_collection = self.db["steps"]

    def __check_db_connection(self):
        with MongoClient(self.mongodb_url, serverSelectionTimeoutMS=2000) as client:
            return client.server_info()

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
    db_manager = MongoManager()
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
