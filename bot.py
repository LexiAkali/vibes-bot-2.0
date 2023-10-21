import os, sys
import discord
from discord.ext import commands, tasks
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Get the bot token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is None:
    print("Error: Discord bot token not found. Set DISCORD_TOKEN in the .env file")
    sys.exit(1)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

# Define a base XP per message
BASE_XP_PER_MESSAGE = 50

# Define the XP data and last message time dictionaries
xp_data = {}
last_message_time = {}

# Define the XP required for each level
level_xp_requirements = [
    # Levels 0-20
    100, 155, 220, 295, 380, 475, 580, 695, 820, 955, 1100, 1255, 1420, 1595, 1780, 1975, 2180, 2395, 2620, 2855, 3100,
    # Levels 21-40
    3355, 3620, 3895, 4180, 4475, 4780, 5095, 5420, 5755, 6100, 6455, 6820, 7195, 7580, 7975, 8380, 8795, 9220, 9655, 10100,
    # Levels 41-60
    10555, 11020, 11495, 11980, 12475, 12980, 13495, 14020, 14555, 15100, 15655, 16220, 16795, 17380, 17975, 18580, 19195, 19820, 20455, 21100
]

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

# Function to calculate user's level and remaining XP
def calculate_level_and_xp(user_id):
    if user_id in xp_data:
        total_xp = xp_data[user_id]

        level = 0
        xp_remaining = total_xp
        while level < len(level_xp_requirements) and xp_remaining >= level_xp_requirements[level]:
            xp_remaining -= level_xp_requirements[level]
            level += 1

        return level, xp_remaining
    return 0, 0

# Function to notify a user when they level up
async def notify_level_up(user, new_level):
    await user.send(f"Congratulations! You've reached level {new_level}!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    current_time = datetime.now()
    
    await bot.process_commands(message)

<<<<<<< HEAD
    await bot.process_commands(message)
=======
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

>>>>>>> 36556f731b498fd2c74a9a8407094e3d5bcabebd

    if user_id not in last_message_time:
        last_message_time[user_id] = current_time

    time_diff = (current_time - last_message_time[user_id]).total_seconds()

    if time_diff >= 60:  # Check if it's been at least 60 seconds
        if user_id not in xp_data:
            xp_data[user_id] = 0  # Initialize XP

        # Calculate the user's level and remaining XP
        level, xp_remaining = calculate_level_and_xp(user_id)

        # Grant XP based on level
        if level < len(level_xp_requirements):
            xp_to_grant = BASE_XP_PER_MESSAGE
            xp_data[user_id] += xp_to_grant
            last_message_time[user_id] = current_time
            save_xp_data()

            # Check if the user leveled up and notify them
            new_level, _ = calculate_level_and_xp(user_id)
            if new_level > level:
                user = message.author
                await notify_level_up(user, new_level)

@bot.command()
async def level(ctx, user: discord.User = None):
    user = user or ctx.author
    user_id = str(user.id)

    if user_id in xp_data:
        current_xp = xp_data[user_id]
        level, xp_remaining = calculate_level_and_xp(user_id)

        if level < len(level_xp_requirements):
            xp_needed_for_next_level = level_xp_requirements[level]
            response = f"{user.name} is level {level}, and needs {xp_needed_for_next_level - current_xp} more XP to reach the next level."
            await ctx.send(response)
        else:
            await ctx.send(f"{user.name} is at the maximum level!")
    else:
        await ctx.send("User not found or has no XP.")

@bot.command()
async def leaderboard(ctx):
    sorted_xp = sorted(xp_data.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "Leaderboard:\n"

    for index, (user_id, xp) in enumerate(sorted_xp[:10], start=1):
        user = bot.get_user(int(user_id))
        if user is not None:
            leaderboard_text += f"{index}. {user.name}: {xp} XP\n"
        else:
            leaderboard_text += f"{index}. Unknown User: {xp} XP (User not found)\n"

    await ctx.send(leaderboard_text)

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(TOKEN)
