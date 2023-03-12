from discord.ext import commands
import discord
from mylib import database
import asyncio
import datetime
from constant import SERVER_ID


class Document(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def submit_document(self, interaction, union):
        def check(m):
            return (
                m.channel == interaction.channel
                and m.author == interaction.user
                and len(m.content) != 0
            )

        await interaction.channel.send("提出先のidを送信してください。")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await interaction.channel.send(
                content="⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
            )
        try:
            dest_id = int(msg.content)
        except ValueError:
            return await interaction.channel.send(
                content="idではない返答を受け取りました。もう一度、最初から操作をやり直してください。"
            )
        dest = database.Dest(id=dest_id)
        role = self.bot.guild.get_role(dest.role_id)
        if role not in interaction.user.roles:
            return await interaction.channel.send(content="あなたはこの提出先の対象ではありません。")
        if database.is_document_exist(dest_id=dest_id, union_id=union.id):
            await interaction.channel.send(
                "既に提出済みです。上書きしますか？`はい`と送信してください。しない場合は`はい`以外を送信して下さい。"
            )
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await interaction.channel.send(
                    content="⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                )
            if msg.content != "はい":
                return await interaction.channel.send(content="中断しました。")
        if dest.format == "ファイル":

            def check(m):
                return (
                    m.channel == interaction.channel
                    and m.author == interaction.user
                    and len(m.content) != 0
                    and len(m.attachments) != 0
                )

        await interaction.channel.send("提出物を送信してください。")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await interaction.channel.send(
                content="⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
            )
        # 書き込み
        if not database.is_document_exist(dest_id=dest_id, union_id=union.id):
            database.document_table.insert(
                dict(dest_id=dest_id, union_id=union.id, msg_url=msg.jump_url)
            )
        else:
            document = database.Document(dest_id=dest_id, union_id=union.id)
            document.msg_url = msg.jump_url
            document.update()
        await interaction.channel.send("提出を受け付けました。")

    async def check_dest(self, interaction, union):
        """未提出の提出先を確認"""
        all_dest = database.get_all_dest()
        if len(all_dest) == 0:
            return await interaction.channel.send("提出先が存在しません。")
        embeds = []
        count = 1
        for dest in all_dest:
            role = self.bot.guild.get_role(dest.role_id)
            if role not in interaction.user.roles:
                continue
            if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                continue
            dt = datetime.datetime.fromtimestamp(dest.limit)
            handler_role = self.bot.guild.get_role(dest.handler_id)
            embed = discord.Embed(
                description=f"""
                            id: {dest.id}
                            📛項目名: {dest.name}
                            👤対象: {role.mention}
                            ⏰期限: {dt.strftime('%Y/%m/%d %H:%M:%S')}
                            💾種類: {dest.format}
                            設定者: {handler_role.mention}
                            """,
                color=discord.Color.green(),
            )
            embeds.append(embed)
            count += 1
        if len(embeds) == 0:
            return await interaction.channel.send("提出先が存在しません。")
        all_embeds = [embeds[idx : idx + 10] for idx in range(0, len(embeds), 10)]
        for embeds in all_embeds:
            await interaction.channel.send(embeds=embeds)

    async def document_list(self, interaction, union):
        """提出したものを閲覧"""
        document_list = database.get_documents(union_id=union.id)
        if len(document_list) == 0:
            return await interaction.channel.send("まだ提出していません。")
        all_document = [
            document_list[idx : idx + 10] for idx in range(0, len(document_list), 10)
        ]
        count = 1
        for document_container in all_document:
            embeds = []
            for document in document_container:
                dest = database.Dest(id=document.dest_id)
                role = self.bot.guild.get_role(union.role_id)
                embed = discord.Embed(
                    description=f"""
                                id: {document.id}
                                提出先: {dest.name}
                                団体名: {role.mention}
                                提出物: [jump]({document.msg_url})
                                """,
                    color=discord.Color.green(),
                )
                embeds.append(embed)
                count += 1
            await interaction.channel.send(
                f"{count-len(embeds)}~{count-1}", embeds=embeds
            )


async def setup(bot):
    await bot.add_cog(Document(bot))
