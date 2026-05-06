import discord
from discord.ext import commands
from discord.ui import Button, View
import os, asyncio, random
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- SISTEMA DE TICKETS ---
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Abrir Suporte", style=discord.ButtonStyle.success, emoji="📩", custom_id="tkt_op")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild, user = interaction.guild, interaction.user
        name = f"ticket-{user.name}".lower()
        if discord.utils.get(guild.text_channels, name=name):
            return await interaction.response.send_message("❌ Você já tem um ticket aberto!", ephemeral=True)
        perms = {guild.default_role: discord.PermissionOverwrite(read_messages=False), user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        channel = await guild.create_text_channel(name, overwrites=perms)
        await interaction.response.send_message(f"✅ Criado em {channel.mention}", ephemeral=True)
        emb = discord.Embed(title="🎫 Suporte", description=f"Olá {user.mention}, relate seu problema.\nUm moderador virá em breve.", color=discord.Color.blue())
        v = View(timeout=None)
        b = Button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
        async def close(i):
            await i.response.send_message("Fechando...")
            await asyncio.sleep(3)
            await channel.delete()
        b.callback = close
        v.add_item(b)
        await channel.send(embed=emb, view=v)

# --- PAINEL PRINCIPAL ---
class MainPainel(View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Status do Servidor", style=discord.ButtonStyle.primary, emoji="📊")
    async def btn_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = interaction.guild
        e = discord.Embed(title=f"📊 {g.name}", color=0x2f3136)
        e.add_field(name="Membros", value=g.member_count)
        e.add_field(name="Canais", value=len(g.channels))
        await interaction.response.send_message(embed=e, ephemeral=True)

# --- EVENTOS ---
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f"🚀 Bot Online: {bot.user}")

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Membro")
    if role: await member.add_roles(role)

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    log = discord.utils.get(message.guild.text_channels, name="logs-bot")
    if log:
        e = discord.Embed(title="🗑️ Mensagem Apagada", color=discord.Color.red())
        e.add_field(name="Autor", value=message.author.mention)
        e.add_field(name="Conteúdo", value=message.content or "Arquivo")
        await log.send(embed=e)

# --- COMANDOS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    e = discord.Embed(title="🛡️ Central de Moderação Pro", description="Use `!clear [qtd]`, `!lock`, `!unlock`, `!say [texto]`, `!slowmode [seg]`, `!setup_ticket`", color=0x2f3136)
    e.add_field(name="Outros", value="`!avatar`, `!userinfo`, `!coinflip`", inline=False)
    await ctx.send(embed=e, view=MainPainel())

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 100):
    await ctx.message.delete()
    deleted = 0
    while amount > 0:
        step = min(amount, 100)
        purged = await ctx.channel.purge(limit=step)
        deleted += len(purged)
        amount -= step
        if len(purged) < step: break
    await ctx.send(f"✅ **{deleted}** mensagens limpas!", delete_after=5)

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
async def say(ctx, *, texto):
    await ctx.message.delete()
    await ctx.send(embed=discord.Embed(description=texto, color=discord.Color.blue()))

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐌 Modo lento: {seconds}s")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    m = member or ctx.author
    e = discord.Embed(title=f"Info: {m.name}", color=m.color)
    e.add_field(name="Entrou", value=m.joined_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=e)

@bot.command()
async def coinflip(ctx):
    await ctx.send(f"🪙 Deu **{random.choice(['Cara', 'Coroa'])}**!")

bot.run(os.getenv('DISCORD_TOKEN'))

