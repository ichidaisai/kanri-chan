# 外部モジュール
import discord
from discord.ext import commands
import logging
import os

# 内部モジュール
from constant import TOKEN, SERVER_ID, RELAYING_CATEGORY_ID


class KanriChan(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
        )
        self.help_command = None

    async def setup_hook(self):
        await self.load_extension("jishaku")
        for cog in os.listdir("./cogs"):
            if cog in ["__pycache__", "mylib"]:
                continue
            await self.load_extension(f"cogs.{cog[:-3]}")
        await self.tree.sync(guild=discord.Object(id=SERVER_ID))

    async def on_ready(self):
        self.guild = self.get_guild(SERVER_ID)
        self.category_channel = self.guild.get_channel(RELAYING_CATEGORY_ID)
        message_relay = self.get_cog("MessageRelay")
        for channel in self.category_channel.text_channels:
            await message_relay.setup_select(channel)
        discord.utils.setup_logging(level=logging.ERROR, root=False)


if __name__ == "__main__":
    bot = KanriChan()
    bot.run(token=TOKEN)
