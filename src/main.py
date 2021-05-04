"""The purpose of this bot is to provide the ability to move the Oki cam to and from a voice channel without admin intervention."""
import discord
import asyncio
from decouple import config

CLIENT_API_KEY = config('DISCORD_API_CLIENT_KEY')
OKI_UID = config('OKI_UID')
OKI_BOT_COMMAND_PREFIX = config('OKI_BOT_COMMAND_PREFIX')

fixingOkiMessage = 'Fixing Oki'
client = discord.Client()

print ('Oki Bot is running but not connected!')

@client.event
async def on_ready():
    """
    The on ready event.
    Called when bot is fun ran and connected to server.
    """
    print('OkiBot is connected and logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    """
    The on message event.
    Called when a message matching the oki command is called.

    Args:
        message: The message from client.
    """
    if message.author == client.user:
        return
    
    if message.content.startswith(OKI_BOT_COMMAND_PREFIX):
        await commands(message, message.content[len(OKI_BOT_COMMAND_PREFIX):])

async def commands(message, command):
    """
    The commands function. Function is async.

    Args:
        message: The message from client.
        command: The command from the client.
    """
    switcher={
        'hello':say_hello(message.channel),
        'broki':fix_oki_cam(message),
        'move_oki':move_oki_cam(message),
        'help':help_manual(message)
    }
    await switcher.get(command, send_command_error(message.channel))

async def say_hello(channel):
    """
    The say hello.
    Replies to the caller when "hello" command is sent.

    Args:
        channel: The channel to send the message to.
    """
    await channel.send('Bork Bork!')

async def help_manual(message):
    """
    The help manual.
    Sends the possible commands to the caller.

    Args:
        message: The message from the  discord api client.
    """
    await message.channel.send('```yaml\nCommands:\n\
        \thello: Say hello to Oki bot!\n\
        \tbroki: Fix oki cam when Darnell or Kevin joins, smh my head\n\
        \tmove_oki: Moves oki to your current voice channel\n\
        \thelp: Show possible commands```')

async def move_oki_cam(message):
    pass
    #oki = await message.guild.fetch_member(OKI_UID)
    #voiceChannelToMoveTo = message.author.voice.channel

    #await oki.move_to(voiceChannelToMoveTo)

async def fix_oki_cam(message):
    """
    The fix oki cam.
    Fixes the oki cam whenever the command is called.
    Oki cam is sent to another voice channel then sent back to the channel it was in previously.

    Args:
        message: The message from the discord api client.
    """
    await message.channel.send(fixingOkiMessage)
    oki = await message.guild.fetch_member(OKI_UID)
    currentVoiceChannel = oki.voice.channel

    afk_channel = message.guild.afk_channel
    
    if currentVoiceChannel == afk_channel:
        return

    await oki.move_to(afk_channel)
    await asyncio.sleep(5)
    await oki.move_to(currentVoiceChannel)

    await message.channel.purge(limit=100, check=meet_criteria)

async def send_command_error(channel):
    """
    The send command error.
    Sends an error message to the caller.

    Args:
        channel: The channel to send the message to.
    """
    print ("Invalid command!")
    pass

def meet_criteria(message):
    '''
    The meet criteria.
    Checks if the criteria is met for purging messages.

    Args:
        message
    '''
    return message.auther == client.user and message.content == fixingOkiMessage

client.run(CLIENT_API_KEY)