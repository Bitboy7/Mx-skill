"""Pruebas del limitador de tasa (sin red ni Telegram)."""

import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import bot.ratelimit as ratelimit  # noqa: E402


class RateLimiterTests(unittest.TestCase):
    def test_allows_up_to_max_then_blocks(self):
        limiter = ratelimit.RateLimiter(2, 60)
        self.assertEqual(limiter.check("u1"), (True, 0.0))
        self.assertEqual(limiter.check("u1"), (True, 0.0))
        allowed, retry_after = limiter.check("u1")
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)

    def test_limits_are_per_key(self):
        limiter = ratelimit.RateLimiter(1, 60)
        self.assertTrue(limiter.check("u1")[0])
        self.assertFalse(limiter.check("u1")[0])
        self.assertTrue(limiter.check("u2")[0])

    def test_global_limit_blocks_across_users(self):
        limiter = ratelimit.RateLimiter(0, 60, global_max_requests=2)
        self.assertTrue(limiter.check("u1")[0])
        self.assertTrue(limiter.check("u2")[0])
        allowed, retry_after = limiter.check("u3")
        self.assertFalse(allowed)
        self.assertGreater(retry_after, 0)

    def test_disabled_always_allows(self):
        limiter = ratelimit.RateLimiter(0, 60, global_max_requests=0)
        for _ in range(10):
            self.assertEqual(limiter.check("u1"), (True, 0.0))

    def test_reset_clears_state(self):
        limiter = ratelimit.RateLimiter(1, 60)
        self.assertTrue(limiter.check("u1")[0])
        self.assertFalse(limiter.check("u1")[0])
        limiter.reset("u1")
        self.assertTrue(limiter.check("u1")[0])

    def test_window_expires(self):
        limiter = ratelimit.RateLimiter(1, 1)
        self.assertTrue(limiter.check("u1")[0])
        future = ratelimit.time.monotonic() + 5
        with mock.patch.object(ratelimit.time, "monotonic", return_value=future):
            self.assertTrue(limiter.check("u1")[0])


if __name__ == "__main__":
    unittest.main()
