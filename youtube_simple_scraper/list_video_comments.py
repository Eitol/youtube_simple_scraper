import abc
from typing import List

from youtube_simple_scraper.entities import VideoComment
from youtube_simple_scraper.list_short import get_shorts, get_short_comments
from youtube_simple_scraper.list_videos_request import get_comments_from_api


class VideoCommentRepository(abc.ABC):
    @abc.abstractmethod
    def next(self, video_id: str) -> List[VideoComment]:
        pass


class ApiVideoCommentRepository(VideoCommentRepository):

    def __init__(self):
        self._tokens = {}

    def next(self, video_id: str) -> List[VideoComment]:
        raw_comments, next_token = get_comments_from_api(video_id, self._tokens.get(video_id, ""))
        self._tokens[video_id] = next_token
        comments: List[VideoComment] = []
        for comment in raw_comments:
            comments.append(VideoComment(
                id=comment["id"],
                text=comment["comment_text"],
                user=comment["author"],
                date=comment["published_time"],
                likes=comment["likes"]
            ))
        return comments


class ApiShortVideoCommentRepository(VideoCommentRepository):
    def __init__(self):
        self._tokens = {}

    def next(self, short_id: str) -> List[VideoComment]:
        token = ""
        if short_id in self._tokens:
            token = self._tokens[short_id]
        raw_comments, s_token = get_short_comments(short_id, token)
        comments: List[VideoComment] = []
        for comment in raw_comments:
            comments.append(VideoComment(
                id=comment["id"],
                text=comment["text"],
                user=comment["author"],
                date=comment["date"],
                likes=comment["like"]
            ))
        return comments
