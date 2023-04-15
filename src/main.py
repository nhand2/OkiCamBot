"""The purpose of this bot is to provide the ability to move the Oki cam to and from a voice channel without admin intervention."""
import sys
import discord
import logging
import pytz

from decouple import config
from discord.ext import commands
from settings import Settings
from logging import handlers
from datetime import datetime
from pymongo import MongoClient

CLIENT_API_KEY = config("DISCORD_API_CLIENT_KEY")

fixingOkiMessage = "Fixing Oki"
voiceErrorMessage = "Oki is not home right now!"
messageList = {fixingOkiMessage, voiceErrorMessage}


class OkiCamBot(commands.Bot):
    oki_bot_extensions = [
        # "cogs.aero_gratter",
        "cogs.apex",
        "cogs.help",
        "cogs.basic",
        "cogs.yelp",
        "cogs.reminder",
    ]

    aeroGratter = None

    # The list of DMs to send to Nam.
    namList = ["Ew Nam is a pee pee poopoo"]

    def __init__(self, intents, db_client):
        super().__init__(
            command_prefix=Settings.OKI_BOT_COMMAND_PREFIX,
            intents=intents,
            member_cache_flags=discord.MemberCacheFlags.from_intents(intents),
        )
        self.db_client = db_client

    async def setup_hook(self):
        for extension in self.oki_bot_extensions:
            await self.load_extension(extension)

    # The on ready.
    # Overrides the API.
    async def on_ready(self):
        logger.info(f"OkiBot is connected and logged in as {client.user}")
        return

    # The on message.
    # Overrides the API.
    # args:
    #   message: message
    async def on_message(self, message):
        if message.author == client.user:
            return
        if isinstance(message.channel, discord.DMChannel):
            userMsg = message.content.lower()
            understand = False

            okiMessage = {
                "hi": "h-hello! bork bork!",
                "love": "i-i love u too :')",
                "bye": "b-bye!!! come back soon!!",
                "food": "DID YOU SAY CHIMKEN!!?!?!?!?! BOROKBROKBORKBROBKROBKROBKROKBROBKROBKROBK",
                "sleep": "i'd take a nap with you!! <3",
                "hand": "**p-paw!**",
                "hug": "i-i can't breattthhhhhhhhhhhhhhhheeeeeeee",
                "come": "ON MYYYY WAY!!",
            }

            okiReply = ""
            for key in okiMessage:
                if key in userMsg:
                    okiReply += " "+ okiMessage[key]

            if okiReply != "":
                understand = True
                await message.channel.send(okiReply)
            if not understand:
                await message.channel.send("dunno wat u said ima sniff mah butt...")
            return
        message.content = message.content.lower()
        await self.process_commands(message)

    # The on command
    # Overrides the API.
    # args:
    #   ctx: context
    async def on_command(self, ctx):
        msg = ctx.message
        logger.info(f"{msg.author} sent command {msg}")
        

    # The meet criteria.
    # Determines if the message meets the criteria for deletion.
    # args:
    #   message: message
    def meet_criteria(message):
        return message.content in messageList


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.messages = True
    intents.dm_messages = True
    intents.message_content = True
    intents.members = True

    logging.getLogger().setLevel(logging.DEBUG)
    discordLogger = logging.getLogger("discord")
    discordLogger.setLevel(logging.DEBUG)
    logging.getLogger("discord.http").setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)

    handler = handlers.RotatingFileHandler(
        filename=f'oki_bot.log',
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,
        backupCount=3,
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)

    # Add the handler to the discord logger
    discordLogger.addHandler(handler)
    # Add the handler to the root logger
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

    logger.warning("OKi bot has started but not connected")
    logger.addHandler(logging.StreamHandler(sys.stdout))
    
    CONNECT_STRING = Settings.MONGO_DB_SECRET
    db_client = MongoClient(CONNECT_STRING)

    client = OkiCamBot(intents, db_client)
    client.run(CLIENT_API_KEY, log_handler=None)
