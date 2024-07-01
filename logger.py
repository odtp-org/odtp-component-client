#!/usr/bin/env python

from mongouploader import MongoManager
from datetime import datetime, timezone
import os
import sys
import time


DELAY = 0.2
LOG_FILE_PATH = "/odtp/odtp-logs/log.txt"
LOG_END_STRING = "--- ODTP COMPONENT ENDING ---"

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


def main():
    step_id = os.getenv("ODTP_STEP_ID")
    try:
        dbManager = MongoManager()
    except Exception as e:
        sys.exit(f"Mongo manager failed to load: Exception {e} occurred")

    log_reader = LogReader(LOG_FILE_PATH)
    log_page = []

    # Active until it finds "--- ODTP COMPONENT ENDING ---"
    ending_detected = False
    while ending_detected == False:
        print("-------- new loop")
        log_reading_batch = log_reader.read_from_last_position()
        print(f"log_reading_batch: {log_reading_batch}")

        for log in log_reading_batch:
            log_page.append(log)

        print(f"log_page: {log_page}")    

        if len(log_page) >= 10:
            print(f"length log_page >= 10: {len(log_page)}")
            log_page_entry = {
                "stepRef": step_id,
                "timestamp": datetime.now(timezone.utc),
                "logstring": "\n".join(log_page)                
            }
            print(f"add log_page_entry to db: {log_page_entry}")
            _ = dbManager.add_logs(log_page_entry)
            print("empty log_page")
            log_page = []

        time.sleep(DELAY)

        # TODO: Improve this
        if log == LOG_END_STRING:
            print("ending was detected")
            print(f"length log_page >= 10: {len(log_page)}")
            log_page_entry = {
                "stepRef": step_id,
                "timestamp": datetime.now(timezone.utc),
                "logstring": "\n".join(log_page)                
            }
            print(f"add log_page_entry to db: {log_page_entry}")
            _ = dbManager.add_logs(log_page_entry)
            print("empty log_page")
            log_page = []            
            ending_detected = True
            break

    dbManager.close()        


if __name__ == '__main__':
    main()

