from django.core.cache import cache
from django.test import SimpleTestCase

from common.ratelimit import allow_attempt, is_limited, register_hit
from common.tests.tests_mixins import RateLimitCacheResetMixin

LIMIT = 3
WINDOW = 3600


class RateLimitTests(RateLimitCacheResetMixin, SimpleTestCase):
    def test_limit_triggers_on_attempt_after_limit(self):
        for _ in range(LIMIT):
            self.assertTrue(allow_attempt("form", "1.1.1.1", LIMIT, WINDOW))
        self.assertFalse(allow_attempt("form", "1.1.1.1", LIMIT, WINDOW))

    def test_different_ips_are_counted_separately(self):
        for _ in range(LIMIT + 1):
            allow_attempt("form", "1.1.1.1", LIMIT, WINDOW)
        self.assertTrue(allow_attempt("form", "2.2.2.2", LIMIT, WINDOW))

    def test_different_forms_are_counted_separately(self):
        for _ in range(LIMIT + 1):
            allow_attempt("form_a", "1.1.1.1", LIMIT, WINDOW)
        self.assertTrue(allow_attempt("form_b", "1.1.1.1", LIMIT, WINDOW))

    def test_window_resets(self):
        for _ in range(LIMIT + 1):
            allow_attempt("form", "1.1.1.1", LIMIT, WINDOW)
        cache.clear()  # имитация истечения окна
        self.assertTrue(allow_attempt("form", "1.1.1.1", LIMIT, WINDOW))

    def test_is_limited_does_not_count(self):
        for _ in range(10):
            self.assertFalse(is_limited("login", "1.1.1.1", LIMIT))
        for _ in range(LIMIT):
            register_hit("login", "1.1.1.1", WINDOW)
        self.assertTrue(is_limited("login", "1.1.1.1", LIMIT))