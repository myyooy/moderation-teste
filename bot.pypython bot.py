import discord
from discord.ext import commands

# Configuração
intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler mensagens

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Testando no celular 📱"))

@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong! Latência: {round(bot.latency * 1000)}ms')

@bot.command()
async def oi(ctx):
    await ctx.send(f'Olá {ctx.author.mention}! Bot funcionando pelo celular! 🔥')

# ================== COLOQUE SEU TOKEN AQUI ==================
bot.run('SEU_TOKEN_AQUI')
