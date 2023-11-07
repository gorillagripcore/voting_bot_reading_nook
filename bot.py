import discord
import asyncio

TOKEN = 'your token'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

voting_ready = False
books_received = 0
book_messages = [] 

@client.event
async def on_ready():
    print(f'{client.user} is now running!')
    await client.change_presence(activity=discord.Game(name="with your feelings"))

@client.event
async def on_message(message):
    global voting_ready, books_received, book_messages

    if message.author == client.user:
        return

    if message.content.lower() == "new vote":
        voting_ready = True
        books_received = 0
        book_messages = [] 
        await message.channel.send("New vote initiated. Please send the first book.")
        return

    if message.channel.name == "vote-input" and voting_ready:
        if books_received < 2:
            book_messages.append(message)
            books_received += 1
            if books_received == 1:
                await message.channel.send("First book received. Please send the second book.")
            elif books_received == 2:
                await message.channel.send("Both books received. Please enter the emojis for voting.")
                emojis = await ask_for_emojis(message)
                if emojis:
                    await process_books(emojis)
                    books_received = 0
                    voting_ready = False

async def process_books(emojis):
    first_book = book_messages[0]
    second_book = book_messages[1]

    embed1 = create_book_embed(first_book)
    embed2 = create_book_embed(second_book)

    voting_channel = discord.utils.get(first_book.guild.channels, name="voting")
    if voting_channel:
        message_to_react = await voting_channel.send(embeds=[embed1, embed2])
        for emoji in emojis:
            await message_to_react.add_reaction(emoji)

def create_book_embed(message):
    image_url = message.attachments[0].url
    parts = message.content.split(",")
    book_title = parts[0].strip()
    author = parts[1].strip()
    embed = discord.Embed(title=book_title, description=f"by {author}")
    embed.set_image(url=image_url)
    return embed

async def ask_for_emojis(message):
    def check(reaction_message):
        return reaction_message.author == message.author and reaction_message.channel == message.channel

    await message.channel.send("Please enter the emojis you want to use for voting. Separate them with spaces.")
    try:
        reaction_message = await client.wait_for('message', check=check, timeout=60.0)
    except asyncio.TimeoutError:
        await message.channel.send("Timeout reached. No emojis provided.")
        return []

    return reaction_message.content.split()

client.run(TOKEN)