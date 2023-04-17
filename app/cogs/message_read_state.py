# 外部モジュール
from discord.ext import commands

# 内部モジュール
from constant import (
    SERVER_ID,
    ALL_ANNOUNCE_CATEGORY_ID,
    OUTSIDE_ANNOUNCE_CATEGORY_ID,
    INSIDE_ANNOUNCE_CATEGORY_ID,
)
from mylib import database


READ_EMOJI = "\U00002705"  # ✅


class MessageReadState(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category_id not in (
            ALL_ANNOUNCE_CATEGORY_ID,
            OUTSIDE_ANNOUNCE_CATEGORY_ID,
            INSIDE_ANNOUNCE_CATEGORY_ID,
        ):
            return
        await message.add_reaction(READ_EMOJI)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel.category_id not in (
            ALL_ANNOUNCE_CATEGORY_ID,
            OUTSIDE_ANNOUNCE_CATEGORY_ID,
            INSIDE_ANNOUNCE_CATEGORY_ID,
        ):
            return
        for role in payload.member.roles:
            if not database.is_union_exist(union_role_id=role.id):
                continue
            union = database.Union(role_id=role.id)
            if database.is_read_log_exist(
                channel_id=payload.channel_id,
                message_id=payload.message_id,
                union_id=union.id,
            ):
                continue
            database.read_log_table.insert(
                dict(
                    channel_id=payload.channel_id,
                    message_id=payload.message_id,
                    member_id=payload.member.id,
                    union_id=union.id,
                )
            )


async def setup(bot):
    await bot.add_cog(MessageReadState(bot))
