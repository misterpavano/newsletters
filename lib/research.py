#!/usr/bin/env python3
"""
research.py — shared newsletter research module.

Usage:
    python3 lib/research.py <slug>
    python3 lib/research.py <slug> --output /path/to/output.json

Config:  newsletters/{slug}/config/research.json
Secrets: ~/.secrets  (GEMINI_API_KEY, TELEGRAM_BOT_TOKEN)
Output:  ~/.openclaw/workspace/tmp/{slug}-content-{YYYYMMDD}.json
"""
import json
import os
import re
import signal
import sys
import time
import http.client
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Resolve lib path so this works when called from any directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)

# Add lib to path for sibling imports
sys.path.insert(0, _HERE)
from secrets import get as get_secret, require as require_secret  # noqa: E402
from filter import filter_file  # noqa: E402


# ── Constants ──────────────────────────────────────────────────────────────────

DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.openclaw/workspace/tmp")
GEMINI_MODEL = "gemini-2.5-flash"
ALERT_TARGET = "-5063061110"  # Pavano Maintenance group


# ── Timeout ───────────────────────────────────────────────────────────────────

class StepTimeoutError(Exception):
    pass

def _timeout_handler(signum, frame):
    raise StepTimeoutError("Step timeout exceeded")


# ── Logging ───────────────────────────────────────────────────────────────────

def log_step(log_path: str, step: str, status: str, detail: str = ""):
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "step": step,
            "status": status,
            "detail": str(detail) if detail else "",
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"  [log error: {e}]", file=sys.stderr)


def prune_old_logs(log_dir: str, days: int = 7):
    try:
        cutoff = datetime.now() - timedelta(days=days)
        for fname in os.listdir(log_dir):
            fpath = os.path.join(log_dir, fname)
            if os.path.isfile(fpath):
                if datetime.fromtimestamp(os.path.getmtime(fpath)) < cutoff:
                    os.remove(fpath)
    except Exception:
        pass


# ── Config ────────────────────────────────────────────────────────────────────

def load_config(slug: str) -> dict:
    """Load research config from newsletters/{slug}/config/research.json."""
    path = os.path.join(_REPO_ROOT, slug, "config", "research.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Research config not found: {path}")
    with open(path) as f:
        return json.load(f)


def gemini_endpoint() -> str:
    key = require_secret("GEMINI_API_KEY")
    return f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"


# ── Alerting ──────────────────────────────────────────────────────────────────

def send_alert(message: str, target: str = ALERT_TARGET):
    """
    Send a Telegram alert. Tries Hermes gateway first, falls back to OpenClaw.
    Best-effort — never raises.
    """
    endpoints = [
        ("hermes",    "http://127.0.0.1:18123/api/messages/send"),
        ("openclaw",  "http://127.0.0.1:18789/api/messages/send"),
    ]
    payload = json.dumps({
        "channel": "telegram",
        "to": target,
        "text": message,
    }).encode()
    for name, url in endpoints:
        try:
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=8)
            print(f"  [alert] Sent via {name}", file=sys.stderr)
            return
        except Exception:
            continue
    print(f"  [alert] All endpoints failed. Message: {message[:100]}", file=sys.stderr)


def fire_gemini_alert(slug: str, log_path: str, n_chars: int, n_sources: int, error_reason: str = None):
    reason = f" Error: {error_reason}." if error_reason else ""
    msg = (
        f"\U0001f6a8 Gemini FAILED for {slug}: {n_sources} sources, {n_chars} chars.{reason} "
        f"Research degraded — check immediately."
    )
    send_alert(msg)
    log_step(log_path, "gemini_alert_fired", "error", msg)


# ── RSS ───────────────────────────────────────────────────────────────────────

def fetch_rss(url: str, source: str, limit: int = 5, skip_terms: list = None) -> list:
    skip_terms = [s.lower() for s in (skip_terms or [])]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="replace")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            root = None

        items = []
        if root is not None:
            for item in (root.findall(".//item") or
                         root.findall(".//{http://www.w3.org/2005/Atom}entry")):
                title = re.sub(
                    r"<[^>]+>", "",
                    item.findtext("title",
                    item.findtext("{http://www.w3.org/2005/Atom}title", "")) or ""
                ).strip()
                link = item.findtext("link", "").strip()
                if not link:
                    for child in item:
                        if "link" in child.tag.lower():
                            link = child.text or child.get("href", "")
                            if link:
                                break
                if not (title and link and link.startswith("http") and len(title) > 10):
                    continue
                if any(s in title.lower() for s in skip_terms):
                    print(f"  [rss] SKIP: {title[:60]}", file=sys.stderr)
                    continue
                items.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "date": date.today().isoformat(),
                })
                if len(items) >= limit:
                    break

        print(f"  [rss] {source}: {len(items)} stories", file=sys.stderr)
        return items
    except Exception as e:
        print(f"  [rss] {source} error: {e}", file=sys.stderr)
        return []


# ── Gemini ────────────────────────────────────────────────────────────────────

def _follow_redirect(url: str) -> str | None:
    try:
        p = urlparse(url)
        c = http.client.HTTPSConnection(p.netloc, timeout=4)
        c.request("HEAD", p.path + ("?" + p.query if p.query else ""),
                  headers={"User-Agent": "Mozilla/5.0"})
        r = c.getresponse()
        loc = r.getheader("Location", "")
        c.close()
        return loc if loc and loc.startswith("http") else None
    except Exception:
        return None


def _resolve_url(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=4).url
    except Exception:
        return url


def _resolve_one(uri: str, use_redirect: bool) -> str | None:
    try:
        real = _follow_redirect(uri) if (use_redirect and "vertexaisearch" in uri) else _resolve_url(uri)
        if real and real.startswith("http") and "google.com" not in real:
            return real
    except Exception:
        pass
    return None


def gemini_search(prompt: str, endpoint: str, retries: int = 3, use_redirect: bool = True) -> tuple:
    """
    Run a Gemini grounded search.
    Returns (text, sources, error_reason).
    """
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192},
    }).encode()

    last_error = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                endpoint, data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=45)
            d = json.loads(resp.read())
            c = d["candidates"][0]
            text = c.get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            chunks = c.get("groundingMetadata", {}).get("groundingChunks", [])

            # Resolve grounding URIs in parallel
            uris = [ch.get("web", {}).get("uri", "") for ch in chunks
                    if ch.get("web", {}).get("uri", "")]
            sources = []
            if uris:
                with ThreadPoolExecutor(max_workers=min(10, len(uris))) as ex:
                    results = list(ex.map(lambda u: _resolve_one(u, use_redirect), uris))
                sources = [r for r in results if r]

            return text, sources, None

        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
            if e.code == 429 and attempt < retries - 1:
                time.sleep(30 * (attempt + 1))
                continue
            return "", [], last_error
        except Exception as e:
            last_error = str(e)
            if attempt < retries - 1:
                time.sleep(10)
                continue
            return "", [], last_error

    return "", [], last_error


# ── Parse Gemini output ───────────────────────────────────────────────────────

def parse_gemini(text: str, sources: list, keys: list, skip_terms: list = None) -> dict:
    skip_terms = [s.lower() for s in (skip_terms or [])]
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```\s*$", "", text.strip())
    try:
        parsed = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        try:
            parsed = json.loads(m.group()) if m else None
        except Exception:
            parsed = None

    if not parsed:
        return {k: [] for k in keys}

    si = 0
    result = {}
    today = date.today().isoformat()

    for k in keys:
        out = []
        for s in (parsed.get(k) or []):
            if not isinstance(s, dict):
                continue
            url = s.get("url", "")
            if not url or "vertexaisearch" in url or not url.startswith("http"):
                if si < len(sources):
                    s["url"] = sources[si]
                    si += 1
            if not s.get("url", "").startswith("http"):
                continue
            if not s.get("source"):
                try:
                    s["source"] = urlparse(s["url"]).netloc.replace("www.", "")
                except Exception:
                    pass
            if not s.get("date"):
                s["date"] = today
            if skip_terms and any(sk in s.get("title", "").lower() for sk in skip_terms):
                continue
            out.append(s)
        result[k] = out

    return result


# ── Extras ────────────────────────────────────────────────────────────────────

def run_github_trending(key: str, log_path: str, today: str) -> list:
    """Fetch trending AI repos from GitHub."""
    try:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        url = (f"https://api.github.com/search/repositories"
               f"?q=created:>{yesterday}+topic:ai&sort=stars&order=desc&per_page=8")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        gh = json.loads(urllib.request.urlopen(req, timeout=8).read())
        trending = [
            {
                "title": r["full_name"],
                "summary": f"{r.get('description') or 'No description'} — {r['stargazers_count']} stars today.",
                "url": r["html_url"],
                "source": "GitHub Trending",
                "date": today,
            }
            for r in gh.get("items", [])[:6]
            if r["stargazers_count"] >= 5
        ]
        print(f"  [extras] GitHub trending: {len(trending)} repos", file=sys.stderr)
        log_step(log_path, "github_trending_complete", "ok", f"{len(trending)} repos")
        return trending
    except Exception as e:
        print(f"  [extras] GitHub trending error: {e}", file=sys.stderr)
        log_step(log_path, "github_trending_error", "error", str(e))
        return []


# ── Main run ──────────────────────────────────────────────────────────────────

def run(slug: str, output_path: str = None) -> str:
    cfg = load_config(slug)
    today = date.today().isoformat()
    short = today.replace("-", "")

    if output_path is None:
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, f"{slug}-content-{short}.json")

    # Logging
    log_dir = os.path.expanduser(f"~/scripts/logs/{slug}")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{short}.jsonl")
    prune_old_logs(log_dir)

    ep = gemini_endpoint()
    skip_terms = cfg.get("skip_terms", [])
    use_threads = cfg.get("use_threads", False)

    print(f"=== {cfg.get('name', slug)} Research {today} ===", file=sys.stderr)
    log_step(log_path, "run_start", "start", slug)

    # ── RSS ──────────────────────────────────────────────────────────────────
    feeds = cfg.get("rss_feeds", [])
    rss_stories = {}
    log_step(log_path, "rss_start", "start", f"{len(feeds)} feeds")

    if use_threads and len(feeds) > 1:
        with ThreadPoolExecutor(max_workers=min(5, len(feeds))) as ex:
            futures = {
                ex.submit(fetch_rss, f["url"], f["source"], f.get("limit", 5), skip_terms): f
                for f in feeds
            }
            for fut in as_completed(futures):
                feed = futures[fut]
                result = fut.result()
                rss_stories[feed["key"]] = result
                log_step(log_path, "rss_feed_complete", "ok",
                         f"{feed['source']}: {len(result)}")
    else:
        for f in feeds:
            result = fetch_rss(f["url"], f["source"], f.get("limit", 5), skip_terms)
            rss_stories[f["key"]] = result
            log_step(log_path, "rss_feed_complete", "ok",
                     f"{f['source']}: {len(result)}")

    sections = dict(rss_stories)

    # ── Gemini ───────────────────────────────────────────────────────────────
    gemini_cfg = cfg.get("gemini", {})
    if gemini_cfg:
        print("--- Gemini search ---", file=sys.stderr)
        covered = [s["title"] for sec in rss_stories.values() for s in sec]
        covered_summary = "; ".join(covered[:12])

        _today_d = date.today()
        _current_month = _today_d.strftime("%B %Y")
        _prior_month = (_today_d.replace(day=1) - timedelta(days=1)).strftime("%B %Y")

        prompt = (gemini_cfg["prompt_template"]
                  .replace("{today}", today)
                  .replace("{covered_summary}", covered_summary)
                  .replace("{CURRENT_MONTH}", _current_month)
                  .replace("{PRIOR_MONTH}", _prior_month))

        log_step(log_path, "gemini_start", "start", f"{len(prompt)} chars")
        text, sources, gemini_err = gemini_search(prompt, ep)
        print(f"  [gemini] {len(text)} chars, {len(sources)} sources", file=sys.stderr)
        log_step(log_path, "gemini_complete",
                 "ok" if text else "error",
                 f"{len(text)} chars, {len(sources)} sources"
                 + (f" | {gemini_err}" if gemini_err else ""))

        # Failure detection
        if len(text) == 0 and len(sources) == 0:
            print(f"  [CRITICAL] Gemini hard failure for {slug}", file=sys.stderr)
            fire_gemini_alert(slug, log_path, 0, 0, error_reason=gemini_err)
        elif len(sources) < 3:
            warn = f"Gemini weak results for {slug}: only {len(sources)} sources"
            print(f"  [WARNING] {warn}", file=sys.stderr)
            log_step(log_path, "gemini_weak_sources", "warning", warn)

        keys = gemini_cfg["sections"]
        niche = parse_gemini(text, sources, keys, skip_terms=skip_terms)
        sections.update(niche)
        log_step(log_path, "parse_complete", "ok",
                 json.dumps({k: len(v) for k, v in niche.items()}))

    # ── Extras ───────────────────────────────────────────────────────────────
    for extra in cfg.get("extras", []):
        if extra["type"] == "github_trending":
            sections[extra["key"]] = run_github_trending(extra["key"], log_path, today)

    # ── Output ───────────────────────────────────────────────────────────────
    output = {
        "date": today,
        "newsletter": slug,
        "verified": True,
        "sections": sections,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    total = sum(len(v) for v in sections.values() if isinstance(v, list))
    print(f"\nSaved: {output_path}")
    for k, v in sections.items():
        if isinstance(v, list):
            print(f"  {k:28s}: {len(v)} stories")
    print(f"  {'TOTAL':28s}: {total}")

    log_step(log_path, "save_complete", "ok", f"{total} stories → {output_path}")

    # Filter stale stories
    filter_file(output_path)
    log_step(log_path, "filter_complete", "ok")

    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Newsletter research runner")
    parser.add_argument("slug", help="Newsletter slug (e.g. ai-news)")
    parser.add_argument("--output", help="Output path (default: workspace/tmp/{slug}-content-{date}.json)")
    args = parser.parse_args()
    run(args.slug, output_path=args.output)
