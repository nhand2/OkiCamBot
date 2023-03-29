import asyncio
import json
import logging
import time
from datetime import timedelta

import discord
import requests
from discord import Embed
from discord.ext import commands, tasks

from settings import Settings


class ApexCommandsCog(commands.Cog, name="Apex Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.getLogger("__main__").handlers[0])
        self.message = None
        self.currentMapEndTime = None

    async def cog_load(self):
        self.logger.info("Loaded Apex Cog")

    async def cog_unload(self) -> None:
        self.logger.info("Unloaded Apex Cog")

    # The Apex map rotation command.
    # Gets the current apex map rotation.
    # args:
    #   ctx: context
    @commands.command(name="apex", aliases=["rotation"])
    @commands.cooldown(rate=1, per=10.0)
    async def apex(self, ctx):
        """What map are we on? Everyone hates Storm Point"""
        self.try_get_map.start(ctx)

        # logging.warn("WARN: Apex timer failed to restart. Please manually restart timer.")

    # Catches errors from the apex command.
    # args:
    #   ctx: context
    #   error: error received
    @apex.error
    async def apex_error(self, ctx, error):
        self.logger.warn(f"WARN: {error} in {ctx.command}")
        await ctx.message.delete()

    # Try to get the current map information
    @tasks.loop(seconds=1)
    async def try_get_map(self, ctx):
        now = int(time.time())
        if self.message is not None and now <= self.currentMapEndTime:
            self.discordEmbed.set_field_at(
                index=0,
                name="Time Remaining",
                value="{:0>8}".format(
                    str(timedelta(seconds=self.currentMapEndTime - now))
                ),
            )
            try:
                await self.message.edit(embed=self.discordEmbed)
            except discord.NotFound:
                self.logger.warn("WARN: Message deleted, breaking loop!")
                self.try_get_map.stop()
            return

        apexJsonResp = self.get_from_apex()

        try:
            currentMap = apexJsonResp["battle_royale"]["current"]
            nextMap = apexJsonResp["battle_royale"]["next"]

            if self.currentMapEndTime is not None and now < self.currentMapEndTime:
                self.discordEmbed.set_field_at(
                    index=0, name="Time Remaining", value=currentMap["remainingTimer"]
                )
            else:
                self.currentMapEndTime = currentMap["end"]
                self.discordEmbed = self.create_apex_embed(currentMap, nextMap)

            try:
                await self.message.edit(embed=self.discordEmbed)
            except:
                self.logger.info("Message does not exist! Creating!")
                self.message = await ctx.send(
                    content=f"Map Rotation", embed=self.discordEmbed
                )
        except Exception as e:
            # Start a 30 second delay to allow the json to refresh between map changes.

            self.logger.warn(f"WARN: Unexpected response fron Apex API: {apexJsonResp}")
            self.logger.warn(f"EXCEPTION: {e}")
            await asyncio.sleep(30)

    # The get from apex api.
    def get_from_apex(self):
        header = {
            "User-Agent": "DiscordBot:OkiCamBot/bot:0.0.1 (by nipdip discord)",
            "Authorization": "Bearer {}".format(Settings.APEX_API_KEY),
        }
        response = requests.get(
            f"https://api.mozambiquehe.re/maprotation?auth={Settings.APEX_API_KEY}&version=1",
            headers=header,
        )

        apexJsonResp = json.loads(response.content)

        return apexJsonResp

    # The create apex embed.
    # Creates the embed to send to the discord server.
    # args:
    #   currentMap: The current map object
    #   nextMap: The next map object
    def create_apex_embed(self, currentMap, nextMap):
        discordEmbed = Embed(title=currentMap["map"], color=0xB93038)
        self.logger.info(currentMap["map"])
        discordEmbed.set_image(url=currentMap["asset"]),
        discordEmbed.add_field(
            name="Time Remaining", value="{0}".format(currentMap["remainingTimer"])
        )
        discordEmbed.add_field(name="\u200B", value="\u200B")
        discordEmbed.add_field(name="Next map", value="{0}".format(nextMap["map"]))

        return discordEmbed


async def setup(bot):
    await bot.add_cog(ApexCommandsCog(bot))
