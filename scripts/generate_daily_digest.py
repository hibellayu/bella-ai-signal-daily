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
APPLICATION_TITLES = {"品牌策略", "數位行銷", "內容行銷", "社群應用", "媒體廣告", "團隊流程"}
SOURCE_EXCERPT_LIMIT = 220
MAX_GENERATION_ATTEMPTS = 2
OPENAI_TIMEOUT_SECONDS = 240


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

    digest: dict[str, Any] | None = None
    quality_feedback = ""
    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
        digest = generate_digest_with_openai(
            api_key=api_key,
            model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            report_date=report_date.isoformat(),
            coverage_date=coverage_date.isoformat(),
            generated_at=generated_at,
            articles=selected,
            tracked_entities=config["trackedEntities"],
            quality_feedback=quality_feedback,
        )
        try:
            validate_digest(digest)
            break
        except ValueError as exc:
            if attempt == MAX_GENERATION_ATTEMPTS:
                raise RuntimeError(f"Digest failed strategy quality checks after {attempt} attempts: {exc}") from exc
            quality_feedback = str(exc)
            print(f"Attempt {attempt} failed strategy quality checks; requesting one rewrite: {quality_feedback}")

    if digest is None:
        raise RuntimeError("Digest generation returned no result.")

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
    quality_feedback: str = "",
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
                "content": build_generation_prompt(
                    report_date,
                    coverage_date,
                    generated_at,
                    articles,
                    tracked_entities,
                    quality_feedback,
                ),
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
        with urllib.request.urlopen(request, timeout=OPENAI_TIMEOUT_SECONDS) as response:
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
    quality_feedback: str = "",
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
    rewrite_instruction = ""
    if quality_feedback:
        rewrite_instruction = textwrap.dedent(
            f"""

            上一版未通過品質檢查，必須完整重寫後再輸出，不可只補字：
            {quality_feedback}
            """
        ).rstrip()

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
        - 內容要以行銷主管與策略者的視角解釋變化，不只複述新聞，也不要用「提升效率、強化信任、帶來機會」等空泛結論收尾。
        - 只使用候選新聞中的事件事實、媒體名稱、發布日期與原文 URL 作為判斷依據。
        - 不得複製來源文章句子，不得翻譯來源段落，不得用接近原文的連續句型改寫。
        - 每則 summary 只提供脈絡，不要取代原文細節；analysis、what、soWhat、nowWhat 必須用新的行銷策略觀點重寫。
        - 如果來源資訊不足以確認事件，請降低收錄優先，不要用推測補成事實。
        - analysis 必須完成兩層推論：第一段指出事件背後的平台、商業模式、使用入口或競爭規則變化；第二段轉譯成品牌、消費者與行銷團隊的決策影響。
        - What「事件本質」不是縮短新聞標題；要說明改變前後的差異，以及這個變化對行銷工作的意義。
        - So What「影響判讀」要說明誰會受影響、行為或競爭規則如何改變、品牌若不調整會失去什麼，不可只寫「影響品牌信任」。
        - Now What 中文標題前台會顯示為「具體行動」。內容使用原子習慣邏輯，必須包含：1 個明確起點、具體數量、實際動作、可看見的產出或完成標準。不要寫「這週」或「本週」，也不要只寫「檢視、評估、探索、嘗試」。
        - 應用切角不是逐則新聞的另一版摘要。必須跨新聞歸納共同變化，從品牌策略、數位行銷、內容行銷、社群應用、媒體廣告、團隊流程中選 4 至 6 個不重複面向。
        - 每個應用切角 title 只能使用上述六個面向名稱；summary 必須包含「趨勢造成什麼變化、策略上應如何重新判斷、可從哪個具體應用開始」。
        - 同一篇來源文章只能出現在一個非 applications 區塊，不可為了湊數重複收錄。
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
        - what: 55-140 字
        - soWhat: 75-180 字
        - nowWhat: 80-180 字，需包含明確數量與可見產出

        applications item 欄位：
        - title: 只能是品牌策略、數位行銷、內容行銷、社群應用、媒體廣告、團隊流程之一
        - summary: 80-180 字，跨新聞統整變化、策略判斷與具體應用

        候選新聞 JSON：
        {json.dumps(article_payload, ensure_ascii=False, indent=2)}
        {rewrite_instruction}
        """
    ).strip()


def validate_digest(digest: dict[str, Any]) -> None:
    issues: list[str] = []
    for key in ["reportDate", "coverageDate", "generatedAt", "headline", "summary", "sections"]:
        if key not in digest:
            issues.append(f"缺少必要欄位 {key}")
    sections = digest.get("sections", [])
    section_ids = [section.get("id") for section in sections]
    if section_ids != SECTION_IDS:
        issues.append(f"區塊順序錯誤：{section_ids}")

    non_app_items = 0
    app_items = 0
    used_source_urls: set[str] = set()
    generic_action_starts = ("檢視", "評估", "探索", "嘗試", "關注", "持續關注")
    for section in sections:
        items = section.get("items", [])
        if section["id"] == "applications":
            app_items = len(items)
            app_titles = [item.get("title", "") for item in items]
            if len(set(app_titles)) != len(app_titles):
                issues.append("應用切角標題不可重複")
            for item in items:
                title = item.get("title", "")
                summary = item.get("summary", "")
                if title not in APPLICATION_TITLES:
                    issues.append(f"應用切角「{title}」未使用固定行銷面向")
                if len(summary) < 65:
                    issues.append(f"應用切角「{title}」不足 65 字，缺少跨新聞策略統整")
            continue
        non_app_items += len(items)
        for item in items:
            title = item.get("title", "未命名")
            analysis = item.get("analysis", [])
            what = item.get("what", "")
            so_what = item.get("soWhat", "")
            now_what = item.get("nowWhat", "")
            if len(analysis) != 2 or any(len(paragraph) < 70 for paragraph in analysis):
                issues.append(f"「{title}」analysis 必須有 2 段且每段至少 70 字")
            if len(what) < 45:
                issues.append(f"「{title}」What 過短，仍像新聞標題摘要")
            if len(so_what) < 65:
                issues.append(f"「{title}」So What 過短，缺少角色與連鎖影響")
            if len(now_what) < 75:
                issues.append(f"「{title}」Now What 過短，缺少原子行動設計")
            if any(term in now_what for term in ["這週", "本週"]):
                issues.append(f"「{title}」Now What 不可限定本週")
            if now_what.startswith(generic_action_starts) and not re.search(r"\d", now_what):
                issues.append(f"「{title}」Now What 只有泛泛動詞，缺少數量與完成標準")
            if not re.search(r"\d", now_what):
                issues.append(f"「{title}」Now What 必須包含具體數量")
            sources = item.get("sources", [])
            if not sources:
                issues.append(f"「{title}」缺少來源")
            for source in sources:
                url = source.get("url", "")
                if url and url in used_source_urls:
                    issues.append(f"來源文章重複收錄：{url}")
                if url:
                    used_source_urls.add(url)
    if non_app_items < 5 or app_items < 4:
        issues.append(f"內容數量不足：新聞 {non_app_items} 則、應用切角 {app_items} 則")
    if issues:
        raise ValueError("；".join(issues))


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
