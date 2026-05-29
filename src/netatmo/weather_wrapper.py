from abc import ABC, abstractmethod

class WeatherWrapper(ABC):

    @abstractmethod
    def getTemperature(self) -> float:
        pass

    @property
    @abstractmethod
    def location(self) -> str:
        pass

    @abstractmethod
    def toString(self) -> str:
        pass