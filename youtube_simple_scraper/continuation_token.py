import base64
import datetime
from typing import Optional

from youtube_simple_scraper.proto import continuation


class CommentsContinuationTokenBuilder:

    @classmethod
    def build_video_list_token(cls, video_id: str, offset: int, timestamp: Optional[int] = 0) -> str:
        if offset > 0:
            if timestamp == 0:
                timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
            sub_message = cls.build_params_str_for_video_list(timestamp)
            msg = f"get_newest_first--{sub_message}"
        else:
            msg = ""
        token = continuation.ContinuationToken(
            video_id=continuation.VideoIdSubMessage(video_id=video_id),
            field_3=6,
            sub_messsage_6=continuation.ParamsSubMessage(
                string_1=msg,
                sub_messsage_4=continuation.ParamsSubSubMessage(
                    video_id=video_id,
                    int_6=1,
                    int_15=1
                ),
                offset=offset,
                string_8="comments-section"
            )
        )
        serialized_message = token.SerializeToString()
        return base64.urlsafe_b64encode(serialized_message).decode("utf-8").replace("=", "%3D")

    @staticmethod
    def build_params_str_for_video_list(timestamp: int):
        params_message = continuation.ParamsMessage()
        params_message.field_1 = continuation.Field1SubMessage(f1=512, f2=953267991)

        params_message.field_array_2 = [
            continuation.TwinIntMessage(int_1=4103, int_3=0),
            continuation.TwinIntMessage(int_1=4104, int_3=0),
            continuation.TwinIntMessage(int_1=4125, int_3=1),
            continuation.TwinIntMessage(int_1=4105, int_3=0),
            continuation.TwinIntMessage(int_1=4136, int_3=0),
        ]

        params_message.int_3 = 0

        field_4_sub_message = continuation.Field4SubMessage(sub_msg=continuation.TwinInt12Message(
            timestamp=timestamp,
            int_2=98729000
        ))

        params_message.sub_messsage_4 = field_4_sub_message
        b = params_message.SerializeToString()
        params_b64 = base64.urlsafe_b64encode(b).decode("utf-8").replace("=", "")
        return params_b64

    @classmethod
    def build_start_short_comment_cont_token(cls, short_id: str) -> str:
        p = continuation.ShortsRequestPagination(
            sub_message_1=continuation.ShortsRequestPaginationSub(
                sub_message_4=continuation.ShortsRequestPaginationSubSub(
                    video_id=short_id,
                    uint_6=0,
                    uint_15=2,
                    uint_25=0
                ),
                uint_6=1,
                string_8="shorts-engagement-panel-comments-section".encode("utf-8")
            )
        )
        pagination_b64 = base64.urlsafe_b64encode(p.SerializeToString()).decode("utf-8").replace("=", "")
        token = continuation.ShortContinuationToken(
            params=continuation.ShortsRequestSub(
                sort_type=b"FEcomment_shorts_web_top_level",
                pagination=pagination_b64.encode("utf-8")
            )
        )
        serialized_message = token.SerializeToString()
        return base64.urlsafe_b64encode(serialized_message).decode("utf-8").replace("=", "%3D")
