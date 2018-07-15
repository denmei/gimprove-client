import os
import json
import datetime
from pathlib import Path


def remove_aws_files(in_aws_path):
    """
    Removes the credentials and the config file from the .aws folder it they exist.
    :param in_aws_path: Path to the .aws directory.
    """
    if os.path.join(in_aws_path, "config") in os.listdir(in_aws_path):
        os.system("rm %s" % os.path.join(in_aws_path, "config"))
    if os.path.join(in_aws_path, "credentials") in os.listdir(in_aws_path):
        os.system("rm %s" % os.path.join(in_aws_path, "credentials"))


def setup_aws(in_aws_path):
    """
    Creates credentials and config file from user-input. Replaces files that already exist. Returns username provided
    by the user.
    :param in_aws_path: Path to the .aws directory.
    :return: Username.
    """
    # remove_aws_files(in_aws_path)
    aws_username = input("Please type your aws-username: ")
    aws_access_key_id = input("Please type the AWS access key id: ")
    aws_secret_access_key = input("Please type the AWS secret access key: ")
    credentials_content = "[default]" '\n' + "aws_access_key_id = %s" % aws_access_key_id + '\n' + \
                          "aws_secret_access_key = %s" % aws_secret_access_key
    with open(os.path.join(in_aws_path, "credentials"), 'w+') as aws_credentials:
        aws_credentials.write(credentials_content)
        aws_credentials.close()

    config_content = "[default]" + '\n' + "region = eu-central-1"
    with open(os.path.join(in_aws_path, "config"), 'w+') as aws_config:
        aws_config.write(config_content)
        aws_config.close()
    return aws_username


# load required packages and install
os.system("sudo pip3 install numpy")
os.system("sudo pip3 install twisted")
os.system("sudo apt-get -y install libatlas3-base")
os.system("sudo pip3 install matplotlib")
os.system("sudo pip3 install tkinter")
os.system("sudo pip3 install pandas")
os.system("sudo pip3 install pytz")
os.system("sudo pip3 install requests")
os.system("sudo pip3 install statistics")
os.system("sudo pip3 install cairocffi")
os.system("sudo pip3 install websocket-client")
os.system("sudo pip3 install boto3")
os.system("sudo apt-get -y install python-smbus")
os.system("sudo apt-get -y install i2c-tools")
os.system("sudo apt-get -y install python-dev python3-dev")
os.system("sudo apt-get -y install python-rpi.gpio python3-rpi.gpio")
os.system("git config --global user.email 'none'")
os.system("git config --global user.name 'pi'")
# maybe necessary for tkinter-problems: sudo apt-get install python3-tk


# configure aws
os.system("sudo pip install awscli --upgrade --user")
aws_path = os.path.join(os.path.expanduser("~"), ".aws")
if ".aws" not in os.listdir(os.path.expanduser("~")):
    os.mkdir(aws_path)

aws_setup = False

while not aws_setup:
    # get credentials from user
    username = setup_aws(aws_path)
    # check whether credentials are valid. Command must return a json with user-information
    state = os.popen("aws sts get-caller-identity").read()
    try:
        json_state = json.loads(state)
        # check whether credentials fit the given username
        if username in json_state['Arn']:
            aws_setup = True
        else:
            print("--- Provided credentials are not valid! Repeat initialization of AWS ---")
    except Exception as e:
        # if json could not be parsed correctly, there occured an error with the credentials
        print("--- Provided credentials are not valid! Repeat initialization of AWS ---")


# Add installation file that indicates a successful installation process
with open("client_repo/Installation/installed", 'a') as installed:
    installed.write("Installation completed. Date: %s" % datetime.datetime.now())


# Update bashrc
print("Installation completed so far. Next and last step would be updating the .bashrc-file. "
      "ONLY EXECUTE THIS STEP ON A RASPBERRY!")
answer = ""
while answer not in ["y", "N"]:
    answer = input("Do you want to update the .bashrc? [y/N]")

if answer == "y":
    os.system("sudo mv /home/pi/.bashrc /home/pi/.bashrc_original")
    copy_command = "sudo mv %s /home/pi/.bashrc" % os.path.join(str(Path(os.path.dirname(os.path.realpath(__file__)))), "new_bashrc")
    os.system(copy_command)


# reboot the system after successful setup
os.system("sudo reboot now")
