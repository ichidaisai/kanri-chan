from discord.ext import commands
import discord
from .mylib import database


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("委員会")
    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("このコマンドにはサブコマンドが必要です。")
    
    @role.command()
    async def make(self, ctx, group_type=None, group_name=None):
        if group_type is None or group_type not in ["屋外", "屋内"]:
            return await ctx.reply("新規作成する団体の出店形式が指定されていません。\n例) `!role make 屋外 団体名A`")
        if group_name is None:
            return await ctx.reply("新規作成する団体名が指定されていません。\n例) `!role make 屋外 団体名A`")
        if database.is_group_exist(group_name, group_type):
            return await ctx.reply("既に存在する団体名です。")

        category = discord.utils.get(self.bot.guild.categories, name=group_type)
        channel = await category.create_text_channel(name=group_name)
        role = await self.bot.guild.create_role(name=group_name)
        await channel.set_permissions(role, view_channel=True)

        database.group_table.insert(dict(role_id=role.id, name=group_name, type=group_type, channel_id=channel.id))
        group = database.Group(role_id=role.id)
        await ctx.reply(vars(group))
        await ctx.reply(f"{group_type}に{group_name}を作成")
    
    @role.command()
    async def make_bulk(self, ctx, group_type=None, *group_name_list):
        for group_name in group_name_list:
            await self.make(ctx, group_type, group_name)
        await ctx.reply(f"{group_type}に`[{group_name_list}]`を作成")

    @role.command()
    async def delete(self, ctx, group_type=None, group_name=None):
        if group_type is None or group_type not in ["屋外", "屋内"]:
            return await ctx.reply("削除する団体の出店形式が指定されていません。\n例) `!role delete 屋外 団体名A`")
        if group_name is None:
            return await ctx.reply("削除する団体名が指定されていません。\n例) `!role delete 屋外 団体名A`")
        if not database.is_group_exist(group_name, group_type):
            return await ctx.reply("存在しない団体名です。")
        
        group = database.Group(name=group_name, type=group_type)
        group.delete()
        channel = self.bot.guild.get_channel(group.channel_id)
        await channel.delete()
        role = self.bot.guild.get_role(group.role_id)
        await role.delete()
        await ctx.reply(f"{group_type}の{group_name}を削除")

    @role.command()
    async def rename(self, ctx, group_type=None, group_name=None, new_name=None):
        if group_type is None or group_type not in ["屋外", "屋内"]:
            return await ctx.reply("名称を変更する団体の出店形式が指定されていません。\n例) `!role rename 屋外 団体名A 団体名B`")
        if group_name is None:
            return await ctx.reply("名称を変更する団体名が指定されていません。\n例) `!role rename 屋外 団体名A 団体名B`")
        if new_name is None:
            return await ctx.reply("新しい名称が指定されていません。\n例) `!role rename 屋外 団体名A 団体名B`")
        if not database.is_group_exist(group_name, group_type):
            return await ctx.reply("存在しない団体が名称を変更する団体として指定されました。")
        if database.is_group_exist(new_name, group_type):
            return await ctx.reply("既に存在している団体名が新しい名称として指定されました。")
        
        group = database.Group(name=group_name, type=group_type)
        group.name = new_name
        group.update()
        channel = self.bot.guild.get_channel(group.channel_id)
        await channel.edit(name=new_name)
        role = self.bot.guild.get_role(group.role_id)
        await role.edit(name=new_name)
        await ctx.reply(f"{group_type}の{group_name}を{new_name}に変更")

async def setup(bot):
    await bot.add_cog(RoleManager(bot))
