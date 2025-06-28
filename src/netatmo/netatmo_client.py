from typing import Dict
import requests
from netatmo.room import Room


class NetatmoClient:
    def __init__(self, clientID:str,clientSecret:str,refreshToken:str):
        self._clientID = clientID
        self._clientSecret = clientSecret
        self._refreshToken = refreshToken
        self._accessToken = None

    
    def _refreshNetatmoToken(self):
        url = "https://api.netatmo.com/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self._refreshToken ,
            "client_id": self._clientID ,
            "client_secret": self._clientSecret
        }

        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        tokens = response.json()
        self._accessToken = tokens["access_token"]
        self._refreshToken = tokens["refresh_token"]

    def _getHttpCall(self,url:str,) -> requests.Response:
        self._refreshNetatmoToken()
        headers = {
            "Authorization": f"Bearer {self._accessToken}"
        }
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        return response

    def listRooms(self) -> list[Room]:
        url = "https://api.netatmo.com/api/homesdata"
        response = self._getHttpCall(url)
        homes = response.json()["body"]["homes"]
        if not homes:
            raise Exception("No homes found.")

        rooms=[]

        for home in homes:
            homeID = home["id"]
            homeName = home["name"]
            url = f"https://api.netatmo.com/api/homestatus?home_id={homeID}"
            response = self._getHttpCall(url)

            ##Do this in a real map entering with ID and returning name 
            roomNames = {}
            for room in home["rooms"]:
                roomNames[room["id"]] = room["name"]
            roomsDic = response.json()["body"]["home"]["rooms"]
            for roomDic in roomsDic:
                roomID = roomDic["id"]
                ##roomName = room["name"]
                roomName = roomNames[roomID]
                temperature = roomDic["therm_measured_temperature"]
                temperatureSet = roomDic["therm_setpoint_temperature"]
                room = Room(homeID,homeName,roomID,roomName,temperature,temperatureSet)
                rooms.append(room)
        return rooms