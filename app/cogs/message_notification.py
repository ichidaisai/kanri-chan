# 外部モジュール
import cv2
import discord
from discord.ext import commands
from discord import app_commands
import io
import numpy as np

# 内部モジュール
from constant import SERVER_ID, CAFE_CONTACT_CATEGORY_ID, MOGI_CONTACT_CATEGORY_ID


class MessageNotification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.TextChannel):
            return
        if message.channel.category_id not in (
            CAFE_CONTACT_CATEGORY_ID,
            MOGI_CONTACT_CATEGORY_ID,
        ):
            return
        async for msg in channel.history(limit=None):
            if msg.content == "@everyone":
                await msg.delete()
                break
        await message.channel.send("@everyone")


async def setup(bot):
    await bot.add_cog(MessageNotification(bot))
