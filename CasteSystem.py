import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ------------- CONFIGURABLE SETTINGS ----------------
ROLE_COLOR_MAP = {
    "Red": "#FF0000",
    "Orange": "#FFA500",
    "Yellow": "#FFFF00",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Indigo": "#4B0082",
    "Violet": "#EE82EE"
}

# Toggle whether to hide user profile pictures for these roles
HIDE_PFPS_FOR_ROLES = True
# -----------------------------------------------------

# Set up the Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Get roles of the user
    user_roles = [role.name for role in message.author.roles]
    matching_roles = [r for r in user_roles if r in ROLE_COLOR_MAP]

    if matching_roles:
        # Pick the first matching color role
        role_name = matching_roles[0]
        color_hex = ROLE_COLOR_MAP[role_name]
        initials = "".join(word[0].upper() for word in message.author.display_name.split())

        embed = discord.Embed(
            description=message.content,
            color=discord.Color(int(color_hex.lstrip("#"), 16))
        )
        embed.set_author(
            name=f"{initials}: {message.author.display_name}",
            icon_url=None if HIDE_PFPS_FOR_ROLES else message.author.display_avatar.url
        )

        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)

# ---------------- KEEP-ALIVE SERVER -------------------
app = Flask('')

@app.route('/')
def home():
    return "Color Role Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()
# -----------------------------------------------------

# Run the bot using Render environment variable
bot.run(os.getenv("DISCORD_TOKEN"))

