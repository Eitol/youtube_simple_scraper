import datetime
import json
from typing import Tuple, List

import dateparser
import requests

from youtube_simple_scraper.continuation_token import CommentsContinuationTokenBuilder
from youtube_simple_scraper.counters import comment_counter_to_int

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/125.0.0.0 Safari/537.36,gzip(gfe)")


def build_list_videos_request_headers(channel_id: str) -> dict:
    return {
        "accept": "*/*",
        "accept-language": "en",
        "content-type": "application/json",
        "origin": "https://www.youtube.com",
        "priority": "u=1, i",
        "referer": f"https://www.youtube.com/@{channel_id}",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-arch": '"arm"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version": '"125.0.6422.78"',
        "sec-ch-ua-full-version-list": '"Google Chrome";v="125.0.6422.78", '
                                       '"Chromium";v="125.0.6422.78", '
                                       '"Not.A/Brand";v="24.0.0.0"',
        "sec-ch-ua-mobile": '?0',
        "sec-ch-ua-model": '"',
        "sec-ch-ua-platform": '"macOS"',
        "sec-ch-ua-platform-version": '"14.4.1"',
        "sec-ch-ua-wow64": '?0',
        "sec-fetch-dest": 'empty',
        "sec-fetch-mode": 'same-origin',
        "sec-fetch-site": "same-origin",
        "user-agent": USER_AGENT,
        "x-youtube-bootstrap-logged-in": 'false',
        "x-youtube-client-name": '1',
        "x-youtube-client-version": '2.20240530.02.00'
    }


def build_list_videos_request_payload(channel_id: str, browse_id: str, continuation_token: str) -> dict:
    base = {
        "context": {
            "client": {
                "deviceMake": "Apple",
                "userAgent": USER_AGENT,
                "clientName": "WEB",
                "clientVersion": "2.20240530.02.00",
                "osName": "Macintosh",
                "osVersion": "10_15_7",
                "originalUrl": f"https://www.youtube.com/@{channel_id}",
                "screenPixelDensity": 2,
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "screenDensityFloat": 2,
                "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                "browserName": "Chrome",
                "browserVersion": "125.0.0.0",
                "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                                "application/signed-exchange;v=b3;q=0.7",
                "screenWidthPoints": 1526,
                "screenHeightPoints": 1546,
                "utcOffsetMinutes": -240,
            },
            "user": {
                "lockedSafetyMode": True
            },
            "request": {
                "useSsl": True,
                "internalExperimentFlags": [],
                "consistencyTokenJars": []
            },
        },
        "browseId": browse_id,
    }
    if continuation_token:
        base["continuation"] = continuation_token
    return base


def find_channel_basic_info(channel_id: str) -> dict:
    url = f"https://www.youtube.com/@{channel_id}/videos"
    headers = {
        'accept': 'application/json',
        'accept-language': 'en,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        'cache-control': 'max-age=0',
        'service-worker-navigation-preload': 'true',
        'upgrade-insecure-requests': '1',
        'user-agent': USER_AGENT,
    }
    response = requests.request("GET", url, headers=headers)
    start_tag = "ytInitialData = "
    return _extract_channel_basic_info_from_html(response, start_tag)


def get_comments_from_api(video_id: str, token: str = "") -> Tuple[List[dict], str]:
    if token:
        continuation_token = token
    else:
        continuation_token = CommentsContinuationTokenBuilder.build_video_list_token(video_id, 0)
    url = "https://www.youtube.com/youtubei/v1/next?prettyPrint=false"
    payload = json.dumps({
        "context": {
            "client": {
                "deviceModel": "",
                "userAgent": USER_AGENT,
                "clientName": "WEB",
                "clientVersion": "2.20240530.02.00",
                "screenPixelDensity": 2,
                "platform": "DESKTOP",
                "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                "screenDensityFloat": 2,
                "userInterfaceTheme": "USER_INTERFACE_THEME_DARK",
                "timeZone": "America/Santiago",
                "browserName": "Chrome",
                "browserVersion": "125.0.0.0",
                "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                                "application/signed-exchange;v=b3;q=0.7",
                "screenWidthPoints": 1501,
                "screenHeightPoints": 1461,
                "utcOffsetMinutes": -240,
                "connectionType": "CONN_CELLULAR_4G",
                "memoryTotalKbytes": "8000000"
            },
            "user": {
                "lockedSafetyMode": False
            },
            "request": {
                "useSsl": True,
                "internalExperimentFlags": [],
                "consistencyTokenJars": []
            }
        },
        "continuation": continuation_token
    })
    headers = {
        'accept': '*/*',
        'accept-language': 'en',
        'content-type': 'application/json',
        'origin': 'https://www.youtube.com',
        'x-youtube-client-version': '2.20240530.02.00',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    comments, token, is_valid = _extract_raw_comments(response)
    if not is_valid:
        return get_comments_from_api(video_id, token)
    return comments, token


def _extract_raw_comments(response) -> Tuple[List[dict], str, bool]:
    r = response.json()
    comments = []
    continuation_token = ""
    if "onResponseReceivedEndpoints" in r:
        for ep in r["onResponseReceivedEndpoints"]:
            if "appendContinuationItemsAction" not in ep:
                continue
            for ci in ep["appendContinuationItemsAction"]["continuationItems"]:
                if "continuationItemRenderer" in ci:
                    continuation_token = ci["continuationItemRenderer"]["continuationEndpoint"][
                        "continuationCommand"]["token"]
    if "frameworkUpdates" in r:
        for ep in r["frameworkUpdates"]["entityBatchUpdate"]["mutations"]:
            if "commentEntityPayload" in ep["payload"]:
                prop = ep["payload"]["commentEntityPayload"]["properties"]
                comment_id = prop["commentId"]
                comment_text = prop["content"]["content"]
                author = prop["authorButtonA11y"]
                published_time = dateparser.parse(prop["publishedTime"].replace("(edited)", ""), languages=["en"])
                if published_time is None:
                    published_time = datetime.datetime.now()
                likes = 0
                toolbar = ep["payload"]["commentEntityPayload"]["toolbar"]
                if "likeCountA11y" in toolbar:
                    likes = comment_counter_to_int(toolbar["likeCountA11y"])
                replies_count = 0
                if "replyCountA11y" in toolbar:
                    replies_count = comment_counter_to_int(toolbar["replyCountA11y"])
                comments.append({
                    "id": comment_id,
                    "author": author,
                    "published_time": published_time,
                    "likes": likes,
                    "comment_text": comment_text,
                    "replies_count": replies_count
                })
        return comments, continuation_token, True
    if 'responseContext' in r:
        return [], continuation_token, True
    return [], continuation_token, False


def _extract_channel_basic_info_from_html(response, start_tag) -> dict:
    start_idx = response.text.find(start_tag)
    if start_idx == -1:
        return {}
    start_idx += len(start_tag)
    end_tag = "</script>"
    end_idx = response.text.find(end_tag, start_idx)
    if end_idx == -1:
        return {}
    json_str = response.text[start_idx:end_idx].strip()
    json_str = json_str[:json_str.rfind(";")]
    return json.loads(json_str)
