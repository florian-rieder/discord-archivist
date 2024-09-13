import discord
from discord.ext import commands

from spreadsheet import Spreadsheet
from utils import extract_urls


class ArchiveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.hybrid_group(name="archive")
    async def archive(self, ctx: commands.Context[commands.Bot]) -> None:
        """Archive commands group"""
        await ctx.send('Available commands:\n'
                       '`/archive config`: configure the archivist\n'
                       '`/archive purge`: empty the current spreadsheet\n'
                       '`/archive channel`: archive links in the current channel\n'
                       '`/archive all`: archive links in all text channels\n')

    @archive.command(name="config")
    async def archive_config(self, ctx: commands.Context[commands.Bot], key, value) -> None:
        """Configure the archivist"""
        if key == 'help':
            await ctx.send('Available settings:\n'
                           "`spreadsheet`: the name of the spreadsheet to use (the spreadsheet must have been shared with this bot's service account)"
                           '`limit`: the limit of how many messages the bot can retrieve per channel (default=200)')
            return
        
        if key == 'spreadsheet':
            self.bot.config['DEFAULT']['SPREADSHEET_FILENAME'] = value
            self.bot.spreadsheet = Spreadsheet(value)
        if key == 'limit':
            self.bot.config['DEFAULT']['MESSAGES_LIMIT'] = value
        self.bot.save_config()

        await ctx.send(f'Setting {key} set to {value}')
    
    @archive.command(name="purge")
    async def archive_purge(self, ctx: commands.Context[commands.Bot]) -> None:
        """Delete all data from the spreadsheet"""
        self.bot.spreadsheet.purge()
        await ctx.channel.send(f'Spreadsheet "{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}" purged !')

    @archive.command(name="channel")
    async def archive_channel(self, ctx: commands.Context[commands.Bot]) -> None:
        """Archive all URLs in the current channel"""
        await self.archive_messages(ctx.channel)
        await ctx.channel.send(f'Messages from the #{ctx.channel.name} channel archived to "{self.bot.config['SPREADSHEET_FILENAME']}" !')
        return
    
    @archive.command(name="all")
    async def archive_all(self, ctx: commands.Context[commands.Bot]) -> None:
        """Archive all URLs in all text channels"""
        for channel in ctx.guild.text_channels:
            await self.archive_messages(channel)
            await ctx.send(f'Archived all messages from #{channel.name} to the spreadsheet!')

        await ctx.send(f"All channels have been archived to '{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}'!")


    # Function to archive old messages in the given channel, starting from the oldest
    async def archive_messages(self, channel):
        archived_ids = self.bot.spreadsheet.get_archived_message_ids()  # Get archived message IDs
        limit = int(self.bot.config['DEFAULT']['MESSAGES_LIMIT'])

        # Retrieve messages starting from the oldest
        async for message in channel.history(limit=limit, oldest_first=True):
            # Skip messages from the bot itself and already archived messages
            if message.author == self.bot.user or str(message.id) in archived_ids:
                continue

            # Extract URLs from the message
            urls = extract_urls(message.content)

            # Skip messages which do not contain an URL
            if not urls:
                continue

            entries = []

            for url in urls:
                # Format the timestamp and message content for archiving
                timestamp = message.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S')  # Format the timestamp
                message_content = message.content  # Store the entire message content

                # Append the message ID, channel, author, timestamp, URL, and message content to the Google Sheet
                entry = [str(message.id), message.channel.name, message.author.name, timestamp, url, message_content]

                entries.append(entry)

                print(f"Archived URL: {url} from message: {message_content} at {timestamp}")

            # Batch write to the Google spreadsheet
            self.bot.spreadsheet.append_rows(entries)


async def setup(bot: commands.Bot):
    await bot.add_cog(ArchiveCog(bot))


async def teardown(bot):
    #print(f"{__name__} unloaded!")
    pass
