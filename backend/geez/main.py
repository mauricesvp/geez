"""
geez.main

mauricesvp 2021
"""
import re
from time import sleep
from typing import List

import requests
from bs4 import BeautifulSoup as BS

import geez.db as db
from geez.log import setup_logger
from geez.topic import Topic
from geez.utils import date_conv, retry

logger = setup_logger("geez_main")

# Initialize global db instance
geezdb: db.GeezDB


@retry()
def get_(url: str) -> requests.models.Response:
    return requests.get(url, timeout=5)


def get_topics(soup: BS, category: str) -> List[Topic]:
    topics_tmp = []
    table = soup.find("table", class_="table_grid").find("tbody")
    rows = table.find_all("tr")  # Skip head
    for row in rows:
        try:
            cols = row.find_all("td")
            if "windowbg" in cols[0]["class"]:
                try:
                    author = cols[2].find("p").find("a").decode_contents()
                    title = cols[2].find("span").find("a").decode_contents().strip()
                    url = cols[2].find("a")["href"]
                    topic_id = re.findall("topic=([0-9]+).0", url)[0]
                    tmp = (
                        cols[4]
                        .decode_contents()
                        .split("/a>")[1]
                        .split("<br")[0]
                        .strip()
                    )
                    last = date_conv(tmp)
                    topic = Topic(
                        id=int(topic_id),
                        author=author,
                        category=category,
                        latest_comment=last,
                        latest_author_comment=last,
                        title=title,
                        first_changed=last,
                        date=last,
                    )
                    topics_tmp.append(topic)
                except AttributeError as e:
                    logger.warning(f"Error with topic. {e}")
                    # logger.debug(cols)  # multiline ...
                    continue
        except ValueError as e:
            logger.warning(f"Error with row. {e}")
            # logger.debug(row)  # multiline ...
            continue
    return topics_tmp


def scrape_board(board_id: str, offset: int = None) -> None:
    """
    Get all topics from board.
    """
    logger.info(f"Scraping board (id={board_id}).")
    assert board_id in ["70", "132"]
    topics = []
    url = f"https://geekhack.org/index.php?board={board_id}"
    r = get_(url)
    try:
        soup = BS(r.text, "lxml")
    except AttributeError as e:
        logger.error(f"Error getting soup. Skipping {url}. {e}")
        return
    pages = soup.find(class_="pagelinks").find_all("a")
    try:
        last = (
            re.search(f"{board_id}.([0-9]+)0", pages[-3]["href"])
            .group(0)  # type: ignore
            .split(".")[1]
        )
    except AttributeError as e:
        logger.warn(f"Error scraping board {board_id}. {e}")
        return

    category = "IC" if (board_id == "132") else "GB"
    topics += get_topics(soup, category=category)
    for i in range(50, int(last) + 50, 50):
        new_url = url + f".{i}"
        r_tmp = get_(new_url)
        soup_tmp = BS(r_tmp.text, "lxml")
        topics += get_topics(soup_tmp, category=category)

    global geezdb
    geezdb.add_topics(topics)


@retry()
def init_db(host: str) -> None:
    """
    Initialize MongoDB (if necessary).
    """
    logger.info("Initializing database.")
    global geezdb
    geezdb = db.GeezDB(host=host)


def main(host: str = "mongodb") -> None:
    init_db(host=host)
    while True:
        """Main loop, scrape boards every five minutes."""
        global geezdb
        count = geezdb.db["topics"].count_documents({})
        if count == 1:
            logger.info("Deleting dummy topic")
            geezdb.del_topic_id(id=0)
        scrape_board("70")
        scrape_board("132")
        sleep(300)


if __name__ == "__main__":
    main()
