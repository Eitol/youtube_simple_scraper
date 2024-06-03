import json
from typing import List, Tuple

import dateparser
import requests

from youtube_simple_scraper.entities import GetChannelOptions, Video, Channel, VideoComment, VideoListRepository
from youtube_simple_scraper.list_comments import CommentRepository, ApiCommentRepository
from youtube_simple_scraper.list_videos_request import build_list_videos_request_payload, \
    build_list_videos_request_headers, find_channel_basic_info
from youtube_simple_scraper.stop_conditions import ListVideoNeverStopCondition, ListCommentMaxPagesStopCondition


class ApiVideoListRepository(VideoListRepository):

    def __init__(self, comment_repo: CommentRepository):
        self._comment_repo = comment_repo

    def get_channel(self, channel_name: str, opts: GetChannelOptions) -> Channel:
        page_count = 0
        response_body = find_channel_basic_info(channel_name)
        for attempt in range(0, 3):
            channel, continuation_token, is_valid = self._extract_channel_basic_info(response_body)
            if not is_valid:
                continue
            while True:
                if self._should_stop_fetch_videos(channel.videos, page_count, opts):
                    break
                response_body = self._send_next_video_page_request(channel_name, channel.id, continuation_token)
                videos = self._extract_raw_videos(response_body)
                continuation_token = self._extract_token(response_body)
                channel.videos.extend(videos)
                comments_page = 0
                for video in videos:
                    if self._should_stop_fetch_video_comments(video, video.comments, comments_page, opts):
                        break
                    comments = self._comment_repo.next(video.id)
                    video.comments.extend(comments)
                if not continuation_token:
                    break
                page_count += 1
            return channel

    @staticmethod
    def _should_stop_fetch_videos(videos: List[Video], page: int, opts: GetChannelOptions) -> bool:
        return any([condition.should_stop(videos, page) for condition in opts.list_video_stop_conditions])

    @staticmethod
    def _should_stop_fetch_video_comments(video: Video, comments: List[VideoComment], page: int,
                                          opts: GetChannelOptions) -> bool:
        return any([condition.should_stop(video, comments, page) for condition in opts.list_comment_stop_conditions])

    @staticmethod
    def _send_next_video_page_request(channel_id: str, browse_id: str, continuation_token: str) -> dict:
        payload = build_list_videos_request_payload(channel_id, browse_id, continuation_token)
        headers = build_list_videos_request_headers(channel_id)
        payload_json = json.dumps(payload)
        url = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
        resp = requests.post(url, data=payload_json, headers=headers)
        return resp.json()

    @staticmethod
    def _abbreviate_number_to_number(number: str) -> int:
        if '.' in number:
            number = number.replace('.', '')
            if 'M' in number:
                number = number.replace('M', '00000')
            elif 'K' in number:
                number = number.replace('K', '00')
        else:
            if 'M' in number:
                number = number.replace('M', '000000')
            elif 'K' in number:
                number = number.replace('K', '000')
        try:
            subscriber_count = int(number.split(" ")[0].replace(",", ""))
        except:
            subscriber_count = 0
        return subscriber_count

    def _extract_channel_basic_info(self, response_body: dict) -> Tuple[Channel, str, bool]:
        if "header" not in response_body:
            return self._build_empty_channel(), "", False
        if "c4TabbedHeaderRenderer" in response_body["header"]:
            channel, token = self._extract_channel_from_c4_tabbed_header_renderer_tag(response_body)
        else:
            channel, token = self._extract_channel_from_page_header_renderer_tag(response_body)
        channel.videos = self._extract_raw_videos(response_body)
        return channel, token, True

    def _extract_raw_videos(self, response_body: dict) -> List[Video]:
        videos = self._extract_videos_from_next_videos_page_response(response_body)
        if len(videos) > 0:
            return self._adapt_raw_videos(videos)
        try:
            tabs = response_body["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
        except:
            return []

        for tab in tabs:
            try:
                tab_renderer = tab["tabRenderer"]
            except:
                return []
            if 'content' not in tab_renderer:
                continue
            raw_videos: List[dict] = self._extract_raw_videos_from_contents_tag(tab_renderer)
            return self._adapt_raw_videos(raw_videos)

    @classmethod
    def _build_empty_channel(cls):
        channel: Channel = Channel.construct(
            id="",
            title="",
            name="",
            description="",
            subscriber_count=0,
            video_count=0,
            view_count=0,
            thumbnail_url="",
            url="",
            videos=[]
        )
        return channel

    @classmethod
    def _extract_videos_from_next_videos_page_response(cls, response_body: dict) -> List[dict]:
        if "onResponseReceivedActions" not in response_body:
            return []
        raw_videos = []
        for ra in response_body["onResponseReceivedActions"]:
            if 'appendContinuationItemsAction' not in ra:
                continue
            for ci in ra['appendContinuationItemsAction']['continuationItems']:
                if 'richItemRenderer' not in ci:
                    continue
                rir = ci['richItemRenderer']
                if 'content' not in rir:
                    continue
                content = rir['content']
                if 'videoRenderer' not in content:
                    continue
                raw_videos.append(content['videoRenderer'])
        return raw_videos

    @classmethod
    def _extract_channel_from_page_header_renderer_tag(cls, response_body: dict) -> Tuple[Channel, str]:
        channel = cls._build_empty_channel()
        t = response_body["header"]["pageHeaderRenderer"]
        rows = t['content']['pageHeaderViewModel']['metadata']['contentMetadataViewModel']['metadataRows']
        for row in rows:
            for part in row['metadataParts']:
                if 'content' in part:
                    content = part['content']
                elif 'text' in part:
                    content = part['text']['content']
                else:
                    continue
                if 'subscriber' in content:
                    subscriber_count_text = content.split(' ')[0]
                    subscriber_count_text = subscriber_count_text.split(' ')[0]
                    channel.subscriber_count = cls._abbreviate_number_to_number(subscriber_count_text)
                elif 'video' in content:
                    video_count_text = content.split(' ')[0]
                    channel.video_count = cls._abbreviate_number_to_number(video_count_text)
        m = response_body["metadata"]["channelMetadataRenderer"]
        channel.id = m['externalId']
        channel.title = m['title']
        channel.description = m['description']
        token = cls._extract_token(response_body)
        return channel, token

    @classmethod
    def _extract_channel_from_c4_tabbed_header_renderer_tag(cls, response_body: dict) -> Tuple[Channel, str]:
        channel = cls._build_empty_channel()
        t = response_body["header"]["c4TabbedHeaderRenderer"]
        channel.video_count = int(t['videosCountText']['runs'][0]['text'])
        channel.id = t['channelId']
        channel.title = t['title']
        subscriber_count_text = t['subscriberCountText']['simpleText']
        channel.subscriber_count = cls._abbreviate_number_to_number(subscriber_count_text)
        channel.description = t['tagline']["channelTaglineRenderer"]["content"]
        token = cls._extract_token(response_body)
        return channel, token

    @classmethod
    def _extract_raw_videos_from_contents_tag(cls, tab_renderer) -> List[dict]:
        raw_videos: List[dict] = []
        if "sectionListRenderer" in tab_renderer["content"]:
            contents = tab_renderer["content"]["sectionListRenderer"]["contents"]
        else:
            contents = tab_renderer["content"]["richGridRenderer"]["contents"]
        for content in contents:
            if "itemSectionRenderer" in content:
                c = content["itemSectionRenderer"]["contents"][0]["shelfRenderer"]["content"]
            else:
                c = content
            if "horizontalListRenderer" in c:
                hlr = c["horizontalListRenderer"]
                for item in hlr["items"]:
                    raw_videos.append(item['gridVideoRenderer'])
            elif "expandedShelfContentsRenderer" in c:
                hlr = c["expandedShelfContentsRenderer"]
                for item in hlr["items"]:
                    raw_videos.append(item['videoRenderer'])
            elif "richItemRenderer" in c:
                raw_videos.append(c["richItemRenderer"]["content"]["videoRenderer"])
            else:
                continue
        return raw_videos

    @staticmethod
    def _extract_token(response_body: dict) -> str:
        try:
            tabs = response_body["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
            for tab in tabs:
                if "content" not in tab["tabRenderer"]:
                    continue
                contents = tab["tabRenderer"]["content"]["richGridRenderer"]["contents"]
                for i in range(len(contents) - 1, -1, -1):
                    if "continuationItemRenderer" not in contents[i] or "continuationEndpoint" not in \
                            contents[i]["continuationItemRenderer"]:
                        continue
                    return contents[i]["continuationItemRenderer"]["continuationEndpoint"][
                        "continuationCommand"]["token"]
        except:
            pass
        try:
            if "onResponseReceivedActions" in response_body:
                for action in response_body["onResponseReceivedActions"]:
                    if "appendContinuationItemsAction" in action:
                        for item in action["appendContinuationItemsAction"]["continuationItems"]:
                            if "continuationItemRenderer" in item:
                                if "continuationEndpoint" in item["continuationItemRenderer"]:
                                    return item["continuationItemRenderer"]["continuationEndpoint"][
                                        "continuationCommand"]["token"]
        except:
            pass

        try:
            return response_body["header"]["pageHeaderRenderer"]["content"]["pageHeaderViewModel"][
                "description"]["descriptionPreviewViewModel"]["rendererContext"]["commandContext"][
                "onTap"]["innertubeCommand"]["showEngagementPanelEndpoint"]["engagementPanel"][
                "engagementPanelSectionListRenderer"]["content"]["sectionListRenderer"][
                "contents"][0]["itemSectionRenderer"]["contents"][0]["continuationItemRenderer"][
                "continuationEndpoint"]["continuationCommand"]["token"]
        except:
            pass
        try:
            return response_body["header"]["pageHeaderRenderer"]["content"]["pageHeaderViewModel"][
                "attribution"]["attributionViewModel"][
                "suffix"]["commandRuns"][0]["onTap"]["innertubeCommand"]["showEngagementPanelEndpoint"][
                "engagementPanel"]["engagementPanelSectionListRenderer"]["content"]["sectionListRenderer"]["contents"][
                0]["itemSectionRenderer"]["contents"][0]["continuationItemRenderer"]["continuationEndpoint"][
                "continuationCommand"]["token"]
        except:
            pass
        try:
            return response_body['header']['c4TabbedHeaderRenderer']['tagline']['channelTaglineRenderer'][
                'moreEndpoint']['showEngagementPanelEndpoint'][
                'engagementPanel']['engagementPanelSectionListRenderer']['content'][
                'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0][
                'continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
        except:
            pass
        return ""

    def _adapt_raw_videos(self, raw_videos: List[dict]) -> List[Video]:
        extracted_videos: List[Video] = []
        for raw_video in raw_videos:
            view_count_text = raw_video.get("viewCountText", {}).get("simpleText", '')
            view_count = 0
            if view_count_text:
                view_count = int(view_count_text.split(' ')[0].replace(",", ""))
            human_date = raw_video.get("publishedTimeText", {}).get("simpleText", "")
            date = dateparser.parse(human_date, languages=["en"])
            title = ''
            if "title" in raw_video:
                if "simpleText" in raw_video["title"]:
                    title = raw_video["title"]["simpleText"]
                elif "runs" in raw_video["title"]:
                    title = raw_video["title"]["runs"][0]["text"]
            description = raw_video.get("description", {}).get("simpleText", "")
            if not description:
                try:
                    description = raw_video['descriptionSnippet']['runs'][0]['text']
                except:
                    pass
            thumbnail_url = raw_video.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url", "")
            if not thumbnail_url:
                try:
                    thumbnail_url = \
                        raw_video['richThumbnail']['movingThumbnailRenderer']['movingThumbnailDetails']['thumbnails'][0]
                except:
                    pass
            v = Video(
                id=raw_video["videoId"],
                title=title,
                description=description,
                date=date,
                view_count=view_count,
                like_count=int(raw_video.get("likes", 0)),
                dislike_count=int(raw_video.get("dislikes", 0)),
                comment_count=int(raw_video.get("commentCount", 0)),
                thumbnail_url=thumbnail_url,
                comments=[],
            )
            extracted_videos.append(v)
        return self._sort_videos_by_date(extracted_videos)

    @staticmethod
    def _sort_videos_by_date(video_list: List[Video]) -> List[Video]:
        return sorted(video_list, key=lambda x: x.date, reverse=True)

    @classmethod
    def _adapt_raw_comments(cls, raw_comments: dict):
        pass


if __name__ == '__main__':
    comment_repo = ApiCommentRepository()
    repo = ApiVideoListRepository(comment_repo=comment_repo)
    opts = GetChannelOptions(
        list_video_stop_conditions=[ListVideoNeverStopCondition()],
        list_comment_stop_conditions=[ListCommentMaxPagesStopCondition(100)]
    )
    channel_ = repo.get_channel("BancoEstado", opts)
    print(channel_)
