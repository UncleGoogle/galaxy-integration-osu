# GOG Galaxy 2.0 integration for osu!

_Currently shown as "Newegg" as there is no osu id in Galaxy API_


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


## Features:
- total time played
- import achievements (medals)*
- import friend recommendations
- friends online status*
- install
- play

\* works but Galaxy does not use imported data (probably will be fixed in the future)

## Notes to myself:

### Local game:
   - can be osu opened with logged-in user?

### Last time played:
- recently played (24h only) (v1): https://github.com/ppy/osu-api/wiki#recently-played
- https://osu.ppy.sh/api/v2/users/{user_id}/recent_activity
- unofficial api: https://github.com/osufx/osuapi-extended/wiki#stat
    - check what does mean exactly

### Friends:

- user info with presence (id, username, avatar_url, is_online) https://osu.ppy.sh/docs/index.html#usercompact
- chat (groups, rooms, channels, presence) - notification message received: https://osu.ppy.sh/docs/index.html#notification-channel_message


[1]: https://github.com/UncleGoogle/galaxy-integration-osu/releases