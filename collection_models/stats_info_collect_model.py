from typing import Any, Final

from BrownieAtelierMongo import settings
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel


class StatsInfoCollectModel(MongoCommonModel):
    """
    ログ集計コレクション用モデル
    """

    mongo: MongoModel
    COLLECTION_NAME: Final[str] = "stats_info_collect"

    RECORD_TYPE: Final[str] = "record_type"
    START_TIME: Final[str] = "start_time"
    SPIDER_NAME: Final[str] = "spider_name"

    KEY: Final[str] = "key"
    """定数: mongoDBよりインデックスを取得する際の項目名"""

    def __init__(self, mongo: MongoModel):
        super().__init__(mongo)

        # インデックスの有無を確認し、なければ作成する。
        # ※findやsort使用時、indexがないとフルスキャンを行い長時間処理やメモリ不足となるため。
        #   indexes['key']のデータイメージ => SON([('_id', 1)])、SON([('response_time', 1)])
        index_list: list = []
        for indexes in self.mongo.mongo_db[self.COLLECTION_NAME].list_indexes():
            index_list = [idx for idx in indexes[self.KEY]]

        index_key = f"{self.START_TIME}__{self.RECORD_TYPE}__{self.SPIDER_NAME}"
        # 各indexがなかった場合、インデックスを作成する。
        if not index_key in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(index_key)

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
