#!/usr/bin/env python3
"""
publish.py — push rendered newsletter HTML to GitHub Pages.

Usage:
    python3 lib/publish.py <slug>
    python3 lib/publish.py <slug> --html /path/to/newsletter.html

Clones/pulls misterpavano/{slug} into ~/newsletters/.cache/{slug},
copies the HTML as index.html, commits, and pushes.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone

# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)

DEFAULT_TMP = os.path.expanduser("~/.openclaw/workspace/tmp")
CACHE_DIR = os.path.join(_REPO_ROOT, ".cache")


# ── Logging (same pattern as research.py / build.py) ──────────────────────────

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


def find_html(slug: str) -> str:
    """Find today's rendered HTML at the default tmp location."""
    short = date.today().strftime("%Y%m%d")
    path = os.path.join(DEFAULT_TMP, f"{slug}-{short}.html")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Built HTML not found for {slug} today ({short}): {path}"
        )
    return path


def _get_token() -> str:
    """Load GH_TOKEN from ~/.secrets."""
    sys.path.insert(0, _HERE)
    from secrets import require as require_secret
    return require_secret("GH_TOKEN")


# ── Git helpers ───────────────────────────────────────────────────────────────

def _run(cmd: list, cwd: str = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess, printing stderr on failure."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        print(f"  [git] FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(f"  stdout: {result.stdout[:500]}", file=sys.stderr)
        print(f"  stderr: {result.stderr[:500]}", file=sys.stderr)
        result.check_returncode()
    return result


# ── Publish ───────────────────────────────────────────────────────────────────

def publish(slug: str, html_path: str = None) -> str:
    """
    Publish newsletter HTML to GitHub Pages repo.
    Returns the commit hash on success.
    """
    today = date.today()
    short = today.strftime("%Y%m%d")
    today_iso = today.isoformat()

    # Logging
    log_dir = os.path.expanduser(f"~/scripts/logs/{slug}")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{short}.jsonl")

    log_step(log_path, "publish_start", "start", slug)

    # Load config
    config = load_config(slug)
    repo = config.get("delivery", {}).get("github_pages_repo")
    if not repo:
        log_step(log_path, "publish_error", "error", "No github_pages_repo in config")
        raise ValueError(f"No delivery.github_pages_repo configured for {slug}")

    # Find HTML
    if html_path is None:
        html_path = find_html(slug)
    if not os.path.exists(html_path):
        log_step(log_path, "publish_error", "error", f"HTML not found: {html_path}")
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    log_step(log_path, "html_found", "ok", html_path)

    # Auth
    token = _get_token()
    remote_url = f"https://{token}@github.com/{repo}.git"

    # Clone or pull
    os.makedirs(CACHE_DIR, exist_ok=True)
    repo_dir = os.path.join(CACHE_DIR, slug)

    if os.path.isdir(os.path.join(repo_dir, ".git")):
        # Update remote URL (in case token changed) and pull
        _run(["git", "remote", "set-url", "origin", remote_url], cwd=repo_dir)
        _run(["git", "pull", "--rebase", "origin", "main"], cwd=repo_dir, check=False)
        log_step(log_path, "git_pull", "ok", repo_dir)
    else:
        # Fresh clone
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        _run(["git", "clone", "--depth", "1", remote_url, repo_dir])
        log_step(log_path, "git_clone", "ok", repo)

    # Copy HTML as index.html
    dest = os.path.join(repo_dir, "index.html")
    shutil.copy2(html_path, dest)
    log_step(log_path, "html_copied", "ok", dest)

    # Configure git user
    _run(["git", "config", "user.email", "pavano@openclaw.dev"], cwd=repo_dir)
    _run(["git", "config", "user.name", "Pavano"], cwd=repo_dir)

    # Stage, commit, push
    _run(["git", "add", "index.html"], cwd=repo_dir)

    # Check if there are changes to commit
    diff = _run(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, check=False)
    if diff.returncode == 0:
        msg = "No changes to commit (HTML identical to last push)"
        print(f"  {msg}")
        log_step(log_path, "publish_skip", "ok", msg)
        return "no-change"

    commit_msg = f"chore: {today_iso} edition"
    _run(["git", "commit", "-m", commit_msg], cwd=repo_dir)

    _run(["git", "push", "origin", "main"], cwd=repo_dir)

    # Get commit hash
    result = _run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir)
    commit_hash = result.stdout.strip()

    log_step(log_path, "publish_complete", "ok",
             f"Pushed {commit_hash} to {repo}")

    print(f"Published: {repo} @ {commit_hash} ({commit_msg})")
    return commit_hash


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Newsletter GitHub Pages publisher")
    parser.add_argument("slug", help="Newsletter slug (e.g. ai-news)")
    parser.add_argument("--html", help="Path to rendered HTML (default: auto-detect today's)")
    args = parser.parse_args()
    publish(args.slug, html_path=args.html)
