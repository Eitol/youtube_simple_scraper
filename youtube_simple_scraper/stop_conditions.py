from typing import List

from youtube_simple_scraper.entities import ListVideoStopCondition, ListCommentStopCondition, Video, VideoComment


class ListVideoMaxPagesStopCondition(ListVideoStopCondition):
    def __init__(self, max_pages: int):
        self._max_pages = max_pages

    def should_stop(self, videos: List[Video], page: int) -> bool:
        return page >= self._max_pages


class ListVideoNeverStopCondition(ListVideoStopCondition):
    def should_stop(self, videos: List[Video], page: int) -> bool:
        return False


class ListCommentMaxPagesStopCondition(ListCommentStopCondition):
    def __init__(self, max_pages: int):
        self._max_pages = max_pages

    def should_stop(self, video: Video, comments: List[VideoComment], page: int) -> bool:
        return page >= self._max_pages


class ListCommentNeverStopCondition(ListCommentStopCondition):
    def should_stop(self, video: Video, comments: List[VideoComment], page: int) -> bool:
        return False
