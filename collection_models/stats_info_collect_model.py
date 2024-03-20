from typing import Any, Final
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo import settings


class StatsInfoCollectModel(MongoCommonModel):
    """
    ログ集計コレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__STATS_INFO_COLLECT
    COLLECTION_NAME: Final[str] = "stats_info_collect"

    RECORD_TYPE: Final[str] = "record_type"
    START_TIME: Final[str] = "start_time"
    SPIDER_NAME: Final[str] = "spider_name"

    def stats_update(self, records: list, status_key: str = ""):
        """ """
        for record in records:
            conditions: list = []
            conditions.append({self.RECORD_TYPE: record[self.RECORD_TYPE]})
            conditions.append({self.START_TIME: record[self.START_TIME]})
            conditions.append({self.SPIDER_NAME: record[self.SPIDER_NAME]})
            if len(status_key):
                conditions.append({status_key: record[status_key]})
            filter: Any = {"$and": conditions}

            self.update_one(filter, {"$set": record})
