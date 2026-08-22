"""Parsing and formatting for durations."""

import re

_UNIT_SECONDS = {"d": 86400, "h": 3600, "m": 60, "s": 1, "ms": 0.001}
_TOKEN_RE = re.compile(r"([0-9]*\.?[0-9]+)\s*(ms|d|h|m|s)")


def parse_duration(text):
    """Parse a duration string like "90", "1m30s", "2h", or "1d 2h 3m" into seconds."""
    text = text.strip()
    if not text:
        raise ValueError("empty duration string")

    # A bare number means seconds, matching how most tools already accept a timeout value.
    try:
        return float(text)
    except ValueError:
        pass

    tokens = _TOKEN_RE.findall(text)
    if not tokens:
        raise ValueError(f"not a duration: {text!r}")

    # Reject strings with leftover characters the tokenizer skipped over,
    # e.g. "1x" would otherwise silently parse as an empty duration.
    consumed = "".join(f"{value}{unit}" for value, unit in tokens)
    if re.sub(r"\s+", "", text) != consumed:
        raise ValueError(f"not a duration: {text!r}")

    return sum(float(value) * _UNIT_SECONDS[unit] for value, unit in tokens)


def format_duration(seconds):
    """Format a number of seconds as a human string, e.g. 3725 -> "1h 2m 5s"."""
    if seconds < 0:
        raise ValueError("duration cannot be negative")

    if 0 < seconds < 1:
        return f"{seconds * 1000:.0f}ms"

    remaining = seconds
    parts = []
    for unit, unit_seconds in (("d", 86400), ("h", 3600), ("m", 60)):
        count, remaining = divmod(remaining, unit_seconds)
        if count:
            parts.append(f"{int(count)}{unit}")

    if remaining or not parts:
        if remaining == int(remaining):
            parts.append(f"{int(remaining)}s")
        else:
            parts.append(f"{remaining:.2f}s")

    return " ".join(parts)
