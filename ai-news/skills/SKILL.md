# Skill: AI News

## What This Is
Daily AI industry intelligence brief covering model releases, funding, research papers, policy, and trending GitHub repos. Built for Wally and anyone tracking the AI industry seriously.

## Audience & Tone
Tech-literate readers who want signal, not noise. Sharp, technical, no hype. Skip the breathless "AI will change everything" framing. Report what happened, why it matters, move on.

## Research Sources

### RSS Feeds
- **TechCrunch** (5 items): `https://techcrunch.com/feed/`
- **The Verge** (5 items): `https://www.theverge.com/rss/index.xml`
- **Ars Technica** (5 items): `https://feeds.arstechnica.com/arstechnica/technology-lab`
- **VentureBeat** (5 items): `https://feeds.feedburner.com/venturebeat/SZYF`
- **MIT Tech Review** (4 items): `https://www.technologyreview.com/feed/`

### Gemini Search Sections
- **model_releases**: new AI model launches, version releases, benchmark results
- **funding**: AI startup funding rounds, acquisitions, valuations
- **research_papers**: notable AI research papers or findings
- **ai_policy**: AI regulation, government policy, safety announcements

### Extras
- **GitHub Trending Repos**: scraped separately, presented as its own section

## Build Process
1. Run research: `python3 ~/newsletters/lib/research.py ai-news`
2. Run build: `python3 ~/newsletters/lib/build.py ai-news`
3. Publish: `python3 ~/newsletters/lib/publish.py ai-news`
   Or combined: `~/newsletters/scripts/build-and-publish.sh ai-news`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/ai-news-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/ai-news-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/ai-news/

## Delivery
- Telegram group: `-5108093721`
- Schedule: research at 4:00am ET, build at 7:00am ET

## Content Rules
1. **Never fabricate model benchmarks.** If you don't have a verified number, don't include one. "Reported improvements" is fine; fake MMLU scores are not.
2. **GitHub trending repos are their own section.** Don't mix them into the main news flow. Present them as a curated list with repo name, stars, and a one-line description.
3. **Deduplicate aggressively.** RSS feeds and Gemini sections will overlap. The research module uses `use_threads: true` and a covered_summary to reduce this, but verify the final output doesn't repeat stories.
4. **No PR rewrites.** If a story is just a company press release with no substance, skip it or note that it's unverified marketing.
5. **Date-check everything.** Only include stories from today or yesterday. Stale news kills credibility.

## Troubleshooting
- **RSS feed timeout**: TechCrunch and VentureBeat feeds are occasionally slow. The research module has built-in timeouts, but if a feed consistently fails, check if the URL has changed.
- **Gemini returns non-JSON**: The prompt explicitly asks for valid JSON only. If parsing fails, the research module should log the raw response. Check `~/.openclaw/workspace/tmp/` for partial output.
- **GitHub trending empty**: The scraper depends on GitHub's trending page HTML structure. If it returns nothing, the page layout may have changed. Check manually at `https://github.com/trending`.
- **Duplicate stories across sections**: The `covered_summary` in the Gemini prompt should prevent this, but if duplicates persist, the dedup logic in the build step may need tuning.
