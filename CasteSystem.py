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
    initials = "".join(re.findall(r"[A-Z]", nickname))
    if not initials:
        initials = nickname[:2].upper()
    elif len(initials) == 1 and len(nickname) > 1:
        initials = nickname[:2].upper()
    return initials


# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")


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

        # Create embed with sidebar color
        embed = discord.Embed(description=text, color=role.color)

        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)


# ---------------- SLASH COMMAND ----------------
@bot.tree.command(name="changeblood", description="Change your blood color role.")
@app_commands.describe(color="Choose your blood color.")
async def changeblood(interaction: discord.Interaction, color: str):
    member = interaction.user
    guild = interaction.guild

    # Normalize input
    color = color.capitalize()
    if color not in ROLE_NAMES:
        await interaction.response.send_message(
            f"❌ `{color}` isn’t a valid color. Try one of: {', '.join(ROLE_NAMES)}",
            ephemeral=True
        )
        return

    # Remove any old blood roles
    roles_to_remove = [r for r in member.roles if r.name in ROLE_NAMES]
    for r in roles_to_remove:
        await member.remove_roles(r)

    # Add the new one
    role_to_add = discord.utils.get(guild.roles, name=color)
    if not role_to_add:
        await interaction.response.send_message(f"⚠️ The role `{color}` doesn’t exist on this server.", ephemeral=True)
        return

    await member.add_roles(role_to_add)
    await interaction.response.send_message(f"🩸 Your blood color is now **{color}**!", ephemeral=True)


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

