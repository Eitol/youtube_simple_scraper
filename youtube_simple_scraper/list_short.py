import json
from typing import List, Tuple

import dateparser
import requests

from youtube_simple_scraper.continuation_token import CommentsContinuationTokenBuilder
from youtube_simple_scraper.counters import comment_counter_to_int
from youtube_simple_scraper.list_videos_request import USER_AGENT
from youtube_simple_scraper.network import Requester


def get_shorts(channel_id: str, continuation_token: str = "") -> Tuple[List[dict], str]:
    url = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
    payload_dict = {
        "context": {
            "client": {
                "deviceModel": "",
                "userAgent": USER_AGENT,
                "clientName": "WEB",
                "clientVersion": "2.20240530.02.00",
                "osName": "Macintosh",
                "osVersion": "10_15_7",
                "originalUrl": "https://www.youtube.com/@IbaiLlanos/shorts",
            },
        }
    }
    if continuation_token == "":
        payload_dict["browseId"] = channel_id
        payload_dict["params"] = "EgZzaG9ydHPyBgUKA5oBAA%3D%3D"
    else:
        payload_dict["continuation"] = continuation_token

    payload = json.dumps(payload_dict)
    headers = {
        'accept': '*/*',
        'accept-language': 'en',
        'content-type': 'application/json',
        'origin': 'https://www.youtube.com',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-arch': '"arm"',
        'sec-ch-ua-bitness': '"64"',
        'user-agent': USER_AGENT,
        'connection': 'keep-alive',
    }
    req = requests.Request("POST", url, headers=headers, data=payload)
    response = Requester.request(req)
    j = response.json()
    raw_videos = []
    next_continuation_token = ""
    # /onResponseReceivedActions/0/appendContinuationItemsAction/continuationItems/48/continuationItemRenderer/continuationEndpoint/continuationCommand/token
    # /onResponseReceivedActions/0/appendContinuationItemsAction/continuationItems/0/richItemRenderer/content/reelItemRenderer/headline/simpleText
    reel_item_renderers = []
    if "onResponseReceivedActions" in j:
        for r in j["onResponseReceivedActions"]:
            if 'appendContinuationItemsAction' not in r:
                continue
            for c in r["appendContinuationItemsAction"]["continuationItems"]:
                if 'continuationItemRenderer' in c:
                    next_continuation_token = \
                        c["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
                if 'richItemRenderer' not in c:
                    continue
                reel_item_renderers.append(c["richItemRenderer"]["content"]["reelItemRenderer"])
    elif "contents" in j and "twoColumnBrowseResultsRenderer" in j["contents"] and "tabs" in \
            j["contents"]["twoColumnBrowseResultsRenderer"]:
        for t in j["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]:
            if ('tabRenderer' not in t or 'content' not in t["tabRenderer"]
                    or 'richGridRenderer' not in t["tabRenderer"]["content"]):
                continue
            for c in t["tabRenderer"]["content"]["richGridRenderer"]["contents"]:
                if 'continuationItemRenderer' in c:
                    next_continuation_token = \
                    c['continuationItemRenderer']['continuationEndpoint']['continuationCommand'][
                        'token']
                if "richItemRenderer" not in c:
                    continue
                reel_item_renderers.append(c["richItemRenderer"]["content"]["reelItemRenderer"])

    for r in reel_item_renderers:
        video_id = r["videoId"]
        title = r["headline"]["simpleText"]
        thumbnail = r['thumbnail']['thumbnails'][0]['url']
        view_count = r['viewCountText']['simpleText']
        raw_videos.append({
            "id": video_id,
            "title": title,
            "thumbnail": thumbnail,
            "view_count": comment_counter_to_int(view_count)
        })
    return raw_videos, next_continuation_token


def get_short_comments(short_id: str, continuation_token: str = "") -> Tuple[List[dict], str]:
    if continuation_token == "":
        continuation_token = CommentsContinuationTokenBuilder.build_start_short_comment_cont_token(short_id)

    url = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
    payload = json.dumps({
        "context": {
            "client": {
                "deviceModel": "",
                "clientName": "WEB",
                "clientVersion": "2.20240530.02.00",
                "osVersion": "10_15_7"
            }
        },
        "continuation": continuation_token
    })
    headers = {
        'accept': '*/*',
        'accept-language': 'en',
        'content-type': 'application/json',
        'user-agent': USER_AGENT,
        'connection': 'keep-alive',
    }
    req = requests.Request("POST", url, headers=headers, data=payload)
    response = Requester.request(req)
    j = response.json()
    raw_comments = []
    continuation_token = ""
    if "contents" in j and "twoColumnBrowseResultsRenderer" in j["contents"] and "tabs" in \
            j["contents"]["twoColumnBrowseResultsRenderer"]:
        for t in j["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]:
            if ('tabRenderer' not in t or 'content' not in t["tabRenderer"] or
                    'richGridRenderer' not in t["tabRenderer"]["content"]):
                continue
            for c in t["tabRenderer"]["content"]["richGridRenderer"]["contents"]:
                if "continuationItemRenderer" in c:
                    continuation_token = c['continuationItemRenderer']['continuationEndpoint'][
                        'continuationCommand']['token']

    if 'frameworkUpdates' not in j or 'entityBatchUpdate' not in j['frameworkUpdates']:
        return [], continuation_token
    for c in j["frameworkUpdates"]["entityBatchUpdate"]["mutations"]:
        if 'payload' not in c or 'commentEntityPayload' not in c['payload']:
            continue
        p = c['payload']['commentEntityPayload']
        if 'properties' not in p or 'content' not in p['properties']:
            continue
        content = p['properties']['content']['content']
        published_time = p['properties']['publishedTime']
        d = dateparser.parse(published_time)
        likes = 0
        if 'toolbar' in p and 'likeCountA11y' in p['toolbar']:
            likes = int(p['toolbar']['likeCountA11y'].split(" ")[0])
        reply_count = 0
        if 'toolbar' in p and 'replyCount' in p['toolbar'] and p['toolbar']['replyCount'] != "":
            reply_count = int(p['toolbar']['replyCount'])
        raw_comments.append({
            "id": p['properties']['commentId'],
            "text": content,
            "date": d,
            "likes": likes,
            "author": p['author']['displayName'],
            "reply_count": reply_count
        })
    return raw_comments, continuation_token


if __name__ == '__main__':
    cid = "UCaY_-ksFSQtTGk0y1HA_3YQ"
    v, token = get_shorts(cid)
    # while True:
    #     if token == "":
    #         break
    #     v2, token = get_shorts(cid, token)
    #     print(v2)
    #     v.extend(v2)

    comments, s_token = get_short_comments(v[0]["id"])
    print(comments)
