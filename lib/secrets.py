"""
secrets.py — load API keys from ~/.secrets or environment variables.
Checks env vars first, falls back to ~/.secrets file.
Never crashes — returns None for missing keys so callers can fail loudly.
"""
import os

_cache = {}

def _load_secrets_file():
    if _cache:
        return
    path = os.path.expanduser("~/.secrets")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            _cache[k.strip()] = v.strip()

def get(key, default=None):
    """Get a secret by key. Checks env first, then ~/.secrets file."""
    val = os.environ.get(key)
    if val:
        return val
    _load_secrets_file()
    return _cache.get(key, default)

def require(key):
    """Get a secret or raise if missing."""
    val = get(key)
    if not val:
        raise RuntimeError(f"Missing required secret: {key}. Add it to ~/.secrets")
    return val
