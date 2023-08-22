# 外部モジュール
import datetime
import discord
from discord.ext import commands, tasks

# 内部モジュール
from mylib import database, UnionNotExist


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timedelta_list = [
            datetime.timedelta(days=3),
            datetime.timedelta(days=1),
            datetime.timedelta(hours=12),
            datetime.timedelta(hours=9),
            datetime.timedelta(hours=6),
            datetime.timedelta(hours=3),
            datetime.timedelta(hours=1),
        ]
        self.reminder.start()
        self.weekly_reminder.start()


    times = []
    for hour in range(24):
        for minute in range(60):
            times.append(datetime.time(hour=hour, minute=minute, tzinfo=datetime.timezone(datetime.timedelta(hours=9))))

    @tasks.loop(time=times)
    async def reminder(self):
        now = datetime.datetime.now()
        now = now.replace(minute=now.minute, second=0, microsecond=0)
        for union in database.get_all_union():
            channel = self.bot.guild.get_channel(union.channel_id)
            type_role = discord.utils.get(self.bot.guild.roles, name=union.type)
            dests = database.get_dests(type_role.id) + database.get_dests(union.role_id)
            for dest in dests:
                if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                    continue
                limit_dt = datetime.datetime.fromtimestamp(dest.limit)
                if not (limit_dt - now) in self.timedelta_list:
                    continue
                async for message in channel.history(limit=None):
                    if (
                        dest.name in message.content
                        and discord.utils.format_dt(limit_dt, style="F") in message.content
                    ):
                        await message.delete()
                        break
                await channel.send(
                    f"{self.bot.guild.get_role(union.role_id).mention} 🔔 **{dest.name}** の提出期限は {discord.utils.format_dt(limit_dt, style='F')}ですが、まだ提出されていないようです。\n"
                    "可能な限りの早めの提出をお願いします！"
                )
    @tasks.loop(time=datetime.time(hour=7, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
    async def weekly_reminder(self):
        now = datetime.datetime.now()
        now = now.replace(minute=now.minute, second=0, microsecond=0)
        if now.weekday() != 0:
            return
        for union in database.get_all_union():
            role = discord.utils.get(self.bot.guild.roles, name=union.type)
            dests_for_type = database.get_dests(role_id=role.id)
            dests_for_union = database.get_dests(role_id=union.role_id)
            dests = set(dests_for_type + dests_for_union)
            for dest in dests:
                if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                    continue
                limit_dt = datetime.datetime.fromtimestamp(dest.limit)
                if (
                    datetime.timedelta(days=0)
                    < (limit_dt - now)
                    <= datetime.timedelta(days=7)
                ):
                    break
            else:
                channel = self.bot.guild.get_channel(union.channel_id)
                # await channel.send("✅ 今週が締切の提出物はありません")

    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()

    @weekly_reminder.before_loop
    async def before_weekly_reminder(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminder(bot))
