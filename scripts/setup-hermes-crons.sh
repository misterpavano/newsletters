#!/bin/bash
# setup-hermes-crons.sh
# Creates all Hermes cron jobs for the newsletter system.
# Run once during cutover from OpenClaw → Hermes.
# Safe to re-run — Hermes cron create will just add duplicates, so
# run `hermes cron list` first to confirm state before re-running.

set -euo pipefail

echo "=== Pavano Newsletter Crons Setup ==="
echo "Creating $(echo '14') cron jobs across 7 newsletters..."
echo ""

# ── RESEARCH CRONS (4-5am) ────────────────────────────────────────────────────
# These run first, build crons depend on their output.

echo "--- Research crons ---"

hermes cron create "0 4 * * *" \
  "Run research for AI News newsletter: python3 ~/newsletters/lib/research.py ai-news
Verify output exists at ~/.openclaw/workspace/tmp/ai-news-content-\$(date +%Y%m%d).json
Report story count. Alert to telegram:-5063061110 if it fails." \
  --name "research:ai-news" \
  --skill ai-news \
  --deliver "telegram:-5063061110"

hermes cron create "0 4 * * *" \
  "Run research for World Happenings newsletter: python3 ~/newsletters/lib/research.py world-happenings
Verify output exists at ~/.openclaw/workspace/tmp/world-happenings-content-\$(date +%Y%m%d).json
Report story count. Alert to telegram:-5063061110 if it fails." \
  --name "research:world-happenings" \
  --skill world-happenings \
  --deliver "telegram:-5063061110"

hermes cron create "0 4 * * *" \
  "Run research for Mandy Intel newsletter: python3 ~/newsletters/lib/research.py mandy-intel
Verify output exists at ~/.openclaw/workspace/tmp/mandy-intel-content-\$(date +%Y%m%d).json
Report story count. Alert to telegram:-5063061110 if it fails." \
  --name "research:mandy-intel" \
  --skill mandy-intel \
  --deliver "telegram:-5063061110"

hermes cron create "0 5 * * *" \
  "Run research for Art Inspiration newsletter: python3 ~/newsletters/lib/research.py art-inspiration
Verify output exists at ~/.openclaw/workspace/tmp/art-inspiration-content-\$(date +%Y%m%d).json
Report story count. Alert to telegram:-5063061110 if it fails." \
  --name "research:art-inspiration" \
  --skill art-inspiration \
  --deliver "telegram:-5063061110"

hermes cron create "0 5 * * 1-5" \
  "Run research for Pavano Trades newsletter (weekdays only): python3 ~/newsletters/lib/research.py pavano-trades
Verify output exists at ~/.openclaw/workspace/tmp/pavano-trades-content-\$(date +%Y%m%d).json
Report story count. Alert to telegram:-5063061110 if it fails." \
  --name "research:pavano-trades" \
  --skill pavano-trades \
  --deliver "telegram:-5063061110"

hermes cron create "0 5 * * *" \
  "Run NBA Bets research (uses custom script, NOT shared research.py):
python3 ~/scripts/nba-bets-research.py
Verify output exists. Report game count and player splits fetched.
Alert to telegram:-5063061110 if it fails." \
  --name "research:nba-bets" \
  --skill nba-bets \
  --deliver "telegram:-5063061110"

hermes cron create "0 5 * * *" \
  "Run research for Job Intel newsletter: python3 ~/newsletters/lib/research.py job-intel
Verify output exists at ~/.openclaw/workspace/tmp/job-intel-content-\$(date +%Y%m%d).json
Report job lead count. Alert to telegram:-5063061110 if it fails." \
  --name "research:job-intel" \
  --skill job-intel \
  --deliver "telegram:-5063061110"

echo ""
echo "--- Build + publish crons ---"

# ── BUILD + PUBLISH CRONS ─────────────────────────────────────────────────────

hermes cron create "0 7 * * *" \
  "Build and publish AI News newsletter:
1. Run: ~/newsletters/scripts/build-and-publish.sh ai-news
2. Verify https://misterpavano.github.io/ai-news/ is updated
3. Send the newsletter link to telegram:-5108093721" \
  --name "build:ai-news" \
  --skill ai-news \
  --deliver "telegram:-5108093721"

hermes cron create "0 7 * * *" \
  "Build and publish World Happenings newsletter:
1. Run: ~/newsletters/scripts/build-and-publish.sh world-happenings
2. Verify https://misterpavano.github.io/world-happenings/ is updated
3. Send the newsletter link to telegram:-5283070369" \
  --name "build:world-happenings" \
  --skill world-happenings \
  --deliver "telegram:-5283070369"

hermes cron create "15 7 * * *" \
  "Build and publish Mandy Intel newsletter:
1. Run: ~/newsletters/scripts/build-and-publish.sh mandy-intel
2. Verify https://misterpavano.github.io/mandy-intel/ is updated
3. Send the newsletter link to telegram:-1003710768958" \
  --name "build:mandy-intel" \
  --skill mandy-intel \
  --deliver "telegram:-1003710768958"

hermes cron create "30 8 * * 1-5" \
  "Build and publish Pavano Trades newsletter (weekdays only):
1. Run: ~/newsletters/scripts/build-and-publish.sh pavano-trades
2. Verify https://misterpavano.github.io/pavano-trades/ is updated
3. Send the newsletter link to telegram:-5191423233" \
  --name "build:pavano-trades" \
  --skill pavano-trades \
  --deliver "telegram:-5191423233"

hermes cron create "0 9 * * *" \
  "Build and publish Art Inspiration newsletter:
1. Run: ~/newsletters/scripts/build-and-publish.sh art-inspiration
2. Verify https://misterpavano.github.io/art-inspiration/ is updated
3. Send the newsletter link to telegram:-1003519302207" \
  --name "build:art-inspiration" \
  --skill art-inspiration \
  --deliver "telegram:-1003519302207"

hermes cron create "0 11 * * *" \
  "Build and publish NBA Bets newsletter (uses custom build script):
1. Run: python3 ~/scripts/nba-bets-build.py
2. Verify output HTML exists
3. Run: python3 ~/newsletters/lib/publish.py nba-bets
4. Send the newsletter link to telegram:-5206093346" \
  --name "build:nba-bets" \
  --skill nba-bets \
  --deliver "telegram:-5206093346"

hermes cron create "0 9 * * *" \
  "Build and publish Job Intel newsletter:
1. Run: ~/newsletters/scripts/build-and-publish.sh job-intel
2. Verify https://misterpavano.github.io/job-intel/ is updated
3. Send the newsletter link to telegram:-1003812435266" \
  --name "build:job-intel" \
  --skill job-intel \
  --deliver "telegram:-1003812435266"

echo ""
echo "=== Done. Crons created ==="
echo "Run 'hermes cron list' to verify."
