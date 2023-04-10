# 外部モジュール
from discord.ext import commands

# 内部モジュール
from constant import ALL_ANNOUNCE_CATEGORY_ID, OUTSIDE_ANNOUNCE_CATEGORY_ID, INSIDE_ANNOUNCE_CATEGORY_ID


READ_EMOJI = "\U00002705"  # ✅


class MessageReadState(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.category_id not in (ALL_ANNOUNCE_CATEGORY_ID, OUTSIDE_ANNOUNCE_CATEGORY_ID, INSIDE_ANNOUNCE_CATEGORY_ID):
            return
        await message.add_reaction(READ_EMOJI)


async def setup(bot):
    await bot.add_cog(MessageReadState(bot))
