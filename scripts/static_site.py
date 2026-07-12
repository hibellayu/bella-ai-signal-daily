#!/usr/bin/env python3
"""Build static daily pages and sitemap for Bella's AI 趨勢日報."""

from __future__ import annotations

import html
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DIGEST_DIR = ROOT / "data" / "digests"
MANIFEST_PATH = DIGEST_DIR / "manifest.json"
DAILY_DIR = ROOT / "daily"
SITEMAP_PATH = ROOT / "sitemap.xml"
SITE_URL = "https://hibellayu.github.io/bella-ai-signal-daily/"
SITE_NAME = "Bella's AI 趨勢日報"
SITE_SUBTITLE = "Daily brief for marketing decisions"
VERSION = "v0.9.1"
VERSION_DATE = "2026/07/12"
ASSET_VERSION = "20260710g"
CONTENT_NOTICE = "本站內容為 AI 趨勢整理、評論與行銷應用解讀；新聞來源與原文著作權屬各原媒體與作者所有。若需完整內容，請閱讀原文。"


def main() -> None:
    build_static_site(ROOT)


def build_static_site(root: Path = ROOT) -> None:
    digests = load_publishable_digests(root)
    daily_dir = root / "daily"
    if daily_dir.exists():
        shutil.rmtree(daily_dir)
    daily_dir.mkdir(parents=True, exist_ok=True)

    for digest in digests:
        write_daily_page(root, digest)

    write_daily_index(root, digests)
    write_sitemap(root, digests)
    print(f"Built {len(digests)} static daily pages.")


def load_publishable_digests(root: Path) -> list[dict[str, Any]]:
    manifest_path = root / "data" / "digests" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digests: list[dict[str, Any]] = []

    for entry in manifest.get("digests", []):
        digest_path = root / entry["path"]
        if not digest_path.exists():
            continue
        digest = json.loads(digest_path.read_text(encoding="utf-8"))
        if is_publishable_digest(digest):
            digests.append(digest)

    digests.sort(key=lambda item: item["reportDate"], reverse=True)
    return digests


def write_daily_page(root: Path, digest: dict[str, Any]) -> None:
    report_date = digest["reportDate"]
    out_dir = root / "daily" / report_date
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(render_daily_page(digest), encoding="utf-8")


def write_daily_index(root: Path, digests: list[dict[str, Any]]) -> None:
    out_dir = root / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(render_daily_index(digests), encoding="utf-8")


def render_daily_index(digests: list[dict[str, Any]]) -> str:
    title = f"{SITE_NAME}｜日報列表"
    description = "依日期整理 Bella's AI 趨勢日報，收錄 AI 產業趨勢、工具更新與行銷應用切角，方便搜尋引擎、AI 搜尋工具與讀者回查每日內容。"
    canonical = f"{SITE_URL}daily/"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": canonical,
        "inLanguage": "zh-Hant-TW",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        "mainEntity": [
            {
                "@type": "Article",
                "headline": digest.get("headline") or SITE_NAME,
                "url": f"{SITE_URL}daily/{digest['reportDate']}/",
                "datePublished": digest.get("generatedAt"),
            }
            for digest in digests
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_TW">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{escape(description)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css?v={ASSET_VERSION}">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-8CQ9L4MXNL"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "G-8CQ9L4MXNL");
  </script>
  <script type="application/ld+json">
{escape_json_ld(json_ld)}
  </script>
</head>
<body>
  {render_header("../", "./")}
  <main id="top" class="archive-shell">
    <section class="archive-hero">
      <p class="eyebrow">Daily Archive</p>
      <h1>AI 趨勢日報列表</h1>
      <p>{escape(description)}</p>
    </section>
    <section class="archive-list" aria-label="日報列表">
{render_archive_cards(digests)}
    </section>
  </main>
  {render_footer()}
</body>
</html>
"""


def render_daily_page(digest: dict[str, Any]) -> str:
    report_date = digest["reportDate"]
    title = f"{escape(digest.get('headline') or SITE_NAME)}｜{format_display_date(report_date)}"
    description = digest.get("summary") or "AI 趨勢、工具更新與行銷應用日報。"
    canonical = f"{SITE_URL}daily/{report_date}/"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": digest.get("headline") or SITE_NAME,
        "description": description,
        "datePublished": digest.get("generatedAt"),
        "dateModified": digest.get("generatedAt"),
        "inLanguage": "zh-Hant-TW",
        "url": canonical,
        "mainEntityOfPage": canonical,
        "author": {"@type": "Person", "name": "Bella Yu"},
        "publisher": {"@type": "Person", "name": "Bella Yu"},
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        "about": digest.get("trackedEntities", []),
    }

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="zh_TW">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{escape(description)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css?v={ASSET_VERSION}">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-8CQ9L4MXNL"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "G-8CQ9L4MXNL");
  </script>
  <script type="application/ld+json">
{escape_json_ld(json_ld)}
  </script>
</head>
<body>
  {render_header("../../", "../")}
  <main id="top" class="shell static-shell">
    {render_meta_panel(digest)}
    <section class="content">
      {render_sections(digest)}
    </section>
  </main>
  {render_footer()}
</body>
</html>
"""


def render_header(home_href: str, archive_href: str) -> str:
    return f"""<header class="topbar">
    <div class="topbar__inner">
      <a class="brand" href="{home_href}" aria-label="{SITE_NAME} 首頁">
        <span class="brand__mark">AI</span>
        <span>
          <strong>{SITE_NAME}</strong>
          <small>{SITE_SUBTITLE}</small>
        </span>
      </a>
      <nav class="static-links" aria-label="靜態頁導覽">
        <a class="static-home-link" href="{archive_href}">日報列表</a>
        <a class="static-home-link" href="{home_href}">互動版日報</a>
      </nav>
    </div>
  </header>"""


def render_meta_panel(digest: dict[str, Any]) -> str:
    priority = digest.get("scoringPolicy", {}).get("priority", [])
    nav = "\n".join(
        f'        <a href="#{escape_attr(section["id"])}">{escape(section.get("title", ""))}</a>'
        for section in digest.get("sections", [])
        if section.get("items")
    )
    return f"""<aside class="panel digest-meta" aria-label="日報資訊">
      <p class="eyebrow">Today's Signal</p>
      <h1>{escape(digest.get("headline", SITE_NAME))}</h1>
      <p class="digest-meta__summary">{escape(digest.get("summary", ""))}</p>

      <dl class="meta-grid">
        <div>
          <dt>日報日期</dt>
          <dd>{format_display_date(digest.get("reportDate"))}</dd>
        </div>
        <div>
          <dt>資料日期</dt>
          <dd>{format_display_date(digest.get("coverageDate"))}</dd>
        </div>
        <div>
          <dt>生成時間</dt>
          <dd>{format_generated_at(digest.get("generatedAt"))}</dd>
        </div>
        <div>
          <dt>收錄上限</dt>
          <dd>10-14 則資訊</dd>
        </div>
      </dl>

      <div class="signal-policy">
        <h2>收錄優先順序</h2>
        <ol>{''.join(f'<li>{escape(item)}</li>' for item in priority)}</ol>
      </div>

      <nav class="section-nav" aria-label="區塊導覽">
{nav}
      </nav>
    </aside>"""


def render_sections(digest: dict[str, Any]) -> str:
    return "\n".join(render_section(section) for section in digest.get("sections", []))


def render_section(section: dict[str, Any]) -> str:
    items = section.get("items", [])
    if not items:
        return ""
    body = render_applications(items) if section.get("id") == "applications" else "\n".join(render_item(item) for item in items)
    return f"""<section id="{escape_attr(section.get("id", ""))}" class="digest-section">
        <div class="section-heading">
          <p class="section-heading__count">{len(items)} 則資訊</p>
          <h2>{escape(section.get("title", ""))}</h2>
          <p>{escape(section.get("description", ""))}</p>
        </div>
        <div class="item-list{' application-list' if section.get('id') == 'applications' else ''}">
{body}
        </div>
      </section>"""


def render_item(item: dict[str, Any]) -> str:
    analysis = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in item.get("analysis", []))
    tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in item.get("tags", []))
    score = item.get("score", {})
    total = score.get("total", "-")
    return f"""          <article class="signal-card">
            <div class="signal-card__head">
              <div>
                <div class="source-line">{render_sources(item)}</div>
                <h3>{escape(item.get("title", ""))}</h3>
              </div>
              <span class="score-badge">{total} 分</span>
            </div>
            <p class="summary">{escape(item.get("summary", ""))}</p>
            <div class="analysis">{analysis}</div>
            <div class="tag-row">{tags}</div>
            <div class="framework">
              <section>
                <h4><span>What</span>事件本質</h4>
                <p>{escape(item.get("what", ""))}</p>
              </section>
              <section>
                <h4><span>So What</span>影響判讀</h4>
                <p>{escape(item.get("soWhat", ""))}</p>
              </section>
              <section>
                <h4><span>Now What</span>具體行動</h4>
                <p>{escape(item.get("nowWhat", ""))}</p>
              </section>
            </div>
          </article>"""


def render_sources(item: dict[str, Any]) -> str:
    sources = item.get("sources") or [{"name": item.get("source", "未標示媒體"), "url": item.get("url", ""), "publishedDate": item.get("publishedDate", "")}]
    parts = ['<span>來源：</span>']
    for index, source in enumerate(sources):
        name = escape(source.get("name") or "未標示媒體")
        url = source.get("url")
        if url:
            parts.append(f'<a href="{escape_attr(url)}" target="_blank" rel="noopener">{name}</a>')
        else:
            parts.append(f"<span>{name}</span>")
        if index < len(sources) - 1:
            parts.append("<span>、</span>")
    published_date = sources[0].get("publishedDate") if sources else item.get("publishedDate")
    parts.append(f'<span class="source-date"> · {format_display_date(published_date)}</span>')
    return "".join(parts)


def render_applications(items: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"""              <li>
                <strong>{escape(item.get("title", ""))}</strong>
                <span>{escape(item.get("summary") or item.get("nowWhat", ""))}</span>
              </li>"""
        for item in items
    )
    return f"""          <ul class="application-bullets">
{rows}
          </ul>"""


def render_archive_cards(digests: list[dict[str, Any]]) -> str:
    if not digests:
        return """      <div class="empty-section">目前還沒有可收錄的日報。</div>"""
    cards = []
    for digest in digests:
        report_date = digest["reportDate"]
        tags = []
        for section in digest.get("sections", []):
            if section.get("items"):
                tags.append(f'{escape(section.get("title", ""))} {len(section["items"])}')
        cards.append(
            f"""      <article class="archive-card">
        <a href="./{escape_attr(report_date)}/">
          <span>{format_display_date(report_date)}</span>
          <h2>{escape(digest.get("headline", SITE_NAME))}</h2>
          <p>{escape(digest.get("summary", ""))}</p>
          <div class="tag-row">{''.join(f'<span class="tag">{tag}</span>' for tag in tags)}</div>
        </a>
      </article>"""
        )
    return "\n".join(cards)


def render_footer() -> str:
    return f"""<footer class="site-footer">
    <p>{CONTENT_NOTICE}</p>
    <p>© 2026 Bella Yu. All rights reserved. Codex 協作開發｜版本 {VERSION}｜版本日期 {VERSION_DATE}</p>
  </footer>"""


def write_sitemap(root: Path, digests: list[dict[str, Any]]) -> None:
    urls = [
        {
            "loc": SITE_URL,
            "lastmod": today_from_digests(digests),
            "changefreq": "daily",
            "priority": "1.0",
        },
        {
            "loc": f"{SITE_URL}daily/",
            "lastmod": today_from_digests(digests),
            "changefreq": "daily",
            "priority": "0.9",
        }
    ]
    for digest in digests:
        urls.append(
            {
                "loc": f"{SITE_URL}daily/{digest['reportDate']}/",
                "lastmod": digest["reportDate"],
                "changefreq": "monthly",
                "priority": "0.8",
            }
        )

    body = "\n".join(
        f"""  <url>
    <loc>{item['loc']}</loc>
    <lastmod>{item['lastmod']}</lastmod>
    <changefreq>{item['changefreq']}</changefreq>
    <priority>{item['priority']}</priority>
  </url>"""
        for item in urls
    )
    (root / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{body}
</urlset>
""",
        encoding="utf-8",
    )


def has_digest_content(digest: dict[str, Any]) -> bool:
    return any(section.get("items") for section in digest.get("sections", []))


def is_publishable_digest(digest: dict[str, Any]) -> bool:
    return has_digest_content(digest) and not digest.get("isDemo") and not digest.get("noindex")


def today_from_digests(digests: list[dict[str, Any]]) -> str:
    if not digests:
        return datetime.now().date().isoformat()
    return max(digest["reportDate"] for digest in digests)


def format_display_date(value: str | None) -> str:
    if not value:
        return "--"
    parts = value.split("-")
    if len(parts) != 3:
        return value
    return f"{parts[0]}/{parts[1]}/{parts[2]}"


def format_generated_at(value: str | None) -> str:
    if not value:
        return "--"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%Y/%m/%d %H:%M")


def escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def escape_attr(value: Any) -> str:
    return html.escape(str(value), quote=True)


def escape_json_ld(data: dict[str, Any]) -> str:
    return html.escape(json.dumps(data, ensure_ascii=False, indent=4), quote=False)


if __name__ == "__main__":
    main()
