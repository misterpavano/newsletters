# Skill: NBA Bets

## What This Is
Daily NBA betting analysis with sharp picks, live data, and injury-adjusted insights. Built for Wally and the NBA betting group. Data-driven, not vibes-driven.

## Audience & Tone
Sports bettors who want actionable information, not hot takes. Confident, data-driven, direct. Every pick should have a clear rationale tied to stats or situational factors. No hedging with "this could go either way" filler.

## Research Sources

### ⚠️ IMPORTANT: Custom Research Pipeline
This newsletter does **NOT** use the shared `~/newsletters/lib/research.py`. It has its own research script:
- **Research script**: `~/newsletters/nba-bets/scripts/research.py` (uses `nba_api` + ESPN APIs)

### Data Sources
- **ESPN Scoreboard**: `https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`
- **ESPN Injuries**: `https://www.espn.com/nba/injuries`
- **nba_api endpoints**: `leaguedashteamstats`, `leaguedashplayerstats`, `leaguedashptteamdefend`, `playerdashboardbygeneralsplits`

### Signal Sources (line movement, consensus)
- covers.com
- actionnetwork.com
- thelines.com
- rotowire.com

## Build Process
1. Run research: `python3 ~/newsletters/nba-bets/scripts/research.py`
2. Run build: `python3 ~/newsletters/nba-bets/scripts/build.py` (or `~/newsletters/lib/build.py nba-bets` if using shared build)
3. Publish: `python3 ~/newsletters/lib/publish.py nba-bets`
   Or combined: `~/newsletters/scripts/build-and-publish.sh nba-bets`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/nba-bets-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/nba-bets-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/nba-bets/

## Delivery
- Telegram group: `-5206093346`
- Schedule: research at 5:00am ET, build at **11:00am ET**
- **Late build is intentional** — captures morning injury reports and line movement before game time

## Content Rules
1. **Never assume player availability from training data.** Always pull live injury reports. A pick based on a player being active when they're actually out is worse than no pick at all.
2. **Every pick needs a data-backed rationale.** "I like the over" isn't analysis. "Team X is 8th in pace, opponent allows 3rd-most points in the paint, and the total has gone over in 7 of last 10 meetings" is.
3. **Include line movement context.** If a line has moved significantly since open, note it and explain why (sharp money, injury news, public action).
4. **No made-up stats.** If nba_api or ESPN doesn't return a stat, don't invent it. Flag missing data rather than guessing.
5. **Acknowledge uncertainty.** If it's a coin-flip game, say so. Credibility comes from honesty, not false confidence.

## Troubleshooting
- **nba_api rate limiting**: The NBA stats API throttles at ~1 request/1.6s. The research script should have built-in delays. If you get 429s, increase the delay.
- **ESPN injuries page scraping fails**: ESPN occasionally changes their HTML structure. If injury data is empty, manually verify at espn.com/nba/injuries and check the scraper selectors.
- **No games today**: During off-days, the newsletter should still publish with a "no games scheduled" note plus any relevant news (trade rumors, injury updates, standings context). Don't skip the issue entirely.
- **Stale nba_api data**: Stats endpoints sometimes lag by a day. The research script should check the `last_game_date` field. If data seems stale, note it in the output.
- **Off-season**: NBA season typically runs October through June. During off-season, this newsletter pauses or shifts to draft/free agency coverage.
