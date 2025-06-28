from typing import Dict

class Room:
    def __init__(self, homeID:str, homeName:str,roomID:str,roomName:str, temperature:float, temperatureSet:float):
        self._homeID = homeID
        self._homeName = homeName
        self._roomID = roomID
        self._roomName = roomName
        self._temperature = temperature
        self._temperatureSet = temperatureSet

    @property
    def homeID(self)->str:
        return self._homeID

    @property
    def homeName(self)->str:
        return self._homeName

    @property
    def roomID(self)->str:
        return self._roomID
    

    @property
    def roomName(self)->str:
        return self._roomName

    @property
    def temperature(self)->float:
        return self._temperature

    @property
    def temperatureSet(self)->float:
        return self._temperatureSet

    def toLongString(self) -> str:
        return f"Room \"{self._roomName}\" [{self._roomID}] in \"{self._homeName}\" [{self._homeID}] has a temperature of \"{self._temperature}\" degrees Celsius and a set temperature of \"{self._temperatureSet}\" degrees Celsius"

    def toShortString(self) -> str:
        return f"Room \"{self._roomName}\" in \"{self._homeName}\": \"{self._temperature}\" °C"