import abc
import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import List

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


class Video(BaseModel):
    id: str
    title: str
    description: str
    date: datetime.datetime
    view_count: int
    like_count: int
    dislike_count: int
    comment_count: int
    thumbnail_url: str
    comments: List[VideoComment] = []

    @property
    def url(self):
        return f'https://www.youtube.com/watch?v={self.id}'


class Channel(BaseModel):
    id: str
    title: str
    name: str
    description: str
    subscriber_count: int
    video_count: int
    view_count: int
    thumbnail_url: str
    url: str
    videos: List[Video]


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
    list_comment_stop_conditions: List[ListCommentStopCondition]


class VideoListRepository(abc.ABC):
    @abc.abstractmethod
    def get_channel(self, channel_id: str, opts: GetChannelOptions) -> List[Video]:
        raise NotImplementedError()
