import argparse
import json
import os
import re
import threading
from typing import Dict

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from netatmo.netatmo_client import NetatmoClient
from netatmo.weather_wrapper import WeatherWrapper
from netatmo.daemon import Daemon

parser = argparse.ArgumentParser(description='Netatmo CLI - Choose one of the available modes to interact with your Netatmo devices.')

parser.add_argument(
    'mode',
    choices=['daemon', 'status', 'list'],
    help=(
        "daemon : Launch the daemon based on the config file\n"
        "status : Print information about the room temperatures and outside temperature\n"
        "list   : List rooms information"
    )
)

rootFolderPath = os.path.dirname(os.path.abspath(__file__))
configurationFolderPath = os.path.join(rootFolderPath, 'configuration')
configurationFilePath = os.path.join(configurationFolderPath, 'configuration.json')
daemonConfigurationFilePath = os.path.join(configurationFolderPath, 'daemon.json')

daemon = None

with open(configurationFilePath, 'r') as config_file:
    config = json.load(config_file)

with open(daemonConfigurationFilePath, 'r') as config_file:
    daemonConfig = json.load(config_file)

app = App(token=daemonConfig["slack_bot_token"])

def main():
    args = parser.parse_args()
    if args.mode == 'daemon':
        launchDaemon()
    elif args.mode == 'status':
        printStatus()
    elif args.mode == 'list':
        listRooms()

def _createClient() -> NetatmoClient:
    clientID = config["netatmo"]["client_id"]
    clientSecret = config["netatmo"]["client_secret"]
    refreshToken = config["netatmo"]["refresh_token"]
    
    return NetatmoClient(clientID, clientSecret, refreshToken)

def launchDaemon():
    netatmoClient = _createClient()
    weatherWrapper = WeatherWrapper(config["weather"]["location"],config["weather"]["meteosourceAPIKey"])

    global daemon
    daemon = Daemon(app, netatmoClient, weatherWrapper, daemonConfig)

    thread = threading.Thread(target=daemon.run, daemon=True)
    thread.start()

    handler = SocketModeHandler(app, daemonConfig["slack_app_token"])
    handler.start()



@app.message(re.compile(daemonConfig["status_keyword"]))
def handle_status_command(message, say):
    say(daemon.getStatusMessage())


def listRooms():
 
    netatmoClient = _createClient()
    rooms = netatmoClient.listRooms()
    for room in rooms:
        print(room.toLongString())

def printStatus():

    weatherWrapper = WeatherWrapper(config["weather"]["location"],config["weather"]["meteosourceAPIKey"])

    message = weatherWrapper.toString()

    print(message)
    print()

    netatmoClient = _createClient()
    rooms = netatmoClient.listRooms()
    for room in rooms:
        print(room.toLongString())



if __name__ == "__main__":
    main()