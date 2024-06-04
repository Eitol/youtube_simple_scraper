from youtube_simple_scraper.entities import GetChannelOptions
from youtube_simple_scraper.list_video_comments import ApiVideoCommentRepository, ApiShortVideoCommentRepository
from youtube_simple_scraper.list_videos import ApiChannelRepository
from youtube_simple_scraper.logger import build_default_logger
from youtube_simple_scraper.network import Requester
from youtube_simple_scraper.stop_conditions import ListCommentMaxPagesStopCondition, \
    ListVideoMaxPagesStopCondition

if __name__ == '__main__':
    Requester.request_rate_per_second = 0.5
    Requester.min_sleep_time_sec = 1
    Requester.max_sleep_time_sec = 5
    Requester.long_sleep_time_sec = 120
    Requester.long_sleep_after_requests = 10
    logger = build_default_logger()
    video_comment_repo = ApiVideoCommentRepository()
    short_comment_repo = ApiShortVideoCommentRepository()
    repo = ApiChannelRepository(
        video_comment_repo=video_comment_repo,
        shorts_comment_repo=short_comment_repo,
        logger=logger,
    )
    opts = GetChannelOptions(
        list_video_stop_conditions=[ListVideoMaxPagesStopCondition(2)],
        list_video_comment_stop_conditions=[ListCommentMaxPagesStopCondition(2)],
        list_short_stop_conditions=[ListVideoMaxPagesStopCondition(2)],
        list_short_comment_stop_conditions=[ListCommentMaxPagesStopCondition(2)]
    )
    channel_ = repo.get_channel("BancoFalabellaChile", opts)
    print(channel_.model_dump_json(indent=2))
