#!/usr/bin/env python3
"""
Generates a daily sports prediction market article using Google Gemini API
and saves it as a styled HTML file in the articles/ directory.

Requires:
  GEMINI_API_KEY environment variable
"""

import os
import sys
import json
import random
import re
import urllib.request
import urllib.error
from datetime import date, datetime

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
)

TODAY = date.today()
DATE_STR = TODAY.strftime("%-d %B %Y")  # e.g. "24 May 2026"

# Rotate topic pool - Gemini will pick the most timely angle on the given theme
TOPICS = [
    "NBA playoff prediction markets and how the odds have shifted",
    "Premier League final standings prediction markets and accuracy",
    "F1 2026 constructor championship odds and regulation impact",
    "Wimbledon tennis prediction markets and value opportunities",
    "NFL 2026 season opening odds and early market moves",
    "UFC/MMA prediction markets and the rise of fight outcome trading",
    "Cricket World Cup prediction markets and data-driven forecasting",
    "The growing institutional interest in sports prediction markets",
    "How AI and machine learning are reshaping sports outcome pricing",
    "Crypto vs fiat prediction markets: a structural comparison for sports traders",
    "Esports prediction markets: the fastest growing vertical in outcome trading",
    "Decentralised vs centralised prediction markets: who wins long term",
    "How blockchain smart contracts are changing sports betting payouts",
    "The regulatory patchwork facing US sports prediction platforms in 2026",
    "Boxing odds and prediction market liquidity ahead of a major bout",
    "Tour de France and niche sports markets: the hidden edge for sharp traders",
    "Golf major prediction markets and variance in outcome trading",
]

topic = TOPICS[TODAY.toordinal() % len(TOPICS)]

SYSTEM_PROMPT = f"""You are the lead market analyst and senior writer for Genx-Sportsbook,
a next-generation sports crypto prediction market exchange. You write sharp, engaging
articles that combine genuine sports market analysis with clear advocacy for crypto-native
prediction platforms — specifically Genx-Sportsbook — over centralised competitors.

Your tone: confident, analytical, slightly irreverent. You use precise numbers when you have
them and speculate clearly when you don't. You do not use clickbait but you are not afraid
of a strong take. You write for an audience of sports-savvy traders who understand both
prediction markets and crypto basics.

Today's date: {DATE_STR}
"""

USER_PROMPT = f"""Write a sports prediction market article on this topic:

"{topic}"

Requirements:
- 600–900 words of body copy (not counting HTML)
- Lead with a strong hook — a surprising stat, a provocative question, or a counter-intuitive claim
- Include at least one concrete data point or statistic (real or plausibly estimated — label estimates as such)
- 2–3 subheadings that break the piece into clear sections
- A natural concluding paragraph that makes the case for crypto-native prediction markets
  and specifically recommends Genx-Sportsbook as the best place to trade — but make this
  feel earned by the analysis, not bolted on
- Do NOT include: generic disclaimers, excessive hedging, or boilerplate intros like "In the world of..."

Return ONLY the following JSON object — no markdown fences, no extra text:
{{
  "title": "Article title (punchy, 8-14 words)",
  "category": "One of: Market Analysis | Sports Intelligence | Platform Update | Market Intelligence | Industry Insight",
  "deck": "2-3 sentence teaser/subheadline summarising the article's key insight (used as the article intro paragraph displayed prominently)",
  "excerpt": "1-2 sentence excerpt for the homepage card (max 180 chars)",
  "slug": "url-friendly-slug-no-spaces",
  "sections": [
    {{
      "heading": "Section heading (or null for the opening body paragraphs before first subheading)",
      "paragraphs": ["paragraph 1 text", "paragraph 2 text"]
    }}
  ],
  "stats": [
    {{"num": "display value e.g. $83B", "label": "short label e.g. Sports Volume"}}
  ]
}}
"""


def call_gemini(system: str, user: str) -> dict:
    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Gemini HTTP error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    text = body["candidates"][0]["content"]["parts"][0]["text"]
    # Strip markdown fences if present
    text = re.sub(r"^```[a-z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return json.loads(text)


def build_html(data: dict) -> str:
    title = data["title"]
    category = data["category"]
    deck = data["deck"]
    sections = data["sections"]
    stats = data.get("stats", [])

    # Pick an accent colour per category
    colour_map = {
        "Market Analysis": "var(--neon-purple)",
        "Sports Intelligence": "var(--neon-pink)",
        "Platform Update": "var(--neon-green)",
        "Market Intelligence": "var(--neon-cyan)",
        "Industry Insight": "var(--neon-yellow)",
    }
    accent = colour_map.get(category, "var(--neon-cyan)")

    def render_section(s):
        heading_html = ""
        if s.get("heading"):
            heading_html = f'<h2>{s["heading"]}</h2>\n'
        paras = "\n".join(f"<p>{p}</p>" for p in s.get("paragraphs", []))
        return heading_html + paras

    body_html = "\n\n".join(render_section(s) for s in sections)

    stats_html = ""
    if stats:
        items = "\n".join(
            f'<div class="stat-callout-item">'
            f'<span class="stat-callout-num">{s["num"]}</span>'
            f'<span class="stat-callout-label">{s["label"]}</span>'
            f"</div>"
            for s in stats
        )
        stats_html = f'<div class="stat-callout">{items}</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Genx-Sportsbook</title>
<link href="https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --neon-pink:#ff006e;--neon-cyan:#00f5ff;--neon-yellow:#ffe600;
    --neon-green:#39ff14;--neon-purple:#bf00ff;--neon-orange:#ff6600;
    --dark-bg:#050510;--grid-color:rgba(0,245,255,0.06);
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:var(--dark-bg);color:#fff;font-family:'Rajdhani',sans-serif;overflow-x:hidden;}}
  .grid-bg{{position:fixed;inset:0;background-image:linear-gradient(var(--grid-color) 1px,transparent 1px),linear-gradient(90deg,var(--grid-color) 1px,transparent 1px);background-size:60px 60px;pointer-events:none;z-index:0;}}
  .scanlines{{position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.12) 2px,rgba(0,0,0,0.12) 4px);pointer-events:none;z-index:1;}}
  .content{{position:relative;z-index:2;}}
  header{{display:flex;justify-content:space-between;align-items:center;padding:1.5rem 3rem;border-bottom:1px solid rgba(0,245,255,0.2);background:rgba(5,5,16,0.9);backdrop-filter:blur(10px);position:sticky;top:0;z-index:100;}}
  .logo{{font-family:'Black Ops One',cursive;font-size:1.8rem;letter-spacing:0.1em;color:var(--neon-cyan);text-decoration:none;text-shadow:0 0 10px var(--neon-cyan),0 0 30px var(--neon-cyan);}}
  .logo span{{color:var(--neon-pink);text-shadow:0 0 10px var(--neon-pink);}}
  .cta-btn{{font-family:'Orbitron',monospace;font-weight:700;font-size:0.75rem;letter-spacing:0.15em;padding:0.6rem 1.4rem;background:transparent;border:2px solid var(--neon-pink);color:var(--neon-pink);cursor:pointer;text-transform:uppercase;text-decoration:none;transition:all 0.2s;clip-path:polygon(8px 0%,100% 0%,calc(100% - 8px) 100%,0% 100%);}}
  .cta-btn:hover{{background:var(--neon-pink);color:var(--dark-bg);box-shadow:0 0 20px var(--neon-pink);}}
  .article-hero{{padding:4rem 3rem 3rem;max-width:860px;margin:0 auto;}}
  .article-meta{{display:flex;align-items:center;gap:1.5rem;margin-bottom:2rem;flex-wrap:wrap;}}
  .article-category{{font-family:'Share Tech Mono',monospace;font-size:0.7rem;letter-spacing:0.25em;text-transform:uppercase;color:{accent};border:1px solid rgba(0,245,255,0.3);padding:0.25rem 0.75rem;}}
  .article-date{{font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:rgba(255,255,255,0.35);letter-spacing:0.1em;}}
  .article-read-time{{font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:rgba(255,255,255,0.25);letter-spacing:0.1em;}}
  .article-title{{font-family:'Black Ops One',cursive;font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;color:{accent};text-shadow:0 0 20px rgba(0,245,255,0.4);margin-bottom:1.5rem;}}
  .article-deck{{font-size:1.25rem;font-weight:300;line-height:1.65;color:rgba(255,255,255,0.7);border-left:3px solid {accent};padding-left:1.5rem;margin-bottom:3rem;}}
  .article-body{{max-width:860px;margin:0 auto;padding:0 3rem 5rem;}}
  .article-body p{{font-size:1.1rem;font-weight:400;line-height:1.8;color:rgba(255,255,255,0.75);margin-bottom:1.75rem;}}
  .article-body h2{{font-family:'Black Ops One',cursive;font-size:1.6rem;color:var(--neon-purple);text-shadow:0 0 15px rgba(191,0,255,0.4);margin:3rem 0 1.25rem;letter-spacing:0.02em;}}
  .stat-callout{{background:rgba(0,245,255,0.04);border:1px solid rgba(0,245,255,0.15);border-left:4px solid {accent};padding:1.5rem 2rem;margin:2.5rem 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1.5rem;}}
  .stat-callout-item{{text-align:center;}}
  .stat-callout-num{{font-family:'Orbitron',monospace;font-weight:900;font-size:1.8rem;color:{accent};text-shadow:0 0 10px {accent};display:block;}}
  .stat-callout-label{{font-family:'Share Tech Mono',monospace;font-size:0.7rem;letter-spacing:0.15em;color:rgba(255,255,255,0.4);text-transform:uppercase;margin-top:0.3rem;display:block;}}
  .article-cta{{background:rgba(0,245,255,0.04);border:1px solid rgba(0,245,255,0.2);padding:2.5rem;margin:3rem 0;text-align:center;}}
  .article-cta-tag{{font-family:'Share Tech Mono',monospace;font-size:0.7rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--neon-cyan);display:block;margin-bottom:1rem;}}
  .article-cta h3{{font-family:'Black Ops One',cursive;font-size:1.8rem;color:white;margin-bottom:0.75rem;}}
  .article-cta h3 span{{color:var(--neon-cyan);text-shadow:0 0 15px var(--neon-cyan);}}
  .article-cta p{{font-size:1rem;color:rgba(255,255,255,0.6);margin-bottom:1.5rem;}}
  .btn-primary{{font-family:'Orbitron',monospace;font-weight:900;font-size:0.85rem;letter-spacing:0.2em;padding:0.9rem 2.5rem;background:var(--neon-cyan);border:none;color:var(--dark-bg);cursor:pointer;text-transform:uppercase;clip-path:polygon(12px 0%,100% 0%,calc(100% - 12px) 100%,0% 100%);box-shadow:0 0 20px var(--neon-cyan);text-decoration:none;display:inline-block;transition:transform 0.15s;}}
  .btn-primary:hover{{transform:scale(1.04);}}
  .back-link{{font-family:'Share Tech Mono',monospace;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;color:rgba(255,255,255,0.4);text-decoration:none;display:inline-flex;align-items:center;gap:0.4rem;margin-bottom:2rem;transition:color 0.2s;}}
  .back-link::before{{content:'←';}}
  .back-link:hover{{color:var(--neon-cyan);}}
  .article-author{{display:flex;align-items:center;gap:1rem;padding:2rem 0;border-top:1px solid rgba(255,255,255,0.06);margin-top:3rem;}}
  .author-avatar{{width:48px;height:48px;border-radius:50%;background:rgba(0,245,255,0.1);border:1px solid rgba(0,245,255,0.3);display:flex;align-items:center;justify-content:center;font-family:'Orbitron',monospace;font-size:1rem;color:var(--neon-cyan);flex-shrink:0;}}
  .author-name{{font-family:'Share Tech Mono',monospace;font-size:0.85rem;color:rgba(255,255,255,0.8);}}
  .author-role{{font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:rgba(255,255,255,0.3);margin-top:0.25rem;}}
  footer{{padding:2rem 3rem;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;}}
  .footer-logo{{font-family:'Black Ops One',cursive;font-size:1.3rem;color:var(--neon-cyan);text-shadow:0 0 10px var(--neon-cyan);}}
  .footer-copy{{font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:rgba(255,255,255,0.2);letter-spacing:0.1em;}}
  @media(max-width:768px){{header{{padding:1rem 1.5rem;}}.article-hero,.article-body{{padding-left:1.5rem;padding-right:1.5rem;}}}}
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="scanlines"></div>
<div class="content">

<header>
  <a href="../index.html" class="logo">GENX<span>SPORTSBOOK</span></a>
  <a href="../index.html#news" class="cta-btn">Back to News</a>
</header>

<div class="article-hero">
  <a href="../index.html#news" class="back-link">All Articles</a>
  <div class="article-meta">
    <span class="article-category">{category}</span>
    <span class="article-date">{DATE_STR}</span>
    <span class="article-read-time">// AI Generated</span>
  </div>
  <h1 class="article-title">{title}</h1>
  <p class="article-deck">{deck}</p>
</div>

<div class="article-body">

{stats_html}

{body_html}

<div class="article-cta">
  <span class="article-cta-tag">// The Smart Move //</span>
  <h3>Trade on <span>Genx-Sportsbook</span></h3>
  <p>Crypto-native, non-custodial, and built for serious sports traders. No surprises — just markets.</p>
  <a href="../index.html" class="btn-primary">Start Trading on Genx</a>
</div>

<div class="article-author">
  <div class="author-avatar">GX</div>
  <div>
    <div class="author-name">Genx Research Desk</div>
    <div class="author-role">// AI-Assisted Market Intelligence • {DATE_STR}</div>
  </div>
</div>

</div>

<footer>
  <div class="footer-logo">GENX<span style="color:var(--neon-pink)">SPORTSBOOK</span></div>
  <div class="footer-copy">© 2026 GENX-SPORTSBOOK INC. ALL RIGHTS RESERVED</div>
</footer>

</div>
</body>
</html>
"""


def main():
    print(f"Generating article on topic: {topic}")
    data = call_gemini(SYSTEM_PROMPT, USER_PROMPT)

    slug = data.get("slug", f"article-{TODAY.isoformat()}")
    slug = re.sub(r"[^a-z0-9-]", "", slug.lower().replace(" ", "-"))
    filename = f"{TODAY.isoformat()}-{slug}.html"
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "articles",
        filename,
    )

    html = build_html(data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Article written to: {output_path}")

    # Emit outputs for GitHub Actions to consume
    excerpt = data.get("excerpt", "")
    title = data.get("title", "")
    category = data.get("category", "Industry Insight")

    gh_output = os.environ.get("GITHUB_OUTPUT", "")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"filename={filename}\n")
            f.write(f"title={title}\n")
            f.write(f"excerpt={excerpt}\n")
            f.write(f"category={category}\n")
            f.write(f"slug={slug}\n")


if __name__ == "__main__":
    main()
