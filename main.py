import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Arquivo para salvar warns
WARN_FILE = "warns.json"

if not os.path.exists(WARN_FILE):
    with open(WARN_FILE, "w") as f:
        json.dump({}, f)

def load_warns():
    with open(WARN_FILE, "r") as f:
        return json.load(f)

def save_warns(warns):
    with open(WARN_FILE, "w") as f:
        json.dump(warns, f, indent=4)

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!painel | Servidor de Amigos"))

# ================== PAINEL ==================
@bot.command()
async def painel(ctx):
    embed = discord.Embed(title="🛠 Painel de Moderação", color=0x00ff00)
    embed.add_field(name="Comandos Principais", value="`!warn` `!warns` `!ban` `!kick` `!mute` `!clear`", inline=False)
    await ctx.send(embed=embed)

# ================== SISTEMA DE WARNS ==================
@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason="Sem motivo"):
    warns = load_warns()
    user_id = str(member.id)
    
    if user_id not in warns:
        warns[user_id] = {"points": 0, "warns": []}
    
    warns[user_id]["points"] += 2
    warns[user_id]["warns"].append({
        "reason": reason,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "moderator": str(ctx.author)
    })
    
    save_warns(warns)
    points = warns[user_id]["points"]
    
    await ctx.send(f"⚠️ **{member}** recebeu warn! (**{points} pontos** total) | Motivo: {reason}")
    
    # Punições automáticas
    if points >= 12:
        await member.ban(reason="12+ pontos")
        await ctx.send(f"🔨 {member} foi banido automaticamente!")
    elif points >= 8:
        await member.timeout(timedelta(hours=12))
        await ctx.send(f"🔇 {member} mutado por 12h (8+ pontos)")
    elif points >= 4:
        await member.timeout(timedelta(hours=2))
        await ctx.send(f"🔇 {member} mutado por 2h (4+ pontos)")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warns(ctx, member: discord.Member):
    warns = load_warns()
    user_id = str(member.id)
    if user_id not in warns or not warns[user_id]["warns"]:
        return await ctx.send(f"✅ {member} está limpo.")
    
    embed = discord.Embed(title=f"Warns de {member}", color=0xff0000)
    for w in warns[user_id]["warns"][-10:]:  # últimos 10
        embed.add_field(name=w['date'], value=f"**Motivo:** {w['reason']}\n**Por:** {w['moderator']}", inline=False)
    embed.set_footer(text=f"Total de pontos: {warns[user_id]['points']}")
    await ctx.send(embed=embed)

# ================== ANTI-SPAM ==================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# Outros comandos básicos
@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! `{round(bot.latency * 1000)}ms`')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} mensagens apagadas!", delete_after=5)

import os
bot.run(os.getenv('DISCORD_TOKEN'))
