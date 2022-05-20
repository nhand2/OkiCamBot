import asyncio
import datetime
import discord
import random
import requests
import json
import pytz

from asyncio import sleep as s
from datetime import datetime, timedelta
from decouple import config
from discord import Embed
from discord.ext import commands, tasks
from main import OkiCamBot
from pytz import timezone, utc
from settings import Settings

class BasicCommandsCog(commands.Cog, name='Basic Commands'):

    # The list of boba messages.
    bobaMessageList = [
        'No. You should not get boba :[',
        'Yes! You should get boba! :]',
        'Of course! Boba time! <3',
        'Boba is always the answer!',
        'Always choose boba!'
    ]

    # The list of messages from oki.
    okiLoveMsgList = [
        'I love {0}! They\'re the best!',
        '{0} is such a cool person!',
        'Bork means I love you in dog!',
        'I love {0} more than I love food! And that\'s a lot!',
        '大好き！！',
        'I love {0} more than I love Mario!',
        'Bork! Bork! Bork! <3'
    ]

    # The list of messages from oki to nam.
    okiNamMsgList = [
        '{0} is smelly >:3',
        '{0} holds me weird :\\',
        '{0} is okay. I guess.',
        'Meh.',
        '{0} is pretty cool ;D',
        'Hello {0}.'
    ]

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

    # The 2b copy pasta.
    twob = '''
⠄⠄⠄⠄⢠⣿⣿⣿⣿⣿⢻⣿⣿⣿⣿⣿⣿⣿⣿⣯⢻⣿⣿⣿⣿⣆⠄⠄⠄
⠄⠄⣼⢀⣿⣿⣿⣿⣏⡏⠄⠹⣿⣿⣿⣿⣿⣿⣿⣿⣧⢻⣿⣿⣿⣿⡆⠄⠄
⠄⠄⡟⣼⣿⣿⣿⣿⣿⠄⠄⠄⠈⠻⣿⣿⣿⣿⣿⣿⣿⣇⢻⣿⣿⣿⣿⠄⠄
⠄⢰⠃⣿⣿⠿⣿⣿⣿⠄⠄⠄⠄⠄⠄⠙⠿⣿⣿⣿⣿⣿⠄⢿⣿⣿⣿⡄⠄
⠄⢸⢠⣿⣿⣧⡙⣿⣿⡆⠄⠄⠄⠄⠄⠄⠄⠈⠛⢿⣿⣿⡇⠸⣿⡿⣸⡇⠄
⠄⠈⡆⣿⣿⣿⣿⣦⡙⠳⠄⠄⠄⠄⠄⠄⢀⣠⣤⣀⣈⠙⠃⠄⠿⢇⣿⡇⠄
⠄⠄⡇⢿⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄⣠⣶⣿⣿⣿⣿⣿⣿⣷⣆⡀⣼⣿⡇⠄
⠄⠄⢹⡘⣿⣿⣿⢿⣷⡀⠄⢀⣴⣾⣟⠉⠉⠉⠉⣽⣿⣿⣿⣿⠇⢹⣿⠃⠄
⠄⠄⠄⢷⡘⢿⣿⣎⢻⣷⠰⣿⣿⣿⣿⣦⣀⣀⣴⣿⣿⣿⠟⢫⡾⢸⡟⠄.
⠄⠄⠄⠄⠻⣦⡙⠿⣧⠙⢷⠙⠻⠿⢿⡿⠿⠿⠛⠋⠉⠄⠂⠘⠁⠞⠄⠄⠄
⠄⠄⠄⠄⠄⠈⠙⠑⣠⣤⣴⡖⠄⠿⣋⣉⣉⡁⠄⢾⣦⠄⠄⠄⠄⠄⠄⠄⠄'''

    # The Oki cam fix status message.
    fixingOkiMessage = 'Fixing Oki'

    # The response if Oki cam is not in voice channel.
    voiceErrorMessage = 'Oki is not home right now!'

    # The list of messages Oki Bot can send.
    messageList = {
        fixingOkiMessage,
        voiceErrorMessage
    }

    # The __init__
    def __init__(self, bot):
        self.bot = bot
        self.initialize.start()

    # The initialize
    # Task loop to initalize all variables. Time out in 60 seconds.
    @tasks.loop(seconds=60.0)
    async def initialize(self):
        self.derek = await self.bot.fetch_user(Settings.DEREK_UID)
        self.jon = await self.bot.fetch_user(Settings.JON_UID)
        self.sophie = await self.bot.fetch_user(Settings.SOAP_UID)
        self.nam = await self.bot.fetch_user(Settings.NAM_UID)
        self.fanfan = await self.bot.fetch_user(Settings.FANFAN_UID)

        self.initialize.cancel()

    # The before initialize loop
    # Triggered before the initalize loop.
    # Waits until the bot is ready to proceed.
    @initialize.before_loop
    async def before_initialize(self):
        await self.bot.wait_until_ready()
        print ('Initializing variables!')

    # The after initialize loop
    # Triggered after task loop is complete
    @initialize.after_loop
    async def after_initialize(self):
        print ('Initialization done!')

    # The hello command.
    # Says hello the the caller.
    # args:
    #   ctx: context
    @commands.command(name='hello')
    async def say_hello(self, ctx):
        """Say hello to oki!"""

        await ctx.send('Bork Bork!')

    # The translate command.
    # Oki will show you some love!
    # args:
    #   ctx: context
    @commands.command(name='translate', aliases=['t'])
    async def oki_love(self, ctx):
        '''I translate what Oki says!'''

        member = ctx.author
        if member.id == int(Settings.NAM_UID):
            await ctx.send(random.choice(self.okiNamMsgList).format(member.mention))
        else:
            if member.id == int(Settings.FANFAN_UID) and random.randrange(20, 25, 3) == 23:
                await ctx.send("{0} is my favorite person! <3".format(member.mention))
            else:
                await ctx.send(random.choice(self.okiLoveMsgList).format(member.mention))

    # The choose command.
    # Oki chooses between the options
    # args:
    #   ctx: context
    #   arg: the key-word argument.
    @commands.command(name='choose', aliases=['c'])
    async def choose(self, ctx, *, arg):
        '''Can't make a decision? Allow Oki to choose for you'''

        choices = arg.split('|')
        if len(choices) <= 1:
            raise commands.MissingRequiredArgument
            return

        await ctx.send(random.choice(self.choiceMessagesList).format(random.choice(choices)))

    # The choose error handler.
    # Handles errors
    # args:
    #   ctx: context
    #   error: error thrown
    @choose.error
    async def choose_error(self, ctx, error):
        print (f'WARN: {error} in {ctx.command}')
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Retry with the format `oki.choose <choice1> | <choice2> | ... | <choice(n)>.`')

    # The broki command.
    # Disconnect and reconnect the Oki cam.
    # args:
    #   ctx: context
    @commands.command(name='broki', aliases=['b'])
    async def fix_oki_cam(self, ctx):
        '''Fixes the Oki cam when Darnell or Kevin joins, smh my head'''

        await ctx.send(self.fixingOkiMessage)
        oki = await ctx.guild.fetch_member(Settings.OKI_UID)

        if oki is not None and oki.voice is not None:
            currentVoiceChannel = oki.voice.channel

            afk_channel = ctx.guild.afk_channel

            if currentVoiceChannel == afk_channel:
                return

            await oki.move_to(afk_channel)
            await asyncio.sleep(2)
            await oki.move_to(currentVoiceChannel)
        else:
            await ctx.send(self.voiceErrorMessage)

        await ctx.message.delete(delay=2)

    # The call 2b commant.
    # Prints the 2b copy pasta.
    @commands.command(name='booty', aliases=['2b'])
    async def call_2b(self, ctx):
        await ctx.send(self.twob)

    # The sik fan command.
    # Used to call the family for dinner.
    # args:
    #   ctx: context
    #   *args: array of arguments
    @commands.command(name='sikfan')
    @commands.cooldown(rate=5, per=60.0)
    async def call_for_dinner(self, ctx, *args):
        '''Time for dinner!'''
        await ctx.message.delete()

        try: 
            args[0] == Settings.SECRET_COMMAND
            await ctx.send(f'Time to eat! {self.derek.mention} {self.jon.mention} {self.sophie.mention} {self.nam.mention}')
        except IndexError:
            await ctx.send('Time to eat!!')

    # The sik fan error handler.
    # args:
    #   ctx: context
    #   error: error object
    @call_for_dinner.error
    async def call_for_dinner_error(self, ctx, error):
        print (f'WARN: {error} in {ctx.command}')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command can only be ran 5 times in 1 minute! Try again in {error.retry_after:.0f} seconds!')

    # The Apex map rotation command.
    # Gets the current apex map rotation.
    # args:
    #   ctx: context
    @commands.command(name='apex', aliases=['rotation'])
    @commands.cooldown(rate=1, per=10.0)
    async def apex(self, ctx):
        '''What map are we on? Everyone hates Storm Point'''

        if OkiCamBot.APEX_RUNNING :
            print ("WARN: Already Running!")
            await ctx.message.delete()
            return

        OkiCamBot.APEX_RUNNING = True

        apexJsonResp = self.get_from_apex()

        currentMap = apexJsonResp['current']
        nextMap = apexJsonResp['next']
        
        currentMapEndTime = datetime.strptime(currentMap['readableDate_end'], '%Y-%m-%d %H:%M:%S')
        discordEmbed = self.create_apex_embed(currentMap, nextMap)

        message = await ctx.send(content=f'Map Rotation', embed=discordEmbed)
        
        retries = 0
        while retries < 3:
            while OkiCamBot.APEX_RUNNING:
                await asyncio.sleep(30)

                now = datetime.now()
                
                apexJsonResp = self.get_from_apex()
                
                try: 
                    currentMap = apexJsonResp['current']
                    nextMap = apexJsonResp['next']

                    if now < currentMapEndTime:
                        discordEmbed.set_field_at(index=0, name="Time Remaining", value=currentMap['remainingTimer'])
                    else:
                        currentMapEndTime = datetime.strptime(currentMap['readableDate_end'], '%Y-%m-%d %H:%M:%S')
                        discordEmbed = self.create_apex_embed(currentMap, nextMap)

                    try:
                        await message.edit(embed=discordEmbed)
                    except discord.NotFound:
                        OkiCamBot.APEX_RUNNING = False
                        print("WARN: Message deleted, breaking loop!")
                        return
                except:
                    # Start a 30 second delay to allow the json to refresh between map changes.
                    
                    print (f"WARN: Unexpected response fron Apex API: {apexJsonResp}")
                    await asyncio.sleep(30)
            
            print ("WARN: Apex timer has stopped working! Retrying in 1 min...")
            retries += 1
            asyncio.sleep(60)
            OkiCamBot.APEX_RUNNING = True
        
        print ("WARN: Apex timer failed to restart. Please manually restart timer.")
                
    # Catches errors from the apex command.
    # args:
    #   ctx: context
    #   error: error received
    @apex.error
    async def apex_error(self, ctx, error):
        print (f"WARN: {error} in {ctx.command}")
        OkiCamBot.APEX_RUNNING = False
        await ctx.message.delete()

    # The get from apex api.
    def get_from_apex(self):
        header = {"User-Agent": "DiscordBot:OkiCamBot/bot:0.0.1 (by nipdip discord)",
                  'Authorization': 'Bearer {}'.format(Settings.APEX_API_KEY)}
        response = requests.get(
            'https://api.mozambiquehe.re/maprotation?auth={}'.format(Settings.APEX_API_KEY), headers=header)

        apexJsonResp = json.loads(response.content)

        return apexJsonResp
    
    # The create apex embed.
    # Creates the embed to send to the discord server.
    # args:
    #   currentMap: The current map object
    #   nextMap: The next map object
    def create_apex_embed(self, currentMap, nextMap):
        discordEmbed = Embed(
            title = currentMap['map'],
            color = 0xB93038 )
        discordEmbed.set_image(url=currentMap['asset']),
        discordEmbed.add_field(
            name='Time Remaining', 
            value='{0}'.format(currentMap['remainingTimer']))
        discordEmbed.add_field(
            name = '\u200B',
            value = '\u200B'
        )
        discordEmbed.add_field(
            name='Next map',
            value='{0}'.format(nextMap['map'])
        )

        return discordEmbed

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
        response = requests.get(
            'https://api.yelp.com/v3/businesses/search', params=params, headers=header)

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

    # The purge command.
    # Purges messages within 100 (total) messages.
    # args:
    #   ctx: context
    @commands.command(name='purge')
    async def purge_commands(self, ctx):
        '''OkiBot can clean it's mess'''
        await ctx.channel.purge(limit=100, check=self.meet_criteria_for_purge)

    # The meet criteria for purge.
    # Determines if the messages meet the criteria for purging.
    # args:
    #   message: message
    def meet_criteria_for_purge(self, message):
        return message.author == self.bot.user or message.content.__contains__(Settings.OKI_BOT_COMMAND_PREFIX)

    # The reminder command.
    # Allows user to set reminders.
    # args:
    #   ctx: context
    #   *args: the indexed arguments.
    @commands.command(name='reminder', aliases=['r', 'remind'])
    async def reminder(self, ctx, *args):
        '''Set a reminder! (format: oki.reminder <w>d <x>h <y>m <z>s <message>)'''

        member = ctx.author
        day = 0
        hour = 0
        mins = 0
        sec = 0
        msg = "default"
        count = 0
        timezone = pytz.timezone("America/Los_Angeles")
        present_time = datetime.now()
        pp_time = timezone.localize(present_time)
        p_time = pp_time.strftime("%b %d, %I:%M:%S %Z")
        print("present time at LV is " + p_time)
        # oki.reminder 1d 3h 3m 2s WOOT
        dCount = 0
        hCount = 0
        mCount = 0
        sCount = 0
        while args[count][0].isnumeric() and args[count][-1].isalpha() and count < 4:
            if args[count][-1] == 'd':
                dCount += 1
                if dCount < 2:
                    day = int(args[count][:-1])
                else:
                    break

            elif args[count][-1] == 'h':
                hCount += 1
                if hCount < 2:
                    hour = int(args[count][:-1])
                else:
                    break

            elif args[count][-1] == 'm':
                mCount += 1
                if mCount < 2:
                    mins = int(args[count][:-1])
                else:
                    break

            elif args[count][-1] == 's':
                sCount += 1
                if sCount < 2:
                    sec = int(args[count][:-1])
                else:
                    break

            print(args[count][-1])
            print(args[count][:-1])
            print(count)
            count += 1

        msg = ' '.join(args[count:])

        await ctx.send("days: " + str(day) + ", hours: " + str(hour) + ", minutes: " + str(mins) + ", seconds: " + str(sec))
        update_time = datetime.now() + timedelta(days=day, hours=hour,
                                                 minutes=mins, seconds=sec)
        u_time = update_time.strftime("%b %d, %I:%M:%S")
        print("updated time at LV is " + u_time)
        while u_time >= p_time:
            present_time = datetime.now()
            pp_time = timezone.localize(present_time)
            p_time = pp_time.strftime("%b %d, %I:%M:%S")
            # print("this is current present time: " +
            # p_time + ", reminder: " + u_time)

            await asyncio.sleep(1)
        await member.send(msg)


def setup(bot):
    bot.add_cog(BasicCommandsCog(bot))
