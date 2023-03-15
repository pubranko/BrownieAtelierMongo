import sys
import logging
from logging import Logger, LoggerAdapter
from decouple import config, AutoConfig
# .envファイルが存在するパスを指定。実行時のカレントディレクトリに.envを配置している場合、以下の設定不要。
# config = AutoConfig(search_path="./shared")

# ロガー設定。
# 各モジュールではここで設定した「logger」が使用できます。
logger: Logger = logging.getLogger('BrownieAtelierNotice')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
format='%(asctime)s %(levelname)s [%(name)s] : %(message)s'
datefmt='%Y-%m-%d %H:%M:%S'
handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))


# mongoDB接続設定
BROWNIE_ATELIER_MONGO__MONGO_SERVER:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_SERVER'))
BROWNIE_ATELIER_MONGO__MONGO_PORT:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_PORT'))
BROWNIE_ATELIER_MONGO__MONGO_USE_DB:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_USE_DB'))
BROWNIE_ATELIER_MONGO__MONGO_USER:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_USER'))
BROWNIE_ATELIER_MONGO__MONGO_PASS:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_PASS'))
BROWNIE_ATELIER_MONGO__MONGO_TLS:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_TLS'))
BROWNIE_ATELIER_MONGO__MONGO_TLS_CA_FILE:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_TLS_CA_FILE'))
BROWNIE_ATELIER_MONGO__MONGO_TLS_CERTTIFICATE_KEY_FILE:str = str(config('BROWNIE_ATELIER_MONGO__MONGO_TLS_CERTTIFICATE_KEY_FILE'))
