import os
import re
import discord
from discord.ext import commands

ROLE_NAMES = [
    "Rust", "Bronze", "Gold", "Olive", "Jade",
    "Teal", "Cobalt", "Indigo", "Purple", "Violet", "Fuchsia"
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_initials(nickname: str) -> str:
    # Get all uppercase letters or first 2 characters if none
    initials = "".join(re.findall(r'[A-Z]', nickname))
    if not initials:
        initials = nickname[:2].upper()
    return initials

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_roles = [role for role in message.author.roles if role.name in ROLE_NAMES]
    if user_roles:
        role = user_roles[0]
        nickname = message.author.display_name
        initials = get_initials(nickname)
        text = f"{initials}: {message.content}"

        embed = discord.Embed(description=text, color=role.color)
        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
