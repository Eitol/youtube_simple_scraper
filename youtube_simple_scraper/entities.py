import abc
import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel


class ReactionType(StrEnum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"


class Reaction(BaseModel):
    type: ReactionType
    count: int


class VideoComment(BaseModel):
    id: str
    text: str
    user: str
    date: datetime.datetime
    likes: int


class VideoType(StrEnum):
    VIDEO = "VIDEO"
    SHORT = "SHORT"


class Video(BaseModel):
    id: str
    title: str
    view_count: int
    thumbnail_url: str
    video_type: VideoType
    description: Optional[str] = ""
    date: Optional[datetime.datetime] = None
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    comments: List[VideoComment] = []

    @property
    def url(self):
        if self.video_type == VideoType.SHORT:
            return f'https://www.youtube.com/shorts/{self.id}'
        return f'https://www.youtube.com/watch?v={self.id}'


class Channel(BaseModel):
    id: str
    name: str
    target_id: str
    title: str
    description: str
    subscriber_count: int
    video_count: int
    url: str
    videos: List[Video]
    shorts: List[Video]


class ListVideoStopCondition(abc.ABC):
    @abc.abstractmethod
    def should_stop(self, videos: List[Video], page: int) -> bool:
        raise NotImplementedError()


class ListCommentStopCondition(abc.ABC):
    @abc.abstractmethod
    def should_stop(self, video: Video, comments: List[VideoComment], page: int) -> bool:
        raise NotImplementedError()


@dataclass
class GetChannelOptions:
    list_video_stop_conditions: List[ListVideoStopCondition]
    list_video_comment_stop_conditions: List[ListCommentStopCondition]
    list_short_stop_conditions: List[ListVideoStopCondition]
    list_short_comment_stop_conditions: List[ListCommentStopCondition]


class ChannelRepository(abc.ABC):
    @abc.abstractmethod
    def get_channel(self, channel_id: str, opts: GetChannelOptions) -> List[Video]:
        raise NotImplementedError()
