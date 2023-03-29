import asyncio
import datetime
import json
import logging
import pandas

from datetime import datetime
from logging import handlers
import pytz
import requests
from discord.ext import commands, tasks
from pytz import UTC, timezone

from database import aerogratter_db
import sys

class AeroGratter(commands.Cog):
    subscriber_list = {}
    no_flights_list = []
    flights_dict = {}
        

    def __init__(self, bot):
        handler = handlers.RotatingFileHandler(
            filename=f'aero_gratter_results_{datetime.now(pytz.timezone("America/Los_Angeles"))}.log',
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,
            backupCount=3,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.bot = bot
        self.db = aerogratter_db.AeroGratterDb(bot.db_client)

    async def cog_load(self):
        self.logger.info("Loaded Aero Gratter Cog")

    async def cog_unload(self) -> None:
        self.get_aero_avail.close()
        self.logger.info("Unloaded Aero Gratter Cog")

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.get_aero_avail.start("https://seats.aero/api/availability", "lifemiles")
        except:
            logging.info('Closing!')
            self.get_aero_avail.close()

    @tasks.loop(hours=1)
    async def get_aero_avail(self, uri, mileage_plan):
        params = {"source": mileage_plan}
        header = {"User-Agent": "DiscordBot:OkiCamBot/bot:0.0.1 (by nipdip discord)"}

        self.flights_dict = {}
        response = requests.get(uri)

        #print (response.json())
        df = pandas.DataFrame.from_records(response.json())
        
        for chunk in [df[i:i+100] for i in range(0, df.shape[0],100)]:
            print (chunk)
            self.logger.info('Processing chunk...')
            await self.process_data(chunk)
            self.logger.info('Done processing chunk! Going to sleep.')
            await asyncio.sleep(0.5)
            
            self.logger.info('Grabbing next chunk!')
        
        for flight in self.flights_dict:
            self.flights_dict[flight] += f"\n```"
            self.logger.info(self.flights_dict[flight])
        
        subs = self.db.get_all_subscribers()
        for sub in subs:
            user = self.bot.get_user(sub["user_id"]) or await self.bot.fetch_user(sub["user_id"])
            await user.send(self.flights_dict[sub['origin']+sub['dest']])
    
    async def process_data(self, chunk):
        for avails in chunk.to_dict('records'):
            if (self.has_subscribers(avails["Route"]["OriginAirport"], avails["Route"]["DestinationAirport"])):
                title = f'=====Flight from {avails["Route"]["OriginAirport"]} to {avails["Route"]["DestinationAirport"]} on {avails["Date"]}====='
                flight = str("=" * title.__len__())
                flight += title
                flight += str("=" * title.__len__())
                flight += f"\tSeats Available:"
                flight += f'\tEconomy {avails["YAvailable"]}'
                flight += f'\tBusiness {avails["JAvailable"]}'
                flight += f'\tFirst Class {avails["FAvailable"]}'
                flight += "=" * title.__len__()
                
                if avails["Route"]["OriginAirport"]+avails["Route"]["DestinationAirport"] in self.flights_dict:
                    self.flights_dict[avails["Route"]["OriginAirport"]+avails["Route"]["DestinationAirport"]] += f"\n{flight}"
                else:
                    self.flights_dict[avails["Route"]["OriginAirport"]+avails["Route"]["DestinationAirport"]] = f"```\nflight"


    @commands.command(name="aerosub")
    async def subscribe_to_aerogratter(self, ctx, *, args):
        """Subscribe the user to aerogratter"""
        member = ctx.author
        
        location = args.split('>')
        self.logger.info(location)
        if len(location) <= 1:
            await ctx.send("Please retry with this format! Origin>Dest")
            return
        
        self.logger.info(f"{member} is making a call!")
        
        try:
            if self.db.insert(member, location[0], location[1]):
                await ctx.send("You are subscribed!")
            else:
                await ctx.send("You are already subscribed!")
        except:
            await ctx.send("I couldn't subscribe you! Try again later!")
            
    @subscribe_to_aerogratter.error
    async def subscribe_to_aerogratter_error(self, ctx, error):
        self.logger.warn(f'WARN: {error} in {ctx.command}')
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send ("Retry with the format `oki.aerogratter ORIGIN>DEST")

    def has_subscribers(self, originAirport, destAirport):
        if originAirport in self.no_flights_list:
            return False
        else:
            sub_count = self.db.get_subscribed_count(originAirport, destAirport)
            if sub_count > 0:
                self.logger.info(f'Flights from {originAirport} to {destAirport} has {sub_count} subscribers.')
            return sub_count > 0

async def setup(bot):
    await bot.add_cog(AeroGratter(bot))