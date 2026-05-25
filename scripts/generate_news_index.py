#!/usr/bin/env python3
"""
Scans web/articles/ for HTML files, extracts metadata from each article,
and writes a complete web/news.html news index page.

No Gemini required — pure file scanning and HTML generation.
"""

import os
import re
from datetime import date, datetime

TODAY = date.today()
DATE_STR = TODAY.strftime("%-d %B %Y")

CATEGORY_COLORS = {
    "Market Analysis":    "var(--neon-purple)",
    "Sports Intelligence":"var(--neon-pink)",
    "Platform Update":    "var(--neon-green)",
    "Market Intelligence":"var(--neon-cyan)",
    "Industry Insight":   "var(--neon-yellow)",
}


def parse_date(date_str: str) -> datetime:
    """Parse article date string, trying both %-d and %d formats."""
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, "%-d %B %Y")
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str, "%d %B %Y")
    except ValueError:
        pass
    # Last-resort fallback
    return datetime.min


def strip_tags(html: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", html).strip()


def extract_article_meta(filepath: str, filename: str) -> dict | None:
    """Extract metadata from an article HTML file. Returns None on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    # Title
    m = re.search(r"<title>(.*?) \| Genx-Sportsbook</title>", content)
    title = m.group(1).strip() if m else filename

    # Category
    m = re.search(r'<span class="article-category">(.*?)</span>', content)
    category = m.group(1).strip() if m else "Industry Insight"

    # Date
    m = re.search(r'<span class="article-date">(.*?)</span>', content)
    date_str = m.group(1).strip() if m else ""
    parsed_date = parse_date(date_str) if date_str else datetime.min

    # Excerpt / deck
    m = re.search(r'<p class="article-deck">(.*?)</p>', content, re.DOTALL)
    excerpt = strip_tags(m.group(1)) if m else ""
    # Trim to a reasonable preview length
    if len(excerpt) > 220:
        excerpt = excerpt[:217].rstrip() + "..."

    return {
        "filename": filename,
        "title": title,
        "category": category,
        "date_str": date_str,
        "date": parsed_date,
        "excerpt": excerpt,
    }


def build_article_card(article: dict) -> str:
    color = CATEGORY_COLORS.get(article["category"], "var(--neon-cyan)")
    return (
        f'    <article class="blog-card" style="--card-color: {color}">\n'
        f'      <div class="blog-category">{article["category"]}</div>\n'
        f'      <div class="blog-date">{article["date_str"]}</div>\n'
        f'      <h3 class="blog-title">{article["title"]}</h3>\n'
        f'      <p class="blog-excerpt">{article["excerpt"]}</p>\n'
        f'      <a href="articles/{article["filename"]}" class="blog-read-more">Read more</a>\n'
        f'    </article>'
    )


def build_news_html(articles: list) -> str:
    count = len(articles)
    count_label = f"{count} article{'s' if count != 1 else ''}"

    if articles:
        cards_html = "\n\n".join(build_article_card(a) for a in articles)
        grid_html = (
            f'  <div class="blog-grid">\n\n'
            f'{cards_html}\n\n'
            f'  </div>'
        )
    else:
        grid_html = (
            '  <div class="no-articles">\n'
            '    <p style="font-family:\'Share Tech Mono\',monospace;color:rgba(255,255,255,0.35);'
            'letter-spacing:0.15em;text-align:center;padding:4rem 0;">'
            '// No articles published yet. Check back soon. //</p>\n'
            '  </div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Latest Articles | Genx-Sportsbook</title>
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
  nav{{display:flex;gap:2rem;align-items:center;}}
  nav a{{font-family:'Share Tech Mono',monospace;font-size:0.85rem;color:rgba(255,255,255,0.7);text-decoration:none;letter-spacing:0.15em;text-transform:uppercase;transition:color 0.2s;}}
  nav a:hover{{color:var(--neon-cyan);text-shadow:0 0 8px var(--neon-cyan);}}
  nav a.active{{color:var(--neon-cyan);text-shadow:0 0 8px var(--neon-cyan);}}
  .cta-btn{{font-family:'Orbitron',monospace;font-weight:700;font-size:0.75rem;letter-spacing:0.15em;padding:0.6rem 1.4rem;background:transparent;border:2px solid var(--neon-pink);color:var(--neon-pink);cursor:pointer;text-transform:uppercase;text-decoration:none;transition:all 0.2s;clip-path:polygon(8px 0%,100% 0%,calc(100% - 8px) 100%,0% 100%);}}
  .cta-btn:hover{{background:var(--neon-pink);color:var(--dark-bg);box-shadow:0 0 20px var(--neon-pink);}}
  .page-hero{{padding:4rem 3rem 3rem;border-bottom:1px solid rgba(0,245,255,0.08);}}
  .section-tag{{font-family:'Share Tech Mono',monospace;font-size:0.75rem;letter-spacing:0.35em;color:var(--neon-pink);text-shadow:0 0 8px var(--neon-pink);text-transform:uppercase;margin-bottom:0.75rem;display:block;}}
  .page-title{{font-family:'Black Ops One',cursive;font-size:clamp(2.5rem,6vw,4.5rem);line-height:1;color:var(--neon-cyan);text-shadow:0 0 30px rgba(0,245,255,0.4);margin-bottom:1rem;}}
  .article-count{{font-family:'Share Tech Mono',monospace;font-size:0.8rem;letter-spacing:0.2em;color:rgba(255,255,255,0.35);text-transform:uppercase;}}
  .news-section{{padding:3rem 3rem 5rem;}}
  .blog-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5px;background:rgba(0,245,255,0.06);border:1px solid rgba(0,245,255,0.08);}}
  .blog-card{{background:var(--dark-bg);padding:2rem;position:relative;overflow:hidden;transition:background 0.2s;display:flex;flex-direction:column;}}
  .blog-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--card-color,var(--neon-cyan));box-shadow:0 0 10px var(--card-color,var(--neon-cyan));pointer-events:none;}}
  .blog-card:hover{{background:rgba(0,245,255,0.02);}}
  .blog-category{{font-family:'Share Tech Mono',monospace;font-size:0.65rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--card-color,var(--neon-cyan));text-shadow:0 0 6px var(--card-color,var(--neon-cyan));margin-bottom:0.75rem;}}
  .blog-date{{font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:rgba(255,255,255,0.3);letter-spacing:0.1em;margin-bottom:0.75rem;}}
  .blog-title{{font-family:'Black Ops One',cursive;font-size:1.2rem;line-height:1.2;color:rgba(255,255,255,0.95);margin-bottom:1rem;}}
  .blog-excerpt{{font-size:0.95rem;font-weight:300;line-height:1.65;color:rgba(255,255,255,0.55);flex:1;margin-bottom:1.5rem;}}
  .blog-read-more{{font-family:'Share Tech Mono',monospace;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--card-color,var(--neon-cyan));text-decoration:none;display:inline-flex;align-items:center;gap:0.4rem;transition:gap 0.2s,text-shadow 0.2s;position:relative;z-index:1;}}
  .blog-read-more::before{{content:'';position:absolute;inset:-999px;z-index:0;}}
  .blog-read-more:hover{{gap:0.8rem;text-shadow:0 0 8px var(--card-color,var(--neon-cyan));}}
  .blog-read-more::after{{content:'→';}}
  footer{{padding:2rem 3rem;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;}}
  .footer-logo{{font-family:'Black Ops One',cursive;font-size:1.3rem;color:var(--neon-cyan);text-shadow:0 0 10px var(--neon-cyan);}}
  .footer-copy{{font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:rgba(255,255,255,0.2);letter-spacing:0.1em;}}
  .footer-links{{display:flex;gap:2rem;}}
  .footer-links a{{font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:rgba(255,255,255,0.35);text-decoration:none;letter-spacing:0.1em;transition:color 0.2s;}}
  .footer-links a:hover{{color:var(--neon-cyan);}}
  @media(max-width:768px){{header{{padding:1rem 1.5rem;}}nav{{display:none;}}.page-hero,.news-section{{padding-left:1.5rem;padding-right:1.5rem;}}}}
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="scanlines"></div>
<div class="content">

<header>
  <a href="index.html" class="logo">GENX<span>SPORTSBOOK</span></a>
  <nav>
    <a href="markets.html">Markets</a>
    <a href="sports.html">Sports</a>
    <a href="live.html">Live</a>
    <a href="news.html" class="active">News</a>
    <a href="docs.html">Docs</a>
  </nav>
  <a href="index.html" class="cta-btn">Get Started</a>
</header>

<div class="page-hero">
  <span class="section-tag">// Insights //</span>
  <h1 class="page-title">LATEST ARTICLES</h1>
  <p class="article-count">// {count_label} published //</p>
</div>

<section class="news-section">
{grid_html}
</section>

<footer>
  <div class="footer-logo">GENX<span style="color:var(--neon-pink)">SPORTSBOOK</span></div>
  <div class="footer-links">
    <a href="markets.html">Markets</a>
    <a href="sports.html">Sports</a>
    <a href="live.html">Live</a>
    <a href="news.html">News</a>
    <a href="docs.html">Docs</a>
  </div>
  <div class="footer-copy">© 2026 GENX-SPORTSBOOK INC. ALL RIGHTS RESERVED</div>
</footer>

</div>
</body>
</html>
"""


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles_dir = os.path.join(base_dir, "web", "articles")
    news_path = os.path.join(base_dir, "web", "news.html")

    articles = []
    if os.path.isdir(articles_dir):
        for filename in os.listdir(articles_dir):
            if not filename.endswith(".html"):
                continue
            filepath = os.path.join(articles_dir, filename)
            meta = extract_article_meta(filepath, filename)
            if meta:
                articles.append(meta)

    # Sort by date descending (newest first)
    articles.sort(key=lambda a: a["date"], reverse=True)

    print(f"Found {len(articles)} article(s) in {articles_dir}")

    html = build_news_html(articles)
    with open(news_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"News index written to: {news_path}")


if __name__ == "__main__":
    main()
