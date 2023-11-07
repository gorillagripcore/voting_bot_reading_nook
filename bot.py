import discord

TOKEN = 'your token'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

voting_ready = False
books_received = 0
book_messages = [] 
voting_month = ""

@client.event
async def on_ready():
    print(f'{client.user} is now running!')
    await client.change_presence(activity=discord.Game(name="with your feelings"))

@client.event
async def on_message(message):
    global voting_ready, books_received, book_messages, voting_month

    if message.author == client.user or message.channel.name != "vote-input":
        return

    if message.content.lower() == "new vote":
        voting_ready = True
        books_received = 0
        book_messages = []
        voting_month = ""
        await message.channel.send("New vote initiated. Please send the first book.")
        return

    if message.channel.name == "vote-input" and voting_ready:
        try:
            if books_received < 2:
                book_messages.append(message)
                books_received += 1
                if books_received == 1:
                    await message.channel.send("First book received. Please send the second book.")
                elif books_received == 2:
                    voting_month = await ask_for_month(message)
                    emojis = await ask_for_emojis(message)
                    if emojis:
                        await process_books(emojis, voting_month)
                        books_received = 0
                        voting_ready = False
        except Exception:
            await message.channel.send(f"An error occurred while processing the vote")
            voting_ready = False
            books_received = 0
            book_messages = []

async def process_books(emojis, month):
    try:
        first_book = book_messages[0]
        second_book = book_messages[1]

        embed1 = create_book_embed(first_book)
        embed2 = create_book_embed(second_book)
        if not embed1 or not embed2:
            await first_book.channel.send("Error: One of the books weren't formatted correctly. Please start over.")
            return

        first_book_title = first_book.content.split(",")[0].strip()
        second_book_title = second_book.content.split(",")[0].strip()

        vote_message = f"Voting for {month}! React with {emojis[0]} for '{first_book_title}' and {emojis[1]} for '{second_book_title}'"

        voting_channel = discord.utils.get(first_book.guild.channels, name="✨-voting-✨")
        if voting_channel:
            message_to_react = await voting_channel.send(content=vote_message, embeds=[embed1, embed2])
            await message_to_react.add_reaction(emojis[0])
            await message_to_react.add_reaction(emojis[1])
        else:
            await first_book.channel.send("Error: Voting channel not found. Please check if the channel '✨-voting-✨' exists.")
    except discord.DiscordException:
        await first_book.channel.send(f"A Discord error occurred")

def create_book_embed(message):
    try:
        image_url = message.attachments[0].url
        parts = message.content.split(",")
        book_title = parts[0].strip()
        author = parts[1].strip()
        embed = discord.Embed(title=book_title, description=f"by {author}")
        embed.set_image(url=image_url)
        return embed
    except IndexError:
        return None

async def ask_for_emojis(message):
    try:
        await message.channel.send("Please enter the emojis you want to use for voting. Separate them with spaces.")
        reaction_message = await client.wait_for('message', check=lambda m: m.author == message.author and m.channel == message.channel)
        emojis = reaction_message.content.split()
        if len(emojis) != 2:
            await message.channel.send("Error: You need to provide exactly two emojis for the vote. Please start over")
            return None
        return emojis
    except Exception:
        await message.channel.send(f"An error occurred while collecting emojis")
        return None

async def ask_for_month(message):
    try:
        await message.channel.send("Please enter the month for the voting.")
        month_message = await client.wait_for('message', check=lambda m: m.author == message.author and m.channel == message.channel)
        return month_message.content.strip()
    except Exception:
        await message.channel.send(f"An error occurred while setting the month")
        return None

client.run(TOKEN)
