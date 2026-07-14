#!/usr/bin/env python3
"""
fetch_contributions.py — Scrape GitHub contribution data from a public profile.
                          No authentication required.

Writes: contributions.json
"""

import json
import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

# ────────────────────── CONFIG ──────────────────────
GH_PROFILE_USER = "Abdullah-Shahriar"
OUTPUT_FILE      = "contributions.json"
# ────────────────────── END CONFIG ──────────────────


def fetch_contributions() -> dict:
    """Scrape the last year of contributions from the GitHub contributions page."""
    # Use the dedicated contributions endpoint — returns calendar HTML directly
    url = f"https://github.com/users/{GH_PROFILE_USER}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"
    }

    print(f"[fetch] Fetching {url} ...")
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract total contributions from the heading
    total = 0
    heading = soup.select_one("h2")
    if heading:
        match = re.search(r"([\d,]+)\s+contributions?", heading.get_text())
        if match:
            total = int(match.group(1).replace(",", ""))

    # Find contribution calendar cells
    cells = soup.select("td.ContributionCalendar-day")

    days = []
    current_streak = 0
    max_streak = 0
    streak_counting = True

    for cell in cells:
        date = cell.get("data-date", "")
        level = int(cell.get("data-level", "0"))

        if date:
            days.append({
                "date": date,
                "count": level,   # use level as intensity (0-4)
                "level": level,
            })

    # Sort by date
    days.sort(key=lambda d: d["date"])

    # Calculate streaks (using level > 0 as "active day")
    for d in reversed(days):
        if d["level"] > 0 and streak_counting:
            current_streak += 1
        else:
            streak_counting = False

    # Calculate max streak
    temp_streak = 0
    for d in days:
        if d["level"] > 0:
            temp_streak += 1
            max_streak = max(max_streak, temp_streak)
        else:
            temp_streak = 0

    result = {
        "user": GH_PROFILE_USER,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "days": days,
    }

    return result


def main():
    data = fetch_contributions()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[fetch] Saved {len(data['days'])} days to {OUTPUT_FILE}")
    print(f"[fetch] Total: {data['total_contributions']} contributions")
    print(f"[fetch] Current streak: {data['current_streak']} days")
    print(f"[fetch] Max streak: {data['max_streak']} days")


if __name__ == "__main__":
    main()
