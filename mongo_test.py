'''
mongoDBとの接続確認テスト用
    以下の用な用途で使用する。
    ・環境変数、または、.envファイルの設定で接続できるか確認
    ・各モデルの実行を手動で実験
'''
from pymongo.mongo_client import MongoClient
from BrownieAtelierMongo.models.mongo_model import MongoModel
from BrownieAtelierMongo.models.controller_model import ControllerModel

mongo = MongoModel()
controller_model = ControllerModel(mongo)

couted = controller_model.count()
print(f'件数 : {couted}')


# print(f'brownie_atelier_mongo_manual_mode_flag : {controller_model.brownie_atelier_mongo_manual_mode_get()}')
# controller_model.brownie_atelier_mongo_manual_mode_set(False)
# print(f'brownie_atelier_mongo_manual_mode_flag : {controller_model.brownie_atelier_mongo_manual_mode_get()}')