from typing import Any, Final
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo import settings


class ControllerModel(MongoCommonModel):
    """
    controllerコレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__CONTROLLER
    COLLECTION_NAME: Final[str] = "controller"

    ###############################
    # コレクション内の項目名定数
    ###############################
    DOMAIN: Final[str] = "domain"
    """コントロール対象のドメイン(key)"""
    DOCUMENT_TYPE: Final[str] = "document_type"
    """各ドキュメントのタイプ(Key)"""
    DOCUMENT_TYPE__CRAWL_POINT: Final[str] = "crawl_point"
    """ドキュメントのタイプ(value): クロールポイント"""
    DOCUMENT_TYPE__STOP_CONTROLLER: Final[str] = "stop_controller"
    """ドキュメントのタイプ(value): ストップコントローラー"""
    DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER: Final[
        str
    ] = "regular_observation_controller"
    """ドキュメントのタイプ(value): 定期観測コントローラー"""

    CRAWLING_STOP_DOMAIN_LIST: Final[str] = "crawling_stop_domain_list"
    """クローリング停止したいドメインを登録するリスト(key)"""
    SCRAPYING_STOP_DOMAIN_LIST: Final[str] = "scrapying_stop_domain_list"
    """スクレイピング停止したいドメインを登録するリスト(key)"""
    SPIDERS_NAME_SET: Final[str] = "spiders_name_set"
    """定期観測対象のスパイダーセット(key)"""
    LATEST_LASTMOD: Final[str] = "latest_lastmod"
    """クロール時の最終更新日時(key)"""
    URLS: Final[str] = "urls"
    """クロール時の直近のurlを保存するリスト(key)"""
    LOC: Final[str] = "loc"
    """クロール対象ページのloc(ロケーション=url)(key)"""
    LASTMOD: Final[str] = "lastmod"
    """クロール対象ページの最終更新日時(key)"""
    SOURCE_URL: Final[str] = "source_url"
    """クロール対象時、元となったsitemapや一覧ページのurl(key)"""
    CRAWLING_START_TIME: Final[str] = "crawling_start_time"
    """クロール開始時間(key)"""

    def crawl_point_get(self, domain_name: str, spider_name: str) -> dict:
        """
        次回のクロールポイント情報(lastmod,urlなど)を取得し返す。
        まだ存在しない場合、空のdictを返す。
        """
        record: Any = self.find_one(
            filter={
                "$and": [
                    {self.DOMAIN: domain_name},
                    {self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__CRAWL_POINT},
                ]
            }
        )

        next_point_record: dict = {}
        # レコードが存在し、かつ、同じスパイダーでクロール実績がある場合
        if not record == None:
            if spider_name in record:
                next_point_record = record[spider_name]

        return next_point_record

    def crawl_point_update(
        self, domain_name: str, spider_name: str, next_point_info: dict
    ) -> None:
        """次回のクロールポイント情報(lastmod,urlなど)を更新する"""
        record: Any = self.find_one(
            filter={
                "$and": [
                    {self.DOMAIN: domain_name},
                    {self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__CRAWL_POINT},
                ]
            }
        )
        if record == None:  # ドメインに対して初クロールの場合
            record = {
                self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__CRAWL_POINT,
                self.DOMAIN: domain_name,
                spider_name: next_point_info,
            }
        else:
            record[spider_name] = next_point_info

        self.update_one(
            {self.DOMAIN: domain_name},
            {"$set": record},
        )

    def crawling_stop_domain_list_get(
        self,
    ) -> list:
        """
        stop_controllerからクローリング停止ドメインリストを取得して返す
        """
        record: Any = self.find_one(
            filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]}
        )

        if record == None:
            return []
        elif not self.CRAWLING_STOP_DOMAIN_LIST in record:
            return []
        else:
            return record[self.CRAWLING_STOP_DOMAIN_LIST]

    def crawling_stop_domain_list_update(self, crawling_stop_domain_list: list) -> None:
        """
        stop_controllerのクローリング停止ドメインリストを更新する。
        """
        record: Any = self.find_one(
            filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]}
        )

        if record == None:  # 初回の場合
            record = {
                self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER,
                self.CRAWLING_STOP_DOMAIN_LIST: crawling_stop_domain_list,
            }
        else:
            record[self.CRAWLING_STOP_DOMAIN_LIST] = crawling_stop_domain_list

        self.update_one(
            {self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER},
            {"$set": record},
        )

    def scrapying_stop_domain_list_get(
        self,
    ) -> list:
        """
        stop_controllerからスクレイピング停止ドメインリストを取得して返す。
        """
        record: Any = self.find_one(
            filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]}
        )

        if record == None:
            return []
        elif not self.SCRAPYING_STOP_DOMAIN_LIST in record:
            return []
        else:
            return record[self.SCRAPYING_STOP_DOMAIN_LIST]

    def scrapying_stop_domain_list_update(
        self, scrapying_stop_domain_list: list
    ) -> None:
        """
        stop_controllerのスクレイピング停止ドメインリストを更新する。
        """
        record: Any = self.find_one(
            filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]}
        )

        if record == None:  # 初回の場合
            record = {
                self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER,
                self.SCRAPYING_STOP_DOMAIN_LIST: scrapying_stop_domain_list,
            }
        else:
            record[self.SCRAPYING_STOP_DOMAIN_LIST] = scrapying_stop_domain_list

        self.update_one(
            {self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER},
            {"$set": record},
        )

    def regular_observation_spider_name_set_get(
        self,
    ) -> set:
        """
        定期観測対象のスパイダーのセットを返す。
        """
        record: Any = self.find_one(
            filter={
                "$and": [
                    {
                        self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER
                    }
                ]
            }
        )

        if record == None:
            return set([])
        else:
            return set(record[self.SPIDERS_NAME_SET])

    def regular_observation_spider_name_set_update(self, spiders_name_set: set) -> None:
        """
        定期観測対象のスパイダーセットを更新する。
        """
        record: Any = self.find_one(
            filter={
                "$and": [
                    {
                        self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER
                    }
                ]
            }
        )

        if record == None:  # 初回の場合
            record = {
                self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER,
                self.SPIDERS_NAME_SET: list(spiders_name_set),
            }
        else:
            record[self.SPIDERS_NAME_SET] = list(spiders_name_set)

        self.update_one(
            {self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER},
            {"$set": record},
        )
