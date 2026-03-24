# Skill: Mandy Intel

## What This Is
Daily pop culture and celebrity news digest built specifically for Mandy. Reality TV, music, film, celebrity gossip, served with Gen Z energy and a neobrutalism visual identity.

## Audience & Tone
**Audience**: Mandy. One person. This newsletter is a gift, curated for her interests. Think of it as a personalized morning briefing from a friend who stays on top of pop culture.

**Tone**: Gen Z energy, fun, opinionated. Not dry news reporting. React to the stories. "Not them doing THIS" energy. Short punchy summaries with personality. But never mean-spirited or cruel.

## Research Sources

### RSS Feeds
- **Page Six** (5 items): `https://pagesix.com/feed/`
- **TMZ** (5 items): `https://www.tmz.com/rss.xml`
- **HollywoodLife** (5 items): `https://www.hollywoodlife.com/feed/`
- **E! Online** (5 items): `https://www.eonline.com/syndication/feeds/rssfeeds/topstories.xml`

### Skip Terms (filtered out during research)
- "meghan markle"
- "prince harry"
- "rape"
- "sexual assault"
- "child abuse"
- "molestation"
- "sex crime"
- "shooting suspect"

### Gemini Search Sections
- **reality_tv**: Real Housewives, Bravo shows, Bachelor/Bachelorette drama, Love Island
- **music_film**: new album/song releases, movie news, award shows, box office

## Build Process
1. Run research: `python3 ~/newsletters/lib/research.py mandy-intel`
2. Run build: `python3 ~/newsletters/lib/build.py mandy-intel`
3. Publish: `python3 ~/newsletters/lib/publish.py mandy-intel`
   Or combined: `~/newsletters/scripts/build-and-publish.sh mandy-intel`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/mandy-intel-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/mandy-intel-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/mandy-intel/

## Delivery
- Telegram group: `-1003710768958`
- Schedule: research at 4:00am ET, build at 7:15am ET

## Design
Bento grid layout, neobrutalism aesthetic. Colors: hot pink, lime, blue. Font: Bricolage Grotesque. Bold borders, chunky cards, high contrast. This is not a corporate newsletter.

## Content Rules
1. **Skip terms are non-negotiable.** Meghan Markle/Prince Harry content and anything involving violent crime or sexual assault must be filtered out. This is a fun newsletter; those topics don't belong here.
2. **Reality TV is a priority section.** Mandy follows Bravo and reality shows closely. If there's Real Housewives drama, it leads. The Gemini prompt specifically targets this because RSS celebrity feeds undercover reality TV.
3. **Keep it light.** If a celebrity story is genuinely dark (serious legal issues, health crises), either skip it or handle it with appropriate sensitivity. The vibe is "morning gossip with a friend," not tabloid exploitation.
4. **No Meghan Markle.** Explicitly excluded in the Gemini prompt. Double-check RSS results too, since Page Six and TMZ love covering the royals.
5. **Gen Z voice, not parody.** The tone should feel natural, not like a millennial's impression of Gen Z. If it reads like "fellow kids," rewrite it.

## Troubleshooting
- **TMZ feed overloads with crime/legal content**: The skip_terms should catch the worst of it, but TMZ covers a lot of arrests and legal drama. Manual review of the research output may be needed.
- **E! Online feed format changes**: This feed has changed URLs before. If it returns empty, check `https://www.eonline.com/rss` for the current feed path.
- **Reality TV coverage thin**: RSS celebrity feeds are weak on reality TV. The Gemini reality_tv section is specifically designed to fill this gap. If Gemini returns nothing, the section will be sparse.
- **Design rendering issues**: The neobrutalism design uses custom fonts (Bricolage Grotesque) loaded from Google Fonts. If the published page looks wrong, check that the font CDN link is intact in the HTML template.
