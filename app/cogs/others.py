from discord.ext import commands
from discord import app_commands, file
import discord
from constant import SERVER_ID
import io
import cv2
import numpy as np


class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(discord.Object(id=SERVER_ID))
    @app_commands.describe(image_file="白黒に変換する画像をアップロードしてください。")
    @app_commands.rename(image_file="画像")
    @app_commands.command(name="白黒変換", description="画像を白黒に変換します")
    async def convert_to_grayscale(
        self,
        interaction,
        image_file: discord.Attachment,
    ):
        if image_file.content_type and not image_file.content_type.startswith("image/"):
            return await interaction.response.send_message("画像を送信してください。")
        byte_image = io.BytesIO()
        await image_file.save(byte_image)
        byte_image.seek(0)
        file_bytes = np.asarray(bytearray(byte_image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        is_success, buffer = cv2.imencode(".jpg", img)
        out_image = io.BytesIO(buffer)
        out_image.seek(0)
        await interaction.response.send_message(
            files=[discord.File(fp=out_image, filename="grayscale.png")]
        )


async def setup(bot):
    await bot.add_cog(Others(bot))
