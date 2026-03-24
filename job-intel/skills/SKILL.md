# Skill: Job Intel

## What This Is
Curated AI job leads for Wally, focused on the RTP/Raleigh NC area and remote US roles. Targets senior AI strategy, leadership, and implementation positions at companies that matter.

## Audience & Tone
**Audience**: Wally only. This is a personal job radar, not a job board.

**Tone**: Practical, actionable, no noise. Each listing should answer: What's the role? Why does it match? What's the next step? Skip the generic "exciting opportunity" language.

## Research Sources

### Target Roles
- AI Strategy / Transformation Consultant
- Head of AI / VP of AI / Director of AI
- Enterprise AI Solutions Engineer / Technical Account Manager
- AI Product Manager
- Field Delivery Engineer / AI Implementation Specialist
- AI Solutions Architect

### RTP Companies (local)
SAS Institute, Red Hat, Cisco, Lenovo North America, Epic Games, Bandwidth, Pendo, MetLife, Fidelity Investments, NetApp, WillowTree, UiPath, IQVIA, Syneos Health, AvidXchange, Relay Payments, Duke Health, UNC Health, IBM RTP

### AI Companies (national/remote)
Anthropic, OpenAI, Cohere, Mistral, Scale AI, Hugging Face, Salesforce AI, Google DeepMind, Microsoft AI, Palantir, C3.ai, DataStax, Dataiku, Weights & Biases, Fractional AI

### Consulting Firms
Deloitte, Accenture, EY, McKinsey, Boston Consulting Group, Booz Allen Hamilton, KPMG, PwC, Leidos

### Job Boards
- linkedin.com/jobs
- indeed.com
- glassdoor.com
- levels.fyi
- wellfound.com
- ycombinator.com/jobs

## Build Process
1. Run research: `python3 ~/newsletters/lib/research.py job-intel`
2. Run build: `python3 ~/newsletters/lib/build.py job-intel`
3. Publish: `python3 ~/newsletters/lib/publish.py job-intel`
   Or combined: `~/newsletters/scripts/build-and-publish.sh job-intel`

## Output
- Research JSON: `~/.openclaw/workspace/tmp/job-intel-content-{YYYYMMDD}.json`
- HTML: `~/.openclaw/workspace/tmp/job-intel-{YYYYMMDD}.html`
- Published to: https://misterpavano.github.io/job-intel/

## Delivery
- Telegram group: `-1003812435266`
- Schedule: research at 5:00am ET, build TBD
- **⚠️ NOT YET ON CRON.** This newsletter is built but not scheduled for automated delivery. Run manually or add to cron when Wally decides on timing.

## Content Rules
1. **Scope is strict.** Only RTP/Raleigh NC area or remote US positions. No "willing to relocate to SF" roles unless they explicitly offer remote.
2. **Target roles only.** The 6 role types above define what belongs. A generic "Software Engineer" listing doesn't qualify unless the description is clearly AI-focused and matches the seniority level.
3. **Deduplicate across job boards.** The same role often appears on LinkedIn, Indeed, and Glassdoor. Include it once with the best source link.
4. **Freshness matters.** Only include postings from the last 48 hours. Stale listings waste time.
5. **Include compensation when available.** Salary ranges, equity mentions, or "competitive" disclaimers. This helps prioritize which roles to pursue.

## Troubleshooting
- **Job board scraping failures**: Most job boards aggressively block automated scraping. If Gemini search can't find fresh listings, try searching with company-specific queries (e.g., "Anthropic AI Strategy remote 2026").
- **Too many generic results**: The target_roles and company lists should constrain results, but Gemini may return broad matches. Filter ruthlessly during build.
- **No Telegram group configured**: The `telegram_group` in newsletter.json is null. Delivery goes to `-1003812435266` (from research.json `deliver_to`). Verify this is correct before enabling cron.
- **Stale listings persist**: Job boards don't always expose posting dates. If a role looks familiar from a previous issue, check the company careers page directly to confirm it's still open.
