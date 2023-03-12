from discord.ext import commands
from mylib import database
import discord


class UnionMenuButtons(discord.ui.View):
    def __init__(self, cog, union):
        super().__init__(timeout=None)
        self.cog = cog
        self.union = union

    @discord.ui.button(label="提出する", style=discord.ButtonStyle.green)
    async def submit_document(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("提出プロセスを開始します。")
        await self.cog.submit_document(interaction, self.union)

    @discord.ui.button(label="未提出を確認", style=discord.ButtonStyle.red)
    async def check_dest(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("提出物確認プロセスを開始します。")
        await self.cog.check_dest(interaction, self.union)

    @discord.ui.button(label="提出したものを確認", style=discord.ButtonStyle.blurple)
    async def document_list(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("提出物確認プロセスを開始します。")
        await self.cog.document_list(interaction, self.union)


class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 出店者用
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content != "メニュー":
            return
        data = database.union_table.find_one(channel_id=message.channel.id)
        if data is None:
            return
        union = database.Union(id=data["id"])
        document_cog = self.bot.get_cog("Document")
        await message.channel.send("メニュー", view=UnionMenuButtons(document_cog, union))


async def setup(bot):
    await bot.add_cog(Menu(bot))
