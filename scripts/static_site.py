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
VERSION = "v0.17.2"
VERSION_DATE = "2026/08/21"
ASSET_VERSION = "20260821c"
CONTENT_NOTICE = "本站內容為 AI 趨勢整理、評論與行銷應用解讀；新聞來源與原文著作權屬各原媒體與作者所有。若需完整內容，請閱讀原文。"
SOCIAL_IMAGE_URL = f"{SITE_URL}assets/og-image.png"
SOCIAL_IMAGE_ALT = "Bella's AI 趨勢日報品牌預覽圖"
SITE_SAME_AS = [
    "https://www.bella.tw/",
    "https://www.instagram.com/hibella/",
    "https://github.com/hibellayu/bella-ai-signal-daily",
]


def main() -> None:
    build_static_site(ROOT)


def build_static_site(root: Path = ROOT) -> None:
    digests = load_publishable_digests(root)
    daily_dir = root / "daily"
    if daily_dir.exists():
        shutil.rmtree(daily_dir)
    daily_dir.mkdir(parents=True, exist_ok=True)

    if digests:
        write_home_page(root, digests[0])

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


def write_home_page(root: Path, latest_digest: dict[str, Any]) -> None:
    (root / "index.html").write_text(render_home_page(latest_digest), encoding="utf-8")


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
    description = build_meta_description("依日期整理 Bella's AI 趨勢日報，收錄 AI 產業趨勢、工具更新與行銷應用切角，方便搜尋引擎、AI 搜尋工具與讀者回查每日內容。")
    canonical = f"{SITE_URL}daily/"
    keywords = base_keywords()
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": canonical,
        "inLanguage": "zh-Hant-TW",
        "image": SOCIAL_IMAGE_URL,
        "keywords": ", ".join(keywords),
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
  <meta name="keywords" content="{escape(', '.join(keywords))}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
{render_icon_links("../")}
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_TW">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
{render_social_image_meta()}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">
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


def render_home_page(latest_digest: dict[str, Any]) -> str:
    title = f"{SITE_NAME}｜AI 趨勢、工具更新與行銷應用"
    description = build_meta_description(
        "Bella's AI 趨勢日報每日整理 AI 產業趨勢、工具更新與行銷應用切角，協助行銷人與品牌決策者快速理解資訊、判斷影響並找到可落地的行動。"
    )
    canonical = SITE_URL
    keywords = digest_keywords(latest_digest)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "alternateName": "Bella's AI Signal Daily",
        "url": canonical,
        "inLanguage": "zh-Hant-TW",
        "description": description,
        "image": SOCIAL_IMAGE_URL,
        "keywords": ", ".join(keywords),
        "publisher": {"@type": "Person", "name": "Bella Yu", "sameAs": SITE_SAME_AS},
        "sameAs": SITE_SAME_AS,
        "about": [
            {"@type": "Thing", "name": "AI 趨勢日報"},
            {"@type": "Thing", "name": "數位行銷"},
            {"@type": "Thing", "name": "品牌策略"},
            {"@type": "Thing", "name": "內容行銷"},
            {"@type": "Thing", "name": "AI 搜尋"},
            {"@type": "Thing", "name": "Generative Engine Optimization"},
        ],
        "mainEntity": {
            "@type": "Article",
            "headline": latest_digest.get("headline") or SITE_NAME,
            "url": f"{SITE_URL}daily/{latest_digest['reportDate']}/",
            "datePublished": latest_digest.get("generatedAt"),
        },
    }
    priority = latest_digest.get("scoringPolicy", {}).get("priority", [])
    section_nav = "\n".join(
        f'        <a href="#{escape_attr(section["id"])}">{escape(section.get("title", ""))}</a>'
        for section in latest_digest.get("sections", [])
        if section.get("items")
    )

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="keywords" content="{escape(', '.join(keywords))}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
{render_icon_links("")}
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_TW">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
{render_social_image_meta()}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v={ASSET_VERSION}">
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
  <header class="topbar">
    <div class="topbar__inner">
      <a class="brand" href="#top" aria-label="{SITE_NAME} 首頁">
        <span class="brand__mark">AI</span>
        <span>
          <strong>{SITE_NAME}</strong>
          <small>{SITE_SUBTITLE}</small>
        </span>
      </a>

      <div class="topbar__tools">
        <a class="static-home-link" href="daily/">日報列表</a>
        <form class="date-picker" aria-label="日報日期篩選">
          <label>
            <span>年</span>
            <select id="yearSelect"></select>
          </label>
          <label>
            <span>月</span>
            <select id="monthSelect"></select>
          </label>
          <label>
            <span>日</span>
            <select id="daySelect"></select>
          </label>
        </form>
      </div>
    </div>
  </header>

  <main id="top" class="shell">
    <aside class="panel digest-meta" aria-label="日報資訊">
      <p class="eyebrow">Report Info</p>
      <h1 id="dailyHeadline">{escape(latest_digest.get("headline") or SITE_NAME)}</h1>

      <dl class="meta-grid">
        <div>
          <dt>日報日期</dt>
          <dd id="reportDate">{format_display_date(latest_digest.get("reportDate"))}</dd>
        </div>
        <div>
          <dt>資料日期</dt>
          <dd id="coverageDate">{format_display_date(latest_digest.get("coverageDate"))}</dd>
        </div>
        <div>
          <dt>生成時間</dt>
          <dd id="generatedAt">{format_generated_at(latest_digest.get("generatedAt"))}</dd>
        </div>
        <div>
          <dt>本日收錄</dt>
          <dd id="collectionCount">{escape(collection_count_text(latest_digest))}</dd>
        </div>
      </dl>

      {render_impact_framework(latest_digest, dynamic=True)}

      <div class="signal-policy">
        <h2>收錄優先順序</h2>
        <ol id="priorityList">{''.join(f'<li>{escape(item)}</li>' for item in priority)}</ol>
      </div>

      <nav class="section-nav" aria-label="區塊導覽">
{section_nav}
      </nav>
    </aside>

    <section class="content" aria-live="polite">
      <div id="statusMessage" class="status" hidden></div>
      <div id="digestContent">
{render_strategy_brief(latest_digest)}
{render_sections(latest_digest)}
      </div>
    </section>
  </main>

  {render_site_identity_section()}
  {render_footer()}
{render_dynamic_templates()}
  <script src="app.js?v={ASSET_VERSION}"></script>
</body>
</html>
"""


def render_site_identity_section() -> str:
    return f"""<section class="site-identity" aria-labelledby="siteIdentityTitle">
    <div>
      <p class="eyebrow">About This Daily</p>
      <h2 id="siteIdentityTitle">關於 Bella's AI 趨勢日報</h2>
      <p>Bella's AI 趨勢日報是給行銷人、品牌決策者與內容工作者閱讀的 AI 趨勢整理。本站每日把 AI 產業新聞、工具更新、搜尋與社群變化，轉譯成品牌策略、數位行銷、內容行銷、媒體廣告與團隊流程可以使用的判讀。</p>
      <p>本站不是一般新聞列表，而是用「國際事件與產業格局、品牌端、使用者端 / 深度工作者、一般社會大眾」四層框架，判斷 AI 變化如何影響品牌被看見、內容被引用、工具被採用，以及行銷工作流程如何調整。</p>
    </div>
    <ul aria-label="本站適合引用的主題">
      <li>AI 趨勢日報</li>
      <li>AI 搜尋與 GEO</li>
      <li>品牌策略</li>
      <li>數位行銷</li>
      <li>內容行銷</li>
      <li>AI 工具工作流</li>
    </ul>
  </section>"""


def render_daily_page(digest: dict[str, Any]) -> str:
    report_date = digest["reportDate"]
    title = f"{escape(digest.get('headline') or SITE_NAME)}｜{format_display_date(report_date)}"
    description = build_meta_description(digest.get("summary") or "AI 趨勢、工具更新與行銷應用日報。")
    canonical = f"{SITE_URL}daily/{report_date}/"
    keywords = digest_keywords(digest)
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
        "image": SOCIAL_IMAGE_URL,
        "keywords": ", ".join(keywords),
        "author": {"@type": "Person", "name": "Bella Yu"},
        "publisher": {"@type": "Person", "name": "Bella Yu"},
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        "about": [{"@type": "Thing", "name": keyword} for keyword in keywords[:12]],
    }

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="keywords" content="{escape(', '.join(keywords))}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
{render_icon_links("../../")}
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="zh_TW">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
{render_social_image_meta()}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">
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
      {render_strategy_brief(digest)}
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
      <p class="eyebrow">Report Info</p>
      <h1>{escape(digest.get("headline") or SITE_NAME)}</h1>

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
          <dt>本日收錄</dt>
          <dd>{escape(collection_count_text(digest))}</dd>
        </div>
      </dl>

      {render_impact_framework(digest)}

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


def render_strategy_brief(digest: dict[str, Any]) -> str:
    takeaways = strategy_takeaways(digest)
    if not takeaways:
        return ""
    items = "\n".join(f"          <li>{escape(item)}</li>" for item in takeaways)
    return f"""<section class="strategy-brief" aria-label="今日策略判讀">
        <p class="eyebrow">Decision Lens</p>
        <h2>今日策略判讀</h2>
        <ul>
{items}
        </ul>
      </section>"""


def strategy_takeaways(digest: dict[str, Any]) -> list[str]:
    explicit = digest.get("strategyTakeaways")
    if isinstance(explicit, list):
        return [str(item).strip() for item in explicit if str(item).strip()][:4]
    summary = str(digest.get("summary", "")).strip()
    if not summary:
        return []
    chunks = [
        chunk.strip()
        for chunk in summary.replace("；", "。").replace("，並", "。並").split("。")
        if chunk.strip()
    ]
    return [chunk + "。" for chunk in chunks[:3]]


def collection_count_text(digest: dict[str, Any]) -> str:
    news_count = 0
    application_count = 0
    for section in digest.get("sections", []):
        items = section.get("items", [])
        if section.get("id") == "applications":
            application_count += len(items)
        else:
            news_count += len(items)
    return f"新聞判讀 {news_count} 則｜應用切角 {application_count} 則"


def render_impact_framework(digest: dict[str, Any], dynamic: bool = False) -> str:
    framework = digest.get("scoringPolicy", {}).get("impactFramework", [])
    if not framework:
        framework = ["國際事件與產業格局", "品牌端", "使用者端 / 深度工作者", "一般社會大眾"]
    list_id = ' id="impactFrameworkList"' if dynamic else ""
    items = "".join(f"<li>{escape(item)}</li>" for item in framework)
    return f"""      <div class="impact-framework">
        <h2>判讀框架</h2>
        <ol{list_id}>{items}</ol>
      </div>"""


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
    score_badge = render_static_score(item)
    angles = render_impact_angles(item)
    return f"""          <article class="signal-card">
            <div class="signal-card__head">
              <div>
                <div class="source-line">{render_sources(item)}</div>
                <h3>{escape(item.get("title", ""))}</h3>
              </div>
              {score_badge}
            </div>
            <p class="summary">{escape(item.get("summary", ""))}</p>
            <div class="analysis">{analysis}</div>
            {angles}
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


def render_impact_angles(item: dict[str, Any]) -> str:
    angles = item.get("impactAngles")
    if not isinstance(angles, list) or not angles:
        return ""
    tags = "".join(f'<span class="angle-pill">{escape(str(angle))}</span>' for angle in angles[:4] if str(angle).strip())
    if not tags:
        return ""
    return f"""<div class="impact-angle-row"><span>判讀角度</span>{tags}</div>"""


def render_static_score(item: dict[str, Any]) -> str:
    score = normalize_score(item.get("score", {}))
    fields = [
        ("產業重大性", score["industryImpact"], "0-5"),
        ("數位行銷影響", score["digitalMarketingImpact"], "0-5"),
        ("內容 / 搜尋 / 社群 / 媒體廣告影響", score["contentSearchSocialAdsImpact"], "0-5"),
        ("工具可用性", score["toolUsability"], "0-5"),
        ("指定追蹤公司 / 工具相關性", score["trackedEntityRelevance"], "0-3"),
    ]
    total = sum(value for _, value, _ in fields)
    rows = "".join(
        f"""<div><dt>{escape(label)}（{escape(scale)}）</dt><dd>{value} 分</dd></div>"""
        for label, value, scale in fields
    )
    formula = " + ".join(str(value) for _, value, _ in fields)
    return f"""<details class="static-score">
                <summary>{total} 分</summary>
                <div class="static-score__body">
                  <p>每則資訊依 5 個面向評分，排序優先看產業重大性，再看數位行銷影響。</p>
                  <dl class="score-breakdown">{rows}</dl>
                  <p class="score-formula">{formula} = {total} 分</p>
                </div>
              </details>"""


def normalize_score(score: dict[str, Any]) -> dict[str, int]:
    limits = {
        "industryImpact": 5,
        "digitalMarketingImpact": 5,
        "contentSearchSocialAdsImpact": 5,
        "toolUsability": 5,
        "trackedEntityRelevance": 3,
    }
    return {key: normalize_score_value(score.get(key, 0), limit) for key, limit in limits.items()}


def normalize_score_value(value: Any, limit: int) -> int:
    try:
        number = round(float(value))
    except (TypeError, ValueError):
        number = 0
    if number < 0:
        return 0
    if number <= limit:
        return int(number)
    if limit == 3:
        if number <= 5:
            return min(limit, round(number * 3 / 5))
        return min(limit, round(number * 3 / 10))
    return min(limit, round(number / 2))


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


def render_dynamic_templates() -> str:
    return """  <dialog id="scoreDialog" class="score-dialog" aria-labelledby="scoreDialogTitle">
    <div class="score-dialog__panel">
      <button class="score-dialog__close" type="button" aria-label="關閉分數說明">×</button>
      <h2 id="scoreDialogTitle">分數怎麼來</h2>
      <div id="scoreDialogBody"></div>
    </div>
  </dialog>

  <template id="sectionTemplate">
    <section class="digest-section">
      <div class="section-heading">
        <p class="section-heading__count"></p>
        <h2></h2>
        <p></p>
      </div>
      <div class="item-list"></div>
    </section>
  </template>

  <template id="itemTemplate">
    <article class="signal-card">
      <div class="signal-card__head">
        <div>
          <div class="source-line"></div>
          <h3></h3>
        </div>
        <span class="score-badge"></span>
      </div>
      <p class="summary"></p>
      <div class="analysis"></div>
      <div class="tag-row"></div>
      <div class="framework">
        <section>
          <h4><span>What</span>事件本質</h4>
          <p class="what"></p>
        </section>
        <section>
          <h4><span>So What</span>影響判讀</h4>
          <p class="so-what"></p>
        </section>
        <section>
          <h4><span>Now What</span>具體行動</h4>
          <p class="now-what"></p>
        </section>
      </div>
    </article>
  </template>
"""


def render_icon_links(prefix: str) -> str:
    return f"""  <link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="{prefix}assets/apple-touch-icon.png">
  <meta name="theme-color" content="#2b2520">"""


def render_social_image_meta() -> str:
    return f"""  <meta property="og:image" content="{SOCIAL_IMAGE_URL}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{SOCIAL_IMAGE_ALT}">"""


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


def build_meta_description(value: str, limit: int = 118) -> str:
    normalized = " ".join(str(value).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip(" ，。、；：") + "…"


def base_keywords() -> list[str]:
    return [
        "AI 趨勢",
        "AI 日報",
        "AI 趨勢日報",
        "數位行銷",
        "品牌策略",
        "內容行銷",
        "社群應用",
        "媒體廣告",
        "AI 搜尋",
        "行銷策略",
        "AI 工具",
        "生成式 AI",
    ]


def digest_keywords(digest: dict[str, Any]) -> list[str]:
    keywords: list[str] = []
    for keyword in base_keywords():
        add_unique(keywords, keyword)
    for entity in digest.get("trackedEntities", []):
        add_unique(keywords, entity)
    for section in digest.get("sections", []):
        add_unique(keywords, section.get("title", ""))
        for item in section.get("items", []):
            for tag in item.get("tags", []):
                add_unique(keywords, tag)
            for source in item.get("sources", []):
                add_unique(keywords, source.get("name", ""))
    return keywords[:28]


def add_unique(items: list[str], value: Any) -> None:
    text = str(value).strip()
    if text and text not in items:
        items.append(text)


def escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def escape_attr(value: Any) -> str:
    return html.escape(str(value), quote=True)


def escape_json_ld(data: dict[str, Any]) -> str:
    return html.escape(json.dumps(data, ensure_ascii=False, indent=4), quote=False)


if __name__ == "__main__":
    main()
