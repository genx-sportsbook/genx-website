# Simplify Genx-Sportsbook to a News/Blog Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the fake trading UI (Markets/Sports/Live pages, live ticker, active-contracts grid, sports showcase, email-capture CTA) and the automation that feeds it, leaving Genx-Sportsbook as a straightforward sports-prediction-market news/blog site built around the generated articles.

**Architecture:** This is a static HTML/CSS site with no build pipeline, no package manager, and no test framework (per `CLAUDE.md`). There is no JS test runner to hook into — "tests" in this plan are verification steps: `grep` checks for dangling references, `python -m py_compile` for script syntax, running the pure-Python `generate_news_index.py` script (no API key needed) to confirm it regenerates correctly, and a manual browser check of the rebuilt homepage. Work proceeds file-by-file in dependency order: homepage first, then the article/news generator templates, then the already-generated article files, then dead automation, then documentation.

**Tech Stack:** Plain HTML/CSS (inline `<style>` blocks), Python 3 standard library only (`urllib`, `re`, `json`), GitHub Actions YAML.

## Global Constraints

- Git commits must use the repository owner identity (simonccc) — never a bot identity (per `CLAUDE.md` "Git commits" section). This applies to commits *we* make while executing this plan; it does not require touching the pre-existing bot identity used inside `daily-content.yml`'s own `git config` calls, which is out of scope for this plan.
- Nav items across the whole site become just `News` (home is reached via the logo) — no Markets/Sports/Live anywhere, in either header nav or footer links.
- Do not touch the two orphaned PNGs in `web/` — out of scope per the approved spec.
- Do not touch `.github/workflows/daily-article.yml` or `.github/workflows/deploy-pages.yml` — out of scope per the approved spec.
- Do not touch already-dead-but-unrelated CSS (`.features-grid`/`.feature-card`/`.btn-primary` in `web/index.html`) — not part of the approved removal list, leave as-is.

---

### Task 1: Rebuild the homepage and delete the trading pages

**Files:**
- Modify: `web/index.html` (full rewrite)
- Delete: `web/markets.html`
- Delete: `web/sports.html`
- Delete: `web/live.html`

**Interfaces:**
- Produces: the new `web/index.html` header/footer pattern (single `News` nav link) that Task 4 and Task 6 (CLAUDE.md) must describe consistently.

- [ ] **Step 1: Delete the three trading pages**

```bash
git rm web/markets.html web/sports.html web/live.html
```

- [ ] **Step 2: Rewrite `web/index.html`**

Replace the entire file with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4125667313511978" crossorigin="anonymous"></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Genx-Sportsbook — Sports Prediction Market News &amp; Analysis</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --neon-pink: #ff006e;
    --neon-cyan: #00f5ff;
    --neon-yellow: #ffe600;
    --neon-green: #39ff14;
    --neon-purple: #bf00ff;
    --neon-orange: #ff6600;
    --dark-bg: #050510;
    --grid-color: rgba(0, 245, 255, 0.06);
    --panel-bg: rgba(5, 5, 20, 0.85);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--dark-bg);
    color: #fff;
    font-family: 'Rajdhani', sans-serif;
    overflow-x: hidden;
  }

  /* GRID BACKGROUND */
  .grid-bg {
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(var(--grid-color) 1px, transparent 1px),
      linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
  }

  /* SCANLINES */
  .scanlines {
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.15) 2px,
      rgba(0,0,0,0.15) 4px
    );
    pointer-events: none;
    z-index: 1;
  }

  /* HORIZON GLOW */
  .horizon {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 300px;
    background: linear-gradient(to top, rgba(191,0,255,0.15), transparent);
    pointer-events: none;
    z-index: 0;
  }

  .content { position: relative; z-index: 2; }

  /* ─── HEADER ─── */
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 3rem;
    border-bottom: 1px solid rgba(0,245,255,0.2);
    background: rgba(5,5,16,0.9);
    backdrop-filter: blur(10px);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .logo {
    font-family: 'Black Ops One', cursive;
    font-size: 1.5rem;
    color: var(--neon-cyan);
    text-decoration: none;
    letter-spacing: 0.05em;
  }

  nav { display: flex; gap: 2rem; align-items: center; }
  nav a {
    font-family: 'Orbitron', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.55);
    text-decoration: none;
    text-transform: uppercase;
    transition: color 0.2s;
  }
  nav a:hover { color: #fff; }
  nav a.active { color: var(--neon-cyan); }

  .cta-btn {
    font-family: 'Orbitron', monospace;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    padding: 0.6rem 1.4rem;
    background: transparent;
    border: 2px solid var(--neon-pink);
    color:var(--neon-pink);
    cursor: pointer;
    text-transform: uppercase;
    text-decoration: none;
    transition: all 0.2s;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
  }
  .cta-btn:hover {
    background: var(--neon-pink);
    color: var(--dark-bg);
    box-shadow: 0 0 20px var(--neon-pink), 0 0 40px rgba(255,0,110,0.4);
  }

  /* ─── HERO ─── */
  .hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2.5rem 2rem 3rem;
    position: relative;
    overflow: hidden;
  }

  /* Neon grid floor */
  .grid-floor {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200px;
    overflow: hidden;
  }
  .grid-floor svg { width: 100%; height: 100%; }

  .hero-eyebrow {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    letter-spacing: 0.3em;
    color: var(--neon-cyan);
    text-shadow: 0 0 10px var(--neon-cyan);
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    animation: flicker 4s infinite;
  }

  @keyframes flicker {
    0%, 96%, 100% { opacity: 1; }
    97% { opacity: 0.6; }
    98% { opacity: 1; }
    99% { opacity: 0.4; }
  }

  .hero-title {
    font-family: 'Black Ops One', cursive;
    font-size: clamp(3.5rem, 10vw, 8rem);
    line-height: 0.9;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
  }

  .hero-title .line1 {
    display: block;
    color: var(--neon-cyan);
  }

  .hero-title .line2 {
    display: block;
    color: var(--neon-pink);
  }

  .hero-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 300;
    font-size: clamp(1rem, 2.5vw, 1.4rem);
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.8);
    max-width: 600px;
    line-height: 1.6;
    margin-bottom: 3rem;
  }

  /* ─── SECTION HEADERS ─── */
  .section { padding: 5rem 3rem; }

  .section-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.35em;
    color:var(--neon-pink);
    text-shadow: 0 0 8px var(--neon-pink);
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    display: block;
  }

  .section-title {
    font-family: 'Black Ops One', cursive;
    font-size: clamp(2rem, 5vw, 3.5rem);
    line-height: 1;
    margin-bottom: 1.5rem;
  }

  /* ─── BLOG / NEWS SECTION ─── */
  .blog-section { background: rgba(0,0,0,0.2); }

  .blog-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5px;
    margin-top: 3rem;
    background: rgba(0,245,255,0.06);
    border: 1px solid rgba(0,245,255,0.08);
  }

  .blog-card {
    background: var(--dark-bg);
    padding: 2rem;
    position: relative;
    overflow: hidden;
    transition: background 0.2s;
    display: flex;
    flex-direction: column;
  }

  .blog-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--card-color, var(--neon-cyan));
    box-shadow: 0 0 10px var(--card-color, var(--neon-cyan));
    pointer-events: none;
  }

  .blog-card:hover { background: rgba(0,245,255,0.02); }

  .blog-category {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--card-color, var(--neon-cyan));
    text-shadow: 0 0 6px var(--card-color, var(--neon-cyan));
    margin-bottom: 0.75rem;
  }

  .blog-date {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
  }

  .blog-title {
    font-family: 'Black Ops One', cursive;
    font-size: 1.2rem;
    line-height: 1.2;
    color: rgba(255,255,255,0.95);
    margin-bottom: 1rem;
  }

  .blog-excerpt {
    font-size: 0.95rem;
    font-weight: 300;
    line-height: 1.65;
    color: rgba(255,255,255,0.55);
    flex: 1;
    margin-bottom: 1.5rem;
  }

  .blog-read-more {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--card-color, var(--neon-cyan));
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: gap 0.2s, text-shadow 0.2s;
    position: relative;
    z-index: 1;
  }

  /* Stretch the link to cover the whole card so clicking anywhere navigates */
  .blog-read-more::before {
    content: '';
    position: absolute;
    inset: -999px;
    z-index: 0;
  }

  .blog-read-more:hover {
    gap: 0.8rem;
    text-shadow: 0 0 8px var(--card-color, var(--neon-cyan));
  }

  .blog-read-more::after { content: '→'; }

  .blog-view-all {
    display: flex;
    justify-content: center;
    margin-top: 2.5rem;
  }

  /* ─── FOOTER ─── */
  footer {
    padding: 2rem 3rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    background: var(--dark-bg);
    position: relative;
    z-index: 2;
  }

  .footer-logo {
    font-family: 'Black Ops One', cursive;
    font-size: 1.3rem;
    color: var(--neon-cyan);
  }

  .footer-links { display: flex; gap: 2rem; }
  .footer-links a {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.35);
    text-decoration: none;
    letter-spacing: 0.1em;
    transition: color 0.2s;
  }
  .footer-links a:hover { color: var(--neon-cyan); }

  .footer-copy {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: rgba(255,255,255,0.2);
    letter-spacing: 0.1em;
  }

  /* BLINKING CURSOR */
  .blink { animation: blink 1s step-end infinite; }
  @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

  /* HAMBURGER */
  .menu-btn {
    display: none;
    background: none;
    border: 1px solid rgba(0,245,255,0.3);
    color: var(--neon-cyan);
    font-size: 1.2rem;
    width: 36px;
    height: 36px;
    cursor: pointer;
    line-height: 1;
    flex-shrink: 0;
  }

  /* RESPONSIVE */
  @media (max-width: 768px) {
    header { padding: 1rem 1.5rem; }
    .menu-btn { display: flex; align-items: center; justify-content: center; }
    nav {
      display: none;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      flex-direction: column;
      background: rgba(5,5,16,0.97);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid rgba(0,245,255,0.2);
      padding: 0.5rem 0;
      gap: 0;
      z-index: 200;
    }
    nav.open { display: flex; }
    nav a { padding: 0.85rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.04); width: 100%; box-sizing: border-box; }
    nav a:last-child { border-bottom: none; }
    .hero { padding: 2rem 1.5rem 2.5rem; }
    .hero-subtitle { font-size: 1rem; }
    .section { padding: 3rem 1.5rem; }
    .blog-grid { grid-template-columns: 1fr; }
    footer { flex-direction: column; align-items: center; text-align: center; }
    .footer-links { flex-wrap: wrap; justify-content: center; gap: 1rem; }
  }
</style>
</head>
<body>

<div class="grid-bg"></div>
<div class="scanlines"></div>
<div class="horizon"></div>

<div class="content">

<!-- HEADER -->
<header>
  <a href="index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav>
    <a href="news.html">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>

<!-- HERO -->
<section class="hero">

  <!-- Neon grid floor -->
  <div class="grid-floor">
    <svg viewBox="0 0 1400 200" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="gridFade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(0,245,255,0.6)"/>
          <stop offset="100%" stop-color="rgba(0,245,255,0.05)"/>
        </linearGradient>
      </defs>
      <line x1="0" y1="200" x2="1400" y2="200" stroke="url(#gridFade)" stroke-width="1"/>
      <line x1="0" y1="160" x2="1400" y2="160" stroke="rgba(0,245,255,0.3)" stroke-width="0.7"/>
      <line x1="0" y1="120" x2="1400" y2="120" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="0" y1="80" x2="1400" y2="80" stroke="rgba(0,245,255,0.12)" stroke-width="0.4"/>
      <line x1="0" y1="40" x2="1400" y2="40" stroke="rgba(0,245,255,0.06)" stroke-width="0.3"/>
      <line x1="700" y1="0" x2="0" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="140" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="280" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="420" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="560" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="700" y2="200" stroke="rgba(0,245,255,0.3)" stroke-width="0.7"/>
      <line x1="700" y1="0" x2="840" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="980" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="1120" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="1260" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
      <line x1="700" y1="0" x2="1400" y2="200" stroke="rgba(0,245,255,0.2)" stroke-width="0.5"/>
    </svg>
  </div>

  <span class="hero-eyebrow">// Sports Prediction Market Intel //</span>

  <h1 class="hero-title">
    <span class="line1">SHARP TAKES.</span>
    <span class="line2">ZERO NOISE.</span>
  </h1>

  <p class="hero-subtitle">
    Daily analysis on sports prediction markets — the trends, the edges, and the stories
    behind the odds, from the Genx team.<span class="blink">_</span>
  </p>

</section>

<!-- NEWS & BLOG SECTION -->
<section class="section blog-section" id="news">
  <span class="section-tag">// Insights //</span>
  <h2 class="section-title" style="color: var(--neon-cyan); text-shadow: 0 0 30px rgba(0,245,255,0.4);">LATEST NEWS</h2>
  <p style="color: rgba(255,255,255,0.5); font-size: 1rem; max-width: 600px; line-height: 1.6;">Analysis, platform updates, and sports market insights from the Genx team.</p>

  <div class="blog-grid">
    <!-- GENX:NEWS_CARDS:START -->
    <article class="blog-card" style="--card-color: var(--neon-purple)">
      <div class="blog-category">Market Analysis</div>
      <div class="blog-date">21 June 2026</div>
      <h3 class="blog-title">Golf Majors: Where the Odds Break and Variance Reigns Supreme</h3>
      <p class="blog-excerpt">The Open Championship just wrapped, and if you traded the outright winner market, you likely felt the burn of golf's inherent unpredictability. This isn't just about a 'bad beat' — it's a fundamental characteristic of...</p>
      <a href="articles/2026-06-21-golf-majors-variance-outcome-trading.html" class="blog-read-more">Read more</a>
    </article>

    <article class="blog-card" style="--card-color: var(--neon-purple)">
      <div class="blog-category">Market Analysis</div>
      <div class="blog-date">19 June 2026</div>
      <h3 class="blog-title">Boxing's Billion-Dollar Bets: Why Liquidity is the Real Heavyweight</h3>
      <p class="blog-excerpt">The upcoming Fury-Usyk rematch is poised to break all previous betting records, but the real story isn't just about the money. It's about where that money flows and why traditional bookmakers are struggling to offer t...</p>
      <a href="articles/2026-06-19-boxing-liquidity-fury-usyk-rematch.html" class="blog-read-more">Read more</a>
    </article>

    <article class="blog-card" style="--card-color: var(--neon-purple)">
      <div class="blog-category">Market Analysis</div>
      <div class="blog-date">18 June 2026</div>
      <h3 class="blog-title">US Prediction Markets: Patchwork Purgatory & the Path to Profit</h3>
      <p class="blog-excerpt">The US sports prediction market landscape in 2026 is less a coherent market and more a regulatory minefield. State-by-state battles and fragmented interpretations of legality are stifling innovation and leaving trader...</p>
      <a href="articles/2026-06-18-us-prediction-market-regulatory-patchwork-2026.html" class="blog-read-more">Read more</a>
    </article>
    <!-- GENX:NEWS_CARDS:END -->
  </div>

  <div class="blog-view-all">
    <a href="news.html" class="cta-btn">View All Articles</a>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="footer-logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></div>
  <div class="footer-links">
    <a href="news.html">News</a>
  </div>
  <div class="footer-copy">© 2026 GENX-SPORTSBOOK INC. ALL RIGHTS RESERVED</div>
</footer>

</div>

</body>
</html>
```

- [ ] **Step 3: Verify no dangling references or leftover dead sections**

Run:
```bash
grep -n "markets.html\|sports.html\|live.html\|ticker-wrap\|markets-grid\|sports-showcase\|leaderboard-wrap\|cta-section\|email-form" web/index.html
```
Expected: no output (empty).

Run:
```bash
test ! -f web/markets.html && test ! -f web/sports.html && test ! -f web/live.html && echo "OK: pages removed"
```
Expected: `OK: pages removed`

- [ ] **Step 4: Commit**

```bash
git add web/index.html
git commit -m "feat: rebuild homepage as a news-focused site, remove trading pages"
```

---

### Task 2: Simplify the news-index generator template and regenerate `news.html`

**Files:**
- Modify: `scripts/generate_news_index.py:135-183` (nav) and `scripts/generate_news_index.py:196-206` (footer)
- Modify (generated): `web/news.html` (regenerated by running the script, not hand-edited)

**Interfaces:**
- Consumes: nothing new — same `build_news_html(articles)` signature as before.
- Produces: `web/news.html` matching the new single-`News`-link header/footer pattern, used by Task 7's verification sweep.

- [ ] **Step 1: Edit the nav block in the generated template**

In `scripts/generate_news_index.py`, find this block (around line 176-185):

```python
<header>
  <a href="index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav>
    <a href="markets.html">Markets</a>
    <a href="sports.html">Sports</a>
    <a href="live.html">Live</a>
    <a href="news.html" class="active">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>
```

Replace it with:

```python
<header>
  <a href="index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav>
    <a href="news.html" class="active">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>
```

- [ ] **Step 2: Edit the footer block in the generated template**

In the same file, find this block (around line 197-206):

```python
<footer>
  <div class="footer-logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></div>
  <div class="footer-links">
    <a href="markets.html">Markets</a>
    <a href="sports.html">Sports</a>
    <a href="live.html">Live</a>
    <a href="news.html">News</a>
  </div>
  <div class="footer-copy">© 2026 GENX-SPORTSBOOK INC. ALL RIGHTS RESERVED</div>
</footer>
```

Replace it with:

```python
<footer>
  <div class="footer-logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></div>
  <div class="footer-links">
    <a href="news.html">News</a>
  </div>
  <div class="footer-copy">© 2026 GENX-SPORTSBOOK INC. ALL RIGHTS RESERVED</div>
</footer>
```

- [ ] **Step 3: Syntax-check the script**

Run: `python3 -m py_compile scripts/generate_news_index.py`
Expected: no output, exit code 0.

- [ ] **Step 4: Run the script to regenerate `web/news.html`**

Run: `python3 scripts/generate_news_index.py`
Expected output: `Found 17 article(s) in .../web/articles` followed by `News index written to: .../web/news.html` and `Homepage news cards updated (3 articles)`.

Note: this will also rewrite the `GENX:NEWS_CARDS` block in `web/index.html` from the real article list — that's expected and correct (it replaces the placeholder snapshot written in Task 1 with the live top-3 articles).

- [ ] **Step 5: Verify the regenerated files have no dangling nav links**

Run:
```bash
grep -n "markets.html\|sports.html\|live.html" web/news.html web/index.html
```
Expected: no output (empty).

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_news_index.py web/news.html web/index.html
git commit -m "feat: simplify news-index nav/footer template and regenerate news.html"
```

---

### Task 3: Simplify the article-page generator template

**Files:**
- Modify: `scripts/generate_article.py:254-263` (nav) and `scripts/generate_article.py:299-302` (footer)

**Interfaces:**
- Produces: the article-page header/footer template used for every future generated article. Existing already-generated articles are handled separately in Task 4 (this script only affects articles generated from this point forward).

- [ ] **Step 1: Edit the nav block in `build_html()`**

Find this block (around line 254-263):

```python
<header>
  <a href="../index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav class="article-nav">
    <a href="../markets.html" style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;color:rgba(255,255,255,0.55);text-decoration:none;text-transform:uppercase;">Markets</a>
    <a href="../sports.html" style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;color:rgba(255,255,255,0.55);text-decoration:none;text-transform:uppercase;">Sports</a>
    <a href="../live.html" style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;color:rgba(255,255,255,0.55);text-decoration:none;text-transform:uppercase;">Live</a>
    <a href="../news.html" style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;color:rgba(255,255,255,0.55);text-decoration:none;text-transform:uppercase;">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>
```

Replace it with:

```python
<header>
  <a href="../index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav class="article-nav">
    <a href="../news.html" style="font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;color:rgba(255,255,255,0.55);text-decoration:none;text-transform:uppercase;">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>
```

- [ ] **Step 2: Verify no other footer nav links exist in the same template**

The article template's `<footer>` block (around line 299-302) already only contains the logo and copyright line, no Markets/Sports/Live links — confirm with:

```bash
sed -n '296,303p' scripts/generate_article.py
```
Expected: shows `<footer>`, `.footer-logo`, `.footer-copy`, `</footer>` only — no `<a href="../markets.html">` etc. If any such link is present, remove it the same way as Step 1.

- [ ] **Step 3: Syntax-check the script**

Run: `python3 -m py_compile scripts/generate_article.py`
Expected: no output, exit code 0.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_article.py
git commit -m "feat: simplify article-page nav template to a single News link"
```

---

### Task 4: Strip dead nav/footer links from the 17 existing article pages

**Files:**
- Modify: all 17 files in `web/articles/*.html`

**Interfaces:**
- Consumes: nothing from earlier tasks — this is a mechanical text substitution applied directly to already-generated static files (the Task 3 template change only affects articles generated from now on).

- [ ] **Step 1: Confirm every article file has the exact same nav/footer boilerplate**

Run:
```bash
grep -c 'href="../markets.html"' web/articles/*.html | awk -F: '{print $2}' | sort -u
grep -c 'href="../sports.html"' web/articles/*.html | awk -F: '{print $2}' | sort -u
grep -c 'href="../live.html"' web/articles/*.html | awk -F: '{print $2}' | sort -u
```
Expected: each command prints a single line `1`, confirming exactly one occurrence per file across all 17 files (i.e. the pattern is uniform, safe to bulk-replace).

- [ ] **Step 2: Bulk-remove the three `<a>` lines from every article file**

Run:
```bash
for f in web/articles/*.html; do
  grep -v 'href="\.\./markets\.html"\|href="\.\./sports\.html"\|href="\.\./live\.html"' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
```

- [ ] **Step 3: Verify the substitution worked and files are still well-formed**

Run:
```bash
grep -rl "markets.html\|sports.html\|live.html" web/articles/ ; echo "exit: $?"
```
Expected: no filenames printed, `exit: 1` (grep found nothing).

Run:
```bash
for f in web/articles/*.html; do
  grep -q '<nav class="article-nav">' "$f" && grep -q 'href="../news.html"' "$f" || echo "BROKEN: $f"
done
```
Expected: no `BROKEN:` lines — every article still has its nav and News link intact.

- [ ] **Step 4: Spot-check one file visually**

Run: `sed -n '253,262p' web/articles/2026-06-21-golf-majors-variance-outcome-trading.html`
Expected: shows `<nav class="article-nav">` immediately followed by a single `<a href="../news.html" ...>News</a>` line, then `</nav>`.

- [ ] **Step 5: Commit**

```bash
git add web/articles/
git commit -m "chore: strip dead Markets/Sports/Live nav links from existing article pages"
```

---

### Task 5: Remove dead automation (scripts + workflows)

**Files:**
- Delete: `scripts/generate_markets.py`
- Delete: `scripts/generate_live.py`
- Delete: `scripts/refresh_homepage.py`
- Delete: `.github/workflows/daily-pages.yml`
- Delete: `.github/workflows/refresh-homepage.yml`
- Modify: `.github/workflows/daily-content.yml`

**Interfaces:**
- None — this task only removes files/steps that fed the now-deleted pages/sections. Nothing downstream depends on these scripts.

- [ ] **Step 1: Delete the dead scripts**

```bash
git rm scripts/generate_markets.py scripts/generate_live.py scripts/refresh_homepage.py
```

- [ ] **Step 2: Delete the dead workflows**

```bash
git rm .github/workflows/daily-pages.yml .github/workflows/refresh-homepage.yml
```

- [ ] **Step 3: Trim `daily-content.yml` to article + news-index + commit**

Read the current file first:
```bash
cat .github/workflows/daily-content.yml
```

Replace its contents with:

```yaml
name: Daily Content Refresh

on:
  schedule:
    - cron: '0 1 * * *'  # 01:00 UTC every day
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Generate content but do not commit (true/false)'
        required: false
        default: 'false'

permissions:
  contents: write

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # 1. Generate today's article
      - name: Generate daily article
        id: article
        timeout-minutes: 15
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python scripts/generate_article.py

      # 2. Rebuild news index (now includes today's new article)
      - name: Rebuild news index
        run: python scripts/generate_news_index.py

      # 3. Commit everything in one go
      - name: Commit and push
        if: ${{ github.event.inputs.dry_run != 'true' }}
        run: |
          git config user.name  "Genx Content Bot"
          git config user.email "bot@genx-sportsbook.io"
          git add web/
          git diff --cached --quiet && echo "No changes to commit" && exit 0
          git commit -m "chore: daily content refresh — ${{ steps.article.outputs.title || 'homepage + pages' }}"
          git push
```

Use the Edit tool to perform this full-file replacement on `.github/workflows/daily-content.yml`.

- [ ] **Step 4: Verify the workflow YAML has no references to deleted scripts**

Run:
```bash
grep -n "generate_markets.py\|generate_live.py\|refresh_homepage.py" .github/workflows/daily-content.yml
```
Expected: no output (empty).

- [ ] **Step 5: Verify no remaining workflow references the deleted scripts/workflows**

Run:
```bash
grep -rl "generate_markets.py\|generate_live.py\|refresh_homepage.py" .github/workflows/ scripts/ web/ 2>/dev/null
```
Expected: no output (empty).

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/daily-content.yml
git commit -m "chore: remove dead markets/live/homepage-refresh automation"
```

---

### Task 6: Update `CLAUDE.md` to describe the simplified architecture

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- None — documentation only.

- [ ] **Step 1: Update the architecture file tree**

Find this block near the top of `CLAUDE.md`:

```
web/                        # Web root deployed to GitHub Pages
  index.html                # Homepage
  markets.html              # Trading page (chart, order book, active contracts)
  sports.html               # Sports browser
  live.html                 # Live trade feed
  news.html                 # News index (regenerated by generate_news_index.py)
  articles/                 # AI-generated article pages
    *.html
scripts/
  generate_article.py       # Gemini-powered article generator
  generate_news_index.py    # Regenerates news.html and updates index.html news cards
  refresh_homepage.py       # Updates dynamic GENX marker sections via Gemini
.github/workflows/
  daily-article.yml         # Runs daily at 08:00 UTC to generate + commit an article
  deploy-pages.yml          # Deploys web/ to GitHub Pages on push to main
```

Replace it with:

```
web/                        # Web root deployed to GitHub Pages
  index.html                # Homepage (hero + latest news grid)
  news.html                 # News index (regenerated by generate_news_index.py)
  articles/                 # AI-generated article pages
    *.html
scripts/
  generate_article.py       # Gemini-powered article generator
  generate_news_index.py    # Regenerates news.html and updates index.html news cards
.github/workflows/
  daily-content.yml         # Runs daily at 01:00 UTC: generate article, rebuild news index, commit
  daily-article.yml         # Manual-dispatch duplicate: generate article + rebuild news index
  deploy-pages.yml          # Deploys web/ to GitHub Pages on push to main
```

- [ ] **Step 2: Update the GENX marker table**

Find this block:

```
Key markers and where they live:
- `GENX:TICKER` — `web/index.html` (live ticker bar), written by `refresh_homepage.py`
- `GENX:MARKETS` — `web/index.html` (active contracts grid), written by `refresh_homepage.py`
- `GENX:STATS` — **`web/markets.html`** (stats bar), written by `refresh_homepage.py`
- `GENX:MKTPAGE_STATUS` — `web/markets.html` (status bar), written by `refresh_homepage.py`
- `GENX:MKTPAGE_FEATURED` — `web/markets.html` (featured market + BUY buttons), written by `refresh_homepage.py`
- `GENX:MKTPAGE_ORDERBOOK` — `web/markets.html`, written by `refresh_homepage.py`
- `GENX:MKTPAGE_INSTRUMENTS` — `web/markets.html` (active contracts table, 5 rows), written by `refresh_homepage.py`
- `GENX:LIVE_FEED` — `web/live.html` (trade feed, 5 items), written by a script
- `GENX:NEWS_CARDS` — `web/index.html`, written by `generate_news_index.py`
```

Replace it with:

```
Key markers and where they live:
- `GENX:NEWS_CARDS` — `web/index.html` (latest 3 articles), written by `generate_news_index.py`
```

- [ ] **Step 3: Update the "Running the scripts locally" section**

Find:

```bash
GEMINI_API_KEY=your_key python scripts/generate_article.py
GEMINI_API_KEY=your_key python scripts/generate_news_index.py
GEMINI_API_KEY=your_key python scripts/refresh_homepage.py
```

Replace it with:

```bash
GEMINI_API_KEY=your_key python scripts/generate_article.py
python scripts/generate_news_index.py   # no API key needed — pure file scanning
```

- [ ] **Step 4: Update the "Header pattern (all pages)" section**

Find:

```html
<header>
  <a href="index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav>
    <a href="markets.html">Markets</a>
    <a href="sports.html">Sports</a>
    <a href="live.html">Live</a>
    <a href="news.html">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>
```

Replace it with:

```html
<header>
  <a href="index.html" class="logo">GENX-<span style="color:var(--neon-pink)">SPORTSBOOK</span></a>
  <nav>
    <a href="news.html">News</a>
  </nav>
  <button class="menu-btn" onclick="this.previousElementSibling.classList.toggle('open')" aria-label="Open menu">☰</button>
</header>
```

Find the sentence directly below it:

```
Nav items are: **Markets, Sports, Live, News** — no Docs link. Article pages use `<nav class="article-nav">` with `../` relative hrefs and require both desktop styles (`nav.article-nav a { font-family: 'Orbitron'... }`) and a mobile dropdown in the `@media(max-width:768px)` block.
```

Replace it with:

```
Nav items are just **News** — home is reached via the logo, no Docs link. Article pages use `<nav class="article-nav">` with `../` relative hrefs and require both desktop styles (`nav.article-nav a { font-family: 'Orbitron'... }`) and a mobile dropdown in the `@media(max-width:768px)` block.
```

- [ ] **Step 5: Remove the "Markets page layout" section**

Find and delete this entire section (including its heading):

```
## Markets page layout

The trading area uses a 2-column CSS grid (`1fr 340px`). Left column (`.chart-panel`) is a flex column: the `.chart-area` div grows with `flex: 1` to fill vertical space, with the featured market details below it. The JS `resizeCanvases()` reads `area.clientHeight` to size the canvas drawing buffer. Right column (`.right-panel`) holds the order book.

Active Contracts table (`GENX:MKTPAGE_INSTRUMENTS`) displays **5 rows**. Live Trade Feed (`GENX:LIVE_FEED`) displays **5 items**.
```

- [ ] **Step 6: Update the GitHub Actions section**

Find:

```
## GitHub Actions

- **`daily-article.yml`** — triggers daily and also accepts `workflow_dispatch` with an optional `dry_run` input. Requires the `GEMINI_API_KEY` repository secret.
- **`deploy-pages.yml`** — deploys on push to `main` when files under `web/**` change, uploading the `web/` directory as the Pages artifact.
```

Replace it with:

```
## GitHub Actions

- **`daily-content.yml`** — runs on a schedule (01:00 UTC daily) and also accepts `workflow_dispatch` with an optional `dry_run` input: generates today's article, rebuilds the news index, and commits. Requires the `GEMINI_API_KEY` repository secret.
- **`daily-article.yml`** — manual-dispatch-only duplicate of the article + news-index steps above.
- **`deploy-pages.yml`** — deploys on push to `main` when files under `web/**` change, uploading the `web/` directory as the Pages artifact.
```

- [ ] **Step 7: Verify no remaining references to the removed pages/scripts**

Run:
```bash
grep -n "markets.html\|sports.html\|live.html\|generate_markets.py\|generate_live.py\|refresh_homepage.py\|daily-pages.yml\|refresh-homepage.yml" CLAUDE.md
```
Expected: no output (empty).

- [ ] **Step 8: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for the simplified news-site architecture"
```

---

### Task 7: Full-repo verification sweep

**Files:** none modified — verification only.

**Interfaces:** none.

- [ ] **Step 1: Confirm the three trading pages are gone and nothing references them**

Run:
```bash
test ! -e web/markets.html && test ! -e web/sports.html && test ! -e web/live.html && echo "OK: pages absent"
grep -rn "markets\.html\|sports\.html\|live\.html" web/ scripts/ .github/ CLAUDE.md 2>/dev/null
```
Expected: `OK: pages absent`, then no further output from the `grep` (empty — meaning zero remaining references anywhere in the repo).

- [ ] **Step 2: Confirm the dead scripts and workflows are gone**

Run:
```bash
test ! -e scripts/generate_markets.py && test ! -e scripts/generate_live.py && test ! -e scripts/refresh_homepage.py && echo "OK: scripts absent"
test ! -e .github/workflows/daily-pages.yml && test ! -e .github/workflows/refresh-homepage.yml && echo "OK: workflows absent"
```
Expected: both `OK:` lines printed.

- [ ] **Step 3: Syntax-check all remaining Python scripts**

Run:
```bash
python3 -m py_compile scripts/generate_article.py scripts/generate_news_index.py && echo "OK: scripts compile"
```
Expected: `OK: scripts compile`

- [ ] **Step 4: Re-run the news-index generator idempotency check**

Run: `python3 scripts/generate_news_index.py`
Expected: `Found 17 article(s)`, no errors, exit code 0 (confirms the script still runs cleanly end-to-end after all edits).

- [ ] **Step 5: Diff check — regenerating news.html twice in a row produces no further changes**

Run:
```bash
git diff --stat web/news.html web/index.html
```
Expected: no output (empty) — Task 2's regeneration already reflects the current article set, so re-running now is a no-op.

- [ ] **Step 6: Manual browser check**

Open `web/index.html` directly in a browser (e.g. `open web/index.html` on macOS or `xdg-open web/index.html` on Linux) and confirm:
- Hero renders with "SHARP TAKES. / ZERO NOISE." and no leftover empty whitespace where the ticker/markets/sports-showcase/CTA sections used to be
- The nav only shows "News", and clicking it goes to `news.html`
- The news grid renders 3 cards and "Read more" / "View All Articles" links work
- On a narrow viewport (or resizing the browser under ~768px), the hamburger menu opens/closes the single-item nav dropdown correctly
- Footer shows only the "News" link

Also open `web/news.html` and one article under `web/articles/` and confirm their nav/footer show only "News" with working links, and there are no broken links to `markets.html`/`sports.html`/`live.html`.

- [ ] **Step 7: Final commit (if any stray changes were made during verification)**

```bash
git status
```
If clean, no commit needed — this task is verification-only and should not have modified any tracked file. If `generate_news_index.py` was run again in Step 4/5 and produced a diff (it shouldn't, per Step 5's expectation), investigate why before committing anything.

---

## Post-plan follow-up (not in scope for this plan)

While reading `scripts/generate_article.py`, note that each article's `SYSTEM_PROMPT`/`USER_PROMPT` still instruct Gemini to write a closing paragraph pitching "Genx-Sportsbook" as the best place to trade, and `build_html()` renders a hardcoded `.article-cta` box ("Trade on Genx-Sportsbook" / "Start Trading on Genx" linking to `../index.html`) inside every article body. This wasn't part of the approved spec (which scoped nav/footer + homepage + dead automation only), but it's the same "fake trading pitch" pattern the rest of this plan removes — worth a follow-up spec if the user wants the article content itself to drop the trading pitch too.
