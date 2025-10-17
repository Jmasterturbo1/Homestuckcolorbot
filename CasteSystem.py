import os
import re
import discord
from discord.ext import commands
from discord import app_commands

# ---------------- CONFIG ----------------
ROLE_NAMES = [
    "Rust", "Bronze", "Gold", "Olive", "Jade",
    "Teal", "Cobalt", "Indigo", "Purple", "Violet", "Fuchsia"
]
# ----------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- HELPER FUNCTIONS ----------------
def get_initials(nickname: str) -> str:
    initials = "".join(re.findall(r'[A-Z]', nickname))
    return initials if initials else nickname[0].upper()

async def assign_role(member: discord.Member, new_role_name: str):
    """Remove any caste roles and assign the new one."""
    for role in member.roles:
        if role.name in ROLE_NAMES:
            await member.remove_roles(role)
    role_to_add = discord.utils.get(member.guild.roles, name=new_role_name)
    if role_to_add:
        await member.add_roles(role_to_add)

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    # Sync slash commands for all guilds the bot is already in
    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=guild)
            print(f"✅ Synced commands for guild: {guild.name} ({guild.id})")
        except Exception as e:
            print(f"❌ Failed to sync commands for {guild.name}: {e}")

@bot.event
async def on_guild_join(guild):
    """Automatically sync commands when joining a new guild."""
    try:
        await bot.tree.sync(guild=guild)
        print(f"🌟 Synced commands for new guild: {guild.name} ({guild.id})")
    except Exception as e:
        print(f"❌ Failed to sync commands for new guild {guild.name}: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_roles = [role for role in message.author.roles if role.name in ROLE_NAMES]
    if user_roles:
        role = user_roles[0]
        initials = get_initials(message.author.display_name)
        text = f"{initials}: {message.content}"

        embed = discord.Embed(description=text, color=role.color)
        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)

# ---------------- SLASH COMMAND ----------------
@bot.tree.command(name="changeblood", description="Change your caste role")
@app_commands.describe(new_role="The new caste role to assign")
async def changeblood(interaction: discord.Interaction, new_role: str):
    await interaction.response.defer(ephemeral=True)

    if new_role not in ROLE_NAMES:
        await interaction.followup.send(
            f"❌ Invalid role. Choose from: {', '.join(ROLE_NAMES)}",
            ephemeral=True
        )
        return

    try:
        await assign_role(interaction.user, new_role)
        await interaction.followup.send(
            f"Your blood caste has been changed to **{new_role}**, Enjoy.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"`{e}`, Could not be found, new blood type perhaps?",
            ephemeral=True
        )

# ---------------- AUTOCOMPLETE ----------------
@changeblood.autocomplete('new_role')
async def new_role_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=r, value=r)
        for r in ROLE_NAMES if current.lower() in r.lower()
    ][:25]

# ---------------- RUN BOT ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
