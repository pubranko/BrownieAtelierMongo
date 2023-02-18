from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from urllib.parse import quote_plus
from decouple import config, AutoConfig
# .envまたはsettings.iniが存在するパスを指定したい場合、以下のAutoConfigを利用してください。
# config = AutoConfig(search_path="./shared")

class MongoModel(object):
    '''
    MongoDB用モデル
    '''
    __mongo_server: str
    __mongo_port: str
    __mongo_db_name: str
    __mongo_user: str
    __mongo_pass: str
    __mongo_client: MongoClient
    mongo_db: Database

    def __init__(self):
        self.__mongo_server = str(config('BROWNIE_ATELIER_MONGO__MONGO_SERVER'))
        self.__mongo_port = str(config('BROWNIE_ATELIER_MONGO__MONGO_PORT'))
        self.__mongo_db_name = str(config('BROWNIE_ATELIER_MONGO__MONGO_USE_DB'))
        self.__mongo_user = str(config('BROWNIE_ATELIER_MONGO__MONGO_USER'))
        self.__mongo_pass = str(config('BROWNIE_ATELIER_MONGO__MONGO_PASS'))
        self.__mongo_tls = str(config('BROWNIE_ATELIER_MONGO__MONGO_TLS'))
        self.__mongo_tls_ca_certs = str(config('BROWNIE_ATELIER_MONGO__MONGO_TLS_CA_FILE'))
        self.__mongo_tls_certtificate_key_file = str(config('BROWNIE_ATELIER_MONGO__MONGO_TLS_CERTTIFICATE_KEY_FILE'))

        param:dict = {
                # 'host': quote_plus(self.__mongo_server),
                'host': self.__mongo_server,
                'port': int(self.__mongo_port),
                'username': self.__mongo_user,
                'password': self.__mongo_pass,
                'authSource': self.__mongo_db_name,     # ユーザー認証を行うDB
        }
        # tls認証を行う場合、以下のパラメータを追加
        if self.__mongo_tls=='true':
            param.update({
                'tls': True,
                'tlsCAFile': self.__mongo_tls_ca_certs,
                'tlsCertificateKeyFile': self.__mongo_tls_certtificate_key_file,
            })

        self.__mongo_client = MongoClient(**param)
        self.mongo_db = self.__mongo_client[self.__mongo_db_name]

    def close(self):
        '''
        MongoClientを閉じる。
        '''
        self.__mongo_client.close()