from datetime import datetime
from typing import Any, Final

from BrownieAtelierMongo import settings
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from pymongo import ASCENDING


class CrawlerResponseModel(MongoCommonModel):
    """
    crawler_responseコレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__CRAWLER_RESPONSE
    COLLECTION_NAME: Final[str] = "crawler_response"

    ###############################
    # コレクション内の項目名定数
    ###############################
    DOMAIN: Final[str] = "domain"
    """定数: リクエスト・レスポンスのドメイン(key)"""
    URL: Final[str] = "url"
    """定数: リクエスト・レスポンスのURL(key)"""
    RESPONSE_TIME: Final[str] = "response_time"
    """定数: レスポンスタイム(key)"""
    RESPONSE_HEADERS: Final[str] = "response_headers"
    """定数: レスポンスのヘッダー部(key)"""
    RESPONSE_BODY: Final[str] = "response_body"
    """定数: レスポンスのボディー部(key)"""
    SPIDER_VERSION_INFO: Final[str] = "spider_version_info"
    """定数: スパイダーのバージョン情報(key)"""
    CRAWLING_START_TIME: Final[str] = "crawling_start_time"
    """定数: クロール開始時間(key)"""

    KEY: Final[str] = "key"
    """定数: mongoDBよりインデックスを取得する際の項目名"""

    SOURCE_OF_INFORMATION: Final[str] = "source_of_information"
    """定数: クロール対象URLの取得の元の情報を保管する項目(key)"""
    SOURCE_OF_INFORMATION__SOURCE_URL: Final[str] = "source_url"
    """定数: クロール対象URLの取得の元のURL(key)"""
    SOURCE_OF_INFORMATION__LASTMOD: Final[str] = "lastmod"
    """定数: クロール対象URLの取得の元の最終更新日時(key)"""
    NEWS_CLIP_MASTER_REGISTER: Final[str] = "news_clip_master_register"
    """定数: ニュースクリップマスターへの登録結果を記録(key)"""

    NEWS_CLIP_MASTER_REGISTER__COMPLETE: Final[str] = "登録完了"
    """定数(value): スクレイプしたデータをニュースクリップマスターへ登録したことを意味する。"""
    NEWS_CLIP_MASTER_REGISTER__SKIP: Final[str] = "登録内容に差異なしのため不要"
    """定数(value): スクレイプしたデータが登録済みであったため、ニュースクリップマスターへの登録をスキップしたことを意味する。"""

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
        if not self.NEWS_CLIP_MASTER_REGISTER in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.NEWS_CLIP_MASTER_REGISTER)

    def news_clip_master_register_result(
        self, url: str, response_time: datetime, news_clip_master_register: str
    ) -> None:
        """news_clip_masterへの登録結果を反映させる"""
        record: Any = self.find_one(
            filter={"$and": [{self.URL: url}, {self.RESPONSE_TIME: response_time}]}
        )

        if record == None:
            self.mongo.logger.warning(
                f"=== 【url= {url}, response_time= {response_time} news_clip_master_register= {news_clip_master_register}】 のデータでが既に削除されていたためnews_clip_masterへの登録結果を反映させる処理をスキップしました。"
            )
        else:
            record[self.NEWS_CLIP_MASTER_REGISTER] = news_clip_master_register

            self.update_one(
                {self.URL: url, self.RESPONSE_TIME: response_time},
                {"$set": record},
            )
