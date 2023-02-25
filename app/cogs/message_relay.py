from discord.ext import commands
from discord import app_commands
import discord
import os


class RelaySelect(discord.ui.View):
    def __init__(
        self, cog_cls, target_channel_dict, message_relaying_map, display_roles_map
    ):
        super().__init__(timeout=None)
        self.add_item(ChannelSelect(cog_cls, target_channel_dict, message_relaying_map))
        self.add_item(RoleSelect(cog_cls, display_roles_map))


class ChannelSelect(discord.ui.Select):
    def __init__(self, cog_cls, target_channel_dict, message_relaying_map):
        self.cog_cls = cog_cls
        self.message_relaying_map = message_relaying_map
        options = []
        for name, _id in target_channel_dict:
            options.append(discord.SelectOption(label=name, description="", value=_id))

        super().__init__(
            placeholder="チャンネル選択", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        self.message_relaying_map[interaction.channel_id] = int(self.values[0])
        await self.cog_cls.on_update(interaction.channel)


class RoleSelect(discord.ui.Select):
    def __init__(self, cog_cls, display_roles_map):
        self.cog_cls = cog_cls
        roles = ["なし", "カフェ局", "模擬局", "システム局"]
        self.display_roles_map = display_roles_map
        options = []
        for role in roles:
            options.append(discord.SelectOption(label=role, description=""))

        super().__init__(
            placeholder="ロール選択", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        self.display_roles_map[interaction.channel_id] = self.values[0]
        await self.cog_cls.on_update(interaction.channel)


class MessageRelay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_relaying_map = {}
        self.display_roles_map = {}

    def get_webfook_icon_url(self, role_name):
        # 緑色 https://discord.com/assets/7c8f476123d28d103efe381543274c25.png
        if role_name == "なし":
            return None
        elif role_name == "カフェ局":
            # 黄色
            return "https://discord.com/assets/6f26ddd1bf59740c536d2274bb834a05.png"
        elif role_name == "模擬局":
            # 赤色
            return "https://discord.com/assets/3c6ccb83716d1e4fb91d3082f6b21d77.png"
        elif role_name == "システム局":
            # 灰色
            return "https://discord.com/assets/c09a43a372ba81e3018c3151d4ed4773.png"
        else:
            # 青色
            return None

    async def setup_select(self, channel):
        target_category = self.bot.guild.get_channel(int(channel.topic))
        target_channel_dict = [(ch.name, ch.id) for ch in target_category.text_channels]
        self.message_relaying_map[channel.id] = target_channel_dict[0][1]
        self.display_roles_map[channel.id] = "なし"
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="送信先", value=target_channel_dict[0][0])
        embed.add_field(name="表示ロール", value="なし")
        await channel.send(embed=embed)
        await channel.send(
            view=RelaySelect(
                self,
                target_channel_dict,
                self.message_relaying_map,
                self.display_roles_map,
            )
        )
        await self.clear_bot_message(channel)

    async def clear_bot_message(self, channel):
        messages = [message async for message in channel.history(oldest_first=True)]
        for i, message in enumerate(messages):
            if i == len(messages) - 1:
                break
            next_message = messages[i + 1]
            if (
                next_message.author == self.bot.user
                and len(next_message.embeds) != 0
                and message.author == self.bot.user
            ):
                await message.delete()

    async def on_update(self, channel):
        target_category = self.bot.guild.get_channel(int(channel.topic))
        target_channel_dict = [(ch.name, ch.id) for ch in target_category.text_channels]
        target_channel_name = self.bot.guild.get_channel(
            self.message_relaying_map[channel.id]
        ).name
        role_name = self.display_roles_map[channel.id]
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="送信先", value=target_channel_name)
        embed.add_field(name="表示ロール", value=role_name)
        await channel.send(embed=embed)
        await channel.send(
            view=RelaySelect(
                self,
                target_channel_dict,
                self.message_relaying_map,
                self.display_roles_map,
            )
        )
        await self.clear_bot_message(channel)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id not in self.message_relaying_map.keys():
            return
        target_channel = self.bot.guild.get_channel(
            self.message_relaying_map.get(message.channel.id)
        )
        name = self.display_roles_map[message.channel.id]
        icon_url = self.get_webfook_icon_url(name)
        webhooks = await target_channel.webhooks()
        webhook = None
        if len(webhooks) != 0:
            webhook = webhooks[0]
        else:
            webhook = await target_channel.create_webhook(name="Spidey Bot")  # 意味はない
        if name == "なし":
            name = message.author.display_name
            icon_url = message.author.display_avatar
        files = [await attachment.to_file() for attachment in message.attachments]
        await webhook.send(
            content=message.content, username=name, avatar_url=icon_url, files=files
        )

    @commands.command()
    async def reload_select(self, ctx):
        for channel in self.bot.category_channel.text_channels:
            await self.setup_select(channel)
        await ctx.send("リロード完了しました")


async def setup(bot):
    await bot.add_cog(MessageRelay(bot))
