## Youtube Simple Scraper

This is a simple youtube scraper that uses the youtube API to get the videos metadata and comments of a channel.

### Features

Scrape the following information of a channel:

- Channel metadata
- Videos metadata and comments
- Shorts metadata and comments

### Installation

```bash
pip install youtube_simple_scraper
```

### Usage

```python
from youtube_simple_scraper.entities import GetChannelOptions
from youtube_simple_scraper.list_video_comments import ApiVideoCommentRepository, ApiShortVideoCommentRepository
from youtube_simple_scraper.list_videos import ApiVideoListRepository
from youtube_simple_scraper.logger import build_default_logger
from youtube_simple_scraper.stop_conditions import ListCommentMaxPagesStopCondition, ListVideoMaxPagesStopCondition

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
    channel = repo.get_channel("IbaiLlanos", opts)
    print(channel.id)
    print(channel.videos[0].title)
    print(channel.videos[0].comments[0].text)
    print(channel.shorts[0].title)
    print(channel.shorts[0].comments[0].text)
    print(channel.model_dump_json(indent=2))
```

Example of the output channel object parsed to json:
```json5
{
  "id": "UCaY_-ksFSQtTGk0y1HA_3YQ",
  "name": "IbaiLlanos",
  "target_id": "668be16f-0000-20de-b6a2-582429cfbdec",
  "title": "Ibai",
  "description": "contenido premium ▶️\n",
  "subscriber_count": 11600000,
  "video_count": 1400,
  "videos": [
    {
      "id": "VFXu8gzcpNc",
      "title": "EL RESTAURANTE MÁS ÚNICO AL QUE HE IDO NUNCA",
      "description": "MI CANAL DE DIRECTOS: https://www.youtube.com/@Ibai_TV\nExtraído de mi canal de TWITCH: https://www.twitch.tv/ibai/\nMI PODCAST: \nhttps://www.youtube.com/channel/UC6jNDNkoOKQfB5djK2IBDoA\nTWITTER:...",
      "date": "2024-06-02T19:18:27.647137",
      "view_count": 1455817,
      "like_count": 0,
      "dislike_count": 0,
      "comment_count": 0,
      "thumbnail_url": "https://i.ytimg.com/vi/VFXu8gzcpNc/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLCEmoQtslruHk-droajdw0KJUI_KA",
      "comments": [
        {
          "id": "UgzV8lY8eJ4dyHjl9Bp4AaABAg",
          "text": "Todo muy rico pero....Y la cuenta?",
          "user": "@eliasabregu2813",
          "date": "2024-06-03T19:11:28.109467",
          "likes": 0
        },
        {
          "id": "UgwHtPZb8jprbCH-ysp4AaABAg",
          "text": "Que humilde Ibai, comiendo todo para generar ingresos a los nuevos negocios",
          "user": "@user-ui2sk7sr5i",
          "date": "2024-06-03T19:04:28.112228",
          "likes": 0
        }
      ]
    },
    // More videos ...
  ],
  "shorts": [
    // the shorts videos and comments
  ]
}

```

### Stop conditions

#### Videos stop conditions

- ListVideoMaxPagesStopCondition: Stops the scraping process when the number of pages scraped is greater than the
  specified value.
- ListVideoNeverStopCondition: The scraping process stop when all the videos of the channel are scraped.

#### Comments stop conditions

- ListCommentMaxPagesStopCondition: Stops the scraping process when the number of pages scraped is greater than the
  specified value.
- ListCommentNeverStopCondition: The scraping process stop when all the comments of the video are scraped.

The stop conditions are used to stop the scraping process. The following stop conditions are available:


