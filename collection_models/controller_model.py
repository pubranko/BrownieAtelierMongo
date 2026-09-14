from typing import Any, ClassVar, Final

from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel


class ControllerModel(MongoCommonModel):
    """
    controllerコレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__CONTROLLER
    COLLECTION_NAME: ClassVar[str] = "controller"

    ###############################
    # コレクション内の項目名定数
    ###############################
    DOMAIN: Final[str] = "domain"
    """コントロール対象のドメイン(key)"""
    DOCUMENT_TYPE: Final[str] = "document_type"
    """各ドキュメントのタイプ(Key)"""
    DOCUMENT_TYPE__CRAWL_POINT: Final[str] = "crawl_point"
    """ドキュメントのタイプ(value): クロールポイント"""
    DOCUMENT_TYPE__DOWNLOAD_CONTROL: Final[str] = "download_control"
    """ドメイン共通の送信間隔・再開可能時刻（クロールポイントとは別レコード）"""
    DOWNLOAD_DELAY: Final[str] = "download_delay"
    """送信制御の基準間隔（秒）を保存する項目名(key)。

    429 による加算後の値を次回起動へ引き継ぐ。AutoThrottle の一時的な調整値は保存しない。
    """
    RETRY_AFTER_UNTIL: Final[str] = "retry_after_until"
    """送信を再開してよい日時（UTC の BSON Date）を保存する項目名(key)。

    429、または有効な Retry-After を持つ 503 の待機期限を記録する。
    次回起動時も期限前なら待機し、再起動によって待機を省略しない。
    """
    DOCUMENT_TYPE__STOP_CONTROLLER: Final[str] = "stop_controller"
    """ドキュメントのタイプ(value): ストップコントローラー"""
    DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER: Final[str] = "regular_observation_controller"
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
        if self.DOCUMENT_TYPE not in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.DOCUMENT_TYPE)

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
        if record:
            if spider_name in record:
                next_point_record = record[spider_name]

        return next_point_record

    def crawl_point_update(self, domain_name: str, spider_name: str, next_point_info: dict) -> None:
        """次回のクロールポイント情報(lastmod,urlなど)を更新する"""
        # 同一 domain に download_control もあるため、必ず文書種別を含めて更新する。
        # 文書全体や _id を書き戻さず、このスパイダーの情報だけを更新する。
        self.update_one(
            {self.DOMAIN: domain_name, self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__CRAWL_POINT},
            {"$set": {spider_name: next_point_info}},
        )

    def download_control_get(self, domain_name: str) -> dict:
        """同じサイトの各スパイダーが共有する減速状態を取得する。"""
        return self.find_one(filter={
            self.DOMAIN: domain_name,
            self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__DOWNLOAD_CONTROL,
        }) or {}

    def download_control_update(self, domain_name: str, state: dict) -> None:
        """変更時に保存し、途中終了でもサーバー指定の待機期限を引き継ぐ。"""
        self.update_one(
            {self.DOMAIN: domain_name, self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__DOWNLOAD_CONTROL},
            {"$set": state},
        )

    def crawling_stop_domain_list_get(
        self,
    ) -> list:
        """
        stop_controllerからクローリング停止ドメインリストを取得して返す
        """
        record: Any = self.find_one(filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]})

        if not record:
            return []
        elif self.CRAWLING_STOP_DOMAIN_LIST not in record:
            return []
        else:
            return record[self.CRAWLING_STOP_DOMAIN_LIST]

    def crawling_stop_domain_list_update(self, crawling_stop_domain_list: list) -> None:
        """
        stop_controllerのクローリング停止ドメインリストを更新する。
        """
        record: Any = self.find_one(filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]})

        if not record:  # 初回の場合
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
        record: Any = self.find_one(filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]})

        if not record:
            return []
        elif self.SCRAPYING_STOP_DOMAIN_LIST not in record:
            return []
        else:
            return record[self.SCRAPYING_STOP_DOMAIN_LIST]

    def scrapying_stop_domain_list_update(self, scrapying_stop_domain_list: list) -> None:
        """
        stop_controllerのスクレイピング停止ドメインリストを更新する。
        """
        record: Any = self.find_one(filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__STOP_CONTROLLER}]})

        if not record:  # 初回の場合
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
            filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER}]}
        )

        if not record:
            return set()
        else:
            return set(record[self.SPIDERS_NAME_SET])

    def regular_observation_spider_name_set_update(self, spiders_name_set: set) -> None:
        """
        定期観測対象のスパイダーセットを更新する。
        """
        record: Any = self.find_one(
            filter={"$and": [{self.DOCUMENT_TYPE: self.DOCUMENT_TYPE__REGULAR_OBSERVATION_CONTROLLER}]}
        )

        if not record:  # 初回の場合
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
