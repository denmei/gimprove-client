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
        print("Start installation...")
        os.system("python3 client_repo/Installation/install.py")
    else:
        print("Shutting down...")
        sys.exit(0)

# Sync from S3.
print("Syncing from S3...")
os.system("aws s3 sync s3://client-repository " +
          os.path.join(str(Path(os.path.dirname(os.path.realpath(__file__)))), "/client_repo/") +
          " --exclude '*/.credentials.json' "
          "--exclude 'test/*' "
          "--exclude '*/config.json' "
          "--exclude '.idea/*' "
          "--exclude */weight_translation.csv "
          "--exclude '*logs/*' "
          "--exclude '*__pycache__/*' "
          "--exclude */client_cache.json "
          "--exclude 'weights.csv' "
          "--exclude=distances.csv "
          "--exclude 'README.md' "
          "--exclude 'readme/*' ")

# Run additional scripts if available.
print("Looking for additional scripts...")
# Todo: Sync additional scripts and execute them.
# Todo: Track executed files in order to avoid that same files are executed on each start

# Start client.
print("Starting client...")
os.system("python3 client_repo/execute.py")
