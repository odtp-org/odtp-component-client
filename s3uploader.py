from datetime import datetime, timezone
import os
import time
import logging
import boto3
import sys

sys.path.append('/odtp/odtp-app/odtp-client')
from logger import MongoManager

### This method needs to create a new entry in snapshots MONGODB and upload the output.zip to s3. 
### At this moment the structure is not that important as to make things works together. 

class s3Manager:
    def __init__(self, s3Server, bucketName, accessKey, secretKey):
        self.s3Server = s3Server
        self.bucketName = bucketName
        self.accessKey = accessKey
        self.secretKey = secretKey

        self.s3 = boto3.client(
            's3', endpoint_url=self.s3Server,
            aws_access_key_id=self.accessKey,
            aws_secret_access_key=self.secretKey
        )

    # Method to create a specific folder 
    # The idea is to create paths such as Digital Twin > Execution > Step > Output 
    def createFolder(self, path):
        """
        Creates a specific folder in the S3 bucket.

        Args:
            path (str): The path of the folder to create.

        Returns:
            None
        """
        self.s3.put_object(Bucket=self.bucketName, Key=path + '/')
        logging.info(f"Folder '{path}' created")

    # Method to upload one file to specific path in s3
    def uploadFile(self, local_path, s3_path):
        """
        Uploads a file to a specific path in the S3 bucket.

        Args:
            local_path (str): The local path of the file to upload.
            s3_path (str): The S3 path where the file should be uploaded.

        Returns:
            None
        """
        self.s3.upload_file(local_path, self.bucketName, s3_path)
        logging.info(f"File '{local_path}' uploaded to '{s3_path}'")

    def close(self):
        del self.s3
        logging.info("S3 Session deleted")


def main():
    S3_SERVER = os.getenv("ODTP_S3_SERVER")
    BUCKET_NAME = os.getenv("ODTP_BUCKET_NAME")
    ACCESS_KEY = os.getenv("ODTP_ACCESS_KEY")
    SECRET_KEY = os.getenv("ODTP_SECRET_KEY")
    STEP_ID = os.getenv("ODTP_STEP_ID")
    odtpS3 = s3Manager(S3_SERVER, BUCKET_NAME, ACCESS_KEY, SECRET_KEY)
    try:
        db_manager = MongoManager()
    except Exception as e:
        sys.exit(f"Mongo manager failed to load: Exception {e} occurred")

    USER_ID = os.getenv("ODTP_USER_ID")
    ODTP_OUTPUT_PATH = f"odtp/{STEP_ID}"

    odtpS3.createFolder(ODTP_OUTPUT_PATH)

    ## Uploading compressed output
    #########################################################################

    odtpS3.uploadFile('/odtp/odtp-output/odtp-output.zip', ODTP_OUTPUT_PATH + "/odtp-output.zip")

    # Maybe this MongoDB needs to be manage outside this one?
    file_size_bytes = os.path.getsize('/odtp/odtp-output/odtp-output.zip')

    output_data = {
        "output_type": "output",
        "s3_bucket": BUCKET_NAME,  # Name of the S3 bucket where the output is stored
        "s3_key": ODTP_OUTPUT_PATH,  # The key (path) in the S3 bucket to the output
        "file_name": "odtp-output.zip",  # The name of the file in the output
        "file_size": file_size_bytes,  # Size of the file in bytes
        "file_type": "application/zip",  # MIME type or file type
        "created_at": datetime.now(timezone.utc),  # Timestamp when the output was created
        "updated_at": datetime.now(timezone.utc),  # Timestamp when the output was last updated
        "metadata": {  # Additional metadata associated with the output
            "description": "Description of the snapshot",
            "tags": ["tag1", "tag2"],
            "other_info": "Other relevant information"
        },
        "access_control": {  # Information about who can access this output
            "public": False,  # Indicates if the output is public or private
            "authorized_users": [USER_ID],  # Array of User ObjectIds who have access
        }
    }

    odtp_output_id = dbManager.add_output(STEP_ID, output_data)

    if os.getenv("ODTP_SAVE_IN_RESULT") == "TRUE":
        dbManager.update_result(os.getenv("ODTP_RESULT"), odtp_output_id)
    
    logging.info("ODTP OUTPUT UPLOADED IN {}".format(odtp_output_id))

    if os.getenv("ODTP_SAVE_SNAPSHOT") == "TRUE":

        ## Uploading compressed workdir snapshot
        #########################################################################

        odtpS3.uploadFile('/odtp/odtp-output/odtp-snapshot.zip', ODTP_OUTPUT_PATH + "/odtp-snapshot.zip")

        file_size_bytes = os.path.getsize('/odtp/odtp-output/odtp-snapshot.zip')

        output_data = {
            "output_type": "snapshot",
            "s3_bucket": BUCKET_NAME,  # Name of the S3 bucket where the output is stored
            "s3_key": ODTP_OUTPUT_PATH,  # The key (path) in the S3 bucket to the output
            "file_name": "odtp-snapshot.zip",  # The name of the file in the output
            "file_size": file_size_bytes,  # Size of the file in bytes
            "file_type": "application/zip",  # MIME type or file type
            "created_at": datetime.now(timezone.utc),  # Timestamp when the output was created
            "updated_at": datetime.now(timezone.utc),  # Timestamp when the output was last updated
            "metadata": {  # Additional metadata associated with the output
                "description": "Description of the snapshot",
                "tags": ["tag1", "tag2"],
                "other_info": "Other relevant information"
            },
            "access_control": {  # Information about who can access this output
                "public": False,  # Indicates if the output is public or private
                "authorized_users": [USER_ID],  # Array of User ObjectIds who have access
            }
        }

        odtp_output_snapshot_id = dbManager.add_output(STEP_ID, output_data)

        logging.info("ODTP WORKDIR SNAPSHOT UPLOADED IN {}".format(odtp_output_snapshot_id))


    dbManager.close()

    # TODO: Upload individual files to S3 (Experimental)


if __name__ == "__main__":
    main()
