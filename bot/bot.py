import traceback
import discord

from discord.ext import commands

from config.config import token, name, log_level, log_type
from .utils.logger import Logger


class Bot(commands.Bot):
    """A subclassed version of commands.Bot"""

    def __init__(self, debug=False, *args, **kwargs):
        super().__init__(command_prefix=self.get_prefix, *args, **kwargs)
        self.debug = debug
        self.logger = Logger(name, log_level, log_type)
        self.logger.info(f"Starting {name}")

    def load_cogs(self, cogs: list):
        """Loads a list of cogs"""

        success, fail = 0, 0

        for cog in cogs:
            if not self.debug:
                try:
                    super().load_extension(cog)
                    success += 1
                except Exception as e:
                    self.logger.error(f"Cog {cog} experienced an error during loading: {e}")
                    fail += 1
            else:
                super().load_extension(cog)

        additional = "" if not self.debug else " (DEBUG)"
        self.logger.info(f"Cog loading complete! (Total: {success + fail} | Loaded: {success} | Failed: {fail}){additional}")

    async def get_prefix(self, message):
        if self.user.id == 776592512562364466:
            return "!"
        return "$"

    async def on_error(self, event: str, **kwargs):
        self.logger.error(f"Runtime error: {event}\n{traceback.format_exc(limit=1750)}")
        traceback.print_exc()


def run(cogs: list, debug=False, help_command=None):
    bot = Bot(
        debug=debug,
        max_messages=10000,
        help_command=help_command,
        intents=discord.Intents.all()
    )

    bot.load_cogs(cogs)
    bot.run(token)
