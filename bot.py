import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- PAINEL INTERATIVO COM BOTÕES ---
class PainelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Limpar Chat", style=discord.ButtonStyle.danger, emoji="🧹")
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Use `!clear [quantidade]` para limpar.", ephemeral=True)
        else:
            await interaction.response.send_message("Sem permissão!", ephemeral=True)

    @discord.ui.button(label="Trancar Canal", style=discord.ButtonStyle.secondary, emoji="🔒")
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels:
            await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
            await interaction.response.send_message("🔒 Canal trancado com sucesso!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Sistema de Elite Online: {bot.user}")

# Comando do Painel Lindo
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    embed = discord.Embed(
        title="🛡️ Central de Comando - Moderation Pro",
        description="Gerencie seu servidor com eficiência abaixo.",
        color=0x2f3136
    )
    embed.add_field(name="🧹 Moderação", value="`!clear`, `!slowmode`, `!lock`, `!unlock`", inline=False)
    embed.add_field(name="👤 Usuários", value="`!ban`, `!kick`, `!mute`, `!unmute`", inline=False)
    embed.set_footer(text="Aperte os botões para ações rápidas")
    embed.set_image(url="https://i.imgur.com/8fO4lW9.png") # Uma linha estética
    
    await ctx.send(embed=embed, view=PainelView())

# Comando Clear Ultra (Limpa muito)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 100):
    await ctx.message.delete()
    # Deletando em blocos de 100 (limite do API)
    deleted = 0
    while amount > 0:
        step = min(amount, 100)
        purged = await ctx.channel.purge(limit=step)
        deleted += len(purged)
        amount -= step
        if len(purged) < step: break # Acabaram as mensagens
    
    msg = await ctx.send(f"✅ **{deleted}** mensagens foram incineradas!")
    await asyncio.sleep(5)
    await msg.delete()

# Comando Slowmode
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐌 Modo lento definido para {seconds} segundos.")

# Comando Lock/Unlock
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Canal trancado para membros!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Canal destrancado!")

bot.run(os.getenv('DISCORD_TOKEN'))

