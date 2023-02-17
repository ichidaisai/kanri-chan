from discord.ext import commands
import discord
import pdf2image
import asyncio
import io


class FileViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supported_extensions = ["application/pdf"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) == 0:
            return
        if message.channel.type != discord.ChannelType.text:
            return
        # 添付されたファイルの中に対応している拡張子がなければ無視
        attachment_content_type_list = [
            attachment.content_type for attachment in message.attachments
        ]
        if len(set(attachment_content_type_list) & set(self.supported_extensions)) == 0:
            return

        thread = await message.create_thread(name=message.attachments[0].filename)
        for attachment in message.attachments:
            loop = asyncio.get_running_loop()
            images = []
            # pdf -> jpeg
            if attachment.content_type == "application/pdf":
                pdf_io = io.BytesIO()
                await attachment.save(pdf_io)
                images = await loop.run_in_executor(
                    None, pdf2image.convert_from_bytes, pdf_io.read()
                )
            else:
                continue

            await thread.send(
                embed=discord.Embed(
                    title=attachment.filename, color=discord.Color.blue()
                )
            )
            images = [images[idx : idx + 10] for idx in range(0, len(images), 10)]
            count = 1
            for image_container in images:
                files = []
                for image in image_container:
                    fileio = io.BytesIO()
                    image.save(fileio, format="jpeg")
                    fileio.seek(0)
                    files.append(discord.File(fileio, filename="image.jpg"))
                    count += 1
                await thread.send(
                    content=f"{count-len(files)}~{count-1}ページ", files=files
                )


async def setup(bot):
    await bot.add_cog(FileViewer(bot))
