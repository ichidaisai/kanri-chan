from discord.ext import commands
from discord import app_commands
import discord
from mylib import database
from constant import SERVER_ID
from typing import Literal


@app_commands.guilds(discord.Object(id=SERVER_ID))
class UnionCommandGroup(app_commands.Group):
    pass


class UnionManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    union_group = UnionCommandGroup(name="団体", description="団体のデータを操作します。")

    @app_commands.describe(union_type="団体をどちらに属させるかを選択", union_name="作成する団体の名前")
    @app_commands.rename(union_type="出店形式")
    @app_commands.rename(union_name="出店名")
    @union_group.command(name="作成", description="団体のチャンネル、ロールを作成")
    async def union_make(
        self, interaction, union_type: Literal["屋外", "屋内"], union_name: str
    ):
        union_names = "".join(union_name.split(",")).split()
        for name in union_names:
            if database.is_union_exist(name, union_type):
                return await interaction.response.send_message(f"{name}は既に存在する団体名です。")
            category = discord.utils.get(self.bot.guild.categories, name=union_type)
            channel = await category.create_text_channel(name=name)
            role = await self.bot.guild.create_role(name=name)
            await channel.set_permissions(role, view_channel=True)
            database.union_table.insert(
                dict(
                    role_id=role.id,
                    name=name,
                    type=union_type,
                    channel_id=channel.id,
                )
            )
        await interaction.response.send_message(f"{union_type}に{union_name}を作成")

    @app_commands.describe(union_type="削除する団体がどちらに属するのかを選択", union_name="削除する団体の名前")
    @app_commands.rename(union_type="出店形式")
    @app_commands.rename(union_name="出店名")
    @union_group.command(name="削除", description="団体のチャンネル、ロールを削除")
    async def union_delete(
        self, interaction, union_type: Literal["屋外", "屋内"], union_name: str
    ):
        if not database.is_union_exist(union_name, union_type):
            return await interaction.response.send_message(f"{union_name}は存在しない団体名です。")
        union = database.Union(name=union_name, type=union_type)
        union.delete()
        channel = self.bot.guild.get_channel(union.channel_id)
        role = self.bot.guild.get_role(union.role_id)
        if channel and role:
            await channel.delete()
            await role.delete()
        else:
            return await interaction.response.send_message(
                f"破損したデータが見つかりました。管理者に連絡してください。id={union.id}"
            )
        await interaction.response.send_message(f"{union_type}の{union_name}を削除")

    @app_commands.describe(
        union_type="改名する団体がどちらに属するのかを選択", union_name="改名する団体の名前", new_name="新しい名前"
    )
    @app_commands.rename(union_type="出店形式")
    @app_commands.rename(union_name="出店名")
    @app_commands.rename(new_name="新しい名前")
    @union_group.command(name="改名", description="団体のチャンネル、ロールの名前を変更")
    async def union_rename(
        self,
        interaction,
        union_type: Literal["屋外", "屋内"],
        union_name: str,
        new_name: str,
    ):
        if not database.is_union_exist(union_name, union_type):
            return await interaction.response.send_message(f"{union_name}は存在しない団体名です。")
        if database.is_union_exist(new_name, union_type):
            return await interaction.response.send_message(f"{new_name}は既に存在する団体名です。")
        union = database.Union(name=union_name, type=union_type)
        union.name = new_name
        union.update()
        channel = self.bot.guild.get_channel(union.channel_id)
        role = self.bot.guild.get_role(union.role_id)
        if channel and role:
            await channel.edit(name=new_name)
            await role.edit(name=new_name)
        else:
            return await interaction.response.send_message(
                f"破損したデータが見つかりました。管理者に連絡してください。id={union.id}"
            )
        await interaction.response.send_message(
            f"{union_type}の{union_name}を{new_name}に改名"
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # ロールが追加されたとき以外をreturn
        if not list(set(after.roles) - set(before.roles)):
            return
        added_role = list(set(after.roles) - set(before.roles))[0]
        if not database.is_union_exist(union_role_id=added_role.id):
            return
        union = database.Union(role_id=added_role.id)
        parent_role = discord.utils.get(self.bot.guild.roles, name=union.type)
        await after.add_roles(parent_role)


async def setup(bot):
    await bot.add_cog(UnionManager(bot))
