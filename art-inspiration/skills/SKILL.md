# Skill: Art Inspiration

## What This Is
Daily creative fuel covering painting, creative process, tech-art, and UX/interface design. Built for the Art Inspiration group. Focused on actual art and design work, not AI tool reviews.

## Audience & Tone
Creatives, designers, and art enthusiasts looking for genuine inspiration. Visual, evocative, minimal text. Let the work speak. Descriptions should make people want to click through and see the art, not summarize it into irrelevance.

## Research Sources

### RSS Feeds
- **Hyperallergic** (4 items): `https://hyperallergic.com/rss/`
- **Colossal** (4 items): `https://www.thisiscolossal.com/feed/`
- **Creative Boom** (4 items): `https://www.creativeboom.com/feed/`
- **UX Collective** (4 items): `https://uxdesign.cc/feed`
- **Abduzeedo** (3 items): `https://abduzeedo.com/rss.xml`

### Skip Terms (filtered out during research)
- "best ai generator"
- "top 10 ai tools"
- "vs runway"
- "vs kling"
- "vs sora"
- "review 2026"
- "which ai is best"

### Gemini Search Sections
- **painting_studio**: working painters, artist spotlights, painting techniques, studio process, exhibition reviews
- **creative_mind**: how artists think, creative process essays, artist interviews, psychology of creativity
- **tech_art**: generative/computational art, creative coding, artistically interesting AI art (not tool reviews)
- **ux_interface**: notable UX/UI design work, interface patterns, design systems, typography in use

## Build Process
1. Run research: `python3 ~/newsletters/lib/research.py art-inspiration`
2. Run build: `python3 ~/newsletters/lib/build.py art-inspiration`
3. Publish: `python3 ~/newsletters/lib/publish.py art-inspiration`
   Or combined: `~/newsletters/scripts/build-and-publish.sh art-inspiration`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/art-inspiration-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/art-inspiration-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/art-inspiration/

## Delivery
- Telegram group: `-1003519302207`
- Schedule: research at 5:00am ET, build at 9:00am ET

## Content Rules
1. **No AI tool comparisons or reviews.** The skip_terms list exists for a reason. This newsletter is about art, not about which AI generator is "best." If a story is really about the tool and not the art, skip it.
2. **Actual art over art-adjacent content.** Prioritize artist spotlights, exhibitions, and creative process over industry news, auction prices, or market analysis.
3. **All 4 Gemini sections should feel distinct.** painting_studio is about physical practice; creative_mind is about the inner game; tech_art is where tech meets genuine artistic expression; ux_interface is applied design. Don't let them blur together.
4. **Visual-first presentation.** When the build generates HTML, the design should lead with imagery. Text descriptions are supporting context, not the main event.
5. **No listicles.** "Top 10 paintings" or "5 design trends" content is explicitly excluded in the Gemini prompt. Enforce this in the output too.

## Troubleshooting
- **UX Collective feed returns Medium paywall content**: RSS descriptions are usually enough. Don't attempt to scrape full articles behind the paywall.
- **Skip terms not filtering**: Check that the filter logic in `~/newsletters/lib/filter.py` is matching case-insensitively. The skip_terms are lowercase but article titles may not be.
- **Gemini returns tool-review content despite prompt instructions**: This happens. The build step should apply skip_terms as a second filter on Gemini results, not just RSS.
- **Abduzeedo feed is flaky**: This feed occasionally goes down or returns malformed XML. If it consistently fails, the other 4 feeds provide enough coverage.
