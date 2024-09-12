import discord
from discord.ext import commands

from spreadsheet import Spreadsheet
from utils import extract_urls


class ArchiveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping")
    async def ping(self, ctx: commands.Context[commands.Bot]) -> None:
        """Pong!"""
        await ctx.send("Pong!")

    @commands.hybrid_command(name="echo")
    async def echo(self, ctx: commands.Context[commands.Bot], message: str):
        """
        Echoes a message

        Parameters
        ----------
        ctx: commands.Context
            The context of the command invocation
        message: str
            The message to echo
        """
        await ctx.send(message)
    
    @commands.hybrid_group(name="archive")
    async def archive(self, ctx: commands.Context[commands.Bot]) -> None:
        """Archive commands"""
        pass

    @archive.command(name="config")
    async def archive_config(self, ctx: commands.Context[commands.Bot], key, value) -> None:
        if key == 'spreadsheet':
            self.bot.config['DEFAULT']['SPREADSHEET_FILENAME'] = value
            self.bot.spreadsheet = Spreadsheet(value)
        self.bot.save_config()
        await ctx.send(f'Config {key} set to {value}')
    
    @archive.command(name="purge")
    async def archive_purge(self, ctx: commands.Context[commands.Bot]) -> None:
        self.bot.spreadsheet.purge()
        await ctx.channel.send(f'Spreadsheet "{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}" purged !')

    @archive.command(name="channel")
    async def archive_channel(self, ctx: commands.Context[commands.Bot]) -> None:
        await self.archive_messages(ctx.channel)
        await ctx.channel.send(f'Messages from the #{ctx.channel.name} channel archived to "{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}" !')
        return

    # Function to archive old messages in the given channel, starting from the oldest
    async def archive_messages(self, channel):
        archived_ids = self.bot.spreadsheet.get_archived_message_ids()  # Get archived message IDs

        # Retrieve messages starting from the oldest, with the oldest_first=True parameter
        async for message in channel.history(limit=200, oldest_first=True):
            # Skip messages from the bot itself and already archived messages
            if message.author == self.bot.user or str(message.id) in archived_ids:
                continue

            # Extract URLs from the message
            urls = extract_urls(message.content)

            if not urls:
                continue

            entries = []

            for url in urls:
                # Format the timestamp and message content for archiving
                timestamp = message.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S')  # Format the timestamp
                message_content = message.content  # Store the entire message content

                # Append the message ID, author, timestamp, URL, and message content to the Google Sheet
                entry = [str(message.id), message.author.name,
                        timestamp, url, message_content]

                entries.append(entry)

                print(f"Archived URL: {url} from message: {message_content} at {timestamp}")

            # Batch write to the Google spreadsheet
            self.bot.spreadsheet.append_rows(entries)


async def setup(bot):
    await bot.add_cog(ArchiveCog(bot))


async def teardown(bot):
    #print(f"{__name__} unloaded!")
    pass
