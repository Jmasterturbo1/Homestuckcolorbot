import os
import re
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ---------------- CONFIG ----------------
ROLE_NAMES = ["Rust", "Bronze", "Gold", "Olive", "Jade", "Teal", "Cobalt", "Indigo", "Purple", "Violet", "Fuchsia",]
# ----------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- HELPER FUNCTIONS ----------------
def get_initials(nickname: str) -> str:
    initials = "".join(re.findall(r'[A-Z]', nickname))
    if not initials:
        initials = nickname[0].upper()
    return initials

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check for role
    user_roles = [role for role in message.author.roles if role.name in ROLE_NAMES]
    if user_roles:
        role = user_roles[0]
        nickname = message.author.display_name
        initials = get_initials(nickname)
        text = f"{initials}: {message.content}"

        # Create embed with role color on sidebar
        embed = discord.Embed(
            description=text,
            color=role.color  # sidebar matches role hex color
        )

        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)

# ---------------- KEEP-ALIVE SERVER ----------------
app = Flask('')

@app.route('/')
def home():
    return "Color Role Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()
# ------------------------------------------------------

# ---------------- RUN BOT ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
