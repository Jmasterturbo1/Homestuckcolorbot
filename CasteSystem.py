import os
import re
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ---------------- CONFIG ----------------
# Roles that control message formatting
ROLE_COLOR_MAP = {
    "Red": "css",     # Use Discord syntax highlighting (css, diff, etc.) for colored text
    "Orange": "fix",
    "Yellow": "ini",
    "Green": "bash",
    "Blue": "css",
    "Indigo": "diff",
    "Violet": "md"
}

# Global toggle: hide profile pictures? (unused here, text only)
HIDE_PFPS_FOR_ROLES = True
# ----------------------------------------

# Setup Discord bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- EVENTS -------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if user has one of the color roles
    user_roles = [role.name for role in message.author.roles]
    matching_roles = [r for r in user_roles if r in ROLE_COLOR_MAP]

    if matching_roles:
        role_name = matching_roles[0]
        syntax = ROLE_COLOR_MAP[role_name]

        # Get initials (supports single-word camel-case names)
        nickname = message.author.display_name
        initials = "".join(re.findall(r'[A-Z]', nickname))
        if not initials:
            initials = nickname[0].upper()

        # Prepend initials to message
        content = f"{initials}: {message.content}"

        # Send text with optional syntax highlighting for "color"
        formatted_message = f"```{syntax}\n{content}\n```"
        await message.channel.send(formatted_message)
        await message.delete()
    else:
        await bot.process_commands(message)

# ----------------- KEEP-ALIVE SERVER -----------------
app = Flask('')

@app.route('/')
def home():
    return "Color Role Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()
# ------------------------------------------------------

# ----------------- RUN BOT -----------------
bot.run(os.getenv("DISCORD_TOKEN"))

