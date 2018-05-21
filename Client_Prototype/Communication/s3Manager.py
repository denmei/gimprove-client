import os
import boto3


class s3Manager:

    def __init__(self, bucket_name, environment):
        self.environment = str(environment).lower()
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

    def upload_logs_to_s3(self, source_path, device_id, file_name):
        self.s3.upload_file(source_path, self.bucket_name, os.path.join(self.environment, device_id, file_name))

    def print_bucket_content_list(self):
        if self.environment in ["test", "production", "unittest"]:
            return os.system("aws s3 ls s3://%s/%s/" % (self.bucket_name, self.environment))
