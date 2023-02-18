from typing import Any
from decouple import config, AutoConfig
from typing import Union
from BrownieAtelierMongo.models.mongo_model import MongoModel
from BrownieAtelierMongo.models.mongo_common_model import MongoCommonModel
# config = AutoConfig(search_path="./shared")


class ControllerModel(MongoCommonModel):
    '''
    controllerコレクション用モデル
    '''
    mongo: MongoModel
    collection_name: str = str(config('BROWNIE_ATELIER_MONGO__MONGO_CONTROLLER', default='controller'))

    def crawl_point_get(self, domain_name: str, spider_name: str) -> dict:
        '''
        次回のクロールポイント情報(lastmod,urlなど)を取得し返す。
        まだ存在しない場合、空のdictを返す。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'domain': domain_name}, {'document_type': 'crawl_point'}]})

        next_point_record: dict = {}
        # レコードが存在し、かつ、同じスパイダーでクロール実績がある場合
        if not record == None:
            if spider_name in record:
                next_point_record = record[spider_name]

        return next_point_record

    def crawl_point_update(self, domain_name: str, spider_name: str, next_point_info: dict) -> None:
        '''次回のクロールポイント情報(lastmod,urlなど)を更新する'''
        record: Any = self.find_one(
            filter={'$and': [{'domain': domain_name}, {'document_type': 'crawl_point'}]})
        if record == None:  # ドメインに対して初クロールの場合
            record = {
                'document_type': 'crawl_point',
                'domain': domain_name,
                spider_name: next_point_info,
            }
        else:
            record[spider_name] = next_point_info

        self.update_one({'domain': domain_name}, {"$set":record},)

    def crawling_stop_domain_list_get(self,) -> list:
        '''
        stop_controllerからクローリング停止ドメインリストを取得して返す
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'stop_controller'}]})

        if record == None:
            return []
        elif not 'crawling_stop_domain_list' in record:
            return []
        else:
            return record['crawling_stop_domain_list']

    def crawling_stop_domain_list_update(self, crawling_stop_domain_list: list) -> None:
        '''
        stop_controllerのクローリング停止ドメインリストを更新する。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'stop_controller'}]})

        if record == None:  # 初回の場合
            record = {
                'document_type': 'stop_controller',
                'crawling_stop_domain_list': crawling_stop_domain_list,
            }
        else:
            record['crawling_stop_domain_list'] = crawling_stop_domain_list

        self.update_one({'document_type': 'stop_controller'}, {"$set":record},)

    def scrapying_stop_domain_list_get(self,) -> list:
        '''
        stop_controllerからスクレイピング停止ドメインリストを取得して返す。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'stop_controller'}]})

        if record == None:
            return []
        elif not 'scrapying_stop_domain_list' in record:
            return []
        else:
            return record['scrapying_stop_domain_list']

    def scrapying_stop_domain_list_update(self, scrapying_stop_domain_list: list) -> None:
        '''
        stop_controllerのスクレイピング停止ドメインリストを更新する。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'stop_controller'}]})

        if record == None:  # 初回の場合
            record = {
                'document_type': 'stop_controller',
                'scrapying_stop_domain_list': scrapying_stop_domain_list,
            }
        else:
            record['scrapying_stop_domain_list'] = scrapying_stop_domain_list

        self.update_one({'document_type': 'stop_controller'}, {"$set":record},)

    def regular_observation_spider_name_set_get(self,) -> set:
        '''
        定期観測対象のスパイダーのセットを返す。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'regular_observation_controller'}]})

        if record == None:
            return set([])
        else:
            return set(record['spiders_name_set'])

    def regular_observation_spider_name_set_update(self, spiders_name_set: set) -> None:
        '''
        定期観測対象のスパイダーリストを更新する。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'regular_observation_controller'}]})

        if record == None:  # 初回の場合
            record = {
                'document_type': 'regular_observation_controller',
                'spiders_name_set': list(spiders_name_set),
            }
        else:
            record['spiders_name_set'] = list(spiders_name_set)

        self.update_one(
            {'document_type': 'regular_observation_controller'}, {"$set":record},)

    def brownie_atelier_mongo_manual_mode_get(self) -> bool:
        '''
        '''
        record: Union[dict[str,bool],None] = self.find_one(
            filter={'$and': [{'document_type': 'brownie_atelier_mongo_manual_mode'}]})

        if record:
            return record['brownie_atelier_mongo_manual_mode_flag']
        else:
            return False

    def brownie_atelier_mongo_manual_mode_set(self, brownie_atelier_manual_mode_flag: bool) -> None:
        '''
        BrownieAtelierMongoのマニュアル操作のフラグ
        true  -> マニュアル操作中。mongoDBコンテナの自動停止させない。
        false -> 定期観測（自動クロール）中。定期観測処理終了後、mongoDBコンテナを自動停止する。
        '''
        record: Any = self.find_one(
            filter={'$and': [{'document_type': 'brownie_atelier_manual_mode'}]})
        record = {
            'document_type': 'brownie_atelier_mongo_manual_mode',
            'brownie_atelier_mongo_manual_mode_flag': brownie_atelier_manual_mode_flag
        }

        self.update_one({'document_type': 'brownie_atelier_mongo_manual_mode'}, {"$set":record},)

