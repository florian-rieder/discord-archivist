# Discord archivist
This is a discord bot meant to archive links from a Discord server to a Google Sheet.

## Installation

1. Get a [Discord bot account](https://discordpy.readthedocs.io/en/stable/discord.html#creating-a-bot-account)
2. Create a `.env` file and add your discord bot token to it
```.env
DISCORD_TOKEN=YOUR TOKEN HERE
```
3. Get a [Google service account](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account) (steps 1-7)
4. Share your Google Sheet with the Google service account email.
5. Create virtual environment and install dependencies with the `make install` command
6. Launch the bot with the `make up` command
7. From your Discord server, define the spreadsheet to be used with the `/archive config spreadsheet "Your spreadsheet name"`


## Launching
Run the bot with the following command:
```
make up
```

## Commands

`/archive purge`: DANGER: clears the spreadsheet

`/archive config`: Configure the bot

`/archive all`: Archive links in all channels

`/archive channel`: Archive links in the current channel


# Requirements
- Python 3
- discordpy
- gspread