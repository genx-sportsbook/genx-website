#!/usr/bin/env python3
"""
Generates fresh trading terminal data for web/markets.html using Gemini.
Updates live market status, instrument table, orderbook, recent fills,
featured chart, and featured instrument metadata.

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

SYSTEM_PROMPT = """You are a data generator for Genx-Sportsbook, a crypto sports prediction exchange. \
Generate realistic, plausible prediction market trading data. Reflect real-world sports events currently \
in season for the given date. Numbers should be internally consistent and feel authentic to a live trading environment."""

USER_PROMPT = f"""Today is {DATE_STR}, {NOW_STR}.

Generate trading terminal data for Genx-Sportsbook. Return ONLY this JSON, no markdown:
{{
  "status": {{
    "market_count": "e.g. 13,847",
    "volume_24h": "e.g. $51.3M",
    "active_traders": "e.g. 3,241",
    "last_updated": "{NOW_STR}"
  }},
  "featured": {{
    "symbol": "e.g. ARSENAL-UCL",
    "name": "Full market question",
    "category": "Football",
    "price": 67,
    "change_24h": 3.2,
    "volume": "$4.2M",
    "high_24h": 71,
    "low_24h": 62,
    "chart_points": [array of 80 integers 1-99 representing price history, ending at current price, forming a realistic-looking chart]
  }},
  "instruments": [
    {{
      "symbol": "SHORT-CODE",
      "name": "Market question (concise)",
      "category": "one of: Football, NFL, NBA, F1, Tennis, Boxing, Cricket, Hockey, Esports, Golf",
      "price": 1-99,
      "change": 3.2,
      "volume": "e.g. $1.4M",
      "open_interest": "e.g. 8,420",
      "trend": [array of 12 integers 1-99 ending at price — used for sparkline]
    }}
  ],
  "orderbook": {{
    "bids": [{{"price": 66, "size": "e.g. $12,400", "total": "e.g. $45,200"}}, {{"price": 65, "size": "e.g. $9,800", "total": "e.g. $32,800"}}, {{"price": 64, "size": "e.g. $7,200", "total": "e.g. $23,000"}}, {{"price": 63, "size": "e.g. $5,100", "total": "e.g. $15,800"}}, {{"price": 62, "size": "e.g. $3,400", "total": "e.g. $10,700"}}],
    "asks": [{{"price": 68, "size": "e.g. $8,300", "total": "e.g. $31,100"}}, {{"price": 69, "size": "e.g. $6,100", "total": "e.g. $22,800"}}, {{"price": 70, "size": "e.g. $4,800", "total": "e.g. $16,700"}}, {{"price": 71, "size": "e.g. $3,200", "total": "e.g. $11,900"}}, {{"price": 72, "size": "e.g. $2,100", "total": "e.g. $8,700"}}]
  }},
  "recent_fills": [
    {{"side": "BUY or SELL", "price": 67, "size": "e.g. $3,200", "time": "e.g. 0:23 ago"}},
    {{"side": "BUY", "price": 66, "size": "e.g. $1,800", "time": "e.g. 0:47 ago"}},
    {{"side": "SELL", "price": 68, "size": "e.g. $4,100", "time": "e.g. 1:12 ago"}},
    {{"side": "BUY", "price": 65, "size": "e.g. $900", "time": "e.g. 1:38 ago"}},
    {{"side": "BUY", "price": 67, "size": "e.g. $2,600", "time": "e.g. 2:05 ago"}},
    {{"side": "SELL", "price": 69, "size": "e.g. $5,400", "time": "e.g. 2:31 ago"}},
    {{"side": "BUY", "price": 66, "size": "e.g. $1,200", "time": "e.g. 3:14 ago"}},
    {{"side": "SELL", "price": 68, "size": "e.g. $3,700", "time": "e.g. 3:52 ago"}},
    {{"side": "BUY", "price": 65, "size": "e.g. $800", "time": "e.g. 4:29 ago"}},
    {{"side": "BUY", "price": 67, "size": "e.g. $2,100", "time": "e.g. 5:03 ago"}}
  ]
}}

Rules:
- 20 instruments covering varied sports currently in season on {DATE_STR}
- Featured market is the highest-volume instrument — copy its symbol/name/category/price/change_24h into the featured block
- Orderbook bids are near featured price (below), asks slightly above
- change field for instruments is a float with sign e.g. 3.2 means +3.2, -1.8 means -1.8
- Chart points should form a realistic price path with narrative shape: a dip, a recovery, momentum — ending at featured price
- Trend arrays for each instrument must end at that instrument's price
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
            retryable = e.code in (429, 500, 502, 503, 504)
            if retryable and attempt < 3:
                wait = 30 * (2 ** attempt)  # 30s, 60s, 120s
                print(f"Gemini HTTP {e.code} (attempt {attempt + 1}), retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"Gemini HTTP error {e.code}: {e.read().decode()}", file=sys.stderr)
                sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < 3:
                wait = 30 * (2 ** attempt)  # 30s, 60s, 120s
                print(f"Gemini request error (attempt {attempt + 1}): {e.reason}, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"Gemini request failed after 4 attempts: {e.reason}", file=sys.stderr)
                sys.exit(1)

    text = body["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```[a-z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return json.loads(text)


def _sparkline_svg(trend: list, change: float) -> str:
    """Return an inline SVG sparkline for a 12-point trend array."""
    if not trend:
        return ""
    mn = min(trend)
    mx = max(trend)
    rng = max(mx - mn, 1)
    # Normalize to SVG height 20, invert Y (SVG 0 is top)
    pts = []
    for i, v in enumerate(trend):
        x = round(i * (60 / max(len(trend) - 1, 1)), 2)
        y = round(20 - ((v - mn) / rng) * 18 - 1, 2)
        pts.append(f"{x},{y}")
    color = "#39ff14" if change >= 0 else "#ff006e"
    points_str = " ".join(pts)
    return (
        f'<svg viewBox="0 0 60 20" width="60" height="20" '
        f'style="display:block;overflow:visible">'
        f'<polyline points="{points_str}" fill="none" stroke="{color}" '
        f'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
        f'</svg>'
    )


def build_status_html(data: dict) -> str:
    s = data["status"]
    items = [
        ("market_count", "Markets", "var(--neon-cyan)"),
        ("volume_24h",   "24h Volume", "var(--neon-green)"),
        ("active_traders", "Active Traders", "var(--neon-yellow)"),
        ("last_updated", "Last Updated", "var(--neon-pink)"),
    ]
    lines = []
    for key, label, color in items:
        val = s.get(key, "—")
        lines.append(
            f'  <div class="terminal-stat" style="--stat-color: {color}">\n'
            f'    <span class="terminal-stat-num">{val}</span>\n'
            f'    <span class="terminal-stat-label">{label}</span>\n'
            f'  </div>'
        )
    return "\n".join(lines)


def build_instruments_html(data: dict) -> str:
    """Returns <tr> rows for the instruments table."""
    rows = []
    for inst in data.get("instruments", []):
        change = inst.get("change", 0)
        try:
            change_f = float(change)
        except (TypeError, ValueError):
            change_f = 0.0
        sign = "+" if change_f >= 0 else ""
        change_class = "change-up" if change_f >= 0 else "change-down"
        change_str = f"{sign}{change_f:.1f}%"
        sparkline = _sparkline_svg(inst.get("trend", []), change_f)
        rows.append(
            f'    <tr class="instrument-row">\n'
            f'      <td class="col-symbol">{inst.get("symbol", "")}</td>\n'
            f'      <td class="col-name">{inst.get("name", "")}</td>\n'
            f'      <td class="col-category">{inst.get("category", "")}</td>\n'
            f'      <td class="col-price">{inst.get("price", "")}¢</td>\n'
            f'      <td class="col-change {change_class}">{change_str}</td>\n'
            f'      <td class="col-volume">{inst.get("volume", "")}</td>\n'
            f'      <td class="col-oi">{inst.get("open_interest", "")}</td>\n'
            f'      <td class="col-sparkline">{sparkline}</td>\n'
            f'    </tr>'
        )
    return "\n\n".join(rows)


def build_orderbook_html(data: dict) -> str:
    ob = data.get("orderbook", {})
    bids = ob.get("bids", [])
    asks = ob.get("asks", [])

    # Find max total for bar widths
    all_totals = []
    for side in (bids, asks):
        for entry in side:
            t = entry.get("total", "$0").replace("$", "").replace(",", "")
            try:
                all_totals.append(float(t))
            except ValueError:
                pass
    max_total = max(all_totals) if all_totals else 1

    lines = ['  <div class="ob-side ob-asks">']
    lines.append('    <div class="ob-header">'
                 '<span>Price</span><span>Size</span><span>Total</span></div>')
    for ask in reversed(asks):
        t_str = ask.get("total", "$0").replace("$", "").replace(",", "")
        try:
            pct = min(float(t_str) / max_total * 100, 100)
        except ValueError:
            pct = 0
        lines.append(
            f'    <div class="ob-row ob-ask" style="--bar-pct: {pct:.1f}%">'
            f'<span class="ob-price-ask">{ask.get("price", "")}¢</span>'
            f'<span class="ob-size">{ask.get("size", "")}</span>'
            f'<span class="ob-total">{ask.get("total", "")}</span>'
            f'</div>'
        )
    lines.append('  </div>')

    lines.append('  <div class="ob-spread"></div>')

    lines.append('  <div class="ob-side ob-bids">')
    lines.append('    <div class="ob-header">'
                 '<span>Price</span><span>Size</span><span>Total</span></div>')
    for bid in bids:
        t_str = bid.get("total", "$0").replace("$", "").replace(",", "")
        try:
            pct = min(float(t_str) / max_total * 100, 100)
        except ValueError:
            pct = 0
        lines.append(
            f'    <div class="ob-row ob-bid" style="--bar-pct: {pct:.1f}%">'
            f'<span class="ob-price-bid">{bid.get("price", "")}¢</span>'
            f'<span class="ob-size">{bid.get("size", "")}</span>'
            f'<span class="ob-total">{bid.get("total", "")}</span>'
            f'</div>'
        )
    lines.append('  </div>')
    return "\n".join(lines)


def build_fills_html(data: dict) -> str:
    fills = data.get("recent_fills", [])
    rows = []
    for fill in fills:
        side = fill.get("side", "BUY")
        side_class = "fill-buy" if side == "BUY" else "fill-sell"
        rows.append(
            f'  <div class="fill-row">'
            f'<span class="fill-side {side_class}">{side}</span>'
            f'<span class="fill-price">{fill.get("price", "")}¢</span>'
            f'<span class="fill-size">{fill.get("size", "")}</span>'
            f'<span class="fill-time">{fill.get("time", "")}</span>'
            f'</div>'
        )
    return "\n".join(rows)


def build_chart_data(data: dict) -> str:
    """Returns just the JS array literal e.g. [67,65,68,...]"""
    points = data.get("featured", {}).get("chart_points", [])
    return "[" + ",".join(str(p) for p in points) + "]"


def build_featured_html(data: dict) -> str:
    f = data.get("featured", {})
    price = f.get("price", 50)
    change = f.get("change_24h", 0)
    try:
        change_f = float(change)
    except (TypeError, ValueError):
        change_f = 0.0
    sign = "+" if change_f >= 0 else ""
    change_class = "change-up" if change_f >= 0 else "change-down"
    no_price = 100 - int(price)
    return (
        f'  <div class="featured-symbol">{f.get("symbol", "")}</div>\n'
        f'  <div class="featured-name">{f.get("name", "")}</div>\n'
        f'  <div class="featured-meta">\n'
        f'    <span class="featured-category">{f.get("category", "")}</span>\n'
        f'    <span class="featured-price">{price}¢</span>\n'
        f'    <span class="featured-change {change_class}">{sign}{change_f:.1f}%</span>\n'
        f'  </div>\n'
        f'  <div class="featured-stats">\n'
        f'    <div class="featured-stat"><span class="fstat-num">{f.get("volume", "")}</span>'
        f'<span class="fstat-label">Volume</span></div>\n'
        f'    <div class="featured-stat"><span class="fstat-num">{f.get("high_24h", "")}¢</span>'
        f'<span class="fstat-label">24h High</span></div>\n'
        f'    <div class="featured-stat"><span class="fstat-num">{f.get("low_24h", "")}¢</span>'
        f'<span class="fstat-label">24h Low</span></div>\n'
        f'  </div>\n'
        f'  <div class="featured-actions">\n'
        f'    <button class="trade-btn trade-yes">BUY YES {price}¢</button>\n'
        f'    <button class="trade-btn trade-no">BUY NO {no_price}¢</button>\n'
        f'  </div>'
    )


def replace_section(content: str, tag: str, new_html: str) -> str:
    pattern = rf"<!-- GENX:{tag}:START -->.*?<!-- GENX:{tag}:END -->"
    replacement = f"<!-- GENX:{tag}:START -->\n{new_html}\n    <!-- GENX:{tag}:END -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def main():
    markets_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "web",
        "markets.html",
    )

    print("Calling Gemini for fresh markets data...")
    data = call_gemini(SYSTEM_PROMPT, USER_PROMPT)

    with open(markets_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_section(content, "MKTPAGE_STATUS",      build_status_html(data))
    content = replace_section(content, "MKTPAGE_FEATURED",    build_featured_html(data))
    content = replace_section(content, "MKTPAGE_CHARTDATA",   build_chart_data(data))
    content = replace_section(content, "MKTPAGE_INSTRUMENTS", build_instruments_html(data))
    content = replace_section(content, "MKTPAGE_ORDERBOOK",   build_orderbook_html(data))
    content = replace_section(content, "MKTPAGE_FILLS",       build_fills_html(data))

    with open(markets_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Markets page refreshed at {NOW_STR}")


if __name__ == "__main__":
    main()
