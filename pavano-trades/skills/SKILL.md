# Skill: Pavano Trades

## What This Is
Daily options trading briefing with portfolio recap, market context, and signals analysis. Built for Wally as a trading accountability tool. Pulls live data from the Alpaca paper account.

## Audience & Tone
**Audience**: Wally only. This is a personal trading journal/briefing, not a public newsletter.

**Tone**: Analytical, plain English, no sugar-coating. Wally is learning options. Every piece of jargon must be explained or avoided entirely. "Your put lost value because the stock went up" beats "theta decay eroded the extrinsic value of your OTM put." Don't dumb it down; make it clear.

## Research Sources

### Live Data
- **Alpaca Paper API**: `https://paper-api.alpaca.markets/v2` (credentials in `~/.secrets`)
  - Current positions, P&L, account value
- **Signals output**: `~/scripts/signals-output.json` (from the trading bot)

### RSS Feeds
- **MarketWatch** (4 items): `https://feeds.marketwatch.com/marketwatch/topstories/`
- **Reuters Finance** (4 items): `https://feeds.reuters.com/reuters/businessNews`

### Gemini Search Sections
- **market_context**: 2-3 major market-moving events (Fed, earnings, macro)
- **options_education**: 1 plain-English concept about options trading relevant to current conditions

## Build Process
1. Run research: `python3 ~/newsletters/pavano-trades/scripts/research.py` (custom script, pulls Alpaca data)
2. Run build: `python3 ~/newsletters/lib/build.py pavano-trades`
3. Publish: `python3 ~/newsletters/lib/publish.py pavano-trades`
   Or combined: `~/newsletters/scripts/build-and-publish.sh pavano-trades`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/pavano-trades-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/pavano-trades-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/pavano-trades/

## Delivery
- Telegram group: `-5191423233`
- Schedule: research at 5:00am ET, build at 8:30am ET
- **Weekdays only.** Markets are closed Saturday/Sunday. No weekend issues.

## Content Rules
1. **Plain English always.** If you use a trading term, explain it in parentheses or in the next sentence. The options_education Gemini section exists specifically for this purpose.
2. **Live portfolio data is the centerpiece.** The Alpaca positions section should lead the newsletter. How are current trades doing? What's the P&L? What changed since yesterday?
3. **Never jargon without explanation.** "IV crush" means nothing to someone learning. "The option lost value because the big event passed and uncertainty dropped (called IV crush)" does.
4. **Be honest about losses.** This is an accountability tool. If a trade is down 40%, say so clearly. Don't soften bad positions.
5. **Market context supports the portfolio.** The RSS feeds and Gemini market_context section should connect to the active positions. "Fed held rates steady" matters because of what it means for the portfolio, not in the abstract.

## Troubleshooting
- **Alpaca API returns empty positions**: Either all positions were closed, or there's an auth issue. Check `~/.secrets` for `ALPACA_KEY` and `ALPACA_SECRET`. Verify with: `curl -H "APCA-API-KEY-ID: $ALPACA_KEY" -H "APCA-API-SECRET-KEY: $ALPACA_SECRET" https://paper-api.alpaca.markets/v2/positions`
- **Weekend cron fires**: The build script should check the day of week and skip weekends. If it runs anyway, the output will show stale Friday data. Not harmful, but wasteful.
- **Signals output file missing or stale**: If `~/scripts/signals-output.json` doesn't exist or hasn't been updated today, note this in the newsletter rather than silently skipping the signals section.
- **Reuters feed blocked**: Reuters occasionally blocks automated access. If the feed returns empty, MarketWatch alone provides enough market context. Log the failure for debugging.
