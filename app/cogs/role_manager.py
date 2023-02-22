from discord.ext import commands
import discord


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("委員会")
    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send("このコマンドにはサブコマンドが必要です。")
    
    @role.command()
    async def make(self, ctx, group_type=None, group_name=None):
        if group_type is None or group_type not in ["屋外", "屋内"]:
            return await ctx.send("新規作成する団体の出店形式が指定されていません。\n例) `!role make 屋外 団体名A`")
        if group_name is None:
            return await ctx.send("新規作成する団体名が指定されていません。\n例) `!role make 屋外 団体名A`")
        await ctx.send(f"{group_type}に{group_name}を作成")
    
    @role.command()
    async def delete(self, ctx, group_type=None, group_name=None):
        if group_type is None or group_type not in ["屋外", "屋内"]:
            return await ctx.send("削除する団体の出店形式が指定されていません。\n例) `!role delete 屋外 団体名A`")
        if group_name is None:
            return await ctx.send("削除する団体名が指定されていません。\n例) `!role delete 屋外 団体名A`")
        await ctx.send(f"{group_type}の{group_name}を削除")

    @role.command()
    async def rename(self, ctx, group_type=None, group_name=None, new_name=None):
        if group_type is None or group_type not in ["屋外", "屋内"]:
            return await ctx.send("名称を変更する団体の出店形式が指定されていません。\n例) `!role rename 屋外 団体名A 団体名B`")
        if group_name is None:
            return await ctx.send("名称を変更する団体名が指定されていません。\n例) `!role rename 屋外 団体名A 団体名B`")
        if new_name is None:
            return await ctx.send("新しい名称が指定されていません。\n例) `!role rename 屋外 団体名A 団体名B`")
        await ctx.send(f"{group_type}の{group_name}を{new_name}に変更")

async def setup(bot):
    await bot.add_cog(RoleManager(bot))
