#!/usr/bin/env python3
"""Generate a Bella's AI Signal Daily digest placeholder.

This script is the automation entrypoint. The MVP creates a structured daily
file so the website and GitHub Actions path are ready; later iterations can
replace `build_digest` with RSS/search/API collection and AI interpretation.
"""

from __future__ import annotations

import json
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIGEST_DIR = ROOT / "data" / "digests"
MANIFEST_PATH = DIGEST_DIR / "manifest.json"
TAIPEI = timezone(timedelta(hours=8))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Bella's AI Signal Daily digest placeholder.")
    parser.add_argument("--report-date", help="Report date in YYYY-MM-DD. Defaults to today's Taipei date.")
    args = parser.parse_args()

    now = datetime.now(TAIPEI)
    report_date = datetime.strptime(args.report_date, "%Y-%m-%d").date() if args.report_date else now.date()
    coverage_date = report_date - timedelta(days=1)
    generated_at = datetime.combine(report_date, datetime.min.time(), TAIPEI).replace(hour=7).isoformat(timespec="seconds")
    if report_date == now.date():
        generated_at = now.isoformat(timespec="seconds")
    digest = build_digest(report_date.isoformat(), coverage_date.isoformat(), generated_at)
    digest_path = DIGEST_DIR / f"{report_date.isoformat()}.json"
    write_json(digest_path, digest)
    update_manifest(report_date.isoformat(), coverage_date.isoformat(), digest)


def build_digest(report_date: str, coverage_date: str, generated_at: str) -> dict:
    return {
        "reportDate": report_date,
        "coverageDate": coverage_date,
        "generatedAt": generated_at,
        "headline": "今日 AI 日報待補內容",
        "summary": "自動化流程已建立。下一階段會接上新聞來源收集、篩選評分，並整理成給行銷人與品牌決策者使用的趨勢解讀。",
        "sourcePolicy": "台灣媒體依台北時間前一日收集；國際媒體依來源網站發布日期，不做時區換算。",
        "trackedEntities": ["OpenAI", "Google", "Meta", "Anthropic", "Perplexity", "Adobe", "Canva", "Midjourney", "Suno"],
        "scoringPolicy": {
            "priority": ["產業重大性", "數位行銷影響", "內容 / 搜尋 / 社群 / 媒體廣告影響", "工具可用性"],
            "thresholds": {"mustInclude": 13, "candidate": "9-12", "skip": "8 以下"},
        },
        "sections": [
            {"id": "major-events", "title": "大事件", "description": "當天最值得先理解的 AI 產業訊號。", "items": []},
            {"id": "tool-updates", "title": "工具更新", "description": "與行銷工作流直接相關的產品與功能變化。", "items": []},
            {"id": "trends", "title": "值得追蹤的趨勢", "description": "由多則訊號整理出的中期觀察。", "items": []},
            {"id": "applications", "title": "應用切角彙整", "description": "品牌、內容、社群與廣告可測的方向。", "items": []},
        ],
    }


def update_manifest(report_date: str, coverage_date: str, digest: dict) -> None:
    manifest = {"latest": report_date, "digests": []}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    entry = {
        "reportDate": report_date,
        "coverageDate": coverage_date,
        "title": f"Bella's AI Signal｜{report_date.replace('-', '/')}",
        "summary": digest["summary"],
        "path": f"data/digests/{report_date}.json",
    }

    existing = [item for item in manifest.get("digests", []) if item.get("reportDate") != report_date]
    existing.append(entry)
    existing.sort(key=lambda item: item["reportDate"], reverse=True)
    manifest["latest"] = existing[0]["reportDate"]
    manifest["digests"] = existing
    write_json(MANIFEST_PATH, manifest)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
