import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import asyncio
from flask import Flask
from threading import Thread

# Load the bot token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True  # To listen to messages and attachments
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Define a basic view with buttons
class UploadView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Upload an Image", style=discord.ButtonStyle.primary, custom_id="upload_image"))

class UploadAnotherView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Upload Another Image", style=discord.ButtonStyle.primary, custom_id="upload_another_image"))

# Flask Setup to keep the bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

# Function to keep the Flask server running in a separate thread
def run():
    app.run(host='0.0.0.0', port=3000)

# Event to handle button interactions
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id") == "upload_image":
        # Acknowledge the interaction
        await interaction.response.defer()

        # Send a private message asking for the image upload
        await interaction.user.send("Please upload an image!")

        # Set up a check function to only respond to the user
        def check(message):
            return message.author == interaction.user and message.attachments

        # Wait for the user to upload an image
        try:
            # Wait for an attachment (image) from the user
            message = await bot.wait_for('message', check=check, timeout=60.0)

            # Get the image URL from the attachment
            image_url = message.attachments[0].url

            # Create the embed
            embed = discord.Embed(title="Smash or Pass?")
            embed.set_image(url=image_url)

            # Send the embed back to the server (same channel as where !start was triggered)
            channel = interaction.channel
            embed_message = await channel.send(embed=embed)

            # Add reactions (tick and cross) to the embed message
            await embed_message.add_reaction("✅")
            await embed_message.add_reaction("❌")

            # Add a button for uploading another image
            upload_button = UploadAnotherView()

            # Send the button to the channel for uploading another image
            await channel.send("Wanna do another one? Press the button below!", view=upload_button)

        except asyncio.TimeoutError:
            await interaction.user.send("You took too long to upload an image. Please try again!")

    elif interaction.data.get("custom_id") == "upload_another_image":
        # Acknowledge the interaction for uploading another image
        await interaction.response.defer()

        # Ask the user to upload another image
        await interaction.user.send("Please upload another image!")

        # Set up a check function to only respond to the user
        def check(message):
            return message.author == interaction.user and message.attachments

        # Wait for the user to upload an image again
        try:
            # Wait for an attachment (image) from the user
            message = await bot.wait_for('message', check=check, timeout=60.0)

            # Get the image URL from the attachment
            image_url = message.attachments[0].url

            # Create the embed for the new image
            embed = discord.Embed(title="Smash or Pass?")
            embed.set_image(url=image_url)

            # Send the embed back to the server (same channel as where the first image was uploaded)
            channel = interaction.channel
            embed_message = await channel.send(embed=embed)

            # Add reactions (tick and cross) to the embed message
            await embed_message.add_reaction("✅")
            await embed_message.add_reaction("❌")

            # Add a button for uploading another image
            upload_button = UploadAnotherView()

            # Send the button to the channel for uploading another image
            await channel.send("Click the button below to upload another image.", view=upload_button)

        except asyncio.TimeoutError:
            await interaction.user.send("You took too long to upload an image. Please try again!")

# Test command
@bot.command()
async def test(ctx):
    await ctx.send("The bot is working!")

# Start command
@bot.command()
async def start(ctx):
    await ctx.send("Smash or Pass! Upload an image!", view=UploadView())

# Start Flask server in a separate thread to keep the bot alive (this is required for serverless deployment)
Thread(target=run).start()

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.start(TOKEN))
