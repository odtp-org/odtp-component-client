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
    
    def add_output(self, step_id, output_data):
        output_collection = self.db["outputs"]
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
    

    def append_log(self, step_id, log_data):
        steps_collection = self.db["steps"]
        steps_collection.update_one(
            {"_id": ObjectId(step_id)},
            {"$push": {"logs": log_data}}
        )
    
    def append_logs(self, step_id, log_data_list):
        steps_collection = self.db["steps"]
        steps_collection.update_one(
            {"_id": ObjectId(step_id)},
            {"$push": {"logs": {"$each": log_data_list}}}
        )
    
    def update_result(self, result_id, output_id):
        results_collection = self.db["results"]
        results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$push": {"output": output_id}}
        )

        results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )

    def update_timestamp(self, step_id, field):
        steps_collection = self.db["steps"]
        steps_collection.update_one(
            {"_id": ObjectId(step_id)},
            {"$set": {field: datetime.now(timezone.utc)}}
        )

    def get_all_collections_as_dict(self):
            """
            Retrieve all documents in all collections as a dictionary.
            """
            all_data = {}
            for collection_name in self.db.list_collection_names():
                cursor = self.db[collection_name].find()
                all_data[collection_name] = [doc for doc in cursor]
            
            return all_data

    def get_all_collections_as_json_string(self):
        """
        Retrieve all documents in all collections as a JSON-formatted string.
        """
        all_data = self.get_all_collections_as_dict()
        return json.dumps(all_data, indent=2, default=str)  # default=str to handle datetime and ObjectId


    def print_all_collections_as_json(self):
        """
        Print all documents in all collections in JSON format.
        """
        for collection_name in self.db.list_collection_names():
            print(f"Collection: {collection_name}")
            cursor = self.db[collection_name].find()
            for doc in cursor:
                print(json.dumps(doc, indent=2, default=str))  # default=str is added to handle datetime and ObjectId
            print("-" * 50)  # separator line between collections


    def export_all_collections_as_json(self, filename):
        """
        Save all documents in all collections as a JSON file.
        """
        all_data = self.get_all_collections_as_dict()
        with open(filename, 'w') as json_file:
            json.dump(all_data, json_file, indent=2, default=str)  # default=str to handle datetime and ObjectId


    ######################################
    # USER METHOD

    def get_all_users(self):
        cursor = self.db.users.find({})

        users = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            users.append(doc)

        return users
    
    def get_digital_twins_by_user_id(self, user_id_str):
        # Convert user_id string to ObjectId
        user_id = ObjectId(user_id_str)
        
        # Fetch digital twins by user_id
        cursor = self.db.digitalTwins.find({"userRef": user_id}, {"_id": 1, "userRef": 1, "executions[0].timestamp": 1, "executions[0].timestamp": 1})
        
        digital_twins = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for pandas compatibility
            digital_twins.append(doc)
            
        return digital_twins
    
    def print_logs_by_indices(self, twin_index, execution_index, step_index):
        # Skip to the digital twin specified by the given index and retrieve it
        digital_twin = self.db.digitalTwins.find().sort("_id", 1).skip(twin_index).limit(1).next()

        try:
            # Navigate to the logs using the given execution index
            logs = digital_twin["executions"][execution_index]["steps"][step_index]["logs"]
        except (IndexError, KeyError):
            print(f"No logs found for execution {execution_index} of digital twin {twin_index}.")

        return logs

    ######################################
    # Closing & Deleting
    ######################################

    def close(self):
        self.client.close()

    def deleteAll(self):
        # Connect to your database. Replace 'mydatabase' with your database name.
        db_odtp = self.db

        # Get a list of all collections in the database
        collections = db_odtp.list_collection_names()
        # Drop each collection
        for collection in collections:
            db_odtp.drop_collection(collection)


########### LogReader 
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


############ Main Method
# This method will push the log to an existing execution step

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
        # _ = dbManager.append_logs(step_id, newLogList)
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
    main(delay=0.5)

