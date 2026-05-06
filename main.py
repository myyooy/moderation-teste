import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio
import random
from datetime import datetime

# --- CONFIGURAÇÃO ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- SISTEMA DE TICKETS ---
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Suporte", style=discord.ButtonStyle.success, emoji="📩", custom_id="persistent:tkt")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"ticket-{user.name}".lower()
        
        exist = discord.utils.get(guild.text_channels, name=channel_name)
        if exist:
            return await interaction.response.send_message(f"❌ Você já tem um ticket: {exist.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Ticket criado: {channel.mention}", ephemeral=True)
        
        emb = discord.Embed(title="🎫 Suporte", description="Aguarde um moderador.", color=discord.Color.blue())
        v = View(timeout=None)
        b = Button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
        async def c(i):
            await i.response.send_message("Fechando...")
            await asyncio.sleep(3)
            await channel.delete()
        b.callback = c
        v.add_item(b)
        await channel.send(embed=emb, view=v)

# --- PAINEL ---
class MainPainel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Status", style=discord.ButtonStyle.primary, emoji="📊")
    async def btn_s(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"👥 Membros: {interaction.guild.member_count}", ephemeral=True)

# --- EVENTOS ---
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f"✅ Bot Online: {bot.user}")

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Membro")
    if role: await member.add_roles(role)

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log = discord.utils.get(message.guild.text_channels, name="logs-bot")
    if log:
        e = discord.Embed(title="🗑️ Apagada", description=f"**De:** {message.author.mention}\n**Conteúdo:** {message.content}", color=discord.Color.red())
        await log.send(embed=e)

# --- COMANDOS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    e = discord.Embed(title="🛡️ Moderação Pro", description="Use `!clear`, `!lock`, `!unlock`, `!say`", color=0x2f3136)
    await ctx.send(embed=e, view=MainPainel())

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 100):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"✅ {len(deleted)} mensagens limpas!", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    e = discord.Embed(title="🎫 Suporte", description="Clique abaixo para abrir um ticket.", color=discord.Color.green())
    await ctx.send(embed=e, view=TicketView())

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Canal trancado!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Canal destrancado!")

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(embed=discord.Embed(description=msg, color=discord.Color.blue()))

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

bot.run(os.getenv('DISCORD_TOKEN'))

