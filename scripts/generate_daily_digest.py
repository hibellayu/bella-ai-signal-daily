#!/usr/bin/env python3
"""Generate Bella's AI Signal Daily from source feeds and OpenAI."""

from __future__ import annotations

import argparse
import email.utils
import html
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from static_site import build_static_site


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "sources.json"
DIGEST_DIR = ROOT / "data" / "digests"
MANIFEST_PATH = DIGEST_DIR / "manifest.json"
TAIPEI = timezone(timedelta(hours=8))

SOURCE_POLICY = "台灣媒體依台北時間前一日收集；國際媒體依來源網站發布日期，不做時區換算。"
PRIORITY = ["產業重大性", "數位行銷影響", "內容 / 搜尋 / 社群 / 媒體廣告影響", "工具可用性"]
SECTION_IDS = ["major-events", "tool-updates", "trends", "applications"]
SOURCE_EXCERPT_LIMIT = 220


@dataclass
class Article:
    title: str
    url: str
    source: str
    region: str
    published_date: str
    summary: str
    score: int
    matched_terms: list[str]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Bella's AI Signal Daily.")
    parser.add_argument("--report-date", help="Report date in YYYY-MM-DD. Defaults to today's Taipei date.")
    parser.add_argument("--dry-run", action="store_true", help="Collect and score sources without writing files.")
    args = parser.parse_args()

    now = datetime.now(TAIPEI)
    report_date = datetime.strptime(args.report_date, "%Y-%m-%d").date() if args.report_date else now.date()
    coverage_date = report_date - timedelta(days=1)
    generated_at = datetime.combine(report_date, datetime.min.time(), TAIPEI).replace(hour=7).isoformat(timespec="seconds")
    if report_date == now.date():
        generated_at = now.isoformat(timespec="seconds")

    config = load_json(CONFIG_PATH)
    candidates = collect_articles(config, coverage_date)
    selected = candidates[:18]
    print(f"Collected {len(candidates)} AI-related candidates; using {len(selected)} for generation.")

    if args.dry_run:
        for article in selected[:12]:
            print(f"- {article.published_date} {article.source} {article.score}: {article.title}")
        return

    if len(selected) < 5:
        raise RuntimeError(f"Only {len(selected)} candidates found; digest was not published to avoid thin content.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set; digest cannot be generated.")

    digest = generate_digest_with_openai(
        api_key=api_key,
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        report_date=report_date.isoformat(),
        coverage_date=coverage_date.isoformat(),
        generated_at=generated_at,
        articles=selected,
        tracked_entities=config["trackedEntities"],
    )
    validate_digest(digest)

    if not has_digest_content(digest):
        raise RuntimeError(f"No digest items generated for {report_date.isoformat()}; empty digest was not published.")

    digest_path = DIGEST_DIR / f"{report_date.isoformat()}.json"
    write_json(digest_path, digest)
    update_manifest(report_date.isoformat(), coverage_date.isoformat(), digest)
    build_static_site(ROOT)
    print(f"Published digest: {digest_path.relative_to(ROOT)}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_articles(config: dict[str, Any], coverage_date: date) -> list[Article]:
    keywords = [term.lower() for term in config["aiKeywords"]]
    tracked = [term.lower() for term in config["trackedEntities"]]
    articles: list[Article] = []
    seen_urls: set[str] = set()

    for source in config["sources"]:
        if not source.get("enabled", True):
            continue
        try:
            feed = fetch_text(source["url"])
            entries = parse_feed(feed, source)
        except Exception as exc:  # noqa: BLE001
            print(f"Source failed: {source['name']} - {exc}")
            continue

        for entry in entries:
            if entry["url"] in seen_urls:
                continue
            if entry["published_date"] != coverage_date.isoformat():
                continue
            score, matched_terms = score_article(entry, keywords, tracked)
            if score < 4:
                continue
            seen_urls.add(entry["url"])
            articles.append(
                Article(
                    title=entry["title"],
                    url=entry["url"],
                    source=source["name"],
                    region=source["region"],
                    published_date=entry["published_date"],
                    summary=entry["summary"],
                    score=score,
                    matched_terms=matched_terms,
                )
            )

    articles.sort(key=lambda item: item.score, reverse=True)
    return articles


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "BellaAISignalDaily/0.3.0 (+https://hibellayu.github.io/bella-ai-signal-daily/)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_feed(feed: str, source: dict[str, Any]) -> list[dict[str, str]]:
    root = ET.fromstring(feed)
    entries: list[dict[str, str]] = []

    if root.tag.lower().endswith("rss"):
        nodes = root.findall(".//item")
        for node in nodes:
            entries.append(parse_rss_item(node, source))
    else:
        nodes = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for node in nodes:
            entries.append(parse_atom_entry(node, source))

    return [entry for entry in entries if entry["title"] and entry["url"] and entry["published_date"]]


def parse_rss_item(node: ET.Element, source: dict[str, Any]) -> dict[str, str]:
    title = clean_text(find_text(node, "title"))
    url = clean_text(find_text(node, "link") or find_text(node, "guid"))
    summary = clean_text(find_text(node, "description") or find_text(node, "{http://purl.org/rss/1.0/modules/content/}encoded"))
    published_raw = find_text(node, "pubDate") or find_text(node, "{http://purl.org/dc/elements/1.1/}date")
    return {
        "title": title,
        "url": url,
        "summary": truncate_source_summary(summary),
        "published_date": parse_source_date(published_raw, source["region"]),
    }


def parse_atom_entry(node: ET.Element, source: dict[str, Any]) -> dict[str, str]:
    ns = "{http://www.w3.org/2005/Atom}"
    title = clean_text(find_text(node, f"{ns}title"))
    url = ""
    for link in node.findall(f"{ns}link"):
        if link.attrib.get("rel", "alternate") == "alternate":
            url = link.attrib.get("href", "")
            break
    summary = clean_text(find_text(node, f"{ns}summary") or find_text(node, f"{ns}content"))
    published_raw = find_text(node, f"{ns}published") or find_text(node, f"{ns}updated")
    return {
        "title": title,
        "url": clean_text(url),
        "summary": truncate_source_summary(summary),
        "published_date": parse_source_date(published_raw, source["region"]),
    }


def find_text(node: ET.Element, tag: str) -> str:
    found = node.find(tag)
    return found.text if found is not None and found.text else ""


def parse_source_date(value: str, region: str) -> str:
    if not value:
        return ""
    value = value.strip()
    try:
        parsed = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        parsed = None

    if parsed is None:
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(value.replace("Z", "+0000"), fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        return ""
    if region == "taiwan" and parsed.tzinfo is not None:
        parsed = parsed.astimezone(TAIPEI)
    return parsed.date().isoformat()


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def truncate_source_summary(value: str) -> str:
    return clean_text(value)[:SOURCE_EXCERPT_LIMIT]


def score_article(entry: dict[str, str], keywords: list[str], tracked: list[str]) -> tuple[int, list[str]]:
    haystack = f"{entry['title']} {entry['summary']}".lower()
    matched = sorted({term for term in keywords + tracked if term and term in haystack})
    score = 0
    score += min(8, len([term for term in keywords if term in haystack]) * 2)
    score += min(6, len([term for term in tracked if term in haystack]) * 3)
    if any(term in haystack for term in ["marketing", "行銷", "advertising", "廣告", "seo", "search", "搜尋", "social", "社群", "content", "內容"]):
        score += 5
    if any(term in haystack for term in ["openai", "google", "meta", "anthropic", "perplexity", "adobe", "canva", "midjourney", "suno"]):
        score += 4
    return score, matched


def generate_digest_with_openai(
    *,
    api_key: str,
    model: str,
    report_date: str,
    coverage_date: str,
    generated_at: str,
    articles: list[Article],
    tracked_entities: list[str],
) -> dict[str, Any]:
    payload = {
        "model": model,
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "你是資深 AI 趨勢編輯與行銷策略顧問，只輸出合法 JSON，不輸出 Markdown。",
            },
            {
                "role": "user",
                "content": build_generation_prompt(report_date, coverage_date, generated_at, articles, tracked_entities),
            },
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI request failed: {exc.code} {detail}") from exc

    content = result["choices"][0]["message"]["content"]
    return json.loads(content)


def build_generation_prompt(
    report_date: str,
    coverage_date: str,
    generated_at: str,
    articles: list[Article],
    tracked_entities: list[str],
) -> str:
    article_payload = [
        {
            "title": item.title,
            "source": item.source,
            "publishedDate": item.published_date,
            "url": item.url,
            "summary": item.summary,
            "score": item.score,
            "matchedTerms": item.matched_terms,
        }
        for item in articles
    ]
    return textwrap.dedent(
        f"""
        請根據候選新聞，產生 Bella's AI Signal Daily 的 JSON。

        固定中繼資料：
        - reportDate: {report_date}
        - coverageDate: {coverage_date}
        - generatedAt: {generated_at}
        - sourcePolicy: {SOURCE_POLICY}
        - trackedEntities: {", ".join(tracked_entities)}

        內容目標：
        - 讀者是行銷人、品牌決策者、數位行銷、內容行銷、社群與媒體廣告工作者。
        - 不要寫給 Bella 個人，不要使用「Bella 的工作視角」。
        - 內容要有觀點，不只複述新聞。
        - 只使用候選新聞中的事件事實、媒體名稱、發布日期與原文 URL 作為判斷依據。
        - 不得複製來源文章句子，不得翻譯來源段落，不得用接近原文的連續句型改寫。
        - 每則 summary 只提供脈絡，不要取代原文細節；analysis、what、soWhat、nowWhat 必須用新的行銷策略觀點重寫。
        - 如果來源資訊不足以確認事件，請降低收錄優先，不要用推測補成事實。
        - Now What 中文標題前台會顯示為「具體行動」，內容請用原子習慣邏輯：小、具體、低負擔、可開始，不要寫「這週」或「本週」。
        - 每則 item 的 sources 必須使用候選新聞中的原文 URL，不可改成媒體首頁。
        - 優先順序：產業重大性 > 數位行銷影響 > 內容 / 搜尋 / 社群 / 媒體廣告影響 > 工具可用性。

        JSON schema 形狀：
        {{
          "reportDate": "{report_date}",
          "coverageDate": "{coverage_date}",
          "generatedAt": "{generated_at}",
          "headline": "string",
          "summary": "string",
          "sourcePolicy": "{SOURCE_POLICY}",
          "trackedEntities": [...],
          "scoringPolicy": {{
            "priority": ["產業重大性", "數位行銷影響", "內容 / 搜尋 / 社群 / 媒體廣告影響", "工具可用性"],
            "thresholds": {{"mustInclude": 13, "candidate": "9-12", "skip": "8 以下"}}
          }},
          "sections": [
            {{"id": "major-events", "title": "大事件", "description": "...", "items": [3 至 4 則]}},
            {{"id": "tool-updates", "title": "工具更新", "description": "...", "items": [2 至 4 則]}},
            {{"id": "trends", "title": "值得追蹤的趨勢", "description": "...", "items": [1 至 3 則]}},
            {{"id": "applications", "title": "應用切角彙整", "description": "...", "items": [4 至 6 則]}}
          ]
        }}

        非 applications item 欄位：
        - title
        - summary
        - analysis: 2 段陣列，每段 70-140 字
        - sources: [{{"name","publishedDate","url"}}]
        - score: industryImpact, digitalMarketingImpact, contentSearchSocialAdsImpact, toolUsability, trackedEntityRelevance, total
        - tags: 3-5 個
        - what
        - soWhat
        - nowWhat

        applications item 欄位：
        - title
        - summary

        候選新聞 JSON：
        {json.dumps(article_payload, ensure_ascii=False, indent=2)}
        """
    ).strip()


def validate_digest(digest: dict[str, Any]) -> None:
    for key in ["reportDate", "coverageDate", "generatedAt", "headline", "summary", "sections"]:
        if key not in digest:
            raise ValueError(f"Digest missing key: {key}")
    sections = digest.get("sections", [])
    section_ids = [section.get("id") for section in sections]
    if section_ids != SECTION_IDS:
        raise ValueError(f"Unexpected section order: {section_ids}")

    non_app_items = 0
    app_items = 0
    for section in sections:
        items = section.get("items", [])
        if section["id"] == "applications":
            app_items = len(items)
            continue
        non_app_items += len(items)
        for item in items:
            if any(term in item.get("nowWhat", "") for term in ["這週", "本週"]):
                raise ValueError("Now What contains week-based wording.")
            if not item.get("sources"):
                raise ValueError(f"Item missing sources: {item.get('title')}")
    if non_app_items < 5 or app_items < 4:
        raise ValueError(f"Digest too thin: {non_app_items} news items, {app_items} application items.")


def update_manifest(report_date: str, coverage_date: str, digest: dict[str, Any]) -> None:
    manifest = {"latest": report_date, "digests": []}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    entry = {
        "reportDate": report_date,
        "coverageDate": coverage_date,
        "title": f"Bella's AI 趨勢日報｜{report_date.replace('-', '/')}",
        "summary": digest["summary"],
        "path": f"data/digests/{report_date}.json",
    }

    existing = [item for item in manifest.get("digests", []) if item.get("reportDate") != report_date]
    existing.append(entry)
    existing.sort(key=lambda item: item["reportDate"], reverse=True)
    manifest["latest"] = existing[0]["reportDate"]
    manifest["digests"] = existing
    write_json(MANIFEST_PATH, manifest)


def has_digest_content(digest: dict[str, Any]) -> bool:
    return any(section.get("items") for section in digest.get("sections", []))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"Digest generation failed: {error}", file=sys.stderr)
        sys.exit(1)
