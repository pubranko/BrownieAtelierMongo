from typing import Final, Generator, Optional, Tuple

from BrownieAtelierMongo import settings
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.data_models.scraper_info_by_domain_data import (
    ScraperInfoByDomainConst, ScraperInfoByDomainData)
from pydantic import ValidationError
from pymongo.cursor import Cursor


class ScraperInfoByDomainModel(MongoCommonModel):
    """
    scraper_by_domainコレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__SCRAPER_BY_DOMAIN
    COLLECTION_NAME: Final[str] = "scraper_by_domain"

    ###########################
    # 定数 ()
    ###########################
    # ScraperInfoByDomainConstクラスに定義しています。

    def find_and_data_models_get(
        self, filter: Optional[dict[str, str]] = None
    ) -> list[ScraperInfoByDomainData]:
        """scraper_by_domainコレクションより取得したデータを「リスト[データクラス,,,]」の形式で返す。"""
        records: Cursor = self.find(filter=filter)
        return [ScraperInfoByDomainData(scraper=record) for record in records]

    def data_check(self, scraper):
        ScraperInfoByDomainData(scraper=scraper)
