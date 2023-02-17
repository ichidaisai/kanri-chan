import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


class KanriChan(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="./",
            intents=discord.Intents.all(),
        )
        self.help_command = None

    async def setup_hook(self):
        print("loading cogs")
        for cog in os.listdir("./cogs"):
            if cog == "__pycache__":
                continue
            await self.load_extension(f"cogs.{cog[:-3]}")
        await self.tree.sync(guild=discord.Object(id=int(os.environ["SERVER_ID"])))
        print("complete")

    async def on_ready(self):
        self.guild = self.get_guild(int(os.environ["SERVER_ID"]))
        self.category_channel = self.guild.get_channel(int(os.environ["RELAYING_CATEGORY_ID"]))
        message_relay = self.get_cog("MessageRelay")
        for channel in self.category_channel.text_channels:
            await message_relay.setup_select(channel)
        print("ready")


if __name__ == "__main__":
    load_dotenv()
    bot = KanriChan()
    bot.run(token=os.environ["TOKEN"])
