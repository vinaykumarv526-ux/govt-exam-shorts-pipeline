"""
Government Exam Notification Scraper:
Fetches daily government job alerts, notifications, vacancies, eligibility,
and dates from public recruitment portals with intelligent fallbacks.
"""

import os
import re
import json
import time
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SCRAPED_DIR = os.path.join(DATA_DIR, "scraped")
MOCK_FILE = os.path.join(DATA_DIR, "mock_exams.json")

os.makedirs(SCRAPED_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def load_mock_exams() -> List[Dict[str, Any]]:
    """Loads validated mock exam notifications matching reference layout."""
    if os.path.exists(MOCK_FILE):
        with open(MOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_vacancies_number(text: str) -> str:
    match = re.search(r"(\d[\d,]*)\s*(posts?|vacanc(y|ies))?", text, re.IGNORECASE)
    if match:
        num = match.group(1).replace(",", "")
        return f"{int(num):,} Posts" if num.isdigit() else text
    return text


def scrape_freejobalert_latest(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Scrapes latest notifications from FreeJobAlert home/latest notifications tables.
    Extracts recruitment details and structures them into standardized exam objects.
    """
    url = "https://www.freejobalert.com/"
    print(f"[Scraper] Connecting to recruitment portal: {url}")
    results = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            print(f"[Scraper] Portal responded with status {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:  # skip headers
                cols = row.find_all(["td", "th"])
                if len(cols) >= 4:
                    raw_title = clean_text(cols[1].get_text()) if len(cols) > 1 else ""
                    raw_post = clean_text(cols[0].get_text()) if len(cols) > 0 else ""
                    raw_qual = clean_text(cols[2].get_text()) if len(cols) > 2 else ""
                    raw_last_date = clean_text(cols[3].get_text()) if len(cols) > 3 else ""

                    # Link extraction
                    link_elem = row.find("a", href=True)
                    notif_url = link_elem["href"] if link_elem else "https://www.freejobalert.com"

                    if len(raw_title) > 5:
                        # Extract vacancies from title if present
                        vac_match = re.search(r"(\d+)\s*(Posts?|Vacanc)", raw_title, re.IGNORECASE)
                        vac_count = f"{vac_match.group(1)} Posts" if vac_match else "Various Posts"

                        org_candidate = raw_title.split("-")[0].strip() if "-" in raw_title else raw_title.split("Recruitment")[0].strip()

                        exam_item = {
                            "id": re.sub(r"[^a-zA-Z0-9_]", "_", raw_title[:30].lower()),
                            "title": f"{raw_title.upper()[:50]}",
                            "org_name": org_candidate or "Government Recruitment",
                            "org_short": org_candidate[:12].strip(),
                            "vacancy_callout": f"{vac_count.upper()}",
                            "highlights": f"{raw_qual[:25]} | Apply Online | FreeJobAlert",
                            "table": {
                                "Post Name": raw_post or raw_title[:40],
                                "Total Vacancies": vac_count,
                                "Qualification": raw_qual or "Degree / Diploma / 10th / 12th",
                                "Salary / Pay": "As per Govt Rules",
                                "Age Limit": "18–40 Years (Relaxation Applicable)",
                                "Application Start Date": "Ongoing",
                                "Application Last Date": raw_last_date or "Check Notification",
                                "Selection Process": "Written Exam & Interview",
                                "Application Mode": "Online",
                                "Job Location": "Across India"
                            },
                            "notification_url": notif_url,
                            "apply_url": notif_url,
                            "profession_tag": "default_job",
                            "tags": ["GovtJobs", "JobAlert", "IndiaJobs", "Recruitment2026", "Shorts"]
                        }
                        results.append(exam_item)
                        if len(results) >= limit:
                            break
            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[Scraper Error] Could not complete live scrape ({e}). Using mock/fallback data.")

    return results


def fetch_notifications(source: str = "auto", limit: int = 4) -> List[Dict[str, Any]]:
    """
    Primary ingestion dispatcher:
    - 'mock': Returns vetted sample data (WBPSC, TNMVMD, NABFINS, ITPO).
    - 'live': Scrapes real-time notifications.
    - 'auto': Attempts live scrape, seamlessly falls back to vetted dataset.
    """
    if source == "mock":
        print("[Scraper] Using vetted mock exam dataset.")
        return load_mock_exams()[:limit]

    scraped = []
    if source in ("live", "auto"):
        scraped = scrape_freejobalert_latest(limit=limit)

    if not scraped:
        print("[Scraper] Falling back to pre-packaged diverse exam alerts.")
        scraped = load_mock_exams()

    # Save to timestamped cache
    cache_path = os.path.join(SCRAPED_DIR, f"scraped_alerts_{int(time.time())}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(scraped, f, indent=2, ensure_ascii=False)
    print(f"[Scraper] Saved {len(scraped)} notification(s) to cache -> {cache_path}")

    return scraped[:limit]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape latest Govt Exam notifications.")
    parser.add_argument("--source", choices=["auto", "live", "mock"], default="mock", help="Data source")
    parser.add_argument("--limit", type=int, default=3, help="Max notifications to fetch")
    args = parser.parse_args()

    exams = fetch_notifications(source=args.source, limit=args.limit)
    print(f"\n--- Extracted {len(exams)} Exam Alert(s) ---")
    for idx, ex in enumerate(exams, 1):
        print(f"{idx}. {ex['title']} | Vacancies: {ex['vacancy_callout']}")
