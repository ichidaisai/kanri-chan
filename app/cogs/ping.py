from discord.ext import commands
from discord import app_commands, ui
import discord
import os


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping")
    @app_commands.guilds(discord.Object(id=int(os.environ["SERVER_ID"])))
    async def ping(self, interaction):
        await interaction.response.send_message("pong!")


async def setup(bot):
    await bot.add_cog(Ping(bot))
