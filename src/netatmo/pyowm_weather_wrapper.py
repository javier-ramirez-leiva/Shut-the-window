from pyowm import OWM
from netatmo.weather_wrapper import WeatherWrapper

class PyOwmWeatherWrapper(WeatherWrapper):
    def __init__(self, location: str, api_key: str):
        self._location = location
        self._owm = OWM(api_key)

    def getTemperature(self) -> float:
        mgr = self._owm.weather_manager()
        observation = mgr.weather_at_place(self._location)
        weather = observation.weather
        return weather.temperature('celsius')['temp']

    @property
    def location(self) -> str:
        return self._location

    def toString(self) -> str:
        temperature = self.getTemperature()
        return f"Current temperature in {self._location}: {temperature}°C"