from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, sections, langs, units
from geopy.geocoders import Nominatim



class WeatherWrapper:
    def __init__(self,location:str, apiKey:str):
        self._location = location
        self._apiKey = apiKey

        geolocator = Nominatim(user_agent="geoapi")
        geoLocation = geolocator.geocode(self._location)

        if location:
            self._lat = geoLocation.latitude
            self._lon = geoLocation.longitude
        else:
            raise ValueError(f"Could not find location: {self._location}")
        


    def getTemperature(self) -> float:

        meteosource = Meteosource(self._apiKey, tiers.FREE)

        # Fetch hourly forecast for a location
        forecast = meteosource.get_point_forecast(
            lat=self._lat,  
            lon=self._lon,
            place_id=None,  # You can specify place_id instead of lat+lon
            sections=[sections.CURRENT, sections.HOURLY],  # Defaults to '("current", "hourly")'
            lang=langs.ENGLISH,
            units=units.METRIC 
        )

        # Get the first entry, which is usually the current hour
        current_hour = forecast['hourly'][0]

        # Extract temperature
        return current_hour['temperature']

    @property
    def location(self) -> str:
        return self._location

    def toString(self) -> str:
        temperature = self.getTemperature()
        return f"Current temperature in {self._location}: {temperature}°C"
