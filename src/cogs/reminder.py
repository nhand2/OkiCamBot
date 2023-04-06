import datetime
import logging
import re
import sys
from datetime import datetime
from datetime import timedelta as td
from logging import handlers

import pytz
from discord.ext import commands, tasks

from database.reminder_db import ReminderDb


class ReminderCog(commands.Cog):
    regex = r"(\s?[\d]{1,2}\s\b[yY]ear[sS]?\b|\s?[\d]{1,2}\s\b\<[yY]\>\b)|(\s?[\d]{1,2}\s\b[mM]onth[sS]?\b|\s?[\d]{1,2}\s\b\<[mM]\>\b)|(\s?[\d]{1,2}\s\bday[sS]?\b|\s?[\d]{1,2}\s\b\<[dD]\>\b)|(\s?[\d]{1,2}\s\b[hH]our[sS]?\b|\s?[\d]{1,2}\s\b\<[hH]\>\b)|(\s?[\d]{1,2}\s\b[mM]inute[sS]?\b|\s?[\d]{1,2}\s\b[mM]in[sS]?\b)"

    def __init__(self, bot):
        # handler = handlers.RotatingFileHandler(
        #     filename=f'reminders_{datetime.now(pytz.timezone("America/Los_Angeles"))}.log',
        #     encoding="utf-8",
        #     maxBytes=32 * 1024 * 1024,
        #     backupCount=3,
        # )
        # dt_fmt = "%Y-%m-%d %H:%M:%S"
        # formatter = logging.Formatter(
        #     "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
        # )
        # handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        #self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        
        self.bot = bot
        self.db = ReminderDb(bot.db_client)
        
    async def cog_load(self):
        self.logger.info("Loaded Reminder Cog")
        
    async def cog_unload(self) -> None:
        self.logger.info("Unloaded Reminder Cog")
        self.check_reminders.stop()
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_reminders.start()

    # The reminder command.
    # Allows user to set reminders.
    # args:
    #   ctx: context
    #   *args: the indexed arguments.
    @commands.command(name="reminder", aliases=["r", "remind"])
    async def reminder(self, ctx, *, args):
        """Set a reminder! (format: oki.reminder <#>years/year/y <#>months/month/m <#>days/day/d <#>hours/hour/h <#>minutes/minute/mins/min | <message>)"""
        try:
            timeMessage = args.split("|")
        except Exception as e:
            print(e)
            await ctx.send("Please check command usage!")
            return

        if len(timeMessage) <= 1:
            await ctx.send("Please check command usage!")
            raise commands.MissingRequiredArgument
            return
        elif len(timeMessage) > 2:
            await ctx.send("Please check command usage!")
            raise commands.TooManyArguments
            return

        date = " ".join(timeMessage[0].split(" "))

        print(date)
        timedelta = td()
        if re.search(self.regex, date):
            timeList = [
                time
                for itemList in re.findall(self.regex, date)
                for time in itemList
                if time
            ]
            for time in timeList:
                time = [time for time in time.split(" ") if time]

                print(time)
                if any(isThere in time for isThere in ("year", "years", "y")):
                    timedelta += td(days=365 * int(time[0]))
                elif any(isThere in time for isThere in ("month", "months", "m")):
                    timedelta += td(days=30 * int(time[0]))
                elif any(isThere in time for isThere in ("day", "days", "d")):
                    timedelta += td(days=int(time[0]))
                elif any(isThere in time for isThere in ("hour", "hours", "h")):
                    timedelta += td(hours=int(time[0]))
                elif any(
                    isThere in time for isThere in ("minute", "minutes", "mins", "min")
                ):
                    timedelta += td(minutes=int(time[0]))
                else:
                    await ctx.send("Couldn't set remind! No time set!")
                    return

            member = ctx.author

            try:
                if self.db.insert(
                    member, str(timeMessage[1].strip()), datetime.now() + timedelta
                ):
                    await ctx.send("Reminder set!")
                else:
                    await ctx.send("Couldn't set remind!")
            except Exception as e:
                print(e)
                await ctx.send("Something happened")
        else:
            await ctx.send("Couldn't set remind! No time set!!")

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        reminderList = list(self.db.check_reminders())
        for reminder in reminderList:
            user = self.bot.get_user(reminder["user_id"]) or await self.bot.fetch_user(
                reminder["user_id"]
            )
            await user.send(str(reminder["reminder"]))

        if len(reminderList) > 0:
            self.db.remove_sent_reminders()


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))
