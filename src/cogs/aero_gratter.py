import asyncio
import datetime
import discord
import random
import requests
import json
import pytz
import logging

from datetime import datetime, timedelta
from pytz import timezone, UTC
from discord.ext import commands, tasks
from logging import handlers

class AeroGratter(commands.Cog):
    subscriber_list = {}
    
    def __init__(self, bot):
        handler = handlers.RotatingFileHandler(filename=f'aero_gratter_results_{datetime.now(pytz.timezone("America/Los_Angeles"))}.log', encoding='utf-8', maxBytes=32 * 1024 * 1024, backupCount=3)
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)
        
        self.bot = bot
        
        
    async def cog_load(self):
        self.logger.info("Loaded Aero Gratter Cog")
        
    async def cog_unload(self) -> None:
        self.logger.info("Unloaded Aero Gratter Cog")
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.get_aero_avail.start('https://seats.aero/api/availability', 'lifemiles')
        
    @tasks.loop(seconds=10)
    async def get_aero_avail(self, uri, mileage_plan):
        params = {'source': mileage_plan}
        header = {"User-Agent": "DiscordBot:OkiCamBot/bot:0.0.1 (by nipdip discord)"}
        
        response = requests.get(uri)
            
        respDict = json.loads(response.content)
        for avails in respDict:
            if (avails['Route']['OriginAirport'] == 'SEA' and avails['Route']['DestinationAirport'] == 'HND'):
                title = f'=====Flight from {avails["Route"]["OriginAirport"]} to {avails["Route"]["DestinationAirport"]} on {avails["Date"]}====='
                self.logger.info("=" * title.__len__())
                self.logger.info(title)
                self.logger.info("=" * title.__len__())
                self.logger.info(f'\tSeats Available:')
                self.logger.info(f'\tEconomy {avails["YAvailable"]}')
                self.logger.info(f'\tBusiness {avails["JAvailable"]}')
                self.logger.info(f'\tFirst Class {avails["FAvailable"]}')
                self.logger.info("=" * title.__len__())

            
    @commands.command(name='aerosub')
    async def subscribe_to_aerogratter(self, ctx):
        """Subscribe the user to aerogratter"""
        member = ctx.author
        
        self.subscriber_list.add(member.id, False)
        
    def try_connect_new_subs(self):
        for id, subbed in self.subscriber_list.items:
            if not subbed:
                self.subscriber_list[id] = True
                
    def send_to_subs(self):
        for id, subbed in self.subscriber_list.items():
            if subbed:
                print(f"Member id is {id}")
                
async def setup(bot):
    await bot.add_cog(AeroGratter(bot))