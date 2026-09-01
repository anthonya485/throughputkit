# throughputkit

Every backup script, sync tool, and batch job I've written ends up with the
same two problems: turning a byte count and an elapsed time into something a
person can read ("1.5 GiB in 1m30s"), and turning that same measurement into
something a monitoring system can parse. Usually the second one gets bolted
on later as a hand-rolled `json.dumps({...})` that drifts out of sync with
the human-readable version.

This is a small standard-library-only toolkit for that: parsing and
formatting byte sizes and durations, plus a `Measurement` type that renders
either a human string or a JSON object from the same data.

It's a library, not a CLI — wire it into whatever script or tool needs it.

## Install

No PyPI package yet. Drop `src/throughputkit` on your `PYTHONPATH`, or
install it from a checkout:

```
pip install -e .
```

## Usage

Parsing and formatting sizes:

```python
from throughputkit import parse_bytes, format_bytes

parse_bytes("1.5MB")      # 1500000
parse_bytes("2GiB")       # 2147483648
parse_bytes("900K")       # 921600  (bare letters mean binary, like `ls -h`)

# Either '.' or ',' works as the decimal point. Whichever one repeats, or
# comes second when both appear, is treated as a thousands separator instead.
parse_bytes("1,5MB")        # 1500000  (EU-style decimal comma)
parse_bytes("1.234,5MB")    # 1234500000

format_bytes(1536)              # "1.5 KiB"
format_bytes(1536, binary=False)  # "1.5 KB"
```

Parsing and formatting durations:

```python
from throughputkit import parse_duration, format_duration

parse_duration("90")       # 90.0
parse_duration("1m30s")    # 90.0
parse_duration("2h")       # 7200.0

format_duration(3725)      # "1h 2m 5s"
format_duration(0.25)      # "250ms"
```

Combining both into a report that supports a `--json` flag:

```python
from throughputkit import Measurement

m = Measurement(label="backup", bytes_total=1_500_000_000, seconds=42.5)
print(m.render())            # "backup: 1.4 GiB in 42.50s (33.9 MiB/s)"
print(m.render(as_json=True))
# {"label": "backup", "bytes": 1500000000, "seconds": 42.5, "bytes_per_sec": 35294117.65}
```

A typical wiring into a script's own argument parser:

```python
import argparse
from throughputkit import Measurement

parser = argparse.ArgumentParser()
parser.add_argument("--json", action="store_true")
args = parser.parse_args()

result = Measurement(label="upload", bytes_total=copied, seconds=elapsed)
print(result.render(as_json=args.json))
```

## Status

Early. Sizes and durations round-trip correctly for the common cases, and
negative and overflow inputs are now rejected consistently across both
parsers. `parse_bytes` accepts locale-style decimal commas and thousands
separators; `parse_duration` doesn't yet. See the roadmap in the repo's
issues.
