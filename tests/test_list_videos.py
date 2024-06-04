import json
from datetime import datetime
from typing import List

from pydantic import BaseModel

from tests.utils import read_test_file, FILE_WITH_PAGE_HEADER_RENDERER, EXPECTED_VIDEOS
from youtube_simple_scraper.entities import GetChannelOptions
from youtube_simple_scraper.list_video_comments import ApiVideoCommentRepository, ApiShortVideoCommentRepository
from youtube_simple_scraper.list_videos import ApiChannelRepository, Video
import unittest

from youtube_simple_scraper.logger import build_default_logger
from youtube_simple_scraper.stop_conditions import ListVideoMaxPagesStopCondition, ListCommentMaxPagesStopCondition


class VideoList(BaseModel):
    videos: List[Video]


class TestApiVideoListRepository(unittest.TestCase):

    def test_extract_videos_from_tab_renderer(self):
        logger = build_default_logger()
        video_comment_repo = ApiVideoCommentRepository()
        short_comment_repo = ApiShortVideoCommentRepository()
        repo = ApiChannelRepository(
            video_comment_repo=video_comment_repo,
            shorts_comment_repo=short_comment_repo,
            logger=logger,
        )
        opts = GetChannelOptions(
            list_video_stop_conditions=[ListVideoMaxPagesStopCondition(1)],
            list_video_comment_stop_conditions=[ListCommentMaxPagesStopCondition(1)],
            list_short_stop_conditions=[ListVideoMaxPagesStopCondition(1)],
            list_short_comment_stop_conditions=[ListCommentMaxPagesStopCondition(1)]
        )
        channel_ = repo.get_channel("IbaiLlanos", opts)
        self.assertEqual(channel_.id, "UCaY_-ksFSQtTGk0y1HA_3YQ")
        self.assertGreaterEqual(len(channel_.videos), 20)
        self.assertGreaterEqual(len(channel_.shorts), 40)
