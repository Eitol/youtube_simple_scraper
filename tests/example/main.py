from youtube_simple_scraper.entities import GetChannelOptions
from youtube_simple_scraper.list_comments import ApiCommentRepository
from youtube_simple_scraper.list_videos import ApiVideoListRepository
from youtube_simple_scraper.logger import build_default_logger
from youtube_simple_scraper.stop_conditions import ListCommentMaxPagesStopCondition, \
    ListVideoMaxPagesStopCondition

if __name__ == '__main__':
    logger = build_default_logger()
    comment_repo = ApiCommentRepository()
    repo = ApiVideoListRepository(comment_repo=comment_repo, logger=logger)
    opts = GetChannelOptions(
        list_video_stop_conditions=[ListVideoMaxPagesStopCondition(2)],
        list_comment_stop_conditions=[ListCommentMaxPagesStopCondition(2)]
    )
    channel_ = repo.get_channel("IbaiLlanos", opts)
    print(channel_.model_dump_json(indent=2))
