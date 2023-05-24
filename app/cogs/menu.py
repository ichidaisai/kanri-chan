# 外部モジュール
import discord
from discord.ext import commands

# 内部モジュール
from mylib import database


class UnionMenuButtons(discord.ui.View):
    def __init__(self, cog, ctx, union):
        super().__init__(timeout=None)
        self.cog = cog
        self.ctx = ctx
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
        await self.cog.check_dest(interaction, self.ctx, self.union)

    @discord.ui.button(label="提出したものを確認", style=discord.ButtonStyle.blurple)
    async def document_list(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("提出物確認プロセスを開始します。")
        await self.cog.document_list(interaction, self.ctx, self.union)


class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 出店者用
    @commands.Cog.listener(name="on_message")
    async def union_menu(self, message):
        if message.author.bot:
            return
        if message.content != "メニュー":
            return
        data = database.union_table.find_one(channel_id=message.channel.id)
        if data is None:
            return
        union = database.Union(id=data["id"])
        document_cog = self.bot.get_cog("Document")
        ctx = await self.bot.get_context(message)
        await message.channel.send("メニュー", view=UnionMenuButtons(document_cog, ctx, union))

    # 委員会用
    @commands.has_role("委員会")
    @commands.Cog.listener(name="on_message")
    async def host_menu(self, message):
        if message.author.bot:
            return
        if message.content != "メニュー":
            return
        data = database.union_table.find_one(channel_id=message.channel.id)
        if data:
            return
        embeds = [
            discord.Embed(
                title="団体関係コマンド",
                description=", ".join(
                    [cmd.mention for cmd in self.bot.app_commands_dict["団体"]]
                ),
                color=discord.Color.blurple(),
            ),
            discord.Embed(
                title="提出先関係コマンド",
                description=", ".join(
                    [cmd.mention for cmd in self.bot.app_commands_dict["提出先"]]
                ),
                color=discord.Color.green(),
            ),
            discord.Embed(
                title="提出物関係コマンド",
                description=", ".join(
                    [cmd.mention for cmd in self.bot.app_commands_dict["提出物"]]
                ),
                color=discord.Color.yellow(),
            ),
            discord.Embed(
                title="その他コマンド",
                description=", ".join(
                    [cmd.mention for cmd in self.bot.app_commands_dict["その他"]]
                ),
                color=discord.Color.brand_red(),
            ),
        ]
        await message.channel.send(embeds=embeds)


async def setup(bot):
    await bot.add_cog(Menu(bot))
