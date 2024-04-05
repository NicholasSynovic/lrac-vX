import re
import warnings
from pprint import pprint as print
from string import Template
from typing import List

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from feedparser import parse
from feedparser.util import FeedParserDict
from pandas import DataFrame
from progress.bar import Bar
from requests import Response

warnings.filterwarnings(action="ignore")


class JOSS:
    def __init__(self) -> None:
        self.feedURL: str = "https://joss.theoj.org/papers/published.atom"

    def get(self) -> DataFrame:
        data: dict[str, List[str]] = {"doi": []}

        feed: FeedParserDict = parse(url_file_stream_or_string=self.feedURL)
        entries: List[FeedParserDict] = feed["entries"]

        entry: FeedParserDict
        for entry in entries:
            data["doi"].append(entry["doi"].strip())

        return DataFrame(data=data)


class JOSS_Historical:
    def __init__(self) -> None:
        self.feedURL: Template = Template(
            template="https://joss.theoj.org/papers/published?page=${page}"
        )

    def _identifyLastPage(self, soup: BeautifulSoup) -> int:
        lastPageURL: str = soup.find(name="link", attrs={"rel": "last"}).get(key="href")
        lastPage: int = int(re.findall(pattern=r"\d+", string=lastPageURL)[0])
        return lastPage

    def get(self) -> DataFrame:
        data: dict[str, List[str]] = {"doi": []}
        page: int = 1
        lastPage: int = 100

        with Bar("Getting historical data from JOSS...", max=lastPage) as bar:
            while True:
                resp: Response = requests.get(url=self.feedURL.substitute(page=page))
                html: bytes = resp.content

                soup: BeautifulSoup = BeautifulSoup(
                    markup=html,
                    features="xml",
                )
                papers: ResultSet = soup.find_all(name="doi")

                paper: Tag
                for paper in papers:
                    data["doi"].append(paper.text.strip())

                if (page == 1) or (page == lastPage):
                    lastPage = self._identifyLastPage(soup=soup)
                    bar.max = lastPage
                    bar.update()

                if page > lastPage:
                    break
                else:
                    page += 1

                bar.next()

        return DataFrame(data=data)
