import os
import re
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ---------------- CONFIG ----------------
ROLE_NAMES = ["Rust", "Bronze", "Gold", "Olive", "Jade", "Teal", "Cobalt", "Indigo", "Purple", "Violet", "Fuchsia"]
# ----------------------------------------

# ---------------- BOT SETUP ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- HELPER FUNCTIONS ----------------
def get_initials(nickname: str) -> str:
    """Extract uppercase initials; fallback to first letter."""
    initials = "".join(re.findall(r'[A-Z]', nickname))
    if not initials:
        initials = nickname[0].upper()
    return initials

# ---------------- BOT EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_disconnect():
    print("⚠️ Bot disconnected from Discord!")

@bot.event
async def on_resumed():
    print("✅ Bot reconnected to Discord!")

@bot.event
async def on_error(event_method, *args, **kwargs):
    print(f"❌ Error in {event_method}: {args} {kwargs}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"📩 Received message: '{message.content}' from {message.author}")

    # Only process users with one of the target roles
    user_roles = [role for role in message.author.roles if role.name in ROLE_NAMES]
    if user_roles:
        role = user_roles[0]  # pick first matching role
        nickname = message.author.display_name
        initials = get_initials(nickname)
        text = f"{initials}: {message.content}"

        # Embed uses role color
        embed = discord.Embed(description=text, color=role.color)

        try:
            await message.channel.send(embed=embed)
            await message.delete()
        except discord.Forbidden:
            print("⚠️ Missing permission to delete/send messages!")
    else:
        await bot.process_commands(message)

# ---------------- FLASK KEEP-ALIVE ----------------
app = Flask('')

@app.route('/')
def home():
    return "Color Role Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ---------------- RUN BOT ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
