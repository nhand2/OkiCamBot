import asyncio
import discord
import random
import datetime
from datetime import datetime, timedelta
import pytz
from pytz import timezone, utc
from asyncio import sleep as s

from discord.ext import commands


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
        if member.id == int(self.bot.NAM_UID):
            await ctx.send(self.okiNamMsgList[random.choice([0, 1, 2, 3])].format(member.mention))
        else:
            await ctx.send(self.okiLoveMsgList[random.choice([0, 1, 2, 3])].format(member.mention))

    # The broki command.
    # Disconnect and reconnect the Oki cam.
    @commands.command(name='broki')
    async def fix_oki_cam(self, ctx):
        '''Fixes the Oki cam when Darnell or Kevin joins, smh my head'''

        await ctx.send(self.fixingOkiMessage)
        oki = await ctx.guild.fetch_member(self.bot.OKI_UID)

        if oki is not None and oki.voice is not None:
            currentVoiceChannel = oki.voice.channel

            afk_channel = ctx.guild.afk_channel

            if currentVoiceChannel == afk_channel:
                return

            await oki.move_to(afk_channel)
            await asyncio.sleep(5)
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
        
        if len(args) == 1 and args[0] == self.bot.SECRET_COMMAND:
            derek = await ctx.guild.fetch_member(self.bot.DEREK_UID)
            jon = await ctx.guild.fetch_member(self.bot.JON_UID)
            sophie = await ctx.guild.fetch_member(self.bot.SOAP_UID)
            nam = await ctx.guild.fetch_member(self.bot.NAM_UID)

            await ctx.send('Time to eat! {0} {1} {2} {3}'.format(derek.mention, jon.mention, sophie.mention, nam.mention))
        else:
            await ctx.send('Time to eat!!')

    # The boba command.
    # Let the bot decide if you should get boba.
    @commands.command(name='boba')
    async def should_get_boba(self, ctx):
        '''Let me decide if you should get boba!'''

        value = random.choice([0, 1, 2, 3])
        await ctx.send(self.bobaMessageList[value])

    # The purge command.
    # Purges messages within 100 (total) messages.
    @commands.command(name='purge')
    async def purge_commands(self, ctx):
        '''OkiBot can clean it's mess'''
        await ctx.channel.purge(limit=100, check=self.meet_criteria_for_purge)

    # The meet criteria for purge.
    # Determines if the messages meet the criteria for purging.
    def meet_criteria_for_purge(self, message):
        return message.author == self.bot.user or message.content.__contains__(self.bot.OKI_BOT_COMMAND_PREFIX)
    

    @commands.command()
    async def reminder(self, ctx, *args):
        member = ctx.author
        day = 0
        hour = 0
        mins = 0
        sec = 0
        msg = "default"
        timezone = pytz.timezone("America/Los_Angeles")
        present_time = datetime.now()
        pp_time = timezone.localize(present_time)
        p_time = pp_time.strftime("%b %d, %I:%M:%S %Z")
        print("present time at LV is "+ p_time)
        # oki.reminder 1d 3h 3m 2s WOOT
        if len(args) == 5:
            day = int(args[0][:-1])
            hour = int(args[1][:-1])
            mins = int(args[2][:-1])
            sec = int(args[3][:-1])
            msg = args[4]
        elif len(args) == 4:
            if args[0][-1] == 'd':
                day = int(args[0][:-1])
                if args[1][-1] == 'h':
                    hour = int(args[1][:-1])
                    if args [2][-1] == 'm':
                        mins = int(args[2][:-1])
                    elif args [2][-1] == 's':
                        sec = int(args[2][:-1])
                elif args[1][-1] == 'm':
                    mins = int(arg[1][:-1])
                    sec = int (arg[2][:-1])
            elif args[0][-1] == 'h':
                hour = int(args[0][:-1])
                mins = int(args[1][:-1])
                sec = int (arg[2][:-1])
            msg = args[3]
        elif len(args) == 3:
            if args[0][-1] == 'd':
                day = int(args[0][:-1])
                if args[1][-1] == 'h':
                    hour = int(args[1][:-1])
                elif args[1][-1] == 'm':
                    mins = int(args[1][:-1])
                elif args[1][-1] == 's':
                    sec = int(args[1][:-1])
            elif args[0][-1] == 'h':
                hour = int(args[0][:-1])
                if args[1][-1] == 'm':
                    mins = int(args[1][:-1])
                elif args[1][-1] == 's':
                    sec = int(args[1][:-1])
            msg = arg[2]
        elif len(args) == 2:
            if args[0][-1] == 'd':
                day = int(args[0][:-1])
            if args[0][-1] == 'h':
                hour = int(args[0][:-1])
            if args[0][-1] == 'm':
                mins = int(args[0][:-1])
            if args[0][-1] == 's':
                sec = int(args[0][:-1])
            msg = args[-1]
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
