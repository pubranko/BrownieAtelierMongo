from BrownieAtelierMongo.models.mongo_model import MongoModel
from BrownieAtelierMongo.models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo import settings


class AsynchronousReportModel(MongoCommonModel):
    '''
    非同期レポートコレクション用モデル
    '''
    mongo: MongoModel
    collection_name: str = settings.BROWNIE_ATELIER_MONGO__COLLECTION__ASYNCHRONOUS_REPORT
