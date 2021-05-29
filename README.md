# @Kanolive_ 推特备份

---

## 简介

- 备份
  - 纯文字版：`kano_hanayori_twitter.txt`
- 源数据
  - 文字
    - 使用`Twitter API`和`tweepy`获取
    - 用户信息：`user_info.pickle`
    - 推特内容：`log.pickle`
  - 媒体
    - 使用`you-get`获取
    - 暂未上传
- 脚本
  - 排版：`tweet_parser.py`

## 源数据格式

- `user_info.pickle`

```json
{
    str<用户 id>: {
        "name": str,
        "username": str,
        "profile_image_url": str,
        "created_at": datetime,
        "tweet_count": int,
        "followers_count": int,
        "following_count": int,
        "description": str
    }
}
```

- `log.pickle`

```json
{
    str<推特 id>: {
        "created_at": datetime,
        "reply_count": int,
        "retweet_count": int,
        "like_count": int,
        "quote_count": int,
        "urls": [
            {
                "expanded_url": str,
                "display_url": str,
                "url": str,
                "start": int,
                "end": int
            },
            ...
        ],
        "text": str
    },
    ...
}
```