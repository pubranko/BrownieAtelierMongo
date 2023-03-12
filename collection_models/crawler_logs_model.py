from typing import Final
from datetime import datetime
from scrapy.statscollectors import MemoryStatsCollector
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo import settings


class CrawlerLogsModel(MongoCommonModel):
    '''
    crawler_logsコレクション用モデル
    '''
    mongo: MongoModel
    collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__CRAWLER_LOGS

    # spider_reportとstatsのログ（他はまだ見ていない）
    START_TIME: Final[str] = 'start_time'
    '''定数: 各種処理の開始時間(key)'''
    RECORD_TYPE: Final[str] = 'record_type'
    '''定数: レコードタイプ(key)'''

    # Flowログ項目
    FLOW_NAME: Final[str] = 'flow_name'
    '''定数: 実行されたprefectのFlow名(key)'''
    LOGS: Final[str] = 'logs'
    '''定数: ログ(key)'''

    # spider_reportのkey項目
    DOMAIN: Final[str] = 'domain'
    '''定数: ドメイン(key)'''
    SPIDER_NAME: Final[str] = 'spider_name'
    '''定数: スパイダー名(key)'''
    STATS: Final[str] = 'stats'
    '''定数: 統計(key)'''

    # クロールURL情報リスト系の項目
    CRAWL_URLS_LIST: Final[str] = 'crawl_urls_list'
    '''定数: クロールURL情報リスト(key)'''
    CRAWL_URLS_LIST__SOURCE_URL: Final[str] = 'source_url'
    '''定数: クロールURL情報リスト_取得元となるURL (key)  サイトマップや一覧ページのURL'''
    CRAWL_URLS_LIST__ITEMS: Final[str] = 'items'
    '''定数: クロールURL情報リスト_取得元となるURL内でクロール対象となったURL・最終更新時間を保存するリスト (key)'''
    CRAWL_URLS_LIST__LOC: Final[str] = 'loc'
    '''定数: クロールURL情報リスト_URL (key)'''
    CRAWL_URLS_LIST__LASTMOD: Final[str] = 'lastmod'
    '''定数: クロールURL情報リスト_最終更新時間 (key)'''

    KEY: Final[str] = 'key'
    '''定数: mongoDBよりインデックスを取得する際の項目名'''


    # レコードタイプ(value)
    RECORD_TYPE__FLOW_REPORTS: Final[str] = 'flow_reports'
    '''レコードタイプ(value): フローレポート  Prefect Flowのログ'''     #現在タスク名にしているレコードタイプをこれに変更したい。
    RECORD_TYPE__SPIDER_REPORTS: Final[str] = 'spider_reports'
    '''レコードタイプ(value): スパイダーレポート  Spiderのログ'''
    # RECORD_TYPE__NEWS_CRAWL_ASYNC: Final[str] = 'news_crawl_async'
    # '''レコードタイプ(value): ニュースクローラー非同期'''
    # RECORD_TYPE__NEWS_CLIP_MASTER_ASYNC: Final[str] = 'news_clip_master_async'
    # '''レコードタイプ(value): ニュースクリップマスター非同期'''
    # RECORD_TYPE__SOLR_NEWS_CLIP_ASYNC: Final[str] = 'solr_news_clip_async'
    # '''レコードタイプ(value): ソーラーニュースクリップ非同期'''
    # RECORD_TYPE__ROBOTS_RESPONSE_STATUS: Final[str] = 'robots_response_status'
    # '''レコードタイプ(value): ロボットレスポンス統計'''


    def __init__(self, mongo: MongoModel):
        super().__init__(mongo)

        # インデックスの有無を確認し、なければ作成する。
        # ※sort使用時、indexがないとメモリ不足となるため。
        create_index_flg:bool = True
        for indexes in self.mongo.mongo_db[self.collection_name].list_indexes():
            for idx in indexes[self.KEY]:
                if idx == self.START_TIME:
                    create_index_flg = False
        if create_index_flg:
            self.mongo.mongo_db[self.collection_name].create_index(self.START_TIME)

    def spider_report_insert(self, crawling_start_time: datetime, domain: str, spider_name: str, stats: MemoryStatsCollector, crawl_urls_list: list[dict]):
        '''
        クロールの統計結果とクロールを行ったサイトの一覧情報を「spider_report」としてログに保存する。
        '''

        # spiderの統計情報（stats）を取得し、mongoDBにKeyとして保存できない文字列ドット(.)をアンダースコア(_)へ変更する。
        stats_edit: dict = {}
        for item in stats.get_stats().items():
            key: str = str(item[0]).replace('.', '_')
            stats_edit[key] = item[1]

        # 【データイメージ】
        # ログに保管するときはsource_urlごとの配列内にlocとlastmodを格納するよう構造変換
        # 引数：crawl_urls_list = [ {'source_url': ①, 'lastmod': ②, 'loc': ③ },,,]
        # ↳ temp = {①:, [ {'loc':② , 'lastmod':③},{~},{~},,, ] }
        #   ↳ crawl_urls_list = [ {source_urls: ① , items: [ { loc:② , lastmod:③},,,,, ] } ]
        temp: dict = {}
        source_urls:list = []
        for record in crawl_urls_list:
            if record[self.CRAWL_URLS_LIST__SOURCE_URL] in temp.keys():
                temp[record[self.CRAWL_URLS_LIST__SOURCE_URL]].append({
                    self.CRAWL_URLS_LIST__LOC: record[self.CRAWL_URLS_LIST__LOC],
                    self.CRAWL_URLS_LIST__LASTMOD: record[self.CRAWL_URLS_LIST__LASTMOD]})
            else:
                temp[record[self.CRAWL_URLS_LIST__SOURCE_URL]] = [{
                    self.CRAWL_URLS_LIST__LOC: record[self.CRAWL_URLS_LIST__LOC],
                    self.CRAWL_URLS_LIST__LASTMOD: record[self.CRAWL_URLS_LIST__LASTMOD], }]
        for key,value in temp.items():
            source_urls.append({
                self.CRAWL_URLS_LIST__SOURCE_URL: key,
                self.CRAWL_URLS_LIST__ITEMS:value,})

        self.insert_one({
            self.START_TIME: crawling_start_time,
            self.RECORD_TYPE: self.RECORD_TYPE__SPIDER_REPORTS,
            self.DOMAIN: domain,
            self.SPIDER_NAME: spider_name,
            self.STATS: stats_edit,
            self.CRAWL_URLS_LIST: source_urls,})
