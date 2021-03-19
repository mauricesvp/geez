"""
geez.topic

mauricesvp 2021
"""
import hashlib
import time

import requests
from bs4 import BeautifulSoup

import geez.utils as utils


class Topic:
    def __init__(
        self,
        id: int,
        author: str = "",
        category: str = "",
        date: float = 0.0,
        post: str = "",
        first_changed: float = 0.0,
        title: str = "",
        latest_comment: float = 0.0,
        latest_author_comment: float = 0.0,
    ):
        self.id = id
        self.url = f"https://geekhack.org/index.php?topic={self.id}"
        self.author = author
        self.category = category
        self.date = date
        self.post = post
        self.first_changed = first_changed
        self.title = title
        self.latest_comment = latest_comment
        self.latest_author_comment = latest_comment

    def populate(self) -> None:
        r = requests.get(self.url)
        assert r.status_code == 200, "Error getting topic."
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            self.title = str(soup.find(class_="keyinfo").a.string)
        except AttributeError:
            print(f"Failed to get title for: {id}")
            raise Exception
        self.author = str(soup.find(class_="poster").a.string)
        self.category = utils.get_category(soup)
        self.date = utils.get_date(soup)
        m = hashlib.sha256(str(soup.find(class_="inner")).encode())
        self.post = m.hexdigest()
        self.first_changed = self.date
        self.update_latest(soup)

    def update(self) -> None:
        r = requests.get(self.url)
        assert r.status_code == 200, "Error getting topic."
        soup = BeautifulSoup(r.text, "html.parser")
        post = str(soup.find(class_="inner"))
        if post != self.post:
            self.post = post
            self.first_changed = time.time()
        self.update_latest(soup)

    def update_latest(self, soup: BeautifulSoup) -> None:
        if soup.find_all(class_="navPages"):
            for entry in soup.find_all(class_="navPages")[-2::-1]:
                r2 = requests.get(entry["href"])
                if self.author in r2.text:
                    break
            soup2 = BeautifulSoup(r2.text, "html.parser")
        else:
            soup2 = soup
        for post in soup2.find_all(class_="post_wrapper")[::-1]:
            if post.a.string == self.author:
                self.latest = utils.get_date(post)
                break

    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, author={self.author}, category={self.category})>"
