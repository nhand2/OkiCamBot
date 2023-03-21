import asyncio
import random
import requests
import json
import logging

from asyncio import sleep as s
from decouple import config
from discord import Embed
from discord.ext import commands, tasks
from pytz import timezone, utc
from settings import Settings
from logging import handlers

class YelpCommandsCog(commands.Cog, name="Yelp Commands"):
    # The list of choice messages.
    choiceMessagesList = [
        '{0} is a good choice!',
        'You can never go wrong with {0}',
        '{0} is best!',
        'Why not go with {0}!',
        'I choose...{0}'
    ]

    # The list of banned locations.
    # Do not show these.
    bannedBobaList = [
        'MadHouse Coffee',
        'Kung Fu Tea',
        'Scoop LV'
    ]

    # The price range list for yelp api.
    priceRange = [
        '1,2,3,4',
        '1',
        '1,2',
        '1,2,3',
        '1,2,3,4'
    ]
    
    # The list of boba messages.
    bobaMessageList = [
        'No. You should not get boba :[',
        'Yes! You should get boba! :]',
        'Of course! Boba time! <3',
        'Boba is always the answer!',
        'Always choose boba!'
    ]
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.getLogger('__main__').handlers[0])

    async def cog_load(self):
        self.logger.info("Loaded Yelp Cog")
        
    async def cog_unload(self) -> None:
        self.logger.info("Unloaded Yelp Cog")
    
    # The recommend command.
    # Recommends a restaurant meeting the criteria.
    # args:
    #   ctx: context
    #   arg: key-word arguments
    @commands.command(name='recommend', aliases=['rec'])
    @commands.cooldown(rate=1, per=10.0)
    async def recommend(self, ctx, *, arg):
        '''Let me recommend you a place! Usage: oki.recommend <category> | <$$$$(price)>'''
        parsedArg = arg.split('|')
        query = parsedArg[0]

        price = 0
        if len(parsedArg) > 1:
            price = parsedArg[1].count('$', 1, 5)

            print(price)

        print(query)
        print(self.priceRange[price])
        await self.get_from_yelp(ctx, query, 'restaurants', self.priceRange[price])

    # The recommend error handler.
    # args:
    #   ctx: context
    #   error: The error thrown in string form.
    @recommend.error
    async def recommend_error(self, ctx, error):
        print (f'WARN: {error} in {ctx.command}')
        if isinstance(error, commands.MissingRequiredArgument):
            self.recommend.reset_cooldown(ctx)
            await ctx.send('You didn\'t specify what you wanted to me to recommend!')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'The command is currently on cooldown! Try again in {error.retry_after:.0f} seconds!')

    # The boba command.
    # Let the bot decide if you should get boba.
    # args:
    #   ctx: context
    @commands.group(name='boba')
    async def boba(self, ctx):
        '''Let me decide if you should get boba!'''
        if ctx.invoked_subcommand is None:
            value = random.randrange(len(self.bobaMessageList))
            await ctx.send(self.bobaMessageList[value])

            if value > 0:
                await asyncio.sleep(0.5)
                await ctx.send("Should I choose? (reply with 'yes' or 'no')", delete_after=18.0)

                # Checks to see if the message is send from the user and matches the input.
                def check(m):
                    return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == ctx.message.channel and m.author == ctx.author

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                except asyncio.TimeoutError:
                    await ctx.send('You did not reply to the message! :[', delete_after=5.0)
                else:
                    if msg.content == 'no':
                        await ctx.send('Okay!', delete_after=5.0)
                        await msg.delete(delay=5.0)
                    else:
                        await self.get_from_yelp(ctx, 'boba', 'bubbletea')

    # The boba where command.
    # If the user enters this subcommand, a random boba location is obtained.
    # args:
    #   ctx: context
    @boba.command(name='where')
    async def where(self, ctx):
        '''I can suggest a place!'''
        await self.get_from_yelp(ctx, 'boba', 'bubbletea')

    # The get query from yelp.
    # Returns the coroutine that contains an embeded version of the the query location suggested from yelp.
    # The query location must be open now, and within Las Vegas
    # args:
    #   ctx: context
    #   query: the query to search for on yelp
    #   price: defaults to '1,2,3,4'. the price range.
    def get_from_yelp(self, ctx, query, category, price='1,2,3,4'):
        params = {'term': f'{query}', 'location': 'Las Vegas',
                  'limit': '20', 'open_now': True, 'price': f'{price}', 
                  'categories': f'{category}'}
        header = {"User-Agent": "DiscordBot:OkiCamBot/bot:0.0.1 (by nipdip discord)",
                  'Authorization': 'Bearer {}'.format(Settings.YELP_API_KEY)}
        
        try:
            response = requests.get(
                'https://api.yelp.com/v3/businesses/search', params=params, headers=header)
        except Exception as e:
            self.logger.warn(f'EXCEPTION: COULD NOT COMPLETE REQUEST DUE TO {e}')
            
        if response.status_code != 200:
            self.logger.warn(f'Yelp responsed with status code: {response.status_code}')
            return ctx.send(content=f'I couldn\'t find anything! Try again later!')

        yelpRespDict = json.loads(response.content)

        suggestionDict = {}
        for businessObj in yelpRespDict['businesses']:
            if businessObj['name'] in self.bannedBobaList or businessObj['rating'] < 3:
                continue
            else:
                suggestionDict[businessObj['name']] = [
                    businessObj['url'], businessObj['image_url'], businessObj['location']]

        try:
            suggested = random.choice(list(suggestionDict.items()))
        except IndexError:
            return ctx.send('Sorry! I couldn\'t find anything. :[')
        else:
            discordEmbed = Embed(
                title = suggested[0],
                url = suggested[1][0],
                color = 0x3a86ff )
            discordEmbed.set_thumbnail(url=suggested[1][1]),
            discordEmbed.add_field(
                name='Address', 
                value='{0}\n{1}, {2}, {3}'.format(suggested[1][2]['address1'], suggested[1][2]['city'], suggested[1][2]['state'], suggested[1][2]['zip_code']) )
            return ctx.send(content=f'How about {suggested[0]}?', embed=discordEmbed)

async def setup(bot):
    await bot.add_cog(YelpCommandsCog(bot))