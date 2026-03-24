# Skill: World Happenings

## What This Is
Daily global news digest covering conflict, economy, climate, and health. Built for Wally and general news followers who want a clear picture of the world without editorial spin.

## Audience & Tone
People who want to know what's happening in the world without wading through opinion pieces. Clear, factual, no spin. Report events, provide context, skip the hot takes. If there's ambiguity, say so rather than picking a side.

## Research Sources

### RSS Feeds
- **BBC World** (5 items): `https://feeds.bbci.co.uk/news/world/rss.xml`
- **BBC US** (5 items): `https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml`
- **NPR News** (5 items): `https://feeds.npr.org/1001/rss.xml`
- **NY Times** (5 items): `https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml`

### Gemini Search Sections
- **conflict**: wars, armed conflict, military operations, geopolitics
- **economy**: global economy, trade, tariffs, inflation, central bank decisions
- **climate**: climate change, extreme weather, environmental news
- **health**: global health, pandemics, disease outbreaks, WHO news

## Build Process
1. Run research: `python3 ~/newsletters/lib/research.py world-happenings`
2. Run build: `python3 ~/newsletters/lib/build.py world-happenings`
3. Publish: `python3 ~/newsletters/lib/publish.py world-happenings`
   Or combined: `~/newsletters/scripts/build-and-publish.sh world-happenings`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/world-happenings-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/world-happenings-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/world-happenings/

## Delivery
- Telegram group: `-5283070369`
- Schedule: research at 4:00am ET, build at 7:00am ET

## Content Rules
1. **Factual only.** No editorial commentary, no "what this means for you" framing. Stick to what happened, who was involved, and verified consequences.
2. **All 4 Gemini sections must be represented.** If a section genuinely has no news today (rare for conflict/economy), note it briefly rather than forcing filler content.
3. **Attribute sources.** Every claim should trace back to a named source. "Reports say" is not good enough. "Reuters reports" is.
4. **No US-centric bias.** This is a world newsletter. US news belongs only if it has global implications. Domestic US politics without international impact goes elsewhere.
5. **Date-check strictly.** Only today's and yesterday's news. Global events move fast; a 3-day-old story is stale.

## Troubleshooting
- **NYT RSS paywall content**: The feed includes paywalled articles. Summaries from the RSS description are usually sufficient; don't try to fetch full article text.
- **Gemini conflict section too broad**: "Geopolitics" can return anything. If results are too scattered, the prompt's `covered_summary` should help focus on gaps. Review for relevance before including.
- **BBC feeds return duplicate items**: BBC World and BBC US overlap on US-related global stories. Dedup during build.
- **Empty sections**: If health or climate returns nothing meaningful from Gemini, check if the search grounding is working. Sometimes rephrasing the date context helps.
