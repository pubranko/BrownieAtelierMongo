"""クロール・スクレイピング設定を別レコードで保存するdomain_infoコレクション。"""

from datetime import UTC, datetime
from typing import Any, ClassVar

from BrownieAtelierMongo.collection_models.mongo_common_model import MongoCommonModel
from BrownieAtelierMongo.collection_models.mongo_model import MongoModel
from BrownieAtelierMongo.data_models.domain_info_data import DomainInfoData
from pymongo import ASCENDING, ReplaceOne


class DomainInfoModel(MongoCommonModel):
    COLLECTION_NAME: ClassVar[str] = "domain_info"

    def __init__(self, mongo: MongoModel):
        super().__init__(mongo)
        # create_indexは同名・同仕様なら何も変更しない。初回はコレクションも作成される。
        self.mongo.mongo_db[self.COLLECTION_NAME].create_index(
            [("domain", ASCENDING), ("kind", ASCENDING), ("profile", ASCENDING)],
            name="domain_kind_profile_unique",
            unique=True,
        )

    def save_definitions(self, loaded: list[dict[str, Any]]) -> int:
        """設定全体を置換するため、YAMLで削除した項目がDBに残らない。"""
        operations = []
        registered_at = datetime.now(UTC)
        for entry in loaded:
            definition = DomainInfoData.model_validate(entry["definition"])
            data = definition.model_dump(mode="json", exclude_none=True)
            for kind in ("crawl", "scrape"):
                key = {"domain": definition.domain, "kind": kind, "profile": definition.profile}
                record = {
                    **key,
                    "site_id": definition.site_id,
                    "schema_version": definition.schema_version,
                    "version": definition.version,
                    "definition_hash": definition.definition_hash(),
                    "source_file": entry["source_file"],
                    "registered_at": registered_at,
                    "config": data[kind],
                }
                operations.append(ReplaceOne(key, record, upsert=True))
        if operations:
            # 複数ドキュメントの原子性はない。通信失敗は呼出元へ伝播し、再登録で復旧する。
            self.mongo.mongo_db[self.COLLECTION_NAME].bulk_write(operations, ordered=True)
        return len(operations)
