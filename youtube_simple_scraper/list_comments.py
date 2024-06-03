import abc
from typing import List

from youtube_simple_scraper.entities import VideoComment
from youtube_simple_scraper.list_videos_request import get_comments_from_api


class CommentRepository(abc.ABC):
    @abc.abstractmethod
    def next(self, video_id: str) -> List[VideoComment]:
        pass


class ApiCommentRepository(CommentRepository):

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
