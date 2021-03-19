"""
geez.db

mauricesvp 2021
"""
from typing import Any, Dict, List

import pymongo
from pymongo.operations import UpdateOne

from geez.log import setup_logger
from geez.topic import Topic
from geez.utils import retry

logger = setup_logger("geez_db")


class GeezDB:
    db: pymongo.database.Database = None

    def __init__(self, host: str = "mongodb"):
        logger.info(f"Init db on host {host}.")
        self.host = host
        if not self.db:
            self.db = self.get_db()
        topics = self.db["topics"]
        if topics.count() == 0:
            # If there are no topics, we need to initialize the table,
            # defining all columns, and creating an index.
            topics.create_index("id", unique=True)
            # The dummy topic will get deleted later on.
            topic = Topic(
                id=0,
                author="dummy_author",
                category="dummy_category",
                date=0,
                post="dummy_post",
                first_changed=0,
                title="dummy title",
                latest_comment=0,
                latest_author_comment=0,
            )
            self.add_topic(topic)

    @retry()
    def connect(self) -> pymongo.MongoClient:
        return pymongo.MongoClient(self.host)

    @retry()
    def get_db(self) -> Any:
        return self.connect()["geezdb"]

    def add_topic(self, topic: Topic) -> None:
        self.add_topics([topic])

    @retry()
    def add_topics(self, topics: List[Topic]) -> None:
        try:
            if not self.db:
                self.db = self.get_db()
            topics_data = self.build_topics(topics)
            if len(topics_data) == 0:
                logger.warn(f"No topics were inserted. {topics}")
                return
            self.db.topics.bulk_write(
                [
                    UpdateOne(filter={"id": d["id"]}, update={"$set": d}, upsert=True)
                    for d in topics_data
                ]
            )
            logger.info(f"Inserted {len(topics_data)} topics.")
        except AttributeError as e:
            logger.error(f"Error inserting topics. {topics}")
            raise e

    def build_topics(self, topics: List[Topic]) -> List[Dict]:
        topics_data = []
        for topic in topics:
            try:
                tmp_dict = {
                    "id": int(float(topic.id)),
                    "author": topic.author,
                    "category": topic.category,
                    "post": topic.post,
                    "title": topic.title,
                    "date": topic.date,
                    "first_changed": topic.first_changed,
                    "latest_comment": topic.latest_comment,
                    "latest_author_comment": topic.latest_author_comment,
                }
                topics_data.append(tmp_dict)
            except AttributeError as e:
                logger.warn(f"Skipping topic {topic}. {e}")
                continue

        return topics_data

    def del_topic_id(self, id: int) -> None:
        self.del_topics_id([id])

    @retry()
    def del_topics_id(self, ids: List[int]) -> None:
        try:
            for id in ids:
                self.db["topics"].delete_one({"id": id})
        except AttributeError as e:
            logger.error(f"Error deleting topics. {ids}")
            raise e

    def del_topic(self, topic: Topic) -> None:
        self.del_topics([topic])

    @retry()
    def del_topics(self, topics: List[Topic]) -> None:
        try:
            if not self.db:
                self.db = self.get_db()
            for topic in topics:
                self.db["topics"].delete_one({"id": topic.id})
        except AttributeError as e:
            logger.error(f"Error deleting topics. {topics}")
            raise e
