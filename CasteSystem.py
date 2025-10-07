import os
import re
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from PIL import Image, ImageDraw, ImageFont
import io

# ---------------- CONFIG ----------------
ROLE_NAMES = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"]
FONT_PATH = "arial.ttf"  # make sure this font is available in your environment
FONT_SIZE = 40
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

def create_text_image(text: str, hex_color: int) -> io.BytesIO:
    # Convert integer hex to RGB tuple
    rgb = ((hex_color >> 16) & 0xFF, (hex_color >> 8) & 0xFF, hex_color & 0xFF)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    width, height = font.getsize(text)
    img = Image.new("RGBA", (width + 20, height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 0), text, fill=rgb, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

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

        # Generate image
        image_buffer = create_text_image(text, role.color.value)

        # Send via webhook to mimic native user message
        webhook = await message.channel.create_webhook(name="ColorTextBot")
        await webhook.send(file=discord.File(fp=image_buffer, filename="message.png"))
        await webhook.delete()
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

