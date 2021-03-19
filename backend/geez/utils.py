"""
geez.utils

mauricesvp 2021
"""
import functools
from datetime import datetime, timedelta
from time import sleep
from typing import no_type_check

from bs4 import BeautifulSoup

from geez.log import setup_logger

logger = setup_logger("geez_utils")


def get_category(soup: BeautifulSoup) -> str:
    return "IC" if "Interest" in str(soup.find(class_="navigate_section")) else "GB"


def get_date(soup: BeautifulSoup) -> float:
    date_str = soup.find(class_="keyinfo").find(class_="smalltext").contents[-1]
    date_str = date_str.replace("»", "").strip()
    return date_conv(date_str)


def date_conv(date_str: str) -> float:
    date = datetime.strptime(date_str, "%a, %d %B %Y, %X") + timedelta(hours=7)
    return date.timestamp()


@no_type_check
def retry(times: int = 3, delay: int = 1):
    def run(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            attempts = 0
            while attempts < times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.debug(f"Trying again. {func} .{e}")
                    attempts += 1
                    sleep(delay)

        return f

    return run
