import os
import discord
from discord.ext import commands
from discord import app_commands

# ---------- TOKEN FROM ENV ----------
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- STORAGE ----------
guild_settings = {}
invites = {}
invite_counts = {}

# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    for guild in bot.guilds:
        invites[guild.id] = await guild.invites()

    await bot.tree.sync()
    print("✅ Slash commands synced")

# ---------- SET JOIN LOG CHANNEL ----------
@bot.tree.command(name="set_log_channel", description="Set channel for join logs")
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_settings.setdefault(interaction.guild.id, {})
    guild_settings[interaction.guild.id]["log_channel"] = channel.id
    await interaction.response.send_message(
        f"✅ Join logs set to {channel.mention}",
        ephemeral=True
    )

# ---------- REMOVE JOIN LOG CHANNEL ----------
@bot.tree.command(name="remove_log_channel", description="Remove join log channel")
async def remove_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    settings = guild_settings.get(interaction.guild.id, {})
    if settings.get("log_channel") == channel.id:
        del settings["log_channel"]
        await interaction.response.send_message(
            f"🗑️ Removed join log channel {channel.mention}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ That channel is not set.",
            ephemeral=True
        )

# ---------- SET INVITE LOG CHANNEL ----------
@bot.tree.command(name="set_invite_channel", description="Set channel for invite logs")
async def set_invite_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_settings.setdefault(interaction.guild.id, {})
    guild_settings[interaction.guild.id]["invite_channel"] = channel.id
    await interaction.response.send_message(
        f"✅ Invite logs set to {channel.mention}",
        ephemeral=True
    )

# ---------- REMOVE INVITE LOG CHANNEL ----------
@bot.tree.command(name="remove_invite_channel", description="Remove invite log channel")
async def remove_invite_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    settings = guild_settings.get(interaction.guild.id, {})
    if settings.get("invite_channel") == channel.id:
        del settings["invite_channel"]
        await interaction.response.send_message(
            f"🗑️ Removed invite log channel {channel.mention}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ That channel is not set.",
            ephemeral=True
        )

# ---------- MEMBER JOIN ----------
@bot.event
async def on_member_join(member):
    guild = member.guild
    settings = guild_settings.get(guild.id, {})

    new_invites = await guild.invites()
    old_invites = invites.get(guild.id, [])
    inviter = None

    for new in new_invites:
        for old in old_invites:
            if new.code == old.code and new.uses > old.uses:
                inviter = new.inviter
                break

    invites[guild.id] = new_invites

    total = 0
    if inviter:
        invite_counts[inviter.id] = invite_counts.get(inviter.id, 0) + 1
        total = invite_counts[inviter.id]

    # Join log
    log_id = settings.get("log_channel")
    if log_id:
        channel = guild.get_channel(log_id)
        if channel:
            await channel.send(f"📥 **{member.mention} joined the server**")

    # Invite log
    invite_id = settings.get("invite_channel")
    if invite_id:
        channel = guild.get_channel(invite_id)
        if channel:
            await channel.send(
                f"📥 **{member.mention} joined**\n"
                f"👤 Invited by: {inviter.mention if inviter else 'Unknown'}\n"
                f"🔢 Total invites: **{total}**"
            )

# ---------- RUN ----------
bot.run(TOKEN)
