from pydantic import ValidationError
from typing import Tuple, Generator, Final, Optional
from pymongo.cursor import Cursor
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo import settings
from BrownieAtelierMongo.data_models.scraper_info_by_domain_data import ScraperInfoByDomainData


class ScraperInfoByDomainModel(MongoCommonModel):
    '''
    scraper_by_domainコレクション用モデル
    '''
    mongo: MongoModel
    # collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__SCRAPER_BY_DOMAIN
    COLLECTION_NAME: Final[str] = 'scraper_by_domain'

    ###########################
    # 定数 ()
    ###########################
    DOMAIN: Final[str] = 'domain'
    SCRAPE_ITEMS: Final[str] = 'scrape_items'
    SCRAPE_ITEMS__TITLE_SCRAPER: Final[str] = 'scrape_items__title_scraper'
    SCRAPE_ITEMS__ARTICLE_SCRAPER: Final[str] = 'scrape_items__article_scraper'
    SCRAPE_ITEMS__PUBLISH_DATE_SCRAPER: Final[str] = 'scrape_items__publish_date_scraper'
    ITEM__PATTERN: Final[str] = 'pattern'
    ITEM__CSS_SELECTER: Final[str] = 'css_selecter'
    ITEM__PRIORITY: Final[str] = 'priority'
    ITEM__REGISTER_DATE: Final[str] = 'register_date'

    # scraper_by_domain_record: dict = {}

    def find_and_data_models_get(self, filter: Optional[dict[str, str]] = None) -> list[ScraperInfoByDomainData]:
        '''scraper_by_domainコレクションより取得したデータを「リスト[データクラス,,,]」の形式で返す。'''
        records: Cursor = self.find(filter=filter)
        return [ScraperInfoByDomainData(scraper=record) for record in records]

    # def record_read(self, filter) -> None:
    #     ''' '''
    #     record = self.find_one(filter=filter)
    #     if type(record) is dict:
    #         self.scraper_by_domain_record = record
    #     else:
    #         self.scraper_by_domain_record = {}

    # def domain_get(self) -> str:
    #     '''ドメインを返す'''
    #     return self.scraper_by_domain_record['domain']

    # def scrape_item_get(self) -> Generator[Tuple[str, list[dict[str, str]]], None, None]:
    #     '''
    #     廃止する！！！！！！！！！！！！！！！！！！！！！　scrape_itemsを返すジェネレーター
    #     '''
    #     scrape_items: dict[str, list[dict[str, str]]
    #                        ] = self.scraper_by_domain_record['scrape_items']
    #     for scraper, pattern_list in scrape_items.items():
    #         # patternリストは、patternで降順にソート
    #         pattern_list = sorted(pattern_list,
    #                     key=lambda d: d['pattern'], reverse=True)
    #         yield scraper, pattern_list

    def data_check(self, scraper):
        ScraperInfoByDomainData(scraper=scraper)

        # try:
        #     ScraperInfoByDomainData(scraper=scraper_info)
        # except ValidationError as e:
        #     error_info: list = e.errors()
        #     self.mongo.logger.error(
        #         f'=== ScraperInfoUploaderTask run エラー({file_name}) : {error_info[0]["msg"]}')
        # else:
        #     self.update_one(
        #         filter={'domain': scraper_info['domain']},
        #         record={"$set":scraper_info})
        #     self.mongo.logger.info(
        #         f'=== ScraperInfoUploaderTask run 登録完了 : {file_name}')
