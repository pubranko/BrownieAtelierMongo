from typing import Final

from BrownieAtelierMongo import settings
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel


class ScrapedFromResponseModel(MongoCommonModel):
    """
    scraped_from_responseコレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__SCRAPED_FROM_RESPONSE
    COLLECTION_NAME: Final[str] = "scraped_from_response"

    ###############
    # 定数
    ###############
    DOMAIN: Final[str] = "domain"
    """定数: domain"""
    URL: Final[str] = "url"
    """定数: url"""
    RESPONSE_TIME: Final[str] = "response_time"
    """定数: response_time"""
    CRAWLING_START_TIME: Final[str] = "crawling_start_time"
    """定数: crawling_start_time"""
    SCRAPYING_START_TIME: Final[str] = "scrapying_start_time"
    """定数: scrapying_start_time"""
    SOURCE_OF_INFORMATION: Final[str] = "source_of_information"
    """定数: source_of_information"""
    SOURCE_URL: Final[str] = "source_url"
    """定数: source_url"""
    LASTMOD: Final[str] = "lastmod"
    """定数: lastmod"""
    PATTERN: Final[str] = "pattern"
    """定数: pattern"""
    TITLE_SCRAPER: Final[str] = "title_scraper"
    """定数: title_scraper"""
    ARTICLE_SCRAPER: Final[str] = "article_scraper"
    """定数: article_scraper"""
    PUBLISH_DATE_SCRAPER: Final[str] = "publish_date_scraper"
    """定数: publish_date_scraper"""
    TITLE: Final[str] = "title"
    """定数: title"""
    ARTICLE: Final[str] = "article"
    """定数: article"""
    PUBLISH_DATE: Final[str] = "publish_date"
    """定数: publish_date"""

    def __init__(self, mongo: MongoModel):
        super().__init__(mongo)

        # インデックスの有無を確認し、なければ作成する。
        # ※sort使用時、indexがないとメモリ不足となるため。
        create_index_flg: bool = True
        for indexes in self.mongo.mongo_db[self.COLLECTION_NAME].list_indexes():
            for idx in indexes["key"]:
                if idx == "response_time":
                    create_index_flg = False
        if create_index_flg:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index("response_time")
