from typing import Final
from BrownieAtelierMongo.collection_models.mongo_common_model import \
    MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel


class NationalDietProceedingsMasterModel(MongoCommonModel):
    """
    国会会議録マスター
    """

    mongo: MongoModel
    COLLECTION_NAME: Final[str] = "national_diet_proceedings_master"
    DOMAIN_VALUE: Final[str] = "kokkai.ndl.go.jp"
    """定数: 国会会議録検索システムのドメイン(kokkai.ndl.go.jp)"""

    ###############################
    # コレクション内の項目名定数
    ###############################
    _ID: Final[str] = "_id"
    """定数: ドキュメントのID(key)"""
    DOMAIN: Final[str] = "domain"
    """定数: リクエスト・レスポンスのドメイン(key)"""
    URL: Final[str] = "url"
    """定数: リクエスト・レスポンスのURL(key)"""
    CRAWLING_START_TIME: Final[str] = "crawling_start_time"
    """定数: クロール開始時間(key)"""
    MASTER_SAVE_START_TIME: Final[str] = "master_save_start_time"
    """定数: マスターへ保存時の開始時間(key)"""
    RESPONSE_TIME: Final[str] = "response_time"
    """定数: レスポンスタイム(key)"""

    # apiより取得した国会会議録のデータ
    ISSUE_ID: Final[str] = "issueID"                # '121405254X00120241001',
    """定数: 会議録ID"""
    IMAGE_KIND: Final[str] = "imageKind"            # '会議録',
    """定数: イメージ種別（会議録・目次・索引・附録・追録）"""
    SEARCH_OBJECT: Final[str] = "searchObject"      # 0,
    """定数: 検索対象箇所（議事冒頭・本文）"""
    SESSION: Final[str] = "session"                 # 214,
    """定数: 国会回次"""
    NAME_OF_HOUSE: Final[str] = "nameOfHouse"       # '衆議院', '参議院'など
    """定数: 院名"""
    NAME_OF_MEETING: Final[str] = "nameOfMeeting"   # '本会議',  '沖縄及び北方問題に関する特別委員会'など
    """定数: 会議名"""
    ISSUE: Final[str] = "issue"                     # '第1号',
    """定数: 号数"""
    DATE: Final[str] = "date"                       # '2024-10-01',
    """定数: 開催日付"""
    CLOSING: Final[str] = "closing"                 # null, True
    """定数: 閉会中フラグ"""
    SPEECH_RECORD: Final[str] = "speechRecord"      # [{スピーチに関する情報},,,,]
    """定数: 各スピーチ毎に記載される情報
        [
            {
                "speechID": 発言ID ,
                "speechOrder": 発言番号 ,
                "speaker": 発言者名 ,
                "speakerYomi": 発言者よみ ,
                "speakerGroup": 発言者所属会派 ,
                "speakerPosition": 発言者肩書き ,
                "speakerRole": 発言者役割 ,
                "speech": 発言 ,
                "startPage": 発言が掲載されている開始ページ ,
                "speechURL": 発言URL ,
            },,,,
        ]
    """
    MEETING_URL: Final[str] = "meetingURL"          # 'https://kokkai.ndl.go.jp/txt/121405254X00120241001',
    """定数: 会議録テキスト表示画面のURL"""
    PDF_URL: Final[str] = "pdfURL"                  # 'https://kokkai.ndl.go.jp/img/121405254X00120241001'
    """定数: 会議録PDF表示画面のURL（※存在する場合のみ）"""

    KEY: Final[str] = "key"
    """定数: mongoDBよりインデックスを取得する際の項目名"""

    def __init__(self, mongo: MongoModel):
        super().__init__(mongo)

        # インデックスの有無を確認し、なければ作成する。
        # ※findやsort使用時、indexがないとフルスキャンを行い長時間処理やメモリ不足となるため。
        #   indexes['key']のデータイメージ => SON([('_id', 1)])、SON([('response_time', 1)])
        index_list: list = []
        for indexes in self.mongo.mongo_db[self.COLLECTION_NAME].list_indexes():
            index_list = [idx for idx in indexes[self.KEY]]

        # 各indexがなかった場合、インデックスを作成する。
        if not self.RESPONSE_TIME in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.RESPONSE_TIME)
        if not self.CRAWLING_START_TIME in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.CRAWLING_START_TIME)
        if not self.DOMAIN in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.DOMAIN)
        if not self.NAME_OF_HOUSE in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.NAME_OF_HOUSE)
        if not self.NAME_OF_MEETING in index_list:
            self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.NAME_OF_MEETING)
        if not self.ISSUE in index_list:
                self.mongo.mongo_db[self.COLLECTION_NAME].create_index(self.ISSUE)