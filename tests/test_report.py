import json
import unittest

from throughputkit.report import Progress


class ProgressTests(unittest.TestCase):
    def test_rate_and_fraction(self):
        p = Progress(label="upload", bytes_done=500, bytes_total=1000, seconds_elapsed=5)
        self.assertEqual(p.rate_bytes_per_sec, 100)
        self.assertEqual(p.fraction_done, 0.5)

    def test_eta_extrapolates_from_current_rate(self):
        p = Progress(label="upload", bytes_done=500, bytes_total=1000, seconds_elapsed=5)
        self.assertEqual(p.eta_seconds, 5)

    def test_eta_is_none_before_any_progress(self):
        # No bytes moved yet means no rate to extrapolate an ETA from.
        p = Progress(label="upload", bytes_done=0, bytes_total=1000, seconds_elapsed=5)
        self.assertIsNone(p.eta_seconds)

    def test_eta_zero_once_done(self):
        p = Progress(label="upload", bytes_done=1000, bytes_total=1000, seconds_elapsed=5)
        self.assertEqual(p.eta_seconds, 0.0)

    def test_eta_zero_when_overshooting_total(self):
        p = Progress(label="upload", bytes_done=1200, bytes_total=1000, seconds_elapsed=5)
        self.assertEqual(p.eta_seconds, 0.0)
        self.assertEqual(p.fraction_done, 1.0)

    def test_zero_elapsed_gives_zero_rate(self):
        p = Progress(label="upload", bytes_done=0, bytes_total=1000, seconds_elapsed=0)
        self.assertEqual(p.rate_bytes_per_sec, 0.0)
        self.assertIsNone(p.eta_seconds)

    def test_zero_total_is_considered_done(self):
        p = Progress(label="upload", bytes_done=0, bytes_total=0, seconds_elapsed=5)
        self.assertEqual(p.fraction_done, 1.0)
        self.assertEqual(p.eta_seconds, 0.0)

    def test_to_human(self):
        p = Progress(label="upload", bytes_done=500, bytes_total=1000, seconds_elapsed=5)
        self.assertEqual(p.to_human(), "upload: 500 B/1000 B (50%) at 100 B/s, ETA 5s")

    def test_to_human_unknown_eta(self):
        p = Progress(label="upload", bytes_done=0, bytes_total=1000, seconds_elapsed=5)
        self.assertIn("ETA unknown", p.to_human())

    def test_render_json(self):
        p = Progress(label="upload", bytes_done=500, bytes_total=1000, seconds_elapsed=5)
        payload = json.loads(p.render(as_json=True))
        self.assertEqual(payload["bytes_done"], 500)
        self.assertEqual(payload["bytes_total"], 1000)
        self.assertEqual(payload["bytes_per_sec"], 100)
        self.assertEqual(payload["eta_seconds"], 5)


if __name__ == "__main__":
    unittest.main()
