from typing import Literal
from discord.ext import commands
import discord
from discord import app_commands
from mylib import database
from mylib import utils
import asyncio
import datetime
from constant import SERVER_ID
from typing import Literal


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
    )
    @app_commands.rename(dest_name="提出先名")
    @app_commands.rename(target_role="団体")
    @app_commands.rename(document_format="提出形式")
    @app_commands.rename(handler_role="設定者")
    @dest_group.command(name="作成", description="提出先作成")
    async def make_dest(
        self,
        interaction,
        dest_name: str,
        target_role: discord.Role,
        document_format: Literal["プレーンテキスト", "ファイル"],
        handler_role: discord.Role,
    ):
        def check(m):
            return (
                m.channel == interaction.channel
                and m.author == interaction.user
                and len(m.content) != 0
            )

        # limit
        await interaction.response.send_message(
            "⏰ 提出期限を指定してください。\n入力例: 2023年4月1日 8時30分 としたい場合は、`2023/4/1 08:30` と入力します。"
        )
        ask_msg = await interaction.original_response()
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ask_msg.edit(
                content="⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", delete_after=10
            )
        if not utils.is_datetime(msg.content):
            return await ask_msg.edit(
                content="⚠ 指定された期限をうまく解釈できませんでした。\n"
                "入力例: 2022年4月1日 8時30分 としたい場合は、`2022/4/1 08:30` と入力します。\n"
                "もう一度、最初から操作をやり直してください。",
                delete_after=10,
            )
        dest_limit = datetime.datetime.strptime(msg.content, "%Y/%m/%d %H:%M")
        if dest_limit < datetime.datetime.now():
            await msg.delete()
            return await ask_msg.edit(
                content="⚠ 提出期限が過去に設定されています。\nもう一度、最初からやり直してください。", delete_after=10
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
        await msg.delete()
        await ask_msg.edit(content=None, embed=embed)

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
        all_dest = [all_dest[idx : idx + 10] for idx in range(0, dest_count, 10)]
        count = 1
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
                count += 1
            await interaction.channel.send(
                f"{count-len(embeds)}~{count-1}", embeds=embeds
            )
        await interaction.response.send_message(f"合計{dest_count}個")


async def setup(bot):
    await bot.add_cog(DestManager(bot))
