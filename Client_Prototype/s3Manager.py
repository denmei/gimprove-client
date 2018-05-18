import os


class s3Manager:

    def __init__(self, environment):
        self.environment = str(environment).lower()

    def upload_logs_to_s3(self, source_path):
        if self.environment in ["test", "production"]:
            print("aws s3 sync %s s3:rasppi-logs/%s/" % (source_path, self.environment))
            os.system("aws s3 sync %s s3://rasppi-logs/%s/ --delete" % (source_path, self.environment))
