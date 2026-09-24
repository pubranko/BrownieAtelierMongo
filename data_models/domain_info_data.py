"""ドメイン別YAMLの登録仕様。操作定義の実行は汎用スパイダー側で実装する。"""

import hashlib
import json
import re
from datetime import datetime
from string import Formatter
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


class DefinitionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def validate_text(value: str) -> str:
    if not value.strip():
        raise ValueError("空白だけの文字列は指定できません")
    return value


Text = Annotated[str, Field(min_length=1), AfterValidator(validate_text)]


def validate_domain(value: str) -> str:
    """クロール対象のホスト名を検証し、比較・保存用に小文字へ統一する。"""
    if not value:
        raise ValueError("domainにはホスト名を指定してください（空文字は不可）")
    if any(char.isspace() for char in value):
        raise ValueError("domainに空白は使用できません")
    if any(char in value for char in "/:@?#\\"):
        raise ValueError("domainにはホスト名だけを指定してください（URL・パス・ポート・認証情報は不可）")
    if "_" in value:
        raise ValueError("domainのホスト名にアンダースコア（_）は使用できません（例: jp.reuters.com）")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", value):
        raise ValueError(
            "domainには半角英数字・ハイフン（-）・ドット（.）のみ使用できます（国際化ドメインはPunycodeで指定）"
        )
    if len(value) > 253:
        raise ValueError("domainは全体で253文字以内にしてください")
    labels = value.split(".")
    if len(labels) < 2 or any(not label for label in labels):
        raise ValueError("domainは空でないラベルをドット（.）で区切って指定してください（例: example.com）")
    if any(len(label) > 63 for label in labels):
        raise ValueError("domainの各ラベル（ドットで区切った部分）は63文字以内にしてください")
    if any(label.startswith("-") or label.endswith("-") for label in labels):
        raise ValueError("domainの各ラベルの先頭・末尾にハイフン（-）は使用できません")
    return value.lower()


def validate_url(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("http/httpsの絶対URLを指定してください（認証情報は不可）")
    if any(char.isspace() for char in value) or parts.port == 0:
        raise ValueError("URLの空白またはポート番号が不正です")
    return value


Domain = Annotated[str, AfterValidator(validate_domain)]
HttpUrlText = Annotated[str, AfterValidator(validate_url)]
PositiveInt = Annotated[int, Field(gt=0)]
Timeout = Annotated[int, Field(gt=0, le=300_000)]


class Target(DefinitionModel):
    """CSSまたはXPathで対象を指定。indexは0始まり、省略時は一意な要素を要求する。"""

    css: Text | None = None
    xpath: Text | None = None
    index: Annotated[int, Field(ge=0)] | None = None

    @model_validator(mode="after")
    def one_selector(self) -> Self:
        if (self.css is None) == (self.xpath is None):
            raise ValueError("targetにはcssかxpathのどちらか一方が必要です")
        return self


class WaitFor(DefinitionModel):
    action: Literal["wait_for"]
    target: Target
    state: Literal["attached", "detached", "visible", "hidden"] = "visible"
    timeout_ms: Timeout = 60_000


class CountIncreased(DefinitionModel):
    type: Literal["count_increased"]
    target: Target
    timeout_ms: Timeout = 60_000


class Click(DefinitionModel):
    action: Literal["click"]
    target: Target
    timeout_ms: Timeout = 60_000
    wait_after: CountIncreased | None = None


class Scroll(DefinitionModel):
    """対象要素が見える位置までスクロールする。"""

    action: Literal["scroll_into_view"]
    target: Target
    timeout_ms: Timeout = 60_000


class SetSlider(DefinitionModel):
    """HTML input[type=range]用。独自UIのドラッグ操作とは別の操作。"""

    action: Literal["set_slider"]
    target: Target
    value: float


class Repeat(DefinitionModel):
    action: Literal["repeat"]
    max_iterations: Annotated[int, Field(gt=0, le=1000)]
    while_visible: Target
    steps: Annotated[list[Action], Field(min_length=1)]


Action = Annotated[WaitFor | Click | Scroll | SetSlider | Repeat, Field(discriminator="action")]
Repeat.model_rebuild()


class FetchSettings(DefinitionModel):
    playwright: bool
    actions: list[Action] = Field(default_factory=list)

    @model_validator(mode="after")
    def browser_actions(self) -> Self:
        if self.actions and not self.playwright:
            raise ValueError("actionsを指定する場合はplaywright: trueが必要です")
        return self


class ArticleSettings(FetchSettings):
    pagination_css_selectors: list[Text] = Field(default_factory=list)


class NumberedPagination(DefinitionModel):
    mode: Literal["numbered"]
    url_template: Text
    start: Annotated[int, Field(ge=0)] = 1
    stop: Annotated[int, Field(ge=0)] = 3
    step: PositiveInt = 1

    @model_validator(mode="after")
    def valid_range(self) -> Self:
        fields = [field for _, field, _, _ in Formatter().parse(self.url_template) if field is not None]
        if fields != ["page"]:
            raise ValueError("url_templateには{page}を1個だけ指定してください")
        if self.stop < self.start:
            raise ValueError("stopはstart以上である必要があります")
        validate_url(self.url_template.format(page=self.start))
        return self


class ActionPagination(DefinitionModel):
    """各ページのリンク収集後にstepsを実行。最終ページでは実行しない。"""

    mode: Literal["actions"]
    max_pages: Annotated[int, Field(gt=0, le=1000)] = 3
    next_page_target: Target
    steps: Annotated[list[Action], Field(min_length=1)]


Pagination = Annotated[NumberedPagination | ActionPagination, Field(discriminator="mode")]


class LinkExtraction(DefinitionModel):
    """item_cssを基準にURL・日時を同じ記事から抽出する。"""

    item_css: Text
    link_css: Text
    link_attribute: Text = "href"
    lastmod_css: Text | None = None
    expected_items_per_page: PositiveInt | None = None


class ListingSettings(FetchSettings):
    start_urls: Annotated[list[HttpUrlText], Field(min_length=1)]
    extract: LinkExtraction
    pagination: Pagination | None = None
    continued_max_pages: PositiveInt = 100

    @model_validator(mode="after")
    def pagination_browser(self) -> Self:
        if isinstance(self.pagination, ActionPagination) and not self.playwright:
            raise ValueError("操作によるページ送りにはplaywright: trueが必要です")
        return self


class SitemapSettings(FetchSettings):
    urls: Annotated[list[HttpUrlText], Field(min_length=1)]
    format: Literal["standard", "google_news_sitemap"] = "standard"
    follow: list[Text] = Field(default_factory=list)
    pagination: NumberedPagination | None = None

    @model_validator(mode="after")
    def valid_patterns(self) -> Self:
        for pattern in self.follow:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ValueError(f"followの正規表現が不正です: {pattern}") from exc
        return self


class FilteringSettings(DefinitionModel):
    """サイトが対応する絞り込み方式。実行時の範囲指定とは分離する。"""

    supported_modes: Annotated[list[Literal["page", "time"]], Field(min_length=1)]
    default_mode: Literal["page", "time"]

    @model_validator(mode="after")
    def valid_modes(self) -> Self:
        if len(set(self.supported_modes)) != len(self.supported_modes):
            raise ValueError("supported_modesが重複しています")
        if self.default_mode not in self.supported_modes:
            raise ValueError("default_modeはsupported_modesに含めてください")
        return self


class SitemapCrawl(DefinitionModel):
    strategy: Literal["sitemap"]
    filtering: FilteringSettings | None = None
    allowed_domains: Annotated[list[Domain], Field(min_length=1)]
    sitemap: SitemapSettings
    article: ArticleSettings


class ListingCrawl(DefinitionModel):
    strategy: Literal["crawl"]
    filtering: FilteringSettings | None = None
    allowed_domains: Annotated[list[Domain], Field(min_length=1)]
    listing: ListingSettings
    article: ArticleSettings


CrawlSettings = Annotated[SitemapCrawl | ListingCrawl, Field(discriminator="strategy")]


class ScrapePattern(DefinitionModel):
    pattern: PositiveInt
    # 既存スクレイパーとの互換性のため、既存の綴りを維持する。
    css_selecter: Text
    priority: PositiveInt
    register_date: Text

    @model_validator(mode="after")
    def valid_date(self) -> Self:
        if datetime.fromisoformat(self.register_date).tzinfo is None:
            raise ValueError("register_dateにはタイムゾーン付きISO日時を指定してください")
        return self


class ScrapeSettings(DefinitionModel):
    scrape_items: dict[
        Literal["title_scraper", "article_scraper", "publish_date_scraper"],
        Annotated[list[ScrapePattern], Field(min_length=1)],
    ] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_patterns(self) -> Self:
        for name, patterns in self.scrape_items.items():
            if len({item.pattern for item in patterns}) != len(patterns):
                raise ValueError(f"{name}のpatternが重複しています")
        return self


class DomainInfoData(DefinitionModel):
    schema_version: Literal[1]
    site_id: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    domain: Domain
    profile: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")] = "main"
    version: PositiveInt
    crawl: CrawlSettings
    scrape: ScrapeSettings

    def definition_hash(self) -> str:
        """コメントやキー順序によらず、検証・既定値補完後の定義を識別する。"""
        payload = json.dumps(
            self.model_dump(mode="json", exclude_none=True),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @model_validator(mode="after")
    def allowed_host(self) -> Self:
        if not any(self.domain == host or self.domain.endswith("." + host) for host in self.crawl.allowed_domains):
            raise ValueError("domainがallowed_domainsの範囲外です")
        return self
