"""Parsing and formatting for byte quantities."""

import math
import re

# Bare letter suffixes (K, M, G, ...) follow the du/ls -h convention and mean
# binary (1024-based) units. Explicit "KB"/"KiB" spell out which base is meant.
_DECIMAL_UNITS = {"B": 1, "KB": 1000, "MB": 1000**2, "GB": 1000**3, "TB": 1000**4, "PB": 1000**5}
_BINARY_UNITS = {
    "B": 1,
    "K": 1024, "KIB": 1024,
    "M": 1024**2, "MIB": 1024**2,
    "G": 1024**3, "GIB": 1024**3,
    "T": 1024**4, "TIB": 1024**4,
    "P": 1024**5, "PIB": 1024**5,
}

_NUMBER_UNIT_RE = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*([A-Za-z]*)\s*$")


def parse_bytes(text):
    """Parse a size string like "512", "1.5MB", "2 GiB", or "900K" into an int byte count."""
    match = _NUMBER_UNIT_RE.match(text)
    if not match:
        raise ValueError(f"not a byte size: {text!r}")

    number, unit = match.groups()
    unit = unit.upper()

    if unit in _DECIMAL_UNITS:
        multiplier = _DECIMAL_UNITS[unit]
    elif unit in _BINARY_UNITS:
        multiplier = _BINARY_UNITS[unit]
    elif unit == "":
        multiplier = 1
    else:
        raise ValueError(f"unknown size unit {unit!r} in {text!r}")

    value = float(number) * multiplier
    # A finite input number can still overflow past float's range once
    # multiplied by a PB-scale multiplier; catch that here rather than
    # letting int() below raise an OverflowError for an out-of-range size.
    if not math.isfinite(value):
        raise ValueError(f"byte size out of range: {text!r}")

    return int(value)


def format_bytes(n_bytes, binary=True, precision=1):
    """Format a byte count as a human string, e.g. 1536 -> "1.5 KiB"."""
    if n_bytes < 0:
        raise ValueError("byte count cannot be negative")

    base = 1024 if binary else 1000
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"] if binary else ["B", "KB", "MB", "GB", "TB", "PB"]

    value = float(n_bytes)
    index = 0
    while value >= base and index < len(units) - 1:
        value /= base
        index += 1

    if index == 0:
        return f"{int(value)} B"
    return f"{value:.{precision}f} {units[index]}"
