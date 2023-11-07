import discord

TOKEN = 'add your token here'
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

def function():
    pass

@client.event
async def on_ready():
      print(f'{client.user} is now running!')

client.run(TOKEN)
