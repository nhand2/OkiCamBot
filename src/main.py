"""The purpose of this bot is to provide the ability to move the Oki cam to and from a voice channel without admin intervention."""
import asyncio
import discord
import random

from decouple import config
from discord.ext import commands
from settings import Settings

CLIENT_API_KEY = config('DISCORD_API_CLIENT_KEY')

fixingOkiMessage = 'Fixing Oki'
voiceErrorMessage = 'Oki is not home right now!'
messageList = {
    fixingOkiMessage,
    voiceErrorMessage
}

print('Oki Bot is running but not connected!')

class OkiCamBot(commands.Bot):
    # Boolean used to determine if the apex command is already running to disallow counter spam.
    APEX_RUNNING = False

    # The list of DMs to send to Nam.
    namList = [
        'Ew Nam is a pee pee poopoo'
    ]

    def __init__(self):
        super().__init__(command_prefix=Settings.OKI_BOT_COMMAND_PREFIX)

    # The on ready.
    # Overrides the API.
    async def on_ready(self):
        print(f'OkiBot is connected and logged in as {client.user}')
        
        self.APEX_RUNNING = False
        self.load_extension('cogs.basic')
        self.load_extension('cogs.help')

    # The on message.
    # Overrides the API.
    # args:
    #   message: message
    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith(Settings.OKI_BOT_COMMAND_PREFIX):
            await self.process_commands(message)

    # The on command
    # Overrides the API.
    # args:
    #   ctx: context
    async def on_command(self, ctx):
        msg = ctx.message

    # The meet criteria.
    # Determines if the message meets the criteria for deletion.
    # args:
    #   message: message
    def meet_criteria(message):
        return message.content in messageList


if __name__ == '__main__':
    client = OkiCamBot()
    client.run(CLIENT_API_KEY)
