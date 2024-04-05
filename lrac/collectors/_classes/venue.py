from abc import ABCMeta, abstractmethod
from typing import Protocol

from bs4 import BeautifulSoup
from pandas import DataFrame


class Venue_Protocol(Protocol):
    feedURL: str


class Venue_ABC(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> DataFrame:
        ...


class Venue_Historical_ABC(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def _identifyLastPage(self, soup: BeautifulSoup) -> int:
        ...

    @abstractmethod
    def get(self) -> DataFrame:
        ...
