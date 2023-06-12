import datetime
from operator import attrgetter
import re


regex_discord_message_url = (
    "(?!<)https://(ptb.|canary.)?discord(app)?.com/channels/"
    "(?P<guild>[0-9]{17,20})/(?P<channel>[0-9]{17,20})/(?P<message>[0-9]{17,20})(?!>)"
)


def is_datetime(string):
    try:
        datetime.datetime.strptime(string, "%Y/%m/%d %H:%M")
    except Exception:
        return False
    return True


async def get_message_from_url(url, guild):
    ids = re.match(regex_discord_message_url, url)
    if ids is None:
        return
    channel = guild.get_channel(int(ids["channel"]))
    if channel is None:
        return
    message = await channel.fetch_message(int(ids["message"]))
    return message


def sort_dests_for_limit(dests):
    return sorted(dests, key=attrgetter("limit", "id"))
