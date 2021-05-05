import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = commands.DefaultHelpCommand()
        bot.help_command.cog = self

    # The cog unload.
    # Overrides the API.
    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
    bot.get_command('help').hidden = True
