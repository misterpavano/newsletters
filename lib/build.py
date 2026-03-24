#!/usr/bin/env python3
"""
build.py — render a newsletter from research JSON to HTML.

Usage:
    python3 lib/build.py <slug>
    python3 lib/build.py <slug> --research /path/to/research.json --output /path/to/output.html

Config:   newsletters/{slug}/config/newsletter.json
Template: {slug}/templates/index.html  →  fallback lib/templates/base.html
Input:    ~/.openclaw/workspace/tmp/{slug}-content-{YYYYMMDD}.json
Output:   ~/.openclaw/workspace/tmp/{slug}-{YYYYMMDD}.html
"""
import json
import os
import sys
from datetime import date, datetime, timezone

import jinja2

# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)

DEFAULT_TMP = os.path.expanduser("~/.openclaw/workspace/tmp")


# ── Logging (same pattern as research.py) ─────────────────────────────────────

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


# ── Config / discovery ────────────────────────────────────────────────────────

def load_config(slug: str) -> dict:
    """Load newsletter identity from {slug}/config/newsletter.json."""
    path = os.path.join(_REPO_ROOT, slug, "config", "newsletter.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Newsletter config not found: {path}")
    with open(path) as f:
        return json.load(f)


def find_research(slug: str) -> str:
    """Find today's research JSON at the default tmp location."""
    short = date.today().strftime("%Y%m%d")
    path = os.path.join(DEFAULT_TMP, f"{slug}-content-{short}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Research not found for {slug} today ({short}): {path}"
        )
    return path


# ── Render ────────────────────────────────────────────────────────────────────

def render(slug: str, research_path: str = None, output_path: str = None) -> str:
    """
    Render newsletter HTML from research JSON.
    Returns the output file path.
    """
    today = date.today()
    short = today.strftime("%Y%m%d")
    today_iso = today.isoformat()

    # Logging
    log_dir = os.path.expanduser(f"~/scripts/logs/{slug}")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{short}.jsonl")

    log_step(log_path, "build_start", "start", slug)

    # Load config
    config = load_config(slug)
    log_step(log_path, "config_loaded", "ok", config.get("name", slug))

    # Load research
    if research_path is None:
        research_path = find_research(slug)
    if not os.path.exists(research_path):
        log_step(log_path, "research_missing", "error", research_path)
        raise FileNotFoundError(f"Research file not found: {research_path}")

    with open(research_path) as f:
        research = json.load(f)
    sections = research.get("sections", {})
    total_stories = sum(len(v) for v in sections.values() if isinstance(v, list))
    log_step(log_path, "research_loaded", "ok",
             f"{total_stories} stories from {research_path}")

    # Resolve template
    slug_template = os.path.join(_REPO_ROOT, slug, "templates", "index.html")
    base_template_dir = os.path.join(_HERE, "templates")

    if os.path.exists(slug_template):
        template_dir = os.path.join(_REPO_ROOT, slug, "templates")
        template_name = "index.html"
        log_step(log_path, "template", "ok", f"per-slug: {slug_template}")
    else:
        template_dir = base_template_dir
        template_name = "base.html"
        log_step(log_path, "template", "ok", f"fallback: base.html")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=True,
    )
    template = env.get_template(template_name)

    build_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    html = template.render(
        newsletter=config,
        sections=sections,
        date=today_iso,
        build_time=build_time,
    )

    # Write output
    if output_path is None:
        os.makedirs(DEFAULT_TMP, exist_ok=True)
        output_path = os.path.join(DEFAULT_TMP, f"{slug}-{short}.html")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    log_step(log_path, "build_complete", "ok",
             f"{len(html)} bytes -> {output_path}")

    print(f"Built: {output_path} ({len(html)} bytes, {total_stories} stories)")
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Newsletter HTML builder")
    parser.add_argument("slug", help="Newsletter slug (e.g. ai-news)")
    parser.add_argument("--research", help="Path to research JSON (default: auto-detect today's)")
    parser.add_argument("--output", help="Output HTML path (default: workspace/tmp/{slug}-{date}.html)")
    args = parser.parse_args()
    render(args.slug, research_path=args.research, output_path=args.output)
