from BrownieAtelierMongo.collection_models.asynchronous_report_model import \
    AsynchronousReportModel
from BrownieAtelierMongo.collection_models.controller_model import \
    ControllerModel
from BrownieAtelierMongo.collection_models.crawler_logs_model import \
    CrawlerLogsModel
from BrownieAtelierMongo.collection_models.crawler_response_model import \
    CrawlerResponseModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.collection_models.news_clip_master_model import \
    NewsClipMasterModel
from BrownieAtelierMongo.collection_models.scraped_from_response_model import \
    ScrapedFromResponseModel
from BrownieAtelierMongo.collection_models.scraper_info_by_domain_model import \
    ScraperInfoByDomainModel
from BrownieAtelierMongo.collection_models.stats_info_collect_model import \
    StatsInfoCollectModel
from pymongo.mongo_client import MongoClient

mongo = MongoModel()
asynchronous_report_model = AsynchronousReportModel(mongo)
controller_model = ControllerModel(mongo)
crawler_logs_model = CrawlerLogsModel(mongo)
crawler_response_model = CrawlerResponseModel(mongo)
news_clip_master_model = NewsClipMasterModel(mongo)
scraped_from_response_model = ScrapedFromResponseModel(mongo)
scraper_info_by_domain_model = ScraperInfoByDomainModel(mongo)
stats_info_collect_model = StatsInfoCollectModel(mongo)

print(f"asynchronous_report_model      {asynchronous_report_model.count()} :件")
print(f"controller_model               {controller_model.count()} :件")
print(f"crawler_logs_model             {crawler_logs_model.count()} :件")
print(f"crawler_response_model         {crawler_response_model.count()} :件")
print(f"news_clip_master_model         {news_clip_master_model.count()} :件")
print(f"scraped_from_response_model    {scraped_from_response_model.count()} :件")
print(f"scraper_info_by_domain_model   {scraper_info_by_domain_model.count()} :件")
print(f"stats_info_collect_model       {stats_info_collect_model.count()} :件")
