from galaxy.api.types import Achievement


OSU = 'osu!'


async def test_achievements_no_achievements(api_mock, plugin):
    api_mock.get_me.return_value = {}
    context = await plugin.prepare_achievements_context([OSU])
    await plugin.get_unlocked_achievements(OSU, context) == []


async def test_achievements(api_mock, plugin):
    api_mock.get_me.return_value = {
        "user_achievements": [
            {
                "achieved_at": "2020-03-26T19:58:36+00:00",
                "achievement_id": 128
            },
            {
                "achieved_at": "2020-04-20T21:32:31+00:00",
                "achievement_id": 54
            }
        ],
    }
    expected = [
        Achievement(12131132, 128),
        Achievement(23123123, 54)
    ]
    context = await plugin.prepare_achievements_context([OSU])
    await plugin.get_unlocked_achievements(OSU, context) == expected
