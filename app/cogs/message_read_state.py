# 外部モジュール
import discord
from discord import app_commands
from discord.ext import commands

# 内部モジュール
from constant import (
    SERVER_ID,
    ALL_ANNOUNCE_CATEGORY_ID,
    OUTSIDE_ANNOUNCE_CATEGORY_ID,
    INSIDE_ANNOUNCE_CATEGORY_ID,
)
from mylib import database


READ_EMOJI = "\U00002705"  # ✅


class MessageReadState(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="既読確認",
            callback=self.check_read_log,
        )
        self.bot.tree.add_command(self.ctx_menu)

    @app_commands.checks.has_role("委員会")
    @app_commands.guilds(discord.Object(id=SERVER_ID))
    async def check_read_log(self, interaction, message: discord.Message):
        if not isinstance(message.channel, discord.TextChannel):
            return
        if message.channel.category_id not in (
            ALL_ANNOUNCE_CATEGORY_ID,
            OUTSIDE_ANNOUNCE_CATEGORY_ID,
            INSIDE_ANNOUNCE_CATEGORY_ID,
        ):
            return await interaction.response.send_message(
                "このチャンネルでは使用できません。", ephemeral=True
            )
        union_list = database.get_all_union()
        read_table = ""
        not_read_table = ""
        for union in union_list:
            if database.is_read_log_exist(
                channel_id=message.channel.id, message_id=message.id, union_id=union.id
            ):
                read_table += f"{union.name}:  ✅\n"
            else:
                not_read_table += f"{union.name}:  ❌\n"
        embed = discord.Embed(
            title="既読状況",
            description=f"読んだ団体\n{read_table}\n読んでない団体\n{not_read_table}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.channel.category_id not in (
            ALL_ANNOUNCE_CATEGORY_ID,
            OUTSIDE_ANNOUNCE_CATEGORY_ID,
            INSIDE_ANNOUNCE_CATEGORY_ID,
        ):
            return
        await message.add_reaction(READ_EMOJI)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            return
        if channel.category_id not in (
            ALL_ANNOUNCE_CATEGORY_ID,
            OUTSIDE_ANNOUNCE_CATEGORY_ID,
            INSIDE_ANNOUNCE_CATEGORY_ID,
        ):
            return
        for role in payload.member.roles:
            if not database.is_union_exist(union_role_id=role.id):
                continue
            union = database.Union(role_id=role.id)
            if database.is_read_log_exist(
                channel_id=payload.channel_id,
                message_id=payload.message_id,
                union_id=union.id,
            ):
                continue
            database.read_log_table.insert(
                dict(
                    channel_id=payload.channel_id,
                    message_id=payload.message_id,
                    member_id=payload.member.id,
                    union_id=union.id,
                )
            )


async def setup(bot):
    await bot.add_cog(MessageReadState(bot))
