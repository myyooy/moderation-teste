import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import asyncio
import random
from datetime import datetime

# --- CONFIGURAÇÃO DE INTENTS ---
# Isso permite que o bot veja membros, mensagens e estados
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- CLASSE DO SISTEMA DE TICKETS (SUPORTE) ---
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None) # Sem timeout para o botão não parar de funcionar

    @discord.ui.button(label="Abrir Suporte", style=discord.ButtonStyle.success, emoji="📩", custom_id="persistent:ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Nome do canal de ticket
        channel_name = f"ticket-{user.name}"
        
        # Verifica se já existe um canal com esse nome para evitar spam
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name.lower())
        if existing_channel:
            return await interaction.response.send_message(f"❌ Você já tem um ticket aberto em {existing_channel.mention}", ephemeral=True)

        # Permissões do canal privado
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Seu ticket foi criado: {channel.mention}", ephemeral=True)
        
        # Mensagem dentro do Ticket
        embed_ticket = discord.Embed(
            title="🎫 Suporte Moderation Pro",
            description=f"Olá {user.mention}, explique seu problema abaixo.\nUm moderador irá te atender em breve.",
            color=discord.Color.blue()
        )
        
        view_close = View(timeout=None)
        btn_close = Button(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
        
        async def close_callback(inter):
            await inter.response.send_message("🚨 Este canal será deletado em 5 segundos...")
            await asyncio.sleep(5)
            await channel.delete()
            
        btn_close.callback = close_callback
        view_close.add_item(btn_close)
        await channel.send(embed=embed_ticket, view=view_close)

# --- PAINEL DE COMANDOS RÁPIDOS ---
class MainPainel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Limpar Chat", style=discord.ButtonStyle.danger, emoji="🧹")
    async def btn_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Digite `!clear 100` no chat para usar esta função.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Você não tem permissão.", ephemeral=True)

    @discord.ui.button(label="Status do Servidor", style=discord.ButtonStyle.primary, emoji="📊")
    async def btn_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        embed = discord.Embed(title=f"📊 Status: {guild.name}", color=0x2f3136)
        embed.add_field(name="Membros", value=f"👥 {guild.member_count}")
        embed.add_field(name="Canais", value=f"💬 {len(guild.channels)}")
        embed.add_field(name="Dono", value=guild.owner.mention)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- EVENTOS ---
@bot.event
async def on_ready():
    # Registra a view do ticket para que funcione mesmo se o bot reiniciar
    bot.add_view(TicketView())
    print(f"✅ SISTEMA COMPLETO ONLINE: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="🛡️ Moderando com Estilo"))

@bot.event
async def on_member_join(member):
    # CARGO AUTOMÁTICO: Mude "Membro" para o nome do cargo do seu servidor
    role_name = "Membro" 
    role = discord.utils.get(member.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
    
    # Mensagem de boas-vindas no console
    print(f"📥 {member.name} entrou e recebeu o cargo {role_name}")

@bot.event
async def on_message_delete(message):
    # LOG DE MENSAGENS APAGADAS (Precisa de um canal chamado 'logs-bot')
    if message.author.bot: return
    log_channel = discord.utils.get(message.guild.text_channels, name="logs-bot")
    if log_channel:
        embed = discord.Embed(title="🗑️ Mensagem Deletada", color=discord.Color.red(), timestamp=datetime.now())
        embed.add_field(name="Autor", value=message.author.mention)
        embed.add_field(name="Canal", value=message.channel.mention)
        embed.add_field(name="Conteúdo", value=message.content or "Sem texto (Imagem/Embed)")
        await log_channel.send(embed=embed)

# --- COMANDOS DE MODERAÇÃO ---

@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    embed = discord.Embed(
        title="🛡️ Painel de Gestão Moderation Pro",
        description="Clique nos botões abaixo ou use os comandos manuais.",
        color=0x2f3136
    )
    embed.add_field(name="🛠️ Moderação", value="`!clear`, `!lock`, `!unlock`, `!slowmode`", inline=True)
    embed.add_field(name="👤 Usuários", value="`!ban`, `!kick`, `!mute`, `!unmute`", inline=True)
    embed.add_field(name="🎫 Suporte", value="Use `!setup_ticket` para o canal de suporte.", inline=False)
    embed.set_footer(text="Bot desenvolvido para Alta Performance")
    await ctx.send(embed=embed, view=MainPainel())

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
    await ctx.send(f"✅ **{deleted}** mensagens foram limpas!", delete_after=5)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="🎫 Central de Suporte",
        description="Precisa de ajuda da nossa equipe?\

