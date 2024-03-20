import glob
import os
from typing import Any, Final, Generator, Tuple

from pydantic import BaseModel, Field, validator


class ScraperInfoByDomainConst:
    """ScraperInfoByDomainの定数用クラス"""

    DOMAIN: Final[str] = "domain"
    SCRAPE_ITEMS: Final[str] = "scrape_items"
    SCRAPE_ITEMS__TITLE_SCRAPER: Final[str] = "scrape_items__title_scraper"
    SCRAPE_ITEMS__ARTICLE_SCRAPER: Final[str] = "scrape_items__article_scraper"
    SCRAPE_ITEMS__PUBLISH_DATE_SCRAPER: Final[
        str
    ] = "scrape_items__publish_date_scraper"
    ITEM__PATTERN: Final[str] = "pattern"
    ITEM__CSS_SELECTER: Final[str] = "css_selecter"
    ITEM__PRIORITY: Final[str] = "priority"
    ITEM__REGISTER_DATE: Final[str] = "register_date"


class ScraperInfoByDomainData(BaseModel):
    """
    ドメイン別スクレイパー情報用のデータクラス
    """

    scraper: dict = Field(..., title="スクレイパー情報")

    def __init__(self, **data: dict):
        super().__init__(**data)

    """
    定義順にチェックされる。
    valuesにはチェック済みの値のみが入るため順序は重要。(単項目チェック、関連項目チェックの順で定義するのが良さそう。)ScraperInfoByDomainConst.
    """
    ##################################
    # 単項目チェック、省略時の値設定
    ##################################

    @validator("scraper")
    def scraper_domain_check(cls, value: dict, values: dict) -> dict:
        # if not 'domain' in value:
        if not ScraperInfoByDomainConst.DOMAIN in value:
            raise ValueError(
                f"不正データ。ドメイン({ScraperInfoByDomainConst.DOMAIN})が定義されていません。{value}"
            )
        elif not type(value[ScraperInfoByDomainConst.DOMAIN]) is str:
            raise ValueError(
                f'不正データ。ドメイン({ScraperInfoByDomainConst.DOMAIN})の値が文字列型以外はエラー({type(value["domain"])})'
            )
        return value

    @validator("scraper")
    def scraper_items_check(cls, value: dict, values: dict) -> dict:
        # if not 'scrape_items' in value:
        if not ScraperInfoByDomainConst.SCRAPE_ITEMS in value:
            raise ValueError(
                f"不正データ。スクレイプアイテム({ScraperInfoByDomainConst.SCRAPE_ITEMS})が定義されていません。({value})"
            )
        elif not type(value[ScraperInfoByDomainConst.SCRAPE_ITEMS]) is dict:
            raise ValueError(
                f"不正データ。スクレイプアイテム({ScraperInfoByDomainConst.SCRAPE_ITEMS})の値が辞書型以外はエラー。{type(value[ScraperInfoByDomainConst.SCRAPE_ITEMS])}"
            )
        elif len(value[ScraperInfoByDomainConst.SCRAPE_ITEMS]) == 0:
            raise ValueError(
                f"不正データ。スクレイプアイテム({ScraperInfoByDomainConst.SCRAPE_ITEMS})内のスクレイパーが定義されていません。{len(value[ScraperInfoByDomainConst.SCRAPE_ITEMS])}"
            )
        else:
            items: list = [
                ScraperInfoByDomainConst.ITEM__PATTERN,
                ScraperInfoByDomainConst.ITEM__CSS_SELECTER,
                ScraperInfoByDomainConst.ITEM__PRIORITY,
                ScraperInfoByDomainConst.ITEM__REGISTER_DATE,
            ]
            for scrape_item_key, scrape_item_value in value[
                ScraperInfoByDomainConst.SCRAPE_ITEMS
            ].items():
                path = os.path.join("prefect_lib", "scraper", f"{scrape_item_key}.py")
                if len(glob.glob(path)) == 0:
                    raise ValueError(
                        f"不正データ。スクレイプアイテム({ScraperInfoByDomainConst.SCRAPE_ITEMS})で指定されたスクレイパーは登録されていないため使用できません。({scrape_item_key})"
                    )
                elif not type(scrape_item_value) is list:
                    raise ValueError(f"不正データ。スクレイパーの値がリスト型以外はエラー。({scrape_item_value})")
                elif len(scrape_item_value) == 0:
                    raise ValueError(
                        f"不正データ。スクレイパー内のパターンが定義されていません。({scrape_item_value})"
                    )

                for pattern_info in scrape_item_value:
                    if not type(pattern_info) is dict:
                        raise ValueError(
                            f"不正データ。パターン情報の値が辞書型以外はエラー。({scrape_item_value})"
                        )
                    elif not all((s in pattern_info.keys()) for s in items):
                        # 'pattern', 'css_selecter', 'priority', 'register_date']):
                        raise ValueError(
                            f"不正データ。パターン情報内に{str(items)}が揃って定義されていません。({pattern_info})"
                        )
        return value

    ###################################
    # 関連項目チェック
    ###################################

    #####################################
    # カスタマイズデータ
    #####################################
    def domain_get(self) -> str:
        return self.scraper[ScraperInfoByDomainConst.DOMAIN]

    def making_into_a_table_format(self) -> list[dict[str, Any]]:
        """ドメイン別スクレイパー情報を表形式へ加工"""
        result: list = []
        scrape_items: dict = self.scraper[ScraperInfoByDomainConst.SCRAPE_ITEMS]
        for scraper_item_key, scraper_item_value in scrape_items.items():
            for pattern_info in scraper_item_value:
                result.append(
                    {
                        ScraperInfoByDomainConst.DOMAIN: self.scraper[
                            ScraperInfoByDomainConst.DOMAIN
                        ],
                        ScraperInfoByDomainConst.SCRAPE_ITEMS: scraper_item_key,
                        ScraperInfoByDomainConst.ITEM__PATTERN: pattern_info[
                            ScraperInfoByDomainConst.ITEM__PATTERN
                        ],
                        ScraperInfoByDomainConst.ITEM__PRIORITY: pattern_info[
                            ScraperInfoByDomainConst.ITEM__PRIORITY
                        ],
                        # 'count_of_use': 0,
                    }
                )
        return result

    def scrape_item_get(
        self,
    ) -> Generator[Tuple[str, list[dict[str, str]]], None, None]:
        """
        scrape_itemsを返すジェネレーター
        """
        scrape_items: dict[str, list[dict[str, str]]] = self.scraper[
            ScraperInfoByDomainConst.SCRAPE_ITEMS
        ]
        for scraper, pattern_list in scrape_items.items():
            # patternリストは、patternで降順にソート
            pattern_list = sorted(
                pattern_list,
                key=lambda d: d[ScraperInfoByDomainConst.ITEM__PATTERN],
                reverse=True,
            )
            yield scraper, pattern_list

    # コレクション側から移植予定,,,既にあったｗ
    # def domain_get(self) -> str:
    #     '''ドメインを返す'''
    #     return self.scraper_by_domain_record['domain']


"""MongoDB内でのデータイメージ
{
    "_id": ObjectID("62542b32efbb8d4ef6de0356"),
    "domain": "yomiuri.co.jp",
    "scrape_items": {
        "title_scraper": [
            {
                "pattern": 2,
                "css_selecter": "head > title",
                "priority": 2,
                "register_date": "2022-04-16T14:00:00+09:00"
            },
            {
                "pattern": 1,
                "css_selecter": "title",
                "priority": 1,
                "register_date": "2022-04-16T14:00:00+09:00"
            }
        ],
        "article_scraper": [
            {
                "pattern": 4,
                "css_selecter": "div.p-main-contents > p",
                "priority": 4,
                "register_date": "2022-04-16T14:00:00+09:00"
            },
            {
                "pattern": 3,
                "css_selecter": "div.p-main-contents > p[class^=par]",
                "priority": 3,
                "register_date": "2022-04-16T14:00:00+09:00"
            },
            {
                "pattern": 2,
                "css_selecter": "div.p-main-contents > p[iarticle_selecterrop=articleBody]",
                "priority": 2,
                "register_date": "2022-04-16T14:00:00+09:00"
            },
            {
                "pattern": 1,
                "css_selecter": "div.main-contents > p[iarticle_selecterrop=articleBody]",
                "priority": 1,
                "register_date": "2022-04-16T14:00:00+09:00"
            }
        ],
        "publish_date_scraper": [
            {
                "pattern": 2,
                "css_selecter": "head > meta[property=\"article:modified_time\"]",
                "priority": 2,
                "register_date": "2022-04-16T14:00:00+09:00"
            },
            {
                "pattern": 1,
                "css_selecter": "head > meta[property=\"article:published_time\"]",
                "priority": 1,
                "register_date": "2022-04-16T14:00:00+09:00"
            }
        ]
    }
}

"""
