from typing import ClassVar, Final

from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.data_models.scraper_info_by_domain_data import (
    ScraperInfoByDomainData,
)
from pymongo.cursor import Cursor


class ScraperInfoByDomainModel(MongoCommonModel):
    """
    scraper_by_domainコレクション用モデル
    """

    mongo: MongoModel
    COLLECTION_NAME: ClassVar[str] = "scraper_by_domain"

    ###########################
    # 定数 ()
    ###########################
    # ScraperInfoByDomainConstクラスに定義しています。
    DOMAIN: Final[str] = "domain"
    """定数: ドメイン(key)"""

    KEY: Final[str] = "key"
    """定数: mongoDBよりインデックスを取得する際の項目名"""

    def __init__(self, mongo: MongoModel):
        super().__init__(mongo)

        # インデックスの有無を確認し、なければ作成する。
        # ※findやsort使用時、indexがないとフルスキャンを行い長時間処理やメモリ不足となるため。
        #   indexes['key']のデータイメージ => SON([('_id', 1)])、SON([('response_time', 1)])
        index_list: list = []
        for indexes in self.mongo.mongo_db[self.COLLECTION_NAME].list_indexes():
            index_list = list(indexes[self.KEY])

        # 各indexがなかった場合、インデックスを作成する。
        if self.DOMAIN not in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.DOMAIN)

    def find_and_data_models_get(self, filter: dict[str, str] | None = None) -> list[ScraperInfoByDomainData]:
        """scraper_by_domainコレクションより取得したデータを「リスト[データクラス,,,]」の形式で返す。"""
        records: Cursor = self.find(filter=filter)
        return [ScraperInfoByDomainData(scraper=record) for record in records]

    def data_check(self, scraper):
        ScraperInfoByDomainData(scraper=scraper)
