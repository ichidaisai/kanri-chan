from discord.ext import commands
import discord
from .mylib import database
from .mylib import utils
import asyncio
import datetime


class Submission(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role("委員会")
    @commands.group()
    async def item(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.reply("このコマンドにはサブコマンドが必要です。")

    @item.command()
    async def make(self, ctx, item_name=None):
        def check(m):
            return (
                m.channel == ctx.channel
                and m.author == ctx.author
                and len(m.content) != 0
            )

        # name
        if item_name is None:
            msg_ask_item_name = await ctx.reply("📛 提出先の名前は何にしますか？")
            try:
                m_item_name = await self.bot.wait_for(
                    "message", check=check, timeout=60
                )
            except asyncio.TimeoutError:
                return await msg_ask_item_name.reply(
                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                )
            item_name = m_item_name.content

        # targets
        msg_ask_role = await ctx.reply(
            "👤 対象者はどのロールにしますか？\n" + "__Discord のメンション機能を使用して、__ロールを指定してください。"
        )
        try:
            m_item_target = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await msg_ask_role.reply("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        roles = m_item_target.role_mentions
        if len(roles) == 0:
            return await msg_ask_role.reply("正しく指定されませんでした。")
        item_target_role_id_list = [role.id for role in roles]

        # limit
        msg_ask_limit = await ctx.reply(
            "⏰ 提出期限を指定してください。\n"
            + "入力例: 2023年4月1日 21時30分 としたい場合は、`2023/4/1 21:30` と入力します。\n",
        )
        try:
            m_item_limit = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await msg_ask_limit.reply("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        if not utils.is_datetime(m_item_limit.content):
            return await m_item_limit.reply(
                "⚠ 指定された期限をうまく解釈できませんでした。\n"
                + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n"
                + "もう一度、最初から操作をやり直してください。"
            )
        item_limit = datetime.datetime.strptime(m_item_limit.content, "%Y/%m/%d %H:%M")
        if item_limit < datetime.datetime.now():
            return await m_item_limit.reply(
                "⚠ 提出期限が過去に設定されています。\nもう一度、最初からやり直してください。",
            )

        # format
        msg_ask_format = await ctx.reply(
            "💾 提出形式はどちらにしますか？\n" + "ファイル形式の場合は `file`、プレーンテキスト形式の場合は `plain` と返信してください。"
        )
        try:
            m_item_format = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await msg_ask_format.reply(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
            )
        if m_item_format.content not in ["file", "plain"]:
            return await m_item_format.reply(
                "⚠ 提出形式が正確に指定されていません。\n"
                + "`file` か `plain` のどちらかを返信してください。\n"
                + "もう一度、最初から操作をやり直してください。"
            )
        item_format = m_item_format.content

        # handler
        item_handler = ctx.author.roles[-1].name

        for target_role_id in item_target_role_id_list:
            database.item_table.insert(
                dict(
                    name=item_name,
                    target_role_id=target_role_id,
                    limit=item_limit.timestamp(),
                    format=item_format,
                    handler=item_handler,
                )
            )
        embed = discord.Embed(
            title="✅ 提出先作成", description="提出先を登録しました:", color=discord.Color.green()
        )
        embed.add_field(name="📛項目名:", value=item_name, inline=False)
        embed.add_field(
            name="👤対象:", value="".join([role.mention for role in roles]), inline=False
        )
        embed.add_field(name="⏰期限:", value=m_item_limit.content, inline=False)
        embed.add_field(name="💾種類:", value=item_format, inline=False)
        embed.add_field(name="設定者:", value=item_handler, inline=False)
        await ctx.reply(embed=embed)

    @item.command()
    async def delete(self, ctx, item_name=None):
        if item_name is None:
            return await ctx.send("削除する提出物の名前が指定されていません。")
        if not database.is_item_exist(item_name):
            return await ctx.send("存在しない提出物名が指定されました。")
        all_item = database.get_all_item_named(item_name)
        if len(all_item) == 1:
            all_item[0].delete()
            return await ctx.send(f"{item_name}を削除しました。")
        all_item = [all_item[idx : idx + 10] for idx in range(0, len(all_item), 10)]
        count = 1
        for item_container in all_item:
            embeds = []
            for item in item_container:
                role = self.bot.guild.get_role(item.target_role_id)
                dt = datetime.datetime.fromtimestamp(item.limit)
                if role is None:
                    await ctx.send(
                        f"ロールが存在しないデータがありました。管理者に連絡してください。role_id={item.target_role_id}"
                    )
                    continue
                embed = discord.Embed(
                    description=f"📛項目名: {item.name}\n"
                                f"👤対象: {role.mention}\n"
                                f"⏰期限: {dt.strftime('%Y/%m/%d %H:%M:%S')}\n"
                                f"💾種類: {item.format}\n"
                                f"設定者: {item.handler}",
                    color=discord.Color.green(),
                )
                embeds.append(embed)
                count += 1
            await ctx.send(content=f"{count-len(embeds)}~{count-1}", embeds=embeds)

        def check(m):
            return (
                m.channel == ctx.channel
                and m.author == ctx.author
                and len(m.content) != 0
            )

        await ctx.send(
            "上記の提出物をすべて削除しますか？\n承認する場合は`ok`と発言してください。\n指定したい場合は`no`と発言してください。"
        )
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.reply("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        if msg.content == "ok":
            all_item = database.get_all_item_named(item_name)
            for item in all_item:
                item.delete()
        elif msg.content == "no":
            msg_ask_role = await msg.reply(
                "👤 対象者はどのロールにしますか？\n" + "__Discord のメンション機能を使用して、__ロールを指定してください。"
            )
            try:
                m_item_target = await self.bot.wait_for(
                    "message", check=check, timeout=60
                )
            except asyncio.TimeoutError:
                return await msg_ask_role.reply("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
            roles = m_item_target.role_mentions
            if len(roles) == 0:
                return await msg_ask_role.reply("正しく指定されませんでした。")
            target_role_id_list = [role.id for role in roles]
            all_item = database.get_all_item_named(item_name)
            for item in all_item:
                if item.target_role_id in target_role_id_list:
                    item.delete()
        else:
            return await msg.reply("⚠ 期待された返答ではありません。もう一度、最初から操作をやり直してください。")
        return await ctx.send(f"{item_name}を削除しました。")

    @item.command(name="list")
    async def _list(self, ctx):
        all_item = database.get_all_item()
        if len(all_item) == 0:
            return await ctx.send("404: 提出物 Not found")
        all_item = [all_item[idx : idx + 10] for idx in range(0, len(all_item), 10)]
        count = 1
        for item_container in all_item:
            embeds = []
            for item in item_container:
                role = self.bot.guild.get_role(item.target_role_id)
                if role is None:
                    await ctx.send(
                        f"ロールが存在しないデータがありました。管理者に連絡してください。role_id={item.target_role_id}"
                    )
                    continue
                dt = datetime.datetime.fromtimestamp(item.limit)
                embed = discord.Embed(
                    description=f"📛項目名: {item.name}\n"
                                f"👤対象: {role.mention}\n"
                                f"⏰期限: {dt.strftime('%Y/%m/%d %H:%M:%S')}\n"
                                f"💾種類: {item.format}\n"
                                f"設定者: {item.handler}",
                    color=discord.Color.green(),
                )
                embeds.append(embed)
                count += 1
            await ctx.send(content=f"{count-len(embeds)}~{count-1}", embeds=embeds)


async def setup(bot):
    await bot.add_cog(Submission(bot))
