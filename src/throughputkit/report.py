"""Combine a byte count and a duration into a reportable measurement."""

import json
from dataclasses import dataclass

from .durations import format_duration
from .sizes import format_bytes


@dataclass
class Measurement:
    label: str
    bytes_total: int
    seconds: float

    @property
    def rate_bytes_per_sec(self):
        if self.seconds <= 0:
            return 0.0
        return self.bytes_total / self.seconds

    def to_dict(self):
        return {
            "label": self.label,
            "bytes": self.bytes_total,
            "seconds": self.seconds,
            "bytes_per_sec": round(self.rate_bytes_per_sec, 2),
        }

    def to_human(self, binary=True):
        size_str = format_bytes(self.bytes_total, binary=binary)
        time_str = format_duration(self.seconds)
        rate_str = format_bytes(int(self.rate_bytes_per_sec), binary=binary)
        return f"{self.label}: {size_str} in {time_str} ({rate_str}/s)"

    def render(self, as_json=False, binary=True):
        """Render this measurement for a --json flag a caller's CLI might expose."""
        if as_json:
            return json.dumps(self.to_dict())
        return self.to_human(binary=binary)


@dataclass
class Progress:
    """A snapshot of a transfer that's still running, for progress bars and
    status lines. Unlike Measurement, bytes_total here is the expected final
    size, not the amount moved so far.
    """

    label: str
    bytes_done: int
    bytes_total: int
    seconds_elapsed: float

    @property
    def rate_bytes_per_sec(self):
        if self.seconds_elapsed <= 0:
            return 0.0
        return self.bytes_done / self.seconds_elapsed

    @property
    def fraction_done(self):
        if self.bytes_total <= 0:
            return 1.0
        return min(self.bytes_done / self.bytes_total, 1.0)

    @property
    def eta_seconds(self):
        """Seconds left at the current rate, or None if that can't be estimated
        yet (no progress made, so there's no rate to extrapolate from)."""
        remaining = self.bytes_total - self.bytes_done
        if remaining <= 0:
            return 0.0
        rate = self.rate_bytes_per_sec
        if rate <= 0:
            return None
        return remaining / rate

    def to_dict(self):
        return {
            "label": self.label,
            "bytes_done": self.bytes_done,
            "bytes_total": self.bytes_total,
            "seconds_elapsed": self.seconds_elapsed,
            "bytes_per_sec": round(self.rate_bytes_per_sec, 2),
            "eta_seconds": self.eta_seconds,
        }

    def to_human(self, binary=True):
        done_str = format_bytes(self.bytes_done, binary=binary)
        total_str = format_bytes(self.bytes_total, binary=binary)
        rate_str = format_bytes(int(self.rate_bytes_per_sec), binary=binary)
        percent = f"{self.fraction_done * 100:.0f}%"
        eta = self.eta_seconds
        eta_str = format_duration(eta) if eta is not None else "unknown"
        return f"{self.label}: {done_str}/{total_str} ({percent}) at {rate_str}/s, ETA {eta_str}"

    def render(self, as_json=False, binary=True):
        """Render this progress snapshot for a --json flag a caller's CLI might expose."""
        if as_json:
            return json.dumps(self.to_dict())
        return self.to_human(binary=binary)
