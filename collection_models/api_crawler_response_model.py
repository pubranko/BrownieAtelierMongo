from datetime import datetime
from typing import Any, Final

from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from pymongo import ASCENDING


class ApiCrawlerResponseModel(MongoCommonModel):
    """
    crawler_responseコレクション用モデル
    """

    mongo: MongoModel
    COLLECTION_NAME: Final[str] = "api_crawler_response"

    ###############################
    # コレクション内の項目名定数
    ###############################
    DOMAIN: Final[str] = "domain"
    """定数: リクエスト・レスポンスのドメイン(key)"""
    URL: Final[str] = "url"
    """定数: リクエスト・レスポンスのURL(key)"""
    CRAWLING_START_TIME: Final[str] = "crawling_start_time"
    """定数: クロール開始時間(key)"""
    RESPONSE_TIME: Final[str] = "response_time"
    """定数: レスポンスタイム(key)"""
    RESPONSE: Final[str] = "response"
    """定数: レスポンス(key)"""

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

        # 各indexがなかった場合、インデックスを作成する。
        if not self.RESPONSE_TIME in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.RESPONSE_TIME)
        if not self.CRAWLING_START_TIME in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.CRAWLING_START_TIME)
        if not self.DOMAIN in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.DOMAIN)
        if not self.URL in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.URL)
