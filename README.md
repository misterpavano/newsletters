# Pavano Newsletters — Build System

Monorepo for all newsletter research, build logic, and delivery.

## Architecture

```
newsletters/
  ai-news/           ← per-newsletter: config, templates, skill
  world-happenings/
  nba-bets/
  art-inspiration/
  mandy-intel/
  pavano-trades/
  job-intel/
  lib/               ← shared: research.py, kg.py, publish.py
  scripts/           ← CLI helpers: build.sh, publish.sh, research.sh
  .github/workflows/ ← CI/CD: build + push HTML to content repos
```

## Content Repos (GitHub Pages — delivery layer, URLs don't change)

| Newsletter | Repo | Audience |
|---|---|---|
| AI News | misterpavano/ai-news | AI News group |
| World Happenings | misterpavano/world-happenings | World group |
| NBA Bets | misterpavano/nba-bets | NBA Bets group |
| Art Inspiration | misterpavano/art-inspiration | Art group |
| Mandy Intel | misterpavano/mandy-intel | Mandy |
| Pavano Trades | misterpavano/pavano-trades | Trades group |
| Job Intel | misterpavano/job-intel | Wally |

## Each Newsletter Contains

```
{slug}/
  config/
    newsletter.json   ← identity: name, audience, delivery targets
    research.json     ← sources, topics, filters, skip_terms
  templates/
    index.html        ← Jinja2 template for the newsletter
  skills/
    SKILL.md          ← Hermes skill: how to build this newsletter
```

## Shared Library (`lib/`)

- `research.py` — threaded RSS + Gemini grounded search, URL resolution
- `build.py` — Jinja2 rendering, asset inlining
- `publish.py` — git push to content repo
- `kg.py` — knowledge graph: dedup, decay scoring

## Cron Schedule (Hermes)

| Time | Job |
|---|---|
| 4:00am | Research: AI News, World Happenings, Mandy Intel |
| 5:00am | Research: NBA Bets, Pavano Trades, Job Intel, Art Inspiration |
| 7:00am | Build + Publish: AI News |
| 7:00am | Build + Publish: World Happenings |
| 7:15am | Build + Publish: Mandy Intel |
| 8:30am | Build + Publish: Pavano Trades |
| 9:00am | Build + Publish: Art Inspiration |
| 11:00am | Build + Publish: NBA Bets |
