#!/usr/bin/env python3
"""
Refreshes the dynamic sections of web/index.html using Gemini:
  - Ticker items (live market prices)
  - Stats bar (platform stats)
  - Market cards (active prediction markets)
  - Leaderboard rows (top forecasters)

Requires: GEMINI_API_KEY environment variable
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.error
from datetime import date, datetime

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY
)

TODAY = date.today()
DATE_STR = TODAY.strftime("%-d %B %Y")
NOW_STR = datetime.now().strftime("%H:%M UTC")

SYSTEM_PROMPT = """You are a data generator for Genx-Sportsbook, a sports crypto prediction market exchange.
You produce realistic, plausible market data for a sports prediction exchange homepage.
Data should reflect real-world sports currently in season or upcoming (based on the date given).
Numbers should be internally consistent and feel authentic. Vary the data meaningfully each run.
"""

USER_PROMPT = f"""Today is {DATE_STR}, {NOW_STR}.

Generate fresh homepage data for Genx-Sportsbook. Return ONLY this JSON object — no markdown, no extra text:

{{
  "ticker": [
    {{
      "emoji": "sport emoji",
      "label": "MARKET LABEL IN CAPS (e.g. MAN UTD WIN UCL)",
      "price": "price in cents e.g. 34¢",
      "direction": "up or down",
      "change": "e.g. 2.4%"
    }}
  ],
  "stats": [
    {{"num": "e.g. $47.1B", "label": "Total Volume Traded", "color": "var(--neon-cyan)"}},
    {{"num": "e.g. 912K",   "label": "Active Traders",      "color": "var(--neon-pink)"}},
    {{"num": "e.g. 13,200", "label": "Open Markets",        "color": "var(--neon-yellow)"}},
    {{"num": "e.g. 98.9%",  "label": "Resolution Accuracy", "color": "var(--neon-green)"}}
  ],
  "markets": [
    {{
      "emoji": "sport emoji",
      "sport": "SPORT NAME • STATUS (e.g. LIVE, HOT, TRENDING, UPCOMING, SEASON)",
      "question": "prediction market question",
      "yes_price": 63,
      "volume": "e.g. $1.4M",
      "traders": "e.g. 5,210",
      "closes": "e.g. 4h 12m  or  18d  or  2h 05m",
      "color": "one of: var(--neon-cyan) var(--neon-pink) var(--neon-yellow) var(--neon-green) var(--neon-orange) var(--neon-purple)"
    }}
  ],
  "leaderboard": [
    {{
      "rank": "01",
      "top": true,
      "name": "trader display name",
      "handle": "@handle",
      "profit": "+$284,440",
      "win_rate": "71.2%",
      "badge_emoji": "sport emoji",
      "badge_label": "SPORT ABBREV",
      "badge_color": "neon color var",
      "badge_border": "rgba color"
    }}
  ]
}}

Rules:
- ticker: exactly 8 items (they will be duplicated automatically for the scrolling animation)
- stats: exactly 4 items, in the order shown above
- markets: exactly 6 items covering a variety of sports currently in season
- leaderboard: exactly 5 items; first 3 have "top": true, last 2 have "top": false
- yes_price is an integer 1–99 (the NO price is 100 minus yes_price)
- Make the market questions specific and timely — real teams/players, real upcoming events
- Leaderboard profits should be plausible cumulative figures ($50K–$400K range)
"""


def call_gemini(system: str, user: str) -> dict:
    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 3000,
            "responseMimeType": "application/json",
        },
    }).encode("utf-8")

    for attempt in range(4):
        req = urllib.request.Request(
            GEMINI_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                wait = 30 * (2 ** attempt)  # 30s, 60s, 120s
                print(f"Rate limited (attempt {attempt + 1}), retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"Gemini HTTP error {e.code}: {e.read().decode()}", file=sys.stderr)
                sys.exit(1)

    text = body["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```[a-z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return json.loads(text)


def build_ticker_html(items: list) -> str:
    lines = []
    # Duplicate the list for the seamless scroll animation
    for item in items * 2:
        direction_class = item["direction"]
        arrow = "▲" if direction_class == "up" else "▼"
        lines.append(
            f'    <span class="ticker-item">'
            f'<span class="label">{item["emoji"]} {item["label"]}</span> '
            f'{item["price"]} '
            f'<span class="{direction_class}">{arrow}{item["change"]}</span>'
            f'</span>'
        )
    return "\n".join(lines)


def build_stats_html(items: list) -> str:
    lines = []
    for item in items:
        lines.append(
            f'  <div class="stat-item" style="--accent-color: {item["color"]}">\n'
            f'    <span class="stat-num">{item["num"]}</span>\n'
            f'    <span class="stat-label">{item["label"]}</span>\n'
            f'  </div>'
        )
    return "\n".join(lines)


def build_markets_html(items: list) -> str:
    lines = []
    for card in items:
        yes = card["yes_price"]
        no = 100 - yes
        color = card["color"]
        # Derive rgba border from the color var name
        border_map = {
            "var(--neon-cyan)":   "rgba(0,245,255,0.4)",
            "var(--neon-pink)":   "rgba(255,0,110,0.4)",
            "var(--neon-yellow)": "rgba(255,230,0,0.4)",
            "var(--neon-green)":  "rgba(57,255,20,0.4)",
            "var(--neon-orange)": "rgba(255,102,0,0.4)",
            "var(--neon-purple)": "rgba(191,0,255,0.4)",
        }
        br = border_map.get(color, "rgba(0,245,255,0.4)")
        lines.append(
            f'    <div class="market-card" style="--card-color: {color}">\n'
            f'      <div class="bracket-tl" style="border-color: {br}"></div>'
            f'<div class="bracket-tr" style="border-color: {br}"></div>'
            f'<div class="bracket-bl" style="border-color: {br}"></div>'
            f'<div class="bracket-br" style="border-color: {br}"></div>\n'
            f'      <div class="market-sport">{card["emoji"]} {card["sport"]}</div>\n'
            f'      <div class="market-question">{card["question"]}</div>\n'
            f'      <div class="prob-bar"><div class="prob-fill" style="width: {yes}%"></div></div>\n'
            f'      <div class="market-options">\n'
            f'        <button class="option-btn">YES {yes}¢</button>\n'
            f'        <button class="option-btn">NO {no}¢</button>\n'
            f'      </div>\n'
            f'      <div class="market-meta">\n'
            f'        <span>Vol: {card["volume"]}</span>\n'
            f'        <span>{card["traders"]} traders</span>\n'
            f'        <span>Closes: {card["closes"]}</span>\n'
            f'      </div>\n'
            f'    </div>'
        )
    return "\n\n".join(lines)


def build_leaderboard_html(items: list) -> str:
    lines = []
    for row in items:
        rank_class = "lb-rank top" if row.get("top") else "lb-rank"
        lines.append(
            f'    <div class="lb-row">\n'
            f'      <div class="{rank_class}">{row["rank"]}</div>\n'
            f'      <div><div class="lb-name">{row["name"]}</div>'
            f'<div class="lb-handle">{row["handle"]}</div></div>\n'
            f'      <div class="lb-profit">{row["profit"]}</div>\n'
            f'      <div class="lb-pct">{row["win_rate"]}</div>\n'
            f'      <div><span class="lb-badge" style="color: {row["badge_color"]}; '
            f'border-color: {row["badge_border"]}">'
            f'{row["badge_emoji"]} {row["badge_label"]}</span></div>\n'
            f'    </div>'
        )
    return "\n\n".join(lines)


def replace_section(content: str, tag: str, new_html: str) -> str:
    pattern = rf"<!-- GENX:{tag}:START -->.*?<!-- GENX:{tag}:END -->"
    replacement = f"<!-- GENX:{tag}:START -->\n{new_html}\n    <!-- GENX:{tag}:END -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def main():
    index_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "web",
        "index.html",
    )

    print("Calling Gemini for fresh homepage data...")
    data = call_gemini(SYSTEM_PROMPT, USER_PROMPT)

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, "TICKER",      build_ticker_html(data["ticker"]))
    content = replace_section(content, "STATS",       build_stats_html(data["stats"]))
    content = replace_section(content, "MARKETS",     build_markets_html(data["markets"]))
    content = replace_section(content, "LEADERBOARD", build_leaderboard_html(data["leaderboard"]))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Homepage refreshed at {NOW_STR}")


if __name__ == "__main__":
    main()
