"""
filter.py — post-process research JSON, remove stale stories.

Fast-moving sections (breaking news): 1-day cutoff.
Niche/specialist sections: 7-day cutoff.
"""
import json
import sys
from datetime import datetime, timedelta

# Sections covering slow-moving specialist topics — allow up to 7 days
NICHE_SECTIONS = {
    "research_papers",
    "science",
    "legal",
}

def filter_file(path: str) -> int:
    """Filter a research JSON file in-place. Returns total stories remaining."""
    today = datetime.now().date()

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [filter] Failed to parse {path}: {e}", file=sys.stderr)
        return -1

    if not isinstance(data, dict) or "sections" not in data:
        print(f"  [filter] Malformed JSON in {path}", file=sys.stderr)
        return -1

    sections = data["sections"]
    total_before = sum(len(v) for v in sections.values() if isinstance(v, list))
    total_removed = 0

    for section_name, stories in sections.items():
        if not isinstance(stories, list):
            continue
        cutoff_days = 7 if section_name in NICHE_SECTIONS else 1
        cutoff = today - timedelta(days=cutoff_days)
        kept = []
        for story in stories:
            date_str = story.get("date", "")
            if not date_str:
                kept.append(story)
                continue
            try:
                story_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                if story_date >= cutoff:
                    kept.append(story)
                else:
                    total_removed += 1
                    print(f"  [filter] REMOVED stale ({date_str}): {story.get('title','')[:60]}", file=sys.stderr)
            except ValueError:
                kept.append(story)  # can't parse date, keep it
        sections[section_name] = kept

    if total_removed > 0:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  [filter] Removed {total_removed} stale stories, {total_before - total_removed} remain", file=sys.stderr)

    return total_before - total_removed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 filter.py <research-json-file>", file=sys.stderr)
        sys.exit(1)
    remaining = filter_file(sys.argv[1])
    if remaining < 0:
        sys.exit(1)
