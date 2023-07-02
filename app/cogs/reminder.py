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
        if not limit_dt - now in self.timedelta_list:
            return
        # 削除
        async for message in channel.history(limit=None):
            if (
                dest.name in message.content
                and discord.utils.format_dt(limit_dt, style="F") in message.content
            ):
                await message.delete()
                break
        # 送信
        await channel.send(
            f"🔔 **{dest.name}** の提出期限は {discord.utils.format_dt(limit_dt, style='F')}ですが、まだ提出されていないようです。\n"
            "可能な限りの早めの提出をお願いします！"
        )

    @tasks.loop(time=times)
    async def reminder(self):
        now = datetime.datetime.now()
        now = now.replace(minute=now.minute, second=0, microsecond=0)
        all_dest = database.get_all_dest()
        for dest in all_dest:
            role = self.bot.guild.get_role(dest.role_id)
            abstract_channel = discord.utils.get(
                self.bot.guild.channels, name=role.name
            )
            if isinstance(abstract_channel, discord.CategoryChannel):
                category = abstract_channel
                for channel in category.text_channels:
                    await self.send_reminder(dest, channel, now)
            elif isinstance(abstract_channel, discord.TextChannel):
                await self.send_reminder(dest, abstract_channel, now)

        if now.weekday() == 0 and now.hour == 8 and now.minute == 0:  # 月曜日の午前7時0分
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
                    await channel.send("✅ 今週が締切の提出物はありません")

    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminder(bot))
