import discord
from discord.ext import commands

# Intents for message + member info
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Role Names where colors apply
COLOR_ROLES = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"]

# Color overrides (0xRRGGBB)
CUSTOM_COLORS = {
    "Red": 0xFF3333,
    "Orange": 0xFF9900,
    "Yellow": 0xFFF000,
    "Green": 0x00CC66,
    "Blue": 0x3399FF,
    "Indigo": 0x4B0082,
    "Violet": 0x9933FF,
}

# 🧩 Global toggle to show profile pictures (for users with color roles)
SHOW_PROFILE_PIC = False  # Set to True if you want avatars in embeds


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


def get_initials(name: str) -> str:
    """Extract initials from a user's nickname or username."""
    if not name:
        return "??"

    # Split nickname by spaces or underscores
    parts = [p for p in name.replace("_", " ").split(" ") if p]

    if len(parts) == 1:
        # Try to use capital letters for initials if available
        name = parts[0]
        caps = [c for c in name if c.isupper()]
        if len(caps) >= 2:
            return "".join(caps[:2])
        elif len(name) >= 2:
            return (name[0] + name[1]).upper()
        else:
            return name[0].upper()
    else:
        # Take first letter of up to first two words
        return "".join(p[0].upper() for p in parts[:2])


@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only act on users with one of the specified roles
    color_roles = [r for r in message.author.roles if r.name in COLOR_ROLES]
    if not color_roles:
        return  # user doesn't have a color role → do nothing

    color_role = color_roles[0]
    # Use custom color if defined, otherwise use the role's actual color
    embed_color = CUSTOM_COLORS.get(color_role.name, color_role.color.value)

    nickname = message.author.nick or message.author.name
    initials = get_initials(nickname)
    formatted_text = f"**{initials}:** {message.content}"

    embed = discord.Embed(description=formatted_text, color=embed_color)

    # Add author display name (with or without avatar based on toggle)
    if SHOW_PROFILE_PIC:
        embed.set_author(name=message.author.display_name,
                         icon_url=message.author.display_avatar.url)
    else:
        embed.set_author(name=message.author.display_name)

    # Replace message with formatted embed
    await message.channel.send(embed=embed)
    await message.delete()


bot.run("TOKEN")
