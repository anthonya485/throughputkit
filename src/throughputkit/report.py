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
