"""The purpose of this bot is to provide the ability to move the Oki cam to and from a voice channel without admin intervention."""
import asyncio
import discord
import random

from decouple import config
from discord.ext import commands
from settings import Settings

CLIENT_API_KEY = config('DISCORD_API_CLIENT_KEY')

print('Oki Bot is running but not connected!')

class OkiCamBot(commands.Bot):

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
        
        # Checks if nam is mentioned in the message
        if "nam" in message.content.lower():
            nam = await client.fetch_user(Settings.NAM_UID)
            await nam.send(self.namList[0])

    """ if message.content.__contains__('69'):
            await message.channel.send('nice') """

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
