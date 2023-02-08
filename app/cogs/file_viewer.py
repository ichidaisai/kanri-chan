from discord.ext import commands
import discord
import io


class FileViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) == 0:
            return
        if message.channel.type != discord.ChannelType.text:
            return
        thread = await message.create_thread(name=message.attachments[0].filename)
        images = []
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
            await thread.send(content=f"{count-len(files)}~{count-1}ページ", files=files)


async def setup(bot):
    await bot.add_cog(FileViewer(bot))
