#!/usr/bin/env python

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone
import os


ODTP_MONGO_DB = "odtp"
STEPS_COLLECTION = "steps"
RESULTS_COLLECTION = "results"
OUTPUTS_COLLECTION = "outputs"
LOGS_COLLECTION = "logs"


class MongoManager(object):
    def __init__(self):
        mongodb_url = os.getenv("ODTP_MONGO_SERVER")
        self.client = MongoClient(mongodb_url)
        self.db = self.client[ODTP_MONGO_DB]
        self.step_id = os.getenv("ODTP_STEP_ID")
        self.logs = self.db[LOGS_COLLECTION]

    def add_log_page(self, log_page):
        if not log_page:
            return
        log_page_entry = {
            "stepRef": self.step_id,
            "timestamp": datetime.now(timezone.utc),
            "logstring": "\n".join(log_page)                
        }       
        log_id = self.logs.insert_one(log_page_entry).inserted_id

        return log_id       

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

    def close(self):
        self.client.close()