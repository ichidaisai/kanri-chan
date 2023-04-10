# 外部モジュール
from discord.ext import commands

# 内部モジュール


class MessageReadState(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass


async def setup(bot):
    await bot.add_cog(MessageReadState(bot))
