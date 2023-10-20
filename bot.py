import os
import discord
from discord.ext import commands, tasks
import json
import random
from datetime import datetime

intents = discord.Intents.default()
intents.members = True

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="$", intents=intents)

# Defining a dictionary to store user XP
xp_data = {}
last_message_time = {}

# Loading XP data from a JSON file when I get one
try:
    with open("xp.json", "r") as file:
        xp_data = json.load(file)
except FileNotFoundError:
    xp_data = {}

# Function to save XP data to the JSON file
def save_xp_data():
    with open("xp.json", "w") as file:
        json.dump(xp_data, file)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    xp_task.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    current_time = datetime.now()

    if user_id not in last_message_time:
        last_message_time[user_id] = current_time
    else:
        time_diff = (current_time - last_message_time[user_id]).total_seconds()
        if time_diff < 60:
            return

    if user_id not in xp_data:
        xp_data[user_id] = 50  # Set the base XP

    xp_data[user_id] += random.randint(10, 20)  # Add random XP
    last_message_time[user_id] = current_time
    save_xp_data()

    await bot.process_commands(message)

@tasks.loop(minutes=10)
async def xp_task():
    for user_id in list(xp_data.keys()):
        xp_data[user_id] += 10  # Add 10 XP every 10 minutes
    save_xp_data()

@bot.command()
async def level(ctx, user: discord.User = None):
    user = user or ctx.author
    user_id = str(user.id)

    if user_id in xp_data:
        await ctx.send(f"{user.name} is level {xp_data[user_id] // 100}")
    else:
        await ctx.send("User not found or has no XP.")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Get the bot token from the environment variable
bot_token = os.environ.get('DISCORD_BOT_TOKEN')

if bot_token is None:
    print("Error: Discord bot token not found. Set the DISCORD_BOT_TOKEN environment variable.")
else:
    bot.run(bot_token)
