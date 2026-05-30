import argparse
import asyncio
import json
import os
import re
import threading
from typing import Dict

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from netatmo.netatmo_client import NetatmoClient
from netatmo.pymeteosource_weather_wrapper import PyMeteoSourceWeatherWrapper
from netatmo.pyowm_weather_wrapper import PyOwmWeatherWrapper
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
seen_events = set()

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
    if config["weather"]["client"] == "owm":
        weatherWrapper = PyOwmWeatherWrapper(config["weather"]["location"],config["weather"]["owmAPIKey"])
    else:
        weatherWrapper = PyMeteoSourceWeatherWrapper(config["weather"]["location"],config["weather"]["meteosourceAPIKey"])

    global daemon
    daemon = Daemon(app, netatmoClient, weatherWrapper, daemonConfig)

    thread = threading.Thread(target=daemon.run, daemon=True)
    thread.start()

    handler = SocketModeHandler(app, daemonConfig["slack_app_token"])
    handler.start()



@app.message(re.compile(daemonConfig["status_keyword"]))
def handle_status_command(message, say):
    event_id = message.get("client_msg_id") or message.get("ts")
    if event_id in seen_events:
        return  # ignore duplicate
    seen_events.add(event_id)
    print(f"Received status command: {daemonConfig['status_keyword']}")
    say(daemon.getStatusMessage())


def listRooms():
 
    netatmoClient = _createClient()
    rooms = netatmoClient.listRooms()
    for room in rooms:
        print(room.toLongString())

def printStatus():

    pyMeteoSourceWeatherWrapper = PyMeteoSourceWeatherWrapper(config["weather"]["location"],config["weather"]["meteosourceAPIKey"])
    message = pyMeteoSourceWeatherWrapper.toString()
    print(f"PyMeteoSourceWeatherWrapper: {message}")
    print()

    pyOwmWeatherWrapper = PyOwmWeatherWrapper(config["weather"]["location"],config["weather"]["owmAPIKey"])
    message = pyOwmWeatherWrapper.toString()
    print(f"PyOwmWeatherWrapper: {message}")
    print()

    netatmoClient = _createClient()
    rooms = netatmoClient.listRooms()
    for room in rooms:
        print(room.toLongString())



if __name__ == "__main__":
    main()