# 外部モジュール
import asyncio
import datetime
import discord
from discord import app_commands
from discord.ext import commands
import io
import os
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import shutil
import zipfile

# 内部モジュール
from constant import SERVER_ID, GOOGLE_DRIVE_FOLDER_ID, NOTICE_CATEGORY_ID
import mylib
from mylib import database, utils, Pagenator


class Document(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def submit_document(self, interaction, ctx, union):
        type_role = discord.utils.get(self.bot.guild.roles, name=union.type)
        all_dest = database.get_dests(type_role.id) + database.get_dests(union.role_id)
        if len(all_dest) == 0:
            return await interaction.channel.send("提出先が存在しません。")
        all_dest = utils.sort_dests_for_limit(all_dest)
        now = datetime.datetime.now()
        now = now.replace(minute=now.minute, second=0, microsecond=0)
        embeds = []
        for dest in all_dest:
            limit_dt = datetime.datetime.fromtimestamp(dest.limit)
            if now >= limit_dt:
                continue
            role = self.bot.guild.get_role(dest.role_id)
            handler_role = self.bot.guild.get_role(dest.handler_id)
            embed = discord.Embed(
                description=f"id: {dest.id}\n"
                f"📛項目名: {dest.name}\n"
                f"👤対象: {role.mention}\n"
                f"⏰期限: {limit_dt.strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"💾種類: {dest.format}\n"
                f"設定者: {handler_role.mention}",
                color=discord.Color.green(),
            )
            embeds.append(embed)
        if len(embeds) == 0:
            return await interaction.channel.send("提出先が存在しません。")
        all_embeds = [embeds[idx : idx + 5] for idx in range(0, len(embeds), 5)]
        await Pagenator(embed_pages=all_embeds, ctx=ctx).start()

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
        if not database.is_dest_exist(dest_id=dest_id):
            return await interaction.channel.send(
                content="存在しない提出先のIDを受け取りました。もう一度、最初から操作をやり直してください。"
            )
        dest = database.Dest(id=dest_id)
        now = datetime.datetime.now()
        now = now.replace(minute=now.minute, second=0, microsecond=0)
        limit_dt = datetime.datetime.fromtimestamp(dest.limit)
        if now >= limit_dt:
            return await interaction.channel.send(content="提出期限を過ぎたので、提出できません。")
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
        # 提出通知
        document = database.Document(dest_id=dest_id, union_id=union.id)
        notice_channel = discord.utils.get(
            (self.bot.guild.get_channel(NOTICE_CATEGORY_ID)).text_channels,
            name=union.type,
        )
        embed = discord.Embed(
            description=f"提出物id: {document.id}\n"
            f"提出先: {dest.name}(id={dest.id})\n"
            f"団体名: {union.name}\n"
            f"提出物: [jump]({document.msg_url})",
            color=discord.Color.green(),
        )
        await notice_channel.send(content="🔔 新しい提出があります。", embed=embed)

    async def check_dest(self, interaction, ctx, union):
        """未提出の提出先を確認"""
        type_role = discord.utils.get(self.bot.guild.roles, name=union.type)
        all_dest = database.get_dests(type_role.id) + database.get_dests(union.role_id)
        if len(all_dest) == 0:
            return await interaction.channel.send("提出先が存在しません。")
        all_dest = utils.sort_dests_for_limit(all_dest)
        embeds = []
        for dest in all_dest:
            role = self.bot.guild.get_role(dest.role_id)
            if role not in interaction.user.roles:
                continue
            if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                continue
            dt = datetime.datetime.fromtimestamp(dest.limit)
            handler_role = self.bot.guild.get_role(dest.handler_id)
            embed = discord.Embed(
                description=f"id: {dest.id}\n"
                f"📛項目名: {dest.name}\n"
                f"👤対象: {role.mention}\n"
                f"⏰期限: {dt.strftime('%Y/%m/%d %H:%M:%S')}\n"
                f"💾種類: {dest.format}\n"
                f"設定者: {handler_role.mention}",
                color=discord.Color.green(),
            )
            embeds.append(embed)
        if len(embeds) == 0:
            return await interaction.channel.send("提出先が存在しません。")
        all_embeds = [embeds[idx : idx + 5] for idx in range(0, len(embeds), 5)]
        await Pagenator(embed_pages=all_embeds, ctx=ctx).start()

    async def document_list(self, interaction, ctx, union):
        """提出したものを閲覧"""
        document_list = database.get_documents(union_id=union.id)
        if len(document_list) == 0:
            return await interaction.channel.send("まだ提出していません。")
        document_list = utils.sort_documents_for_id(document_list)
        all_document = [
            document_list[idx : idx + 5] for idx in range(0, len(document_list), 5)
        ]
        all_embeds = []
        for document_container in all_document:
            embeds = []
            for document in document_container:
                try:
                    dest = database.Dest(id=document.dest_id)
                except mylib.errors.DestNotExist:
                    dest = None
                role = self.bot.guild.get_role(union.role_id)
                embed = discord.Embed(
                    description=f"提出先id: {dest.id if dest is not None else -1}\n"
                    f"提出先: {dest.name if dest is not None else 'Unknown'}\n"
                    f"団体名: {role.mention}\n"
                    f"提出物: [jump]({document.msg_url})",
                    color=discord.Color.green(),
                )
                embeds.append(embed)
            all_embeds.append(embeds)
        await Pagenator(embed_pages=all_embeds, ctx=ctx).start()


@app_commands.guilds(discord.Object(id=SERVER_ID))
class DocumentCommandGroup(app_commands.Group):
    pass


class DocumentManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

    document_group = DocumentCommandGroup(name="提出物", description="提出物を操作します。")

    @app_commands.describe(
        union_role="作成する団体をロールで指定",
        dest_id="提出する提出先をIDで指定",
    )
    @app_commands.rename(
        union_role="団体", dest_id="提出先", content="プレーンテキスト", attachment="ファイル"
    )
    @document_group.command(name="作成", description="提出物作成")
    async def make_document(
        self,
        interaction,
        union_role: discord.Role,
        dest_id: int,
        content: str = None,
        attachment: discord.Attachment = None,
    ):
        if not database.is_union_exist(union_role_id=union_role.id):
            return await interaction.response.send_message("存在しない団体です。")
        if not database.is_dest_exist(dest_id=dest_id):
            return await interaction.response.send_message("存在しない提出先です。")
        union = database.Union(role_id=union_role.id)
        dest = database.Dest(id=dest_id)
        if dest.format == "プレーンテキスト" and content is None:
            return await interaction.response.send_message("プレーンテキストで提出してください。")
        elif dest.format == "ファイル" and attachment is None:
            return await interaction.response.send_message("ファイルで提出してください。")
        if attachment:
            file_io = io.BytesIO()
            await attachment.save(file_io)
            file_io.seek(0)
            msg = await interaction.channel.send(
                content, files=[discord.File(file_io, filename=attachment.filename)]
            )
        else:
            msg = await interaction.channel.send(content)
        if not database.is_document_exist(dest_id=dest_id, union_id=union.id):
            database.document_table.insert(
                dict(dest_id=dest_id, union_id=union.id, msg_url=msg.jump_url)
            )
        else:
            document = database.Document(dest_id=dest_id, union_id=union.id)
            document.msg_url = msg.jump_url
            document.update()
        await interaction.response.send_message("提出を受け付けました。")

    @app_commands.describe(
        union_role="提出物を削除する団体をロールで指定",
        dest_id="削除する提出物の提出先をIDで指定",
    )
    @app_commands.rename(
        union_role="団体",
        dest_id="提出先",
    )
    @document_group.command(name="削除", description="提出物削除")
    async def delete_document(
        self,
        interaction,
        union_role: discord.Role,
        dest_id: int,
    ):
        if not database.is_union_exist(union_role_id=union_role.id):
            return await interaction.response.send_message("存在しない団体です。")
        if not database.is_dest_exist(dest_id=dest_id):
            return await interaction.response.send_message("存在しない提出先です。")
        union = database.Union(role_id=union_role.id)
        if not database.is_document_exist(dest_id=dest_id, union_id=union.id):
            return await interaction.response.send_message("存在しない提出物です。")
        document = database.Document(dest_id=dest_id, union_id=union.id)
        document.delete()
        await interaction.response.send_message("提出物を削除しました。")

    @app_commands.describe(
        union_role="提出物を出力する団体をロールで指定",
        dest_id="提出物確認リストを出力する提出先をIDで指定",
    )
    @app_commands.rename(
        union_role="団体",
        dest_id="提出先",
    )
    @document_group.command(name="確認", description="提出物確認")
    async def check_document(
        self,
        interaction,
        union_role: discord.Role = None,
        dest_id: int = None,
    ):
        if union_role and dest_id:
            if not database.is_union_exist(union_role_id=union_role.id):
                return await interaction.response.send_message("存在しない団体です。")
            union = database.Union(role_id=union_role.id)
            if not database.is_dest_exist(dest_id=dest_id):
                return await interaction.response.send_message("存在しない提出先です。")
            dest = database.Dest(id=dest_id)
            if not database.is_document_exist(dest_id=dest_id, union_id=union.id):
                return await interaction.response.send_message("未提出です。")
            document = database.Document(dest_id=dest_id, union_id=union.id)
            embed = discord.Embed(
                description=f"id: {document.id}\n"
                f"提出先: {dest.name}\n"
                f"団体名: {union_role.mention}\n"
                f"提出物: [jump]({document.msg_url})",
                color=discord.Color.green(),
            )
            return await interaction.response.send_message("提出済みです。", embed=embed)
        elif union_role:
            if not database.is_union_exist(union_role_id=union_role.id):
                return await interaction.response.send_message("存在しない団体です。")
            union = database.Union(role_id=union_role.id)
            abs_role = discord.utils.get(self.bot.guild.roles, name=union.type)
            dests_for_type = database.get_dests(role_id=abs_role.id)
            dests_for_union = database.get_dests(role_id=union.role_id)
            dests = list(set(dests_for_type + dests_for_union))
            if len(dests) == 0:
                return await interaction.response.send_message("この団体に指示されている提出先はありません。")
            table = f"union_name: {union.name}\nunion_type: {union.type}\n\n"
            for dest in dests:
                if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                    table += f"{dest.name}:  ✅\n"
                else:
                    table += f"{dest.name}:  ❌\n"
            embed = discord.Embed(
                title=f"{union.name}に指示されている提出先の一覧",
                description=table,
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)
        elif dest_id:
            if not database.is_dest_exist(dest_id=dest_id):
                return await interaction.response.send_message("存在しない提出先です。")
            dest = database.Dest(id=dest_id)
            role = self.bot.guild.get_role(dest.role_id)
            if database.is_union_exist(union_role_id=role.id):
                union = database.Union(role_id=role.id)
                if not database.is_document_exist(dest_id=dest_id, union_id=union.id):
                    return await interaction.response.send_message("未提出です。")
                document = database.Document(dest_id=dest_id, union_id=union.id)
                embed = discord.Embed(
                    description=f"id: {document.id}\n"
                    f"提出先: {dest.name}\n"
                    f"団体名: {role.mention}\n"
                    f"提出物: [jump]({document.msg_url})",
                    color=discord.Color.green(),
                )
                return await interaction.response.send_message("提出済みです。", embed=embed)
            union_list = [
                union for union in database.get_all_union() if union.type == role.name
            ]
            table = f"dest_id: {dest.id}\ndest_name: {dest.name}\n\n"
            for union in union_list:
                if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                    table += f"id: {union.id}: {union.name}:  ✅\n"
                else:
                    table += f"id: {union.id}: {union.name}:  ❌\n"
            embed = discord.Embed(
                title=f"{dest.name}の提出状況",
                description=table,
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)
        else:
            return await interaction.response.send_message("団体もしくは提出先を指定してください。")

    @app_commands.describe(
        dest_id="リストを出力する提出先をIDで指定",
    )
    @app_commands.rename(
        dest_id="提出先",
    )
    @document_group.command(name="出力", description="提出物出力")
    async def export_document(
        self,
        interaction,
        dest_id: int,
    ):
        if not database.is_dest_exist(dest_id=dest_id):
            return await interaction.response.send_message("存在しない提出先です。")
        dest = database.Dest(id=dest_id)
        role = self.bot.guild.get_role(dest.role_id)
        if database.is_union_exist(union_role_id=role.id):
            union = database.Union(role_id=role.id)
            if not database.is_document_exist(dest_id=dest_id, union_id=union.id):
                return await interaction.response.send_message("未提出です。")
            document = database.Document(dest_id=dest_id, union_id=union.id)
            embed = discord.Embed(
                description=f"id: {document.id}\n"
                f"提出先: {dest.name}\n"
                f"団体名: {role.mention}\n"
                f"提出物: [jump]({document.msg_url})",
                color=discord.Color.green(),
            )
            return await interaction.response.send_message(
                "提出済みです。リンクから提出内容を確認してください。", embed=embed
            )
        await interaction.response.defer(thinking=True)
        union_list = [
            union for union in database.get_all_union() if union.type == role.name
        ]
        now = datetime.datetime.now()
        if dest.format == "プレーンテキスト":
            file_name = f"{now.strftime('%Y-%m-%d-%H-%M-%S')}_dest_{dest.id}.xlsx"
            export_list = []
            for union in union_list:
                if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                    document = database.Document(dest_id=dest.id, union_id=union.id)
                    message = await utils.get_message_from_url(
                        document.msg_url, self.bot.guild
                    )
                    if message is None:
                        await interaction.followup.send(
                            f"message not found {document.union_id}:{document.msg_url}"
                        )
                        continue
                    export_list.append(
                        [
                            document.id,
                            message.created_at.strftime("%Y-%m-%d-%H:%M:%S"),
                            message.author.display_name,
                            message.channel.name,
                            message.content,
                        ]
                    )
            df = pd.DataFrame(export_list)
            df.set_axis(
                ["提出 ID", "提出日時", "提出者", "提出元ロール", "提出内容"], axis="columns", copy=False
            )
            df.to_excel(file_name, sheet_name="結果", index=False)
            await interaction.followup.send(file=discord.File(file_name))
            os.remove(file_name)
        elif dest.format == "ファイル":
            folder_path = f"{now.strftime('%Y-%m-%d-%H-%M-%S')}_dest_{dest.id}"
            os.mkdir(folder_path)
            zip_path = folder_path + ".zip"
            zip_f = zipfile.ZipFile(zip_path, "w")
            for union in union_list:
                if database.is_document_exist(dest_id=dest.id, union_id=union.id):
                    document = database.Document(dest_id=dest.id, union_id=union.id)
                    message = await utils.get_message_from_url(
                        document.msg_url, self.bot.guild
                    )
                    if message is None:
                        await interaction.channel.send(
                            f"message not found {document.union_id}:{document.msg_url}"
                        )
                        continue
                    if len(message.attachments) == 0:
                        await interaction.channel.send(
                            f"attachiment not found {document.union_id}:{document.msg_url}"
                        )
                        continue
                    attachment = message.attachments[0]
                    await attachment.save(
                        folder_path
                        + f"/{union.name}.{attachment.filename.split('.')[-1]}"
                    )

                    zip_f.write(
                        folder_path
                        + f"/{union.name}.{attachment.filename.split('.')[-1]}",
                        compress_type=zipfile.ZIP_LZMA,
                    )
            zip_f.close()
            try:
                await interaction.followup.send(file=discord.File(zip_path))
            except Exception:
                try:
                    drive_file = self.drive.CreateFile(
                        {"parents": [{"id": GOOGLE_DRIVE_FOLDER_ID}]}
                    )
                    drive_file.SetContentFile(zip_path)
                    drive_file.Upload()
                    await interaction.followup.send(
                        f"ファイルが大きすぎたため、Google Driveにアップロードしました。\nhttps://drive.google.com/uc?export=download&id={drive_file['id']}"
                    )
                except Exception:
                    await interaction.followup.send("エラーが発生しました。管理者まで連絡してください。")
            shutil.rmtree(folder_path)


async def setup(bot):
    await bot.add_cog(Document(bot))
    await bot.add_cog(DocumentManager(bot))
