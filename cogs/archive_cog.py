import traceback

import discord
from discord.ext import commands

from spreadsheet import Spreadsheet
from utils import extract_urls
from entry import MessageEntry


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
                           '`limit`: the limit of how many messages the bot can retrieve per channel (max=100)')
            return
        
        try:
            if key == 'spreadsheet':
                self.bot.config['DEFAULT']['SPREADSHEET_FILENAME'] = value
                self.bot.spreadsheet = Spreadsheet(value)
            if key == 'limit':
                self.bot.config['DEFAULT']['MESSAGES_LIMIT'] = value
            self.bot.save_config()

            await ctx.send(f'Setting {key} set to {value}')
        except Exception as e:
            self.bot.logger.error('An error occurred: ', exc_info=True)
            await ctx.send(f'An error occurred: {traceback.format_exc()}')

    @archive.command(name="purge")
    async def archive_purge(self, ctx: commands.Context[commands.Bot]) -> None:
        """Delete all data from the spreadsheet"""
        try:
            self.bot.spreadsheet.purge()
            await ctx.channel.send(f'Spreadsheet "{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}" purged !')
        except Exception as e:
            self.bot.logger.error('An error occurred: ', exc_info=True)
            await ctx.send(f'An error occurred: {traceback.format_exc()}')

    @archive.command(name="channel")
    async def archive_channel(self, ctx: commands.Context[commands.Bot]) -> None:
        """Archive all URLs in the current channel"""
        
        try:
            await self.archive_messages(ctx.channel)
            await ctx.channel.send(f'Messages from the #{ctx.channel.name} channel archived to "{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}" !')
        except Exception as e:
            self.bot.logger.error('An error occurred: ', exc_info=True)
            await ctx.send(f'An error occurred: {traceback.format_exc()}')
        return
    
    @archive.command(name="all")
    async def archive_all(self, ctx: commands.Context[commands.Bot]) -> None:
        """Archive all URLs in all text channels"""
        for channel in ctx.guild.text_channels:
            try:
                await self.archive_messages(channel)
                await ctx.send(f'Archived all messages from #{channel.name} to the spreadsheet!')
            except Exception as e:
                self.bot.logger.error('An error occurred: ', exc_info=True)
                await ctx.send(f'An error occurred: {traceback.format_exc()}')

        await ctx.send(f"All channels have been archived to '{self.bot.config['DEFAULT']['SPREADSHEET_FILENAME']}'!")


    # Function to archive old messages in the given channel, starting from the oldest
    # Function to archive old messages in the given channel, starting from the oldest
    async def archive_messages(self, channel):
        archived_ids = self.bot.spreadsheet.get_archived_message_ids()  # Get archived message IDs
        limit = int(self.bot.config['DEFAULT']['MESSAGES_LIMIT'])
        last_message = None  # This will store the ID of the last message processed

        while True:
            # Retrieve messages in batches of up to limit, starting from the oldest
            messages = [message async for message in channel.history(limit=limit, after=last_message, oldest_first=True)]

            # If no more messages are returned, break the loop
            if not messages:
                break

            entries = []

            for message in messages:
                # Skip messages from the bot itself and already archived messages
                if message.author == self.bot.user or str(message.id) in archived_ids:
                    continue

                # Extract URLs from the message
                urls = extract_urls(message.content)

                # Skip messages which do not contain an URL
                if not urls:
                    continue

                for url in urls:
                    # Format the timestamp and message content for archiving
                    timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp
                    message_content = message.content  # Store the entire message content

                    # Append the message ID, channel, author, timestamp, URL, and message content to the Google Sheet
                    entry = MessageEntry(
                        message_id=str(message.id),
                        channel_name=message.channel.name,
                        author_name=message.author.name,
                        timestamp=timestamp,
                        url=url,
                        message_content=message_content,
                        jump_url=message.jump_url
                    )

                    entries.append(entry)

                    print(f"Archived URL: {url} from message: {message_content} at {timestamp}")

            # Batch write to the Google spreadsheet
            if entries:
                self.bot.spreadsheet.append_rows(entries)

            # Update the last_message_id to the ID of the last message in the current batch
            last_message = messages[-1]


async def setup(bot: commands.Bot):
    await bot.add_cog(ArchiveCog(bot))


async def teardown(bot):
    #print(f"{__name__} unloaded!")
    pass
