import os
import re
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# ---------------- CONFIG ----------------
ROLE_NAMES = ["Rust", "Bronze", "Gold", "Olive", "Jade", "Teal", "Cobalt", "Indigo", "Purple", "Violet", "Fuchsia"]
# ----------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- HELPER FUNCTIONS ----------------
def get_initials(nickname: str) -> str:
    initials = "".join(re.findall(r'[A-Z]', nickname))
    if not initials:
        initials = nickname[:2].upper()
    return initials

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

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

        embed = discord.Embed(
            description=text,
            color=role.color
        )

        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)

# ---------------- SLASH COMMANDS ----------------
@bot.tree.command(name="changeblood", description="Change your caste/blood color role.")
@app_commands.describe(new_role="The name of your new blood caste (e.g., Gold, Teal, etc.)")
async def changeblood(interaction: discord.Interaction, new_role: str):
    guild = interaction.guild
    member = interaction.user

    # Case-insensitive match
    matching_roles = [r for r in guild.roles if r.name.lower() == new_role.lower() and r.name in ROLE_NAMES]
    if not matching_roles:
        await interaction.response.send_message(f"❌ '{new_role}' is not a valid caste role.", ephemeral=True)
        return

    new_role_obj = matching_roles[0]

    # Remove old caste roles
    old_roles = [r for r in member.roles if r.name in ROLE_NAMES]
    for r in old_roles:
        await member.remove_roles(r)

    # Add new one
    await member.add_roles(new_role_obj)
    await interaction.response.send_message(f"✅ Your blood caste has been changed to **{new_role_obj.name}**!", ephemeral=True)

# ---------------- KEEP-ALIVE SERVER ----------------
app = Flask('')

@app.route('/')
def home():
    return "Color Role Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# ---------------- RUN BOT ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
