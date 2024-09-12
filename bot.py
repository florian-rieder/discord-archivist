from configparser import ConfigParser
import os
import discord
from dotenv import load_dotenv

from spreadsheet import Spreadsheet

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CONFIG_FILE = 'config.ini'

config = ConfigParser()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

spreadsheet = None # Google Spreadsheet instance

# Function to extract URLs from message content


def startup():
    if os.path.isfile(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        config['DEFAULT']['SPREADSHEET_FILENAME'] = os.getenv('DEFAULT_SPREADSHEET_NAME')

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    
    
    Spreadsheet(config['DEFAULT']['SPREADSHEET_FILENAME'])
    


def extract_urls(message_content):
    import re
    url_regex = r'(https?://\S+)'
    return re.findall(url_regex, message_content)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: discord.Message):
    global spreadsheet
    spreadsheet_filename = config['DEFAULT']['SPREADSHEET_FILENAME']

    if message.author == client.user:
        return

    if message.content.startswith('$archive purge'):
        spreadsheet.purge()
        await message.channel.send(f'Spreadsheet "{spreadsheet_filename}" purged !')
        return

    # Command to archive old messages in the channel
    if message.content.startswith('$archive channel'):
        await archive_messages(message.channel)
        await message.channel.send(f'Messages from the #{message.channel.name} channel archived to "{spreadsheet_filename}" !')
        return

    if message.content.startswith('$archive config spreadsheet'):
        parts = message.content.split('$archive config spreadsheet ')
        spreadsheet_filename = parts[1]
        spreadsheet = Spreadsheet(spreadsheet_filename)  # Google Spreadsheet instance
        
        config['DEFAULT']['SPREADSHEET_FILENAME'] = spreadsheet_filename

        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

        await message.channel.send(f'Spreadsheet changed to "{spreadsheet_filename}" !')
        return


# Function to archive old messages in the given channel, starting from the oldest
async def archive_messages(channel):
    archived_ids = spreadsheet.get_archived_message_ids()  # Get archived message IDs

    # Retrieve messages starting from the oldest, with the oldest_first=True parameter
    async for message in channel.history(limit=200, oldest_first=True):
        # Skip messages from the bot itself and already archived messages
        if message.author == client.user or str(message.id) in archived_ids:
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

            print(f"Archived URL: {url} from message: {
                  message_content} at {timestamp}")

        # Batch write to the Google spreadsheet
        spreadsheet.append_rows(entries)

if __name__ == '__main__':
    startup()
    client.run(TOKEN)
