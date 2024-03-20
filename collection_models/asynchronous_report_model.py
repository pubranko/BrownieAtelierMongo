from typing import Final

from BrownieAtelierMongo import settings
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel


class AsynchronousReportModel(MongoCommonModel):
    """
    非同期レポートコレクション用モデル
    """

    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__ASYNCHRONOUS_REPORT
    COLLECTION_NAME: Final[str] = "asynchronous_report"

    ##################
    # 定数
    ##################
    RECORD_TYPE: Final[str] = "record_type"
    """定数: 非同期レポートのレコードタイプ"""
    START_TIME: Final[str] = "start_time"
    """定数: 非同期レポートの作成日時"""
    PARAMETER: Final[str] = "parameter"
    """定数: 非同期レポート作成時のパラメータ"""
    DOMAIN: Final[str] = "domain"
    """定数: 非同期レポート作成時のパラメータ → ドメイン"""
    START_TIME_FROM: Final[str] = "start_time_from"
    """定数: 非同期レポート作成時のパラメータ → レポート期間(FROM)"""
    START_TIME_TO: Final[str] = "start_time_to"
    """定数: 非同期レポート作成時のパラメータ → レポート期間(TO)"""
    ASYNC_LIST: Final[str] = "async_list"
    """定数: 非同期レポートの結果リスト"""

    RECORD_TYPE__NEWS_CRAWL_ASYNC: Final[str] = "record_type__news_crawl_async"
    """定数(value): 非同期レポートレコードタイプ → ニュースクローラー非同期"""
    RECORD_TYPE__NEWS_CLIP_MASTER_ASYNC: Final[str] = "news_clip_master_async"
    """定数(value): 非同期レポートレコードタイプ → ニュースクリップマスター非同期"""
    RECORD_TYPE__SOLR_NEWS_CLIP_ASYNC: Final[str] = "solr_news_clip_async"
    """定数(value): 非同期レポートレコードタイプ → ソーラーニュースクリップ非同期"""
