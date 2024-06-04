import unittest
from youtube_simple_scraper.counters import comment_counter_to_int


class TestCommentCounterToInt(unittest.TestCase):

    def test_comment_counter_to_int_views(self):
        test_cases = [
            ("1 Views", 1),
            ("12 Views", 12),
            ("1K Views", 1000),
            ("1.2K Views", 1200),
            ("12.3K Views", 12300),
            ("123.4K Views", 123400),
            ("123K Views", 123000),
            ("1.23K Views", 1230),
            ("1.234M Views", 1234000),
            ("12M Views", 12000000),
            ("12.34M Views", 12340000),
            ("12.345M Views", 12345000),
            ("1K  Views  Multi Space 1 K", 1000),
            ("1k", 1000),
            ("1m", 1000000),
            ("1 m", 1000000),
            ("123.4  k views", 123400),
            ("123.4k Likes", 123400),
            ("123.456 ", 123456),
            ("12 m", 12000000),
        ]
        for test_input, expected_output in test_cases:
            with self.subTest(msg=test_input):
                self.assertEqual(comment_counter_to_int(test_input), expected_output)


if __name__ == '__main__':
    unittest.main()
