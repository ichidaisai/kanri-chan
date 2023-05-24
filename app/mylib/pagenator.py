from __future__ import annotations

import discord
from discord.ext import commands


class Pagenator(discord.ui.View):
    def __init__(
        self,
        embed_pages,
        ctx,
        initial_page: int = 0,
        allow_others_access: bool = False,
        ephemeral: bool = False,
    ):
        super().__init__(timeout=None)
        self.embed_pages = embed_pages
        self.ctx = ctx
        self.initial_page = initial_page
        self.allow_others_access = allow_others_access
        self.ephemeral = ephemeral

        self.total_page_count = len(embed_pages)
        self.current_page = self.initial_page
        self.message = None

        self.back_button = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025c0"))
        self.next_button = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025b6"))
        self.page_counter_style = discord.ButtonStyle.grey
        self.back_button.callback = self.back_button_callback
        self.next_button.callback = self.next_button_callback
        self.page_counter = PageCounter(
            style=self.page_counter_style,
            total_page_count=self.total_page_count,
            initial_page=self.initial_page,
        )
        self.add_item(self.back_button)
        self.add_item(self.page_counter)
        self.add_item(self.next_button)

    async def start(self):
        self.message = await self.ctx.send(
            embeds=self.embed_pages[self.initial_page], view=self, ephemeral=self.ephemeral
        )

    async def go_back(self):
        self.current_page = (self.current_page - 1) % self.total_page_count
        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.message.edit(embeds=self.embed_pages[self.current_page], view=self)

    async def go_next(self):
        self.current_page = (self.current_page + 1) % self.total_page_count
        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.message.edit(embeds=self.embed_pages[self.current_page], view=self)

    async def next_button_callback(self, interaction):
        if interaction.user != self.ctx.author and self.allow_others_access:
            embed = discord.Embed(
                description="実行者のみ操作可能です。",
                color=discord.Colour.red(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.go_next()
        await interaction.response.defer()

    async def back_button_callback(self, interaction):
        if interaction.user != self.ctx.author and self.allow_others_access:
            embed = discord.Embed(
                description="実行者のみ操作可能です。",
                color=discord.Colour.red(),
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.go_back()
        await interaction.response.defer()


class PageCounter(discord.ui.Button):
    def __init__(self, style: discord.ButtonStyle, total_page_count, initial_page):
        super().__init__(
            label=f"{initial_page + 1}/{total_page_count}", style=style, disabled=True
        )
