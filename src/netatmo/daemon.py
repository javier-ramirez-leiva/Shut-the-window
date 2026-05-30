import time
import re
import asyncio
from typing import Any, Optional

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
        rooms, outsideTemp = self._fetchCurrentData()
        self._refreshWindowStatus(rooms, outsideTemp)
        msg = f"Current temperature in {self._weatherWrapper.location}: {outsideTemp}°C\n\n"

        for room in rooms:
            if room.roomID not in self._windowClosedMap:
                continue
            msg += room.toShortString() + ". Window should be "
            msg +=  "closed" if self._windowClosedMap[room.roomID] else "open"

        return f"```{msg.strip()}```"

    def run(self):
        self._initWindowStatus()
        print("Daemon monitor loop started.")
        statusMessage = self.getStatusMessage()
        print(f"Sending status message: {statusMessage}")
        self._app.client.chat_postMessage(channel=self._channelID, text=self.getStatusMessage())
        while True:
            rooms, outsideTemp = self._fetchCurrentData()
            for room in rooms:
                message = None
                print(f"Checking room {room.roomName} in {room.homeName}")
                if room.roomID not in self._windowClosedMap:
                    continue
                wasWindowClosed = self._windowClosedMap[room.roomID]
                print()
                print(f"Current window status: {'closed' if wasWindowClosed else 'open'}")
                shouldWindowBeClosed = self._computeWindowClosedStatus(room, outsideTemp, wasWindowClosed)
                print(f"Room temperature: {room.temperature}°C, Outside temperature: {outsideTemp}°C")
                print(f"Computed window status: {'closed' if shouldWindowBeClosed else 'open'}")
                print()
                self._windowClosedMap[room.roomID] = shouldWindowBeClosed

                if wasWindowClosed != shouldWindowBeClosed:
                    action = "Close" if shouldWindowBeClosed else "Open"
                    message = f"*{action} the window in {room.roomName} in {room.homeName}!*"

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

    def _fetchCurrentData(self) -> tuple[list[Room], float]:
        rooms = self._netatmoClient.listRooms()
        outsideTemp = self._weatherWrapper.getTemperature()
        return rooms, outsideTemp

    def _refreshWindowStatus(self, rooms: list[Room], outsideTemp: float):
        for room in rooms:
            if room.roomID not in self._windowClosedMap:
                continue
            currentWindowClosed = self._windowClosedMap[room.roomID]
            self._windowClosedMap[room.roomID] = self._computeWindowClosedStatus(room, outsideTemp, currentWindowClosed)

    def _computeWindowClosedStatus(self, room: Room, outsideTemp: float, currentWindowClosed: bool) -> bool:
        thresholdOpen, thresholdClose = self._getTrehsholdTemperatures(room)
        if currentWindowClosed and room.temperature > (outsideTemp + thresholdOpen):
            return False
        if (not currentWindowClosed) and room.temperature < (outsideTemp - thresholdClose):
            return True
        return currentWindowClosed

    def _getTrehsholdTemperatures(self, room: Room) -> list[float]:
        thresholds = self._daemonConfig.get("alert", {}).get("temp_thresholds", {})
        thresholdConfig = self._resolveRoomThresholds(thresholds, room)
        if thresholdConfig is None:
            return [0, 0]

        thresholdOpen = self._toFloat(thresholdConfig.get("open"), 0)
        thresholdClose = self._toFloat(thresholdConfig.get("close"), 0)
        return [thresholdOpen, thresholdClose]

    def _resolveRoomThresholds(self, thresholds: dict[str, Any], room: Room) -> Optional[dict[str, Any]]:
        roomKeys = [
            room.roomID,
            room.roomName,
            f"{room.homeName}/{room.roomName}",
            f"{room.homeID}/{room.roomID}",
        ]
        for key in roomKeys:
            if key in thresholds:
                return thresholds[key]
        return None

    def _toFloat(self, value: Any, defaultValue: float) -> float:
        if value is None:
            return defaultValue
        try:
            return float(value)
        except (TypeError, ValueError):
            return defaultValue
        
