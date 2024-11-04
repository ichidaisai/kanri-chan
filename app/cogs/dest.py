# 外部モジュール
import asyncio
import datetime
import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal

# 内部モジュール
from constant import SERVER_ID
from mylib import database, utils, Pagenator


@app_commands.guilds(discord.Object(id=SERVER_ID))
class DestCommandGroup(app_commands.Group):
    pass


class DestManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    dest_group = DestCommandGroup(name="提出先", description="提出先を操作します。")

    @app_commands.describe(
        dest_name="作成する提出先の名前",
        target_role="提出を課す団体をロールで指定",
        document_format="提出形式を選択",
        handler_role="作成元を指定",
        date="提出期限の日付を MM/DDの形で指定",
        time="提出期限の時間を hh:mmの形で指定",
    )
    @app_commands.rename(dest_name="提出先名")
    @app_commands.rename(target_role="団体")
    @app_commands.rename(document_format="提出形式")
    @app_commands.rename(handler_role="設定者")
    @app_commands.rename(date="日付")
    @app_commands.rename(date="時間")
    @dest_group.command(name="作成", description="提出先作成")
    async def make_dest(
        self,
        interaction,
        dest_name: str,
        target_role: discord.Role,
        document_format: Literal["プレーンテキスト", "ファイル"],
        handler_role: discord.Role,
        year: str = "2024",
        date: str = "12/31",
        time: str = "23:59",
    ):
        dest_limit = datetime.datetime.strptime(
            f"{year}/{date} {time}", "%Y/%m/%d %H:%M"
        )
        if dest_limit < datetime.datetime.now():
            return await interaction.response.send_message(
                content="⚠ 提出期限が過去に設定されています。\nもう一度、最初からやり直してください。",
            )
        database.dest_table.insert(
            dict(
                name=dest_name,
                role_id=target_role.id,
                limit=dest_limit.timestamp(),
                format=document_format,
                handler_id=handler_role.id,
            )
        )
        embed = discord.Embed(
            title="✅ 提出先作成",
            description="提出先を作成しました。\n"
            f"📛項目名: {dest_name}\n"
            f"👤対象: {target_role.mention}\n"
            f"⏰期限: {discord.utils.format_dt(dest_limit, style='F')}\n"
            f"💾種類: {document_format}\n"
            f"設定者: {handler_role.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.describe(id="削除する提出先のid")
    @dest_group.command(name="削除", description="提出先を削除")
    async def delete_dest(self, interaction, id: int):
        if not database.is_dest_exist(dest_id=id):
            return await interaction.response.send_message(
                "存在しない提出先です。", delete_after=10
            )
        dest = database.Dest(id=id)
        dest.delete()
        dt = datetime.datetime.fromtimestamp(dest.limit)
        handler_role = self.bot.guild.get_role(dest.handler_id)
        embed = discord.Embed(
            title="✅ 提出先削除",
            description="提出先を削除しました。\n"
            f"id: {dest.id}\n"
            f"📛項目名: {dest.name}\n"
            f"👤対象: <@&{dest.role_id}>\n"
            f"⏰期限: {discord.utils.format_dt(dt, style='F')}\n"
            f"💾種類: {dest.format}\n"
            f"設定者: {handler_role.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.describe(target_role="削除する提出先のid")
    @app_commands.rename(target_role="ロール")
    @dest_group.command(name="一覧", description="提出先一覧を表示")
    async def dest_list(self, interaction, target_role: discord.Role = None):
        if target_role:
            all_dest = database.get_dests(role_id=target_role.id)
        else:
            all_dest = database.get_all_dest()
        dest_count = len(all_dest)
        if dest_count == 0:
            return await interaction.response.send_message(
                "提出先は存在しません。", delete_after=10
            )
        all_dest = [all_dest[idx : idx + 5] for idx in range(0, dest_count, 5)]
        embed_container = []
        for dest_container in all_dest:
            embeds = []
            for dest in dest_container:
                dt = datetime.datetime.fromtimestamp(dest.limit)
                handler_role = self.bot.guild.get_role(dest.handler_id)
                embed = discord.Embed(
                    description=f"id: {dest.id}\n"
                    f"📛項目名: {dest.name}\n"
                    f"👤対象: <@&{dest.role_id}>\n"
                    f"⏰期限: {discord.utils.format_dt(dt, style='F')}\n"
                    f"💾種類: {dest.format}\n"
                    f"設定者: {handler_role.mention}",
                    color=discord.Color.green(),
                )
                embeds.append(embed)
            embed_container.append(embeds)
        ctx = await commands.Context.from_interaction(interaction)
        await Pagenator(embed_pages=embed_container, ctx=ctx).start()


async def setup(bot):
    await bot.add_cog(DestManager(bot))
