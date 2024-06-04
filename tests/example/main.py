from youtube_simple_scraper.entities import GetChannelOptions
from youtube_simple_scraper.list_video_comments import ApiVideoCommentRepository, ApiShortVideoCommentRepository
from youtube_simple_scraper.list_videos import ApiVideoListRepository
from youtube_simple_scraper.logger import build_default_logger
from youtube_simple_scraper.stop_conditions import ListCommentMaxPagesStopCondition, \
    ListVideoMaxPagesStopCondition

if __name__ == '__main__':
    logger = build_default_logger()
    video_comment_repo = ApiVideoCommentRepository()
    short_comment_repo = ApiShortVideoCommentRepository()
    repo = ApiVideoListRepository(
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
    channel_ = repo.get_channel("IbaiLlanos", opts)
    print(channel_.model_dump_json(indent=2))
