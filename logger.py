#!/usr/bin/env python

from mongouploader import MongoManager
import os
import sys
import time


DELAY = 0.2
LOG_FILE_PATH = "/odtp/odtp-logs/log.txt"
LOG_END_STRING = "--- ODTP COMPONENT ENDING ---"
DEFAULT_PAGE_SIZE = 10

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
    try:
        page_size = os.getenv("ODTP_LOG_PAGE_SIZE")
        page_size = int(page_size)
    except Exception as e:
        page_size = DEFAULT_PAGE_SIZE
   
    try:
        dbManager = MongoManager()
    except Exception as e:
        sys.exit(f"Mongo manager failed to load: Exception {e} occurred")

    log_reader = LogReader(LOG_FILE_PATH)
    log_page = []

    # Active until it finds "--- ODTP COMPONENT ENDING ---"
    ending_detected = False
    while ending_detected == False:
        log_reading_batch = log_reader.read_from_last_position()

        for log in log_reading_batch:
            log_page.append(log)   

        if len(log_page) >= 10:
            _ = dbManager.add_log_page(log_page)
            log_page = []

        time.sleep(DELAY)

        # TODO: Improve this
        if log == LOG_END_STRING:
            _ = dbManager.add_log_page(log_page)          
            ending_detected = True
            break

    dbManager.close()        


if __name__ == '__main__':
    main()

