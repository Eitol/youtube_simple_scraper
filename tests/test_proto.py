import base64
import unittest

from youtube_simple_scraper.continuation_token import CommentsContinuationTokenBuilder
from youtube_simple_scraper.proto import continuation


class TestContinuationToken(unittest.TestCase):

    def test_parse_continuation_for_video_list(self):
        expected = "CggIgAQVF7fROBIFCIcgGAASBQiIIBgAEgUInSAYARIFCIkgGAASBQioIBgAGAAiDQoLCNXK8rIGEKj4iS8"
        p = CommentsContinuationTokenBuilder.build_params_str_for_video_list(1717347669)
        self.assertEqual(p, expected)
        serializedb64 = CommentsContinuationTokenBuilder.build_video_list_token("bkRcuK2i7oM", 60, 1717347669)
        expected = ("Eg0SC2JrUmN1SzJpN29NGAYyjgEKZWdldF9uZXdlc3RfZmlyc3QtLUNnZ0lnQVFW"
                    "RjdmUk9CSUZDSWNnR0FBU0JRaUlJQmdBRWdVSW5TQVlBUklGQ0lrZ0dBQVNCUWlvSUJnQUdBQWlEUW9MQ0"
                    "5YSzhySUdFS2o0aVM4IhEiC2JrUmN1SzJpN29NMAF4ASg8QhBjb21tZW50cy1zZWN0aW9u")
        self.assertEqual(serializedb64, expected)

    def test_parse_continuation_for_short_list(self):
        expected = ("4qmFsgJ-Eh5GRWNvbW1lbnRfc2hvcnRzX3dlYl90b3BfbGV2ZWwaXHFnTkNJ"
                    "aFFpQzFBNWIyOHRja0psTjA5Vk1BQjRBc2dCQURBQlFpaHphRzl5ZEhNdFpX"
                    "NW5ZV2RsYldWdWRDMXdZVzVsYkMxamIyMXRaVzUwY3kxelpXTjBhVzl1")
        p = CommentsContinuationTokenBuilder.build_start_short_comment_cont_token("P9oo-rBe7OU")
        self.assertEqual(p, expected)
