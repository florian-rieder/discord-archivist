import os
import discord
from dotenv import load_dotenv

from spreadsheet import Spreadsheet

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

spreadsheet_filename = os.getenv('SPREADSHEET_NAME')
sh = Spreadsheet(spreadsheet_filename)  # Google Spreadsheet instance

# Function to extract URLs from message content


def extract_urls(message_content):
    import re
    url_regex = r'(https?://\S+)'
    return re.findall(url_regex, message_content)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Command to archive old messages in the channel
    if message.content.startswith('$archive'):
        await archive_messages(message.channel)

    if message.content.startswith('$spreadsheet set'):
        parts = message.content.split(' ')
        spreadsheet_filename = parts[2]
        sh = Spreadsheet(spreadsheet_filename)  # Google Spreadsheet instance


# Function to archive old messages in the given channel, starting from the oldest
async def archive_messages(channel):
    archived_ids = sh.get_archived_message_ids()  # Get archived message IDs

    # Retrieve messages starting from the oldest, with the oldest_first=True parameter
    async for message in channel.history(limit=200, oldest_first=True):
        # Skip messages from the bot itself and already archived messages
        if message.author == client.user or str(message.id) in archived_ids:
            continue

        # Extract URLs from the message
        urls = extract_urls(message.content)

        if not urls:
            continue

        for url in urls:
            # Format the timestamp and message content for archiving
            timestamp = message.created_at.strftime(
                '%Y-%m-%d %H:%M:%S')  # Format the timestamp
            message_content = message.content  # Store the entire message content

            # Append the message ID, author, timestamp, URL, and message content to the Google Sheet
            sh.append_archive_entry(str(message.id), message.author.name, timestamp, url, message_content)
            print(f"Archived URL: {url} from message: {message_content} at {timestamp}")


if __name__ == '__main__':
    client.run(TOKEN)
