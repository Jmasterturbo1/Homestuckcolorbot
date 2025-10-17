import os
import re
import discord
from discord.ext import commands
from discord import app_commands

# ---------------- CONFIG ----------------
ROLE_NAMES = ["Rust", "Bronze", "Gold", "Olive", "Jade", "Teal", "Cobalt", "Indigo", "Purple", "Violet", "Fuchsia"]
GUILD_ID = 123456789012345678  # <- Replace with your Discord server ID
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

async def assign_role(member: discord.Member, new_role_name: str):
    # Remove any existing caste roles
    for role in member.roles:
        if role.name in ROLE_NAMES:
            await member.remove_roles(role)
    # Assign new role
    role_to_add = discord.utils.get(member.guild.roles, name=new_role_name)
    if role_to_add:
        await member.add_roles(role_to_add)

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    try:
        # Sync commands to your server instantly
        await bot.tree.sync(guild=guild)
        print("✅ Slash commands synced!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

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

        # Send embed with role color
        embed = discord.Embed(
            description=text,
            color=role.color
        )

        await message.channel.send(embed=embed)
        await message.delete()
    else:
        await bot.process_commands(message)

# ---------------- SLASH COMMAND ----------------
@bot.tree.command(name="changeblood", description="Change your caste role", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(new_role="The new caste role to assign")
async def changeblood(interaction: discord.Interaction, new_role: str):
    await interaction.response.defer(ephemeral=True)  # <-- immediately respond to avoid timeout

    if new_role not in ROLE_NAMES:
        await interaction.followup.send(
            f"❌ Invalid role. Choose from: {', '.join(ROLE_NAMES)}", 
            ephemeral=True
        )
        return

    try:
        await assign_role(interaction.user, new_role)
        await interaction.followup.send(
            f"✅ Your role has been changed to **{new_role}**!", 
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Something went wrong while changing your role: `{e}`", 
            ephemeral=True
        )
# ---------------- AUTOCOMPLETE ----------------
@changeblood.autocomplete('new_role')
async def new_role_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=r, value=r) 
        for r in ROLE_NAMES if current.lower() in r.lower()
    ][:25]  # Discord limits to 25 suggestions

# ---------------- RUN BOT ----------------
bot.run(os.getenv("DISCORD_TOKEN"))
