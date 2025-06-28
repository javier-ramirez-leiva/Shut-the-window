import argparse
import json
import os
from typing import Dict

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

with open(configurationFilePath, 'r') as config_file:
    config = json.load(config_file)

def main():
    args = parser.parse_args()
    if args.mode == 'daemon':
        launchDaemon()
    elif args.mode == 'status':
        printStatus()
    elif args.mode == 'list':
        listRooms()

def _createClient() -> NetatmoClient:
    clientID = config["netatmo"]["clientID"]
    clientSecret = config["netatmo"]["clientSecret"]
    refreshToken = config["netatmo"]["refreshToken"]
    
    return NetatmoClient(clientID, clientSecret, refreshToken)

def launchDaemon():
    netatmoClient = _createClient()
    weatherWrapper = WeatherWrapper(config["weather"]["location"],config["weather"]["meteosourceAPIKey"])

    daemonConfigurationFilePath = os.path.join(configurationFolderPath, 'daemon.json')

    with open(daemonConfigurationFilePath, 'r') as daemon_config_file:
        daemonConfig = json.load(daemon_config_file)

    daemon = Daemon(netatmoClient, weatherWrapper, daemonConfig)
    daemon.run()

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