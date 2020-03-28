# GOG Galaxy 2.0 integartion for Osu!

**State**: Alpha

## Installation

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
https://osu.ppy.sh/docs/index.html#authentication

- if client_secret should be hidden, then I need to expose js app that will exchange code to access_token
Then Galaxy will:
- open login page
- redirect to my app with `code` in url params
- redirect to dummy END_URI with tokens and other data in url params
- those params will be redirected to pass_login_credentials
- the plugin should deal with access/refresh tokens on its own.

Or do not care somebody will use this client_secret and exploit api limits.

### Local game:
- install: https://osu.ppy.sh/home/download (both windows and mac)
- launch: just open exe

### Games data:
game played  (UserStatistics -> play_time) https://osu.ppy.sh/docs/index.html#userstatistics

### Last time played
?

### Achievements:
so called "medals"
don't see in API, but can be parsed from user profile https://osu.ppy.sh/users/<user_id>
Or there is endpoint for notifications:

https://osu.ppy.sh/home/notifications?unread=1
response:
{"notifications":[{"id":64586606,"name":"user_achievement_unlock","created_at":"2020-03-26T19:58:37+00:00","object_type":"user","object_id":16517116,"source_user_id":null,"is_read":false,"details":{"slug":"all-intro-halftime","title":"Slowboat","user_id":16517116,"username":null,"cover_url":"https:\/\/assets.ppy.sh\/medals\/web\/all-intro-halftime.png","achievement_id":128}},{"id":64586605,"name":"user_achievement_unlock","created_at":"2020-03-26T19:58:37+00:00","object_type":"user","object_id":16517116,"source_user_id":null,"is_read":false,"details":{"slug":"mania-secret-meganekko","title":"A meganekko approaches","user_id":16517116,"username":null,"cover_url":"https:\/\/assets.ppy.sh\/medals\/web\/mania-secret-meganekko.png","achievement_id":54}}],"stacks":[{"category":"user_achievement_unlock","cursor":null,"name":"user_achievement_unlock","object_type":"user","object_id":16517116,"total":2}],"timestamp":"2020-03-26T20:12:03+00:00","types":[{"cursor":{"id":64586606},"name":null,"total":2},{"cursor":{"id":64586606,"type":"beatmapset"},"name":"beatmapset","total":0},{"cursor":{"id":64586606,"type":"build"},"name":"build","total":0},{"cursor":{"id":64586606,"type":"channel"},"name":"channel","total":0},{"cursor":{"id":64586606,"type":"forum_topic"},"name":"forum_topic","total":0},{"cursor":{"id":64586606,"type":"news_post"},"name":"news_post","total":0},{"cursor":{"id":64586606,"type":"user"},"name":"user","total":2}],"unread_count":2,"notification_endpoint":"wss:\/\/notify.ppy.sh"}

### Friends:

- user info with presence (id, username, avatar_url, is_online) https://osu.ppy.sh/docs/index.html#usercompact
- chat (groups, rooms, channels, presence) - notification message received: https://osu.ppy.sh/docs/index.html#notification-channel_message


[1]: https://github.com/UncleGoogle/galaxy-integration-osu/releases