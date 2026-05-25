#!/usr/bin/env python3
"""
Generates a live activity feed for web/live.html using Gemini.
Updates platform stats, trending markets, and the scrolling activity feed.

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

SYSTEM_PROMPT = """You generate realistic live trading activity for Genx-Sportsbook. \
Activities should reference real sports events currently in season and feel like actual \
trades happening right now on a busy platform."""

USER_PROMPT = f"""Generate live activity data for Genx-Sportsbook. Today: {DATE_STR}, {NOW_STR}. \
Return ONLY this JSON:
{{
  "stats": {{
    "active_users": "e.g. 2,847",
    "bets_today": "e.g. 19,241",
    "volume_today": "e.g. $3.8M",
    "biggest_win_today": "e.g. $28,400"
  }},
  "trending": [
    {{"name": "Short market name", "volume": "$X.XM", "price": 67, "change": "+3.2%", "color": "var(--neon-cyan)"}},
    {{"name": "Short market name", "volume": "$X.XM", "price": 41, "change": "-1.8%", "color": "var(--neon-pink)"}},
    {{"name": "Short market name", "volume": "$X.XM", "price": 58, "change": "+5.1%", "color": "var(--neon-yellow)"}},
    {{"name": "Short market name", "volume": "$X.XM", "price": 29, "change": "+0.7%", "color": "var(--neon-green)"}},
    {{"name": "Short market name", "volume": "$X.XM", "price": 73, "change": "-2.3%", "color": "var(--neon-purple)"}}
  ],
  "activities": [
    {{
      "initials": "2-letter initials",
      "username": "plausible trader name",
      "action": "BOUGHT or SOLD",
      "qty": "e.g. 2,400",
      "market": "concise market name referencing real current event",
      "price": "e.g. 67¢",
      "total": "e.g. $1,608",
      "time_ago": "e.g. just now",
      "category": "Football",
      "color": "var(--neon-cyan)",
      "big": false
    }}
  ]
}}

Rules:
- trending: exactly 5 items, each with a distinct neon color from: var(--neon-cyan) var(--neon-pink) var(--neon-yellow) var(--neon-green) var(--neon-purple)
- activities: exactly 60 items
- Mix of small (under $500) and medium ($500-$5000) trades
- 5-8 "big" trades (big:true, over $5000) scattered through the list — not all at the top
- time_ago ranges from "just now" to "18m ago" — distribute realistically (many recent, fewer old)
- Reference a wide variety of current sports events in season on {DATE_STR}
- Make usernames varied and fun with crypto-trader vibes: e.g. SharpLondoner, QuantMaven88, GridironGhost, SatoshiSharps, EdgeSeeker, AlphaFade, DegenProphet
- color for each activity: one of var(--neon-cyan) var(--neon-pink) var(--neon-yellow) var(--neon-green) var(--neon-orange) var(--neon-purple)
- category: one of Football/NFL/NBA/F1/Tennis/Boxing/Cricket/Hockey/Esports/Golf/Politics
"""


def call_gemini(system: str, user: str) -> dict:
    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": 0},
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


def build_live_stats_html(data: dict) -> str:
    s = data.get("stats", {})
    items = [
        ("active_users",     "Active Now",       "var(--neon-cyan)"),
        ("bets_today",       "Trades Today",     "var(--neon-yellow)"),
        ("volume_today",     "Volume Today",     "var(--neon-green)"),
        ("biggest_win_today","Biggest Win Today","var(--neon-pink)"),
    ]
    lines = []
    for key, label, color in items:
        val = s.get(key, "—")
        lines.append(
            f'  <div class="live-stat" style="--stat-color: {color}">\n'
            f'    <span class="live-stat-num">{val}</span>\n'
            f'    <span class="live-stat-label">{label}</span>\n'
            f'  </div>'
        )
    return "\n".join(lines)


def build_live_trending_html(data: dict) -> str:
    items = data.get("trending", [])
    cards = []
    for item in items:
        change = item.get("change", "+0.0%")
        change_str = str(change)
        change_class = "trend-change-up" if change_str.startswith("+") else "trend-change-down"
        color = item.get("color", "var(--neon-cyan)")
        price = item.get("price", 50)
        no_price = 100 - int(price)
        cards.append(
            f'  <div class="trending-card" style="--card-color: {color}">\n'
            f'    <div class="trending-name">{item.get("name", "")}</div>\n'
            f'    <div class="trending-price">{price}¢ <span class="{change_class}">{change_str}</span></div>\n'
            f'    <div class="trending-vol">{item.get("volume", "")}</div>\n'
            f'    <div class="trending-actions">'
            f'<button class="trend-btn">YES {price}¢</button>'
            f'<button class="trend-btn">NO {no_price}¢</button>'
            f'</div>\n'
            f'  </div>'
        )
    return "\n\n".join(cards)


def build_live_feed_html(data: dict) -> str:
    activities = data.get("activities", [])
    items = []
    for act in activities:
        big = act.get("big", False)
        item_class = "activity-item big" if big else "activity-item"
        color = act.get("color", "var(--neon-cyan)")
        action = act.get("action", "BOUGHT")
        action_class = "action-buy" if action == "BOUGHT" else "action-sell"
        initials = act.get("initials", "??")
        username = act.get("username", "trader")
        qty = act.get("qty", "0")
        market = act.get("market", "")
        price = act.get("price", "—")
        total = act.get("total", "—")
        time_ago = act.get("time_ago", "")
        category = act.get("category", "")

        items.append(
            f'  <div class="{item_class}" style="--activity-color: {color}">\n'
            f'    <div class="activity-avatar" style="--avatar-color: {color}">{initials}</div>\n'
            f'    <div class="activity-body">\n'
            f'      <div class="activity-top">\n'
            f'        <span class="activity-username">{username}</span>\n'
            f'        <span class="activity-action {action_class}">{action}</span>\n'
            f'        <span class="activity-category">{category}</span>\n'
            f'      </div>\n'
            f'      <div class="activity-mid">\n'
            f'        <span class="activity-qty">{qty} shares</span>\n'
            f'        <span class="activity-sep">·</span>\n'
            f'        <span class="activity-market">{market}</span>\n'
            f'      </div>\n'
            f'      <div class="activity-bot">\n'
            f'        <span class="activity-price">@ {price}</span>\n'
            f'        <span class="activity-total">{total}</span>\n'
            f'        <span class="activity-time">{time_ago}</span>\n'
            f'      </div>\n'
            f'    </div>\n'
            f'  </div>'
        )
    return "\n\n".join(items)


def replace_section(content: str, tag: str, new_html: str) -> str:
    pattern = rf"<!-- GENX:{tag}:START -->.*?<!-- GENX:{tag}:END -->"
    replacement = f"<!-- GENX:{tag}:START -->\n{new_html}\n    <!-- GENX:{tag}:END -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def main():
    live_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "web",
        "live.html",
    )

    print("Calling Gemini for fresh live feed data...")
    data = call_gemini(SYSTEM_PROMPT, USER_PROMPT)

    with open(live_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, "LIVE_STATS",    build_live_stats_html(data))
    content = replace_section(content, "LIVE_TRENDING", build_live_trending_html(data))
    content = replace_section(content, "LIVE_FEED",     build_live_feed_html(data))

    with open(live_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Live feed page refreshed at {NOW_STR}")


if __name__ == "__main__":
    main()
