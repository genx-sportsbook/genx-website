# Simplify Genx-Sportsbook to a news/blog site

## Goal

The site currently pretends to be a working sports prediction market exchange (live ticker, fake order books, fake trading pages) around a core that's actually just AI-generated articles. Strip out everything that isn't the article/news content so the site honestly presents itself as what it is: a sports prediction market news & analysis blog.

## Scope

### Pages removed

Delete entirely:
- `web/markets.html`
- `web/sports.html`
- `web/live.html`

### Homepage (`web/index.html`) rebuilt

Keep:
- Header — logo + single `News` nav link + hamburger menu (mobile)
- Hero section, rewritten copy (no more "trade outcome shares" pitch):
  - Eyebrow: `// SPORTS PREDICTION MARKET INTEL //`
  - Title: `SHARP TAKES.` / `ZERO NOISE.`
  - Subtitle: "Daily analysis on sports prediction markets — the trends, the edges, and the stories behind the odds, from the Genx team."
- News/blog grid section — unchanged mechanically, still driven by the `GENX:NEWS_CARDS` marker, still links out to `news.html`
- Footer — logo + single `News` link + copyright line

Remove entirely (markup + associated CSS, not just hidden):
- Live ticker (`GENX:TICKER` section and `.ticker-wrap`/`.ticker-item`/`@keyframes ticker` styles)
- "Active Contracts" trading grid (`GENX:MARKETS` section and `.markets-grid`/`.market-card`/`.prob-bar`/`.option-btn` styles)
- Sports-icon showcase section and `.sports-showcase`/`.sport-icon-*` styles
- Leaderboard CSS (`.leaderboard-wrap` and related — already unused in current markup, dead code)
- Email-capture CTA section (`.cta-section`/`.email-form` and related styles)
- The inline `<script>` block that only exists to drive the market-card option buttons and prob-bar scroll animation

Update `<title>` and meta description to drop "Trade outcome shares" framing.

### Site-wide nav/footer cleanup

`web/news.html` and all files in `web/articles/*.html` currently link to `../markets.html`, `../sports.html`, `../live.html` in both header nav and footer. Strip these down to just a `News` link (home is reachable via the logo), consistently with the new homepage header/footer.

### Generator scripts updated to match

- `scripts/generate_article.py` — update the embedded article-page nav/footer template so all future article pages generate with the simplified nav.
- `scripts/generate_news_index.py` — update the embedded `news.html` header/footer template, then re-run the script to regenerate `web/news.html` from the real article set (rather than hand-editing the generated file).

### Dead automation removed

These scripts/workflows exist only to generate content for the pages being deleted, so they become fully dead once those pages are gone:

- Delete `scripts/generate_markets.py`
- Delete `scripts/generate_live.py`
- Delete `scripts/refresh_homepage.py` (its only job was populating the ticker/markets sections on `index.html` and the stats bar on `markets.html`, all removed)
- Delete `.github/workflows/daily-pages.yml`
- Delete `.github/workflows/refresh-homepage.yml`
- Trim `.github/workflows/daily-content.yml` down to: generate article → regenerate news index → commit. Remove the "Refresh homepage content", "Refresh markets page", and "Refresh live feed page" steps.

Out of scope / left alone:
- `.github/workflows/daily-article.yml` and `.github/workflows/deploy-pages.yml` — unaffected by this change, no edits needed.
- Two orphaned PNGs in `web/` (`17d5db07-1e42-41f2-8645-9c4f714d0b25.png`, `fb4ca946-26e1-419c-a46f-d4a598d95761.png`) — not referenced anywhere in the site; pre-existing cruft unrelated to this change, not touched.

### `CLAUDE.md` updated

Update the architecture tree, GENX marker table, and GitHub Actions section to reflect the new reality: no markets/sports/live pages, no `generate_markets.py`/`generate_live.py`/`refresh_homepage.py`, no `daily-pages.yml`/`refresh-homepage.yml`. Update the "Header pattern" and "Nav items" sections to reflect the single `News` nav link.

## Verification

- Every internal link across `index.html`, `news.html`, and all article pages resolves to an existing file (no dangling links to the deleted pages).
- `scripts/generate_news_index.py` runs cleanly and regenerates `web/news.html` matching the new template.
- `scripts/generate_article.py` still runs and produces an article page with the simplified nav (can be verified by inspecting its template output or a dry run).
- Visual check of `index.html` in a browser: hero renders, news grid renders and links work, no leftover empty sections/whitespace where removed sections used to be, mobile nav still toggles correctly.
