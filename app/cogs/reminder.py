from typing import Union
from discord.ext import commands, tasks
import datetime
import discord
from mylib import database
from mylib.errors import UnionNotExist


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder.start()

    times = []
    for hour in range(24):
        for minute in range(60):
            times.append(datetime.time(hour=hour, minute=minute))

    async def send_reminder(self, dest, channel, now):
        try:
            union = database.Union(channel_id=channel.id)
        except UnionNotExist:
            return
        if database.is_document_exist(dest_id=dest.id, union_id=union.id):
            return
        # 時間
        limit_dt = datetime.datetime.fromtimestamp(dest.limit)
        timedelta_list = [
            datetime.timedelta(days=3),
            datetime.timedelta(days=1),
            datetime.timedelta(hours=12),
            datetime.timedelta(hours=9),
            datetime.timedelta(hours=6),
            datetime.timedelta(hours=3),
            datetime.timedelta(hours=1)
        ]
        if limit_dt - now in timedelta_list:
            return
        # 削除
        async for message in channel.history(limit=None):
            if dest.name in message.content and discord.utils.format_dt(limit_dt, style="F") in message.content:
                await message.delete()
                break
        # 送信
        await channel.send(f"🔔 **{dest.name}** の提出期限は {discord.utils.format_dt(limit_dt, style='F')}ですが、まだ提出されていないようです。\n"
                            "可能な限りの早めの提出をお願いします！")

    @tasks.loop(time=times)
    async def reminder(self):
        now = datetime.datetime.now()
        now = now.replace(minute=now.minute - now.minute % 15, second=0, microsecond=0)
        all_dest = database.get_all_dest()
        for dest in all_dest:
            role = self.bot.guild.get_role(dest.role_id)
            abstract_channel = discord.utils.get(self.bot.guild.channels, name=role.name)
            if isinstance(abstract_channel, discord.CategoryChannel):
                category = abstract_channel
                for channel in category.text_channels:
                    await self.send_reminder(dest, channel, now)
            elif isinstance(abstract_channel, discord.TextChannel):
                await self.send_reminder(dest, abstract_channel, now)
        # channel = self.bot.guild.get_channel(1040087038793367652)
        # await channel.send("15分立ちました、チェックします")

    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminder(bot))
