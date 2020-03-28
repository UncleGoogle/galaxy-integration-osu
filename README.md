# GOG Galaxy 2.0 integartion for Osu!

**State**: Alpha

## Installation
_Currently not available_

Download asset `osu_v{}.zip` from [releases][1] and upack to:
- Windows: `%localappdata%\GOG.com\Galaxy\plugins\installed`
- MacOS: `~/Library/Application Support/GOG.com/Galaxy/plugins/installed`

#### From source:
_Requires `python3.6` or higher_

1. `git clone https://github.com/UncleGoogle/galaxy-integration-osu.git`
2. `cd galaxy-integration-osu`
3. `pip install -r requirements/dev.txt`
4. `inv dist`  # this will forcelly restart Galaxy


## Notes to myself

### Auth:
API v2
https://osu.ppy.sh/docs/index.html#authentication

Flow:
- `authentication` -> `NextStep` -> auth/authorize osu api
- redirect to own server where oauth grant_type `code` included as URL param is exchanged to `referesh_token`
- redirect to dummy URI specified in `NextStep` params with credentials in URL

API v1
just generate api key

### Local game:
- install: https://osu.ppy.sh/home/download (both windows and mac)
   - need to  implement OSCompability
   - download and run installer behalf the user
- launch: just open exe
   - can be osu opened with logged-in user?

### Games data:
game played  (UserStatistics -> play_time) https://osu.ppy.sh/docs/index.html#userstatistics

### Last time played
? ideas:
- recently played (24h only) (v1): https://github.com/ppy/osu-api/wiki#recently-played
- unofficial api: https://github.com/osufx/osuapi-extended/wiki#stat
    - check what does mean exactly

### Achievements:
so called "medals"
don't see in API, but can be parsed from user profile https://osu.ppy.sh/users/<user_id>
Or there is endpoint for `notifications`:

https://osu.ppy.sh/home/notifications?unread=1
response:

```
{"notifications":[{"id":64586606,"name":"user_achievement_unlock","created_at":"2020-03-26T19:58:37+00:00","object_type":"user","object_id":16517116,"source_user_id":null,"is_read":false,"details":{"slug":"all-intro-halftime","title":"Slowboat","user_id":16517116,"username":null,"cover_url":"https:\/\/assets.ppy.sh\/medals\/web\/all-intro-halftime.png","achievement_id":128}},{"id":64586605,"name":"user_achievement_unlock","created_at":"2020-03-26T19:58:37+00:00","object_type":"user","object_id":16517116,"source_user_id":null,"is_read":false,"details":{"slug":"mania-secret-meganekko","title":"A meganekko approaches","user_id":16517116,"username":null,"cover_url":"https:\/\/assets.ppy.sh\/medals\/web\/mania-secret-meganekko.png","achievement_id":54}}],"stacks":[{"category":"user_achievement_unlock","cursor":null,"name":"user_achievement_unlock","object_type":"user","object_id":16517116,"total":2}],"timestamp":"2020-03-26T20:12:03+00:00","types":[{"cursor":{"id":64586606},"name":null,"total":2},{"cursor":{"id":64586606,"type":"beatmapset"},"name":"beatmapset","total":0},{"cursor":{"id":64586606,"type":"build"},"name":"build","total":0},{"cursor":{"id":64586606,"type":"channel"},"name":"channel","total":0},{"cursor":{"id":64586606,"type":"forum_topic"},"name":"forum_topic","total":0},{"cursor":{"id":64586606,"type":"news_post"},"name":"news_post","total":0},{"cursor":{"id":64586606,"type":"user"},"name":"user","total":2}],"unread_count":2,"notification_endpoint":"wss:\/\/notify.ppy.sh"}
```

### Friends:

- user info with presence (id, username, avatar_url, is_online) https://osu.ppy.sh/docs/index.html#usercompact
- chat (groups, rooms, channels, presence) - notification message received: https://osu.ppy.sh/docs/index.html#notification-channel_message


[1]: https://github.com/UncleGoogle/galaxy-integration-osu/releases