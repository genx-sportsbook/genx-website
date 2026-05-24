# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a static HTML/CSS website for **Genx-Sportsbook**, a sports crypto prediction market exchange. There is no build pipeline, no package manager, and no JavaScript framework.

```
web/                        # Web root deployed to GitHub Pages
  index.html                # Single-page homepage (all CSS inline)
  articles/                 # AI-generated article pages
    *.html
scripts/
  generate_article.py       # Gemini-powered article generator
.github/workflows/
  daily-article.yml         # Runs daily at 08:00 UTC to generate + commit an article
  deploy-pages.yml          # Deploys web/ to GitHub Pages on push to main
```

## Running the article generator locally

Requires `GEMINI_API_KEY` set in the environment. The script has no dependencies beyond the Python standard library.

```bash
GEMINI_API_KEY=your_key python scripts/generate_article.py
```

The script selects a topic deterministically based on `date.today().toordinal() % len(TOPICS)`, calls `gemini-1.5-flash`, and writes a self-contained HTML file.

The script resolves its output path as `web/articles/{filename}` (two `dirname` levels up from `scripts/`, then into `web/articles/`). When adding articles manually, place them in `web/articles/` and add the corresponding card to the `#news` blog grid in `web/index.html`.

## Design system

Both `index.html` and article pages share a retro-neon aesthetic defined entirely in inline `<style>` blocks (no external stylesheet). Key CSS variables:

```css
--neon-pink: #ff006e
--neon-cyan: #00f5ff
--neon-yellow: #ffe600
--neon-green: #39ff14
--neon-purple: #bf00ff
--neon-orange: #ff6600
--dark-bg: #050510
```

Fonts (loaded from Google Fonts): `Black Ops One` (headings), `Orbitron` (numbers/buttons), `Share Tech Mono` (labels/meta), `Rajdhani` (body copy).

Article pages use a per-category accent colour mapped in `build_html()` in `generate_article.py`.

## Article card format

To add a news card to `web/index.html`, insert an `<article class="blog-card">` element into the `<div class="blog-grid">` inside the `#news` section:

```html
<article class="blog-card" style="--card-color: var(--neon-cyan)">
  <div class="blog-category">Market Intelligence</div>
  <div class="blog-date">24 May 2026</div>
  <h3 class="blog-title">Article Title Here</h3>
  <p class="blog-excerpt">Short excerpt (max ~180 chars).</p>
  <a href="articles/filename.html" class="blog-read-more">Read more</a>
</article>
```

## GitHub Actions

- **`daily-article.yml`** — triggers daily and also accepts `workflow_dispatch` with an optional `dry_run` input. Requires the `GEMINI_API_KEY` repository secret.
- **`deploy-pages.yml`** — deploys on push to `main` when files under `web/**` change, uploading the `web/` directory as the Pages artifact.
