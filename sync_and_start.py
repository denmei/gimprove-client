import os
import sys
from pathlib import Path

# Check whether installation ok.
if "installed" not in os.listdir("client_repo/Installation"):
    answer = ""
    while answer not in ["y", "N"]:
        answer = input("Could not find 'installed' file in client_repo/Installation. "
                       "Do you want to run install.py now? [y/N]")
    if answer == "y":
        os.system("python3 client_repo/Installation/install.py")
    else:
        print("Shutting down...")
        sys.exit(0)

# Sync from S3.
print("Syncing from S3...")
os.system("aws s3 sync" +
          os.path.join(str(Path(os.path.dirname(os.path.realpath(__file__)))), "/client_repo/") +
          " s3://client-repository "
          "--exclude '*credentials*' "
          "--exclude 'test/*' "
          "--exclude 'config.json' "
          "--exclude '.idea/*' "
          "--exclude 'weight_translation.csv' "
          "--exclude '/logs/*'  "
          "--exclude '__pycache__/*'")

# Run additional scripts if available.
print("Looking for additional scripts...")

# Start client.
print("Starting client...")
os.system("python3 client_repo/execute.py")
