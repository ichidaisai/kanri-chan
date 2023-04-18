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
        self.app_commands = await self.tree.sync(guild=discord.Object(id=SERVER_ID))
        self.app_commands_dict = {"団体": [], "提出先": [], "提出物": [], "その他": []}
        for app_command in self.app_commands:
            if app_command.name in ["団体", "提出先", "提出物"]:
                for cmd in app_command.options:
                    self.app_commands_dict[app_command.name].append(cmd)
            elif app_command.name == "既読確認":
                continue
            else:
                self.app_commands_dict["その他"].append(app_command)

    async def on_ready(self):
        self.guild = self.get_guild(SERVER_ID)
        if self.guild is None:
            raise Exception("guildが正しく指定されていません。")
        self.category_channel = self.guild.get_channel(RELAYING_CATEGORY_ID)
        if not isinstance(self.category_channel, discord.CategoryChannel):
            raise Exception("category_channelが正しく指定されていません。")
        message_relay = self.get_cog("MessageRelay")
        for channel in self.category_channel.text_channels:
            await message_relay.setup_select(channel)
        discord.utils.setup_logging(level=logging.ERROR, root=False)


if __name__ == "__main__":
    bot = KanriChan()
    bot.run(token=TOKEN)
