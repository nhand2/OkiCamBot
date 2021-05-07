import asyncio
import discord
import random
import datetime
from datetime import datetime, timedelta
import pytz
from pytz import timezone, utc
from asyncio import sleep as s
import json
import requests
import sys

from discord.ext import commands
from discord import Embed
from decouple import config
from settings import Settings


class BasicCommandsCog(commands.Cog, name='Basic Commands'):

    # The list of boba messages.
    bobaMessageList = [
        'No. You should not get boba :[',
        'Yes! You should get boba! :]',
        'Of course! Boba time! <3',
        'Boba is always the answer!'
    ]

    # The list of messages from oki.
    okiLoveMsgList = [
        'I love {0}! They\'re the best!',
        '{0} is such a cool person!',
        'Bork means I love you in dog!',
        'I love {0} more than I love food! And that\'s a lot!'
    ]

    # The list of messages from oki to nam.
    okiNamMsgList = [
        '{0} is smelly >:3',
        '{0} holds me weird :\\',
        '{0} is okay. I guess.',
        'Meh.'
    ]

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

    # The cog command error.
    # Overrides the base class function.
    async def cog_command_error(self, ctx, error):
        print('ERROR: {0.command.qualified_name}:{1}'.format(ctx, error))

    # The hello command.
    # Says hello the the caller.
    @commands.command(name='hello')
    async def say_hello(self, ctx):
        """Say hello to oki!"""

        await ctx.send('Bork Bork!')

    # The translate command.
    # Oki will show you some love!
    @commands.command(name='translate')
    async def oki_love(self, ctx):
        '''I translate what Oki says!'''

        member = ctx.author
        if member.id == int(Settings.NAM_UID):
            await ctx.send(random.choice(self.okiNamMsgList).format(member.mention))
        else:
            await ctx.send(random.choice(self.okiLoveMsgList).format(member.mention))

    # The broki command.
    # Disconnect and reconnect the Oki cam.
    @commands.command(name='broki')
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

    # The sik fan command.
    # Used to call the family for dinner.
    @commands.command(name='sikfan')
    async def call_for_dinner(self, ctx, *args):
        '''Time for dinner!'''
        await ctx.message.delete()

        if len(args) == 1 and args[0] == Settings.SECRET_COMMAND:
            derek = await ctx.guild.fetch_member(Settings.DEREK_UID)
            jon = await ctx.guild.fetch_member(Settings.JON_UID)
            sophie = await ctx.guild.fetch_member(Settings.SOAP_UID)
            nam = await ctx.guild.fetch_member(Settings.NAM_UID)

            await ctx.send('Time to eat! {0} {1} {2} {3}'.format(derek.mention, jon.mention, sophie.mention, nam.mention))
        else:
            await ctx.send('Time to eat!!')

    # The boba command.
    # Let the bot decide if you should get boba.
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
                    return (m.content == 'yes' or m.content == 'no') and m.channel == ctx.message.channel and m.author == ctx.author

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=15.0)
                except asyncio.TimeoutError:
                    await ctx.send('You did not reply to the message! :[', delete_after=5.0)
                else:
                    if msg.content == 'no':
                        await ctx.send('Okay!', delete_after=5.0)
                        await msg.delete(delay=5.0)
                    else:
                        await self.get_boba_from_yelp(ctx)

    # The boba where command.
    # If the user enters this subcommand, a random boba location is obtained.
    @boba.command(name='where')
    async def where(self, ctx):
        '''I can suggest a place!'''
        await self.get_boba_from_yelp(ctx)

    # The get boba from yelp.
    # Returns the coroutine that contains an embeded version of the the boba location suggested from yelp.
    # The boba location must be open now, and within Las Vegas
    def get_boba_from_yelp(self, ctx):
        params = {'term': 'boba', 'location': '89148',
                'limit': '20', 'open_now': True}
        header = {"User-Agent": "DiscordBot:OkiCamBot/bot:0.0.1 (by nipdip discord)", 'Authorization': 'Bearer {}'.format(Settings.YELP_API_KEY)}
        response = requests.get(
            'https://api.yelp.com/v3/businesses/search', params=params, headers=header)

        yelpRespDict = json.loads(response.content)

        suggestionDict = {}
        for businessObj in yelpRespDict['businesses']:
            if businessObj['name'] == 'Kung Fu Tea':
                continue
            else:
                suggestionDict[businessObj['name']] = [
                    businessObj['url'], businessObj['image_url'], businessObj['location']]

        suggested = random.choice(list(suggestionDict.items()))

        discordEmbed = Embed()
        discordEmbed.title = suggested[0]
        discordEmbed.set_thumbnail(url=suggested[1][1])
        discordEmbed.url = suggested[1][0]
        discordEmbed.add_field(
            name='Address', value='{0}\n{1}, {2}, {3}'.format(suggested[1][2]['address1'], suggested[1][2]['city'], suggested[1][2]['state'], suggested[1][2]['zip_code']))
        return ctx.send(content='How about {0}?'.format(suggested[0]), embed=discordEmbed)

    # The purge command.
    # Purges messages within 100 (total) messages.
    @commands.command(name='purge')
    async def purge_commands(self, ctx):
        '''OkiBot can clean it's mess'''
        await ctx.channel.purge(limit=100, check=self.meet_criteria_for_purge)

    # The meet criteria for purge.
    # Determines if the messages meet the criteria for purging.
    def meet_criteria_for_purge(self, message):
        return message.author == self.bot.user or message.content.__contains__(Settings.OKI_BOT_COMMAND_PREFIX)

    @commands.command()
    async def reminder(self, ctx, *args):
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
        print("present time at LV is "+ p_time)
        # oki.reminder 1d 3h 3m 2s WOOT
        dCount = 0
        hCount = 0
        mCount = 0
        sCount = 0
        while args[count][0].isnumeric() and  args[count][-1].isalpha() and count < 4:
            if args[count][-1] == 'd':
                dCount += 1
                if dCount < 2: 
                    day = int(args[count][:-1])
                else:
                    break
                
            elif args[count][-1] == 'h':
                hCount += 1
                if hCount < 2:
                    hour = int(arg[count][:-1])
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
        
        await ctx.send("days: " + str(day) + ", hours: " + str(hour) + ", minutes: " + str(mins) + ", seconds: "+ str(sec))
        update_time = datetime.now() + timedelta(days = day, hours = hour, minutes = mins, seconds = sec)
        u_time = update_time.strftime("%b %d, %I:%M:%S")
        print("updated time at LV is "+ u_time)
        while u_time >= p_time:
            present_time = datetime.now()
            pp_time = timezone.localize(present_time)
            p_time = pp_time.strftime("%b %d, %I:%M:%S")
            print("this is current present time: " + p_time + ", reminder: " + u_time)

            await asyncio.sleep(1)
        await member.send(msg)
        

def setup(bot):
    bot.add_cog(BasicCommandsCog(bot))
