import asyncio
import logging
import random
import os
from asyncio import sleep as s

from decouple import config
from discord.ext import commands
from discord import Embed
from discord import File
from pytz import timezone, utc
from random import randrange
from googlesearch import search
from googletrans import Translator

from bot_helper import UID_ENUM
from settings import Settings

# Helper functions
def fileCount(fileSubString):
    count = 0
    for file in os.listdir(f"./src/images/"):
        if(file.__contains__(fileSubString)):
            count += 1
    return count

class BasicCommandsCog(commands.Cog, name="Basic Commands"):
    # The list of messages from oki.
    okiLoveMsgList = [
        "I love {0}! They're the best!",
        "{0} is such a cool person!",
        "Bork means I love you in dog!",
        "I love {0} more than I love food! And that's a lot!",
        "大好き！！",
        "I love {0} more than I love Mario!",
        "Bork! Bork! Bork! <3",
    ]

    # The list of messages from oki to nam.
    okiNamMsgList = [
        "{0} is smelly >:3",
        "{0} holds me weird :\\",
        "{0} is okay. I guess.",
        "Meh.",
        "{0} is pretty cool ;D",
        "Hello {0}.",
    ]

    okiDunnoList = [
        "bork bork? wat did u say owo?",
        "h-hek!?",
        "bork bork?",
        "dunno what u saying...",
        "u have food??",
        "l-love!"
    ]

    # The 2b copy pasta.
    twob = """
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
⠄⠄⠄⠄⠄⠈⠙⠑⣠⣤⣴⡖⠄⠿⣋⣉⣉⡁⠄⢾⣦⠄⠄⠄⠄⠄⠄⠄⠄"""

    # The Oki cam fix status message.
    fixingOkiMessage = "Fixing Oki"

    # The response if Oki cam is not in voice channel.
    voiceErrorMessage = "Oki is not home right now!"
    
    # The list of choice messages.
    choiceMessagesList = [
        '{0} is a good choice!',
        'You can never go wrong with {0}',
        '{0} is best!',
        'Why not go with {0}!',
        'I choose...{0}'
    ]

    # The list of messages Oki Bot can send.
    messageList = {fixingOkiMessage, voiceErrorMessage}

    userUidDict = {}

    # The __init__
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.getLogger("__main__").handlers[0])

    @commands.Cog.listener()
    async def on_ready(self):
        for key, uid in Settings.USER_UIDS.items():
            try:
                self.userUidDict[key] = await self.bot.fetch_user(int(uid))
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
    @commands.command(name="hello")
    async def say_hello(self, ctx):
        """Say hello to oki!"""

        await ctx.send("Bork Bork!")

    # The translate command.
    # Oki will show you some love!
    # args:
    #   ctx: context
    @commands.command(name="translate", aliases=["t"])
    async def oki_love(self, ctx):
        """I translate what Oki says!"""
        member = ctx.author
        if member.id == int(Settings.USER_UIDS.get(UID_ENUM.NAM)):
            await ctx.send(random.choice(self.okiNamMsgList).format(member.mention))
        else:
            if (
                member.id == int(Settings.USER_UIDS.get(UID_ENUM.FANFAN))
                and random.randrange(20, 25, 3) == 23
            ):
                fanfan = await ctx.bot.fetch_user(Settings.USER_UIDS.get(UID_ENUM.FANFAN))
                await fanfan.send(random.choice(self.okiLoveMsgList).format(member.mention))
                await ctx.send("{0} is my favorite person! <3".format(member.mention))
            else:
                await ctx.send(
                    random.choice(self.okiLoveMsgList).format(member.mention)
                )

    # The choose command.
    # Oki chooses between the options
    # args:
    #   ctx: context
    #   arg: the key-word argument.
    @commands.command(name="choose", aliases=["c"])
    async def choose(self, ctx, *, arg):
        """Can't make a decision? Allow Oki to choose for you"""

        choices = arg.split("|")
        if len(choices) <= 1:
            raise commands.MissingRequiredArgument
            return

        await ctx.send(
            random.choice(self.choiceMessagesList).format(random.choice(choices).strip())
        )

    # The choose error handler.
    # Handles errors
    # args:
    #   ctx: context
    #   error: error thrown
    @choose.error
    async def choose_error(self, ctx, error):
        self.logger.warn(f"WARN: {error} in {ctx.command}")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Retry with the format `oki.choose <choice1> | <choice2> | ... | <choice(n)>.`"
            )

    # The broki command.
    # Disconnect and reconnect the Oki cam.
    # args:
    #   ctx: context
    @commands.command(name="broki", aliases=["b"])
    async def fix_oki_cam(self, ctx):
        """Fixes the Oki cam when Darnell or Kevin joins, smh my head"""

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
    @commands.command(name="booty", aliases=["2b"])
    async def call_2b(self, ctx):
        """What that booty do?"""
        await ctx.send(self.twob)

    # The sik fan command.
    # Used to call the family for dinner.
    # args:
    #   ctx: context
    #   *args: array of arguments
    @commands.command(name="sikfan")
    @commands.cooldown(rate=5, per=60.0)
    async def call_for_dinner(self, ctx, *args):
        """Time for dinner!"""
        await ctx.message.delete()

        try:
            args[0] == Settings.SECRET_COMMAND
            await ctx.send(
                f"Time to eat! {self.userUidDict.get(UID_ENUM.SOAP).mention} {self.userUidDict.get(UID_ENUM.DEREK).mention} {self.userUidDict.get(UID_ENUM.JON).mention} {self.userUidDict.get(UID_ENUM.NAM).mention}"
            )
        except IndexError:
            await ctx.send("Time to eat!!")

    # The sik fan error handler.
    # args:
    #   ctx: context
    #   error: error object
    @call_for_dinner.error
    async def call_for_dinner_error(self, ctx, error):
        self.logger.warn(f"WARN: {error} in {ctx.command}")
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"This command can only be ran 5 times in 1 minute! Try again in {error.retry_after:.0f} seconds!"
            )

    # The purge command.
    # Purges messages within 100 (total) messages.
    # args:
    #   ctx: context
    @commands.command(name="purge")
    async def purge_commands(self, ctx):
        """OkiBot can clean it's mess"""
        await ctx.channel.purge(limit=100, check=self.meet_criteria_for_purge)

    # The meet criteria for purge.
    # Determines if the messages meet the criteria for purging.
    # args:
    #   message: message
    def meet_criteria_for_purge(self, message):
        return message.author == self.bot.user or message.content.__contains__(
            Settings.OKI_BOT_COMMAND_PREFIX
        )
    
    # The oki what command.
    # Translate language for you
    # args:
    @commands.command(name="wat")
    async def oki_what(self, ctx, *, args):
        """Oki can translate for you!"""
        oki = '<:stupid:694254790607372318>'
        translation = Translator().translate(args, dest="en")
        await ctx.send(f"{oki}{oki}  I t-think that means:  {oki}{oki}\n\n{translation.text}")

    # The oki react command.
    # Reacts with an oki image
    # args:
    @commands.command(name="oki")
    async def oki_image(self, ctx):
        """Send an image of oki"""
        number = randrange(fileCount("oki"))
        file = File(f"./src/images/oki{number}.PNG", filename=f"oki{number}.PNG")
        discordEmbed = Embed()
        discordEmbed.set_image(url=f"attachment://oki{number}.PNG")
        await ctx.send(file=file, embed=discordEmbed)

    # The oki react command.
    # Reacts with an oki image
    # args:
    @commands.command(name="tristan")
    async def oki_tristan(self, ctx):
        """tristan fantasy xiv"""
        file = File(f"./src/images/tristan.jpg", filename=f"tristan.jpg")
        discordEmbed = Embed()
        discordEmbed.set_image(url=f"attachment://tristan.jpg")
        await ctx.send(file=file)

    @commands.command(name="booba")
    async def oki_booba(self, ctx):
        """noooo0o0o0o"""
        await ctx.send("N-nooo!")

    @commands.command(name="message", aliases=["audie", "betty", "derek", "fanfan", "fannie", "haku", "soap"])
    async def oki_message(self, ctx):
        """Send dm"""
        number = randrange(fileCount("oki"))
        user_uid = None
        
        match ctx.invoked_with:
            case "audie":
                user_uid = Settings.USER_UIDS.get(UID_ENUM.AUDIE)
            case "betty":
                user_uid = Settings.USER_UIDS.get(UID_ENUM.BETTY)
            case "derek":
                user_uid = Settings.USER_UIDS.get(UID_ENUM.DEREK)
            case "fanfan" | "fannie":
                user_uid = Settings.USER_UIDS.get(UID_ENUM.FANFAN)
            case "haku":
                user_uid = Settings.USER_UIDS.get(UID_ENUM.HAKU)
            case "soap":
                user_uid = Settings.USER_UIDS.get(UID_ENUM.SOAP)
            case _:
                ctx.send("dunno who you are.... h-hek!")
                return
            
        user = None
        user = self.bot.get_user(user_uid) or await self.bot.fetch_user(user_uid)

        file = File(f"./src/images/oki{number}.PNG", filename=f"oki{number}.PNG")
        await user.send(random.choice(self.okiLoveMsgList).format(user.mention), file=file)
        await ctx.send("I-I send a message! " + random.choice(self.okiLoveMsgList).format(user.mention), file=file)

    @commands.command(name="poll")
    async def oki_poll(self, ctx, *, arg):
        """Create a poll."""
        
        parsedArg = arg.split('|')
        oki = '<:stupid:694254790607372318>'
        pollString = f'O-oki here is your poll!! {oki}{oki}{oki}{oki}{oki}{oki}{oki}{oki}{oki}{oki}\n'
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        for index, arg in enumerate(parsedArg, start=0):
            if index == 0:
                pollString += f'**{parsedArg[index]}?**\n'
            else:
                pollString += f'> **{index}:**    {parsedArg[index]}\n'

        poll = await ctx.send(pollString)
        for index, arg in enumerate(parsedArg, start=0):
            if index == len(parsedArg) - 1:
                continue
            await poll.add_reaction(reactions[index])
    
    @commands.command(name="think")
    async def oki_think(self, ctx):
        """What's in my head?"""
        oki = '<:stupid:694254790607372318>'
        defaultString = f'I am thinking about {oki}{oki}{oki}{oki}{oki}{oki}{oki}{oki}{oki}{oki}\n'
        thoughts = [
            '<:angie:289680060422553611>',
            '<:audie:263974148877844483>',
            '<:daddynam:313500774015696897>',
            '<:derek:263972470501933056>',
            '<:imsosorry:1090321461056647248>',
            '<:gee:812530165212119071>',
            '<:jennifer:812949626650230785>',
            '<:tiddytoucher:812949521095983104>',
            '<:fannie:283825203375767552>',
            '<:jeff:257734884372643840>',
            '<:treshia:263975107788013568>',
            '<:imgonnabeatyouup:908988785193283604>',
            '<:tristan:263978864538157056>'
        ]
        await ctx.send(f'{defaultString} {thoughts[random.randrange(len(thoughts) - 1)]}')
    
    @commands.command(name="frog")
    async def oki_frog(self, ctx):
        number = randrange(fileCount("frog"))
        file = File(f"./src/images/frog{number}.PNG", filename=f"frog{number}.PNG")
        await ctx.send("froggy boi is my best fren!!\n **Art credit: AYU**", file=file)
    
    @commands.command(name="search")
    async def oki_search(self, ctx, *, arg):
        for URL in search(arg, num_results=1):
            await ctx.send(url=URL)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print (error)
        await ctx.send(random.choice(self.okiDunnoList))
    
async def setup(bot):
    await bot.add_cog(BasicCommandsCog(bot))
