from netatmo.weather_wrapper import WeatherWrapper
import os
import json

class TestWeatherWrapper(WeatherWrapper):
    def __init__(self, location: str, api_key: str):
        self._location = location
        self._api_key = api_key

    def getTemperature(self) -> float:
        rootFolderPath = os.path.dirname(os.path.abspath(__file__))
        configurationFolderPath = os.path.join(rootFolderPath, 'configuration')
        testTemperatureFilePath = os.path.join(configurationFolderPath, 'test_temperature.json')
        with open(testTemperatureFilePath, 'r') as temp_file:
            temp_data = json.load(temp_file)
        return temp_data.get('temperature', 0.0)    

    @property
    def location(self) -> str:
        return self._location

    def toString(self) -> str:
        temperature = self.getTemperature()
        return f"Current temperature in {self._location}: {temperature}°C"