import statistics
from typing import Union

from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from pymongo.cursor import Cursor


class MongoCommonModel(object):
    """
    mongoDBへの共通アクセス処理。
    各コレクション別のクラスでは当クラスを継承することで共通の関数を定義する必要がなくなる。
    """

    mongo: MongoModel
    COLLECTION_NAME: str = "sample"

    def __init__(self, mongo: MongoModel):
        self.mongo = mongo

    def count(self, filter: Union[dict, None] = None) -> int:
        """
        コレクションのカウント。
        絞り込み条件がある場合、filterを指定してください。
        コレクション内ドキュメント総数のカウントであれば、filterに指定は不要です。
        """
        if type(filter) is dict:
            # return self.count_documents(filter)
            return self.aggregation_pipeline(filter)
        else:
            return self.estimated_document_count()

    def aggregation_pipeline(self, filter: Union[dict, None] = {}):
        """
        フィルターで絞り込みを行ったコレクション内のドキュメント数を返す。
        Args:
            filter (Union[dict, None], optional): フィルターを設定。値がない場合は空の辞書({})とする。
        """
        pipeline = [
            filter, # フィルター条件
            {"$count": "count"} # ドキュメント数をカウント
        ]
        result = self.mongo.mongo_db[self.COLLECTION_NAME].aggregate(pipeline)
        return list(result)[0]["count"] if result else 0
        
    # def count_documents(self, filter: dict):
    #     """
    #     コレクション内の条件付き件数のカウント。
    #     絞り込み条件がある場合、filterを指定してください。
    #     """
    #     return self.mongo.mongo_db[self.COLLECTION_NAME].count_documents(filter=filter)

    def estimated_document_count(self):
        """コレクション内のドキュメント総数のカウント"""
        return self.mongo.mongo_db[self.COLLECTION_NAME].estimated_document_count()

    def find_one(self, projection=None, filter=None):
        return self.mongo.mongo_db[self.COLLECTION_NAME].find_one(
            projection=projection, filter=filter
        )

    def find(self, projection=None, filter=None, sort=None):
        return self.mongo.mongo_db[self.COLLECTION_NAME].find(
            projection=projection, filter=filter, sort=sort
        )

    def insert_one(self, item):
        self.mongo.mongo_db[self.COLLECTION_NAME].insert_one(item)

    def insert(self, items: list):
        self.mongo.mongo_db[self.COLLECTION_NAME].insert_many(items)

    def update_one(self, filter, record: dict) -> None:
        self.mongo.mongo_db[self.COLLECTION_NAME].update_one(
            filter, record, upsert=True
        )

    # def update_many(self, filter, record: dict) -> None:
    #     self.mongo.mongo_db[self.collection_name].update_many(
    #         filter, record, upsert=True)

    def delete_many(self, filter) -> int:
        result = self.mongo.mongo_db[self.COLLECTION_NAME].delete_many(filter=filter)
        return int(result.deleted_count)

    def custom_aggregate(self, aggregate_key: str):
        """渡された集計keyによる集計結果を返す。"""
        pipeline = [
            {"$unwind": "$" + aggregate_key},
            {"$group": {"_id": "$" + aggregate_key, "count": {"$sum": 1}}},
        ]
        return self.mongo.mongo_db[self.COLLECTION_NAME].aggregate(pipeline=pipeline)

    def limited_find(
        self, projection=None, filter: dict[str, list] = {}, sort=None, limit: int = 100
    ):
        """
        ・findした結果をレコード単位で返すジェネレーター。
        ・デフォルトで100件単位でデータを取得するが、当メソッドの呼び出し元では
          取得件数の制限を意識すること無く検索結果を参照できる。
        ・以下のような繰り返し処理で使用することを想定
            for record in news_clip_master.limited_find(filter=filter):
                pass
        """
        # 対象件数を確認
        record_count = self.mongo.mongo_db[self.COLLECTION_NAME].count_documents(
            filter=filter if filter else {}
        )
        # 100件単位で処理を実施
        skip_list = list(range(0, record_count, limit))
        for skip in skip_list:
            records: Cursor = (
                self.find(filter=filter, projection=projection, sort=sort)
                .skip(skip)
                .limit(limit)
            )
            for record in records:
                yield record
            del records  # 念の為処理が終わったオブジェクトを削除

    def document_size_info(self) -> dict:
        """
        コレクション内のドキュメントサイズ情報を辞書で返す。
        return = {count, max, min, mean, sum}
        """
        document_size_list: list[int] = []
        # ドキュメント内の各要素のサイズを合計しドキュメントのサイズとする。
        # ドキュメントサイズのリストを生成
        for record in self.limited_find():
            document_size: int = sum([value.__sizeof__() for value in record.values()])
            document_size_list.append(document_size)

        return dict(
            document_coumt=self.count(),
            document_max=max(document_size_list),
            document_min=min(document_size_list),
            document_mean=round(statistics.mean(document_size_list), 1),  # 小数点以下1位まで
            document_sum=sum(document_size_list),
        )
