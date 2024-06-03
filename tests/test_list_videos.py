import json
from datetime import datetime
from typing import List

from pydantic import BaseModel

from tests.utils import read_test_file, FILE_WITH_PAGE_HEADER_RENDERER, EXPECTED_VIDEOS
from youtube_simple_scraper.list_videos import ApiVideoListRepository, Video
import unittest


class VideoList(BaseModel):
    videos: List[Video]


class TestApiVideoListRepository(unittest.TestCase):

    def test_extract_videos_from_tab_renderer(self):
        file = read_test_file(FILE_WITH_PAGE_HEADER_RENDERER)
        repository = ApiVideoListRepository()
        file_dict = json.loads(file)
        videos = repository._extract_raw_videos(file_dict)
        exp_json = read_test_file(EXPECTED_VIDEOS)
        expected_videos = VideoList.model_validate_json(exp_json).videos
        self.assertIsNotNone(videos)
        self.assertEqual(len(videos), len(expected_videos))
        for i in range(len(videos)):
            self.assertIsNotNone(videos[i].date)
            videos[i].date = datetime.now()
            expected_videos[i].date = videos[i].date
            self.assertEqual(videos[i], expected_videos[i])
        self.assertEqual(videos, expected_videos)
