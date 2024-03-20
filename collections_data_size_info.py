from BrownieAtelierMongo.collection_models.asynchronous_report_model import \
    AsynchronousReportModel
from BrownieAtelierMongo.collection_models.controller_model import \
    ControllerModel
from BrownieAtelierMongo.collection_models.crawler_logs_model import \
    CrawlerLogsModel
from BrownieAtelierMongo.collection_models.crawler_response_model import \
    CrawlerResponseModel
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.collection_models.news_clip_master_model import \
    NewsClipMasterModel
from BrownieAtelierMongo.collection_models.scraped_from_response_model import \
    ScrapedFromResponseModel
from BrownieAtelierMongo.collection_models.scraper_info_by_domain_model import \
    ScraperInfoByDomainModel
from BrownieAtelierMongo.collection_models.stats_info_collect_model import \
    StatsInfoCollectModel
from pymongo.cursor import Cursor
from pymongo.mongo_client import MongoClient

"""
これは手動実行専用。情報はprintでログへ出力。
"""


mongo = MongoModel()

collections: list[MongoCommonModel] = [
    AsynchronousReportModel(mongo),
    ControllerModel(mongo),
    CrawlerLogsModel(mongo),
    CrawlerResponseModel(mongo),
    NewsClipMasterModel(mongo),
    ScrapedFromResponseModel(mongo),
    ScraperInfoByDomainModel(mongo),
    StatsInfoCollectModel(mongo),
]

print(f'{"コレクション名":<18}{"件数":>16}{"最大":>16}{"最小":>16}{"平均":>16}{"合計":>16}')
for collection in collections:
    collection_info: str = ""
    collection_info = f"{collection.COLLECTION_NAME :<25}"
    for value in collection.document_size_info().values():
        collection_info = collection_info + f"{value :>18,}"
    print(collection_info)
