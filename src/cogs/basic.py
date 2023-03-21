import asyncio
import random
import requests
import json
import logging

from asyncio import sleep as s
from datetime import datetime, timedelta
from decouple import config
from discord import Embed
from discord.ext import commands, tasks
from pytz import timezone, utc
from settings import Settings
from bot_helper import UID_ENUM

class BasicCommandsCog(commands.Cog, name='Basic Commands'):

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
    
    userUidDict = {}
    
    # The __init__
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.getLogger('__main__').handlers[0])
        
    @commands.Cog.listener()
    async def on_ready(self):
        for key, uid in Settings.USER_UIDS.items():
            try:
                self.userUidDict[key] = await self.bot.fetch_user(int (uid))
            except:
                self.logger.info(f"{key} {uid} ")
                
    async def cog_load(self):
        self.logger.info("Loaded Basic Cog")
        
    async def cog_unload(self) -> None:
        self.logger.info("Unloaded Basic Cog")

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
        if member.id == int(Settings.USER_UIDS.get(UID_ENUM.NAM)):
            await ctx.send(random.choice(self.okiNamMsgList).format(member.mention))
        else:
            if member.id == int(Settings.USER_UIDS.get(UID_ENUM.FANFAN)) and random.randrange(20, 25, 3) == 23:
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
        self.logger.warn(f'WARN: {error} in {ctx.command}')
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
            await ctx.send(f'Time to eat! {self.userUidDict.get(UID_ENUM.SOAP).mention} {self.userUidDict.get(UID_ENUM.DEREK).mention} {self.userUidDict.get(UID_ENUM.JON).mention} {self.userUidDict.get(UID_ENUM.NAM).mention}')
        except IndexError:
            await ctx.send('Time to eat!!')

    # The sik fan error handler.
    # args:
    #   ctx: context
    #   error: error object
    @call_for_dinner.error
    async def call_for_dinner_error(self, ctx, error):
        self.logger.warn(f'WARN: {error} in {ctx.command}')
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command can only be ran 5 times in 1 minute! Try again in {error.retry_after:.0f} seconds!')

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

"""
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
"""

async def setup(bot):
    await bot.add_cog(BasicCommandsCog(bot))
