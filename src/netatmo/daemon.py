import time
import re
import asyncio

from netatmo.room import Room
from netatmo.netatmo_client import NetatmoClient
from netatmo.weather_wrapper import WeatherWrapper


class Daemon:
    def __init__(self,app, netatmoClient : NetatmoClient, weatherWrapper : WeatherWrapper, daemonConfig):
        self._app = app
        self._netatmoClient = netatmoClient
        self._weatherWrapper = weatherWrapper
        self._daemonConfig = daemonConfig

        self._returnStatusOnAlert = daemonConfig["alert"]["return_status_on_alert"]
        self._ignore = daemonConfig["alert"]["ignore"]
        self._timeout = daemonConfig["alert"]["timeout"]
        self._channelID = daemonConfig["alert"]["channel_id"]

        self._windowClosedMap = {}

    def getStatusMessage(self) -> str:
        msg = self._weatherWrapper.toString() + "\n\n"
        rooms = self._netatmoClient.listRooms()

        for room in rooms:
            msg += room.toShortString() + ". Window should be "
            msg +=  "closed" if self._windowClosedMap[room.roomID] else "open"

        return f"```{msg.strip()}```"

    def run(self):
        self._initWindowStatus()
        print("Daemon monitor loop started.")
        statusMessage = self.getStatusMessage()
        print(f"Sending status message: {statusMessage}")
        self._app.client.chat_postMessage(channel=self._channelID, text=self.getStatusMessage())
        time.sleep(self._timeout * 60)
        while True:
            rooms = self._netatmoClient.listRooms()
            message = None
            outsideTemp = self._weatherWrapper.getTemperature()
            for room in rooms:
                print(f"Checking room {room.roomName} in {room.homeName}")
                if room.roomID not in self._windowClosedMap:
                    continue
                thresholdOpen, thresholdClose = self._getTrehsholdTemperatures(room)
                if room.temperature > (outsideTemp + thresholdOpen) and self._windowClosedMap[room.roomID] == True:
                    self._windowClosedMap[room.roomID] = False
                    message = f"*Open the window in {room.roomName} in {room.homeName}!*"
                elif room.temperature < (outsideTemp - thresholdClose) and self._windowClosedMap[room.roomID] == False:
                    self._windowClosedMap[room.roomID] = True
                    message = f"*Close the window in {room.roomName} in {room.homeName}!*"

                if message is not None:
                    print(f"Sending message: {message}")
                    self._app.client.chat_postMessage(channel=self._channelID, text=message)
                    if self._returnStatusOnAlert:
                        statusMessage = self.getStatusMessage()
                        print(f"Sending status message: {statusMessage}")
                        self._app.client.chat_postMessage(channel=self._channelID, text=statusMessage)

            time.sleep(self._timeout * 60)

    def _initWindowStatus(self):
        rooms = self._netatmoClient.listRooms()
        outsideTemp = self._weatherWrapper.getTemperature()
        for room in rooms:  
            if room.homeID in self._ignore or room.roomID in self._ignore or room.homeName in self._ignore or room.roomName in self._ignore:
                continue
            self._windowClosedMap[room.roomID] = room.temperature < outsideTemp

    def _getTrehsholdTemperatures(self, room: Room) -> list[float]:
        thresholds = self._daemonConfig.get("alert", {}).get("temp_thresholds", {})
        if room.roomID in thresholds:
            return [thresholds[room.roomID].get("open"), thresholds[room.roomID].get("close")]
        else:
            return [0, 0]
        
       
         
    




        