
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
from plugins.insta_lazydeveloper import download_from_lazy_instagram 
from plugins.tiktok_x_lazydeveloper import download_from_lazy_tiktok_and_x
from plugins.pintrest_lazydeveloepr import download_pintrest_vid
from plugins.ytdl_lazydeveloper import download_from_youtube
from plugins.echo import youtube_and_other_download_lazy

# from plugins.facebook_lazydeveloper import download_and_send_video
# from plugins.ytdl_lazy import handle_youtube_link, handle_youtube_playlist_link

# @Client.on_message(filters.private & filters.text)
# async def handle_youtube_links(bot, message):
#     try:
#         if "youtube" in message.text.lower() or "youtu.be" in message.text.lower():
#             url = message.text.strip()
#             if "playlist" in url and "list=" in url:
#                 # Handle playlist link
#                 await handle_youtube_playlist_link(bot, message, url)
#             elif "watch?v=" in url or "youtu.be/" in url:
#                 # Handle video link
#                 await handle_youtube_link(bot, message, url)
#             else:
#                 await handle_youtube_link(bot, message, url)
#                 await message.reply("Invalid YouTube link. Please send a valid video or playlist URL.")
#         else:
#             await message.reply("This doesn't look like a YouTube link.")
#     except Exception as e:
#         print(f"Error: {e}")

# @Client.on_message(filters.regex(r'https?:\/\/(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?([a-zA-Z0-9_-]{11})$'))
# async def handle_single(bot, message):
#     try:
#         url = message.text.strip()
#         await handle_youtube_link(bot, message, url)
#     except Exception as e:
#         print(e)

# @Client.on_message(filters.regex(r"(?:(?:https?:)?//)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)"))
# async def handle_playlist(bot, message):
#     try:
#         url = message.text.strip()
#         await handle_youtube_playlist_link(bot, message, url)
#     except Exception as e:
#         print(e)

from pyrogram import Client, filters
from pyrogram.types import Message
import re

@Client.on_message(filters.private & filters.command(["spdl"]))
async def handle_seperate_download(client: Client, message: Message):
    # Extract the text after the command
    command_parts = message.text.split(maxsplit=1)  # Split the message into command and arguments
    if len(command_parts) < 2:
        await message.reply("⚠️ Please provide a valid URL after the command. Example: `/spdl <url>`")
        return
    
    url = command_parts[1].strip()  # Extract the URL part
    # Optional: Use regex to validate the URL format
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    if not url_pattern.match(url):
        await message.reply("⚠️ The provided text is not a valid URL. Please check and try again.")
        return

    # Inform the user about the process
    ok = await message.reply("🔄 Detecting URL type and processing the download...")
    
    # Call your download function
    await youtube_and_other_download_lazy(client, message, url)
    await ok.edit_text("Thank you for using me ❤")

@Client.on_message(filters.private & filters.text & ~filters.command(['start','users','broadcast']))
async def handle_incoming_message(client: Client, message: Message):
    try:
        user_id = message.from_user.id  # Get user ID dynamically

        if user_id not in ADMIN:
            await client.send_message(chat_id=message.chat.id, text=f"Sorry Sweetheart! cant talk to you \nTake permission from my Lover @LazyDeveloperr")
        # Extract the message text and user ID
        url = message.text.strip()
        ok = await message.reply("🔄 ᴅᴇᴛᴇᴄᴛɪɴɢ ᴜʀʟ ᴛʏᴘᴇ ᴀɴᴅ ᴘʀᴏᴄᴇssɪɴɢ ᴛʜᴇ ᴅᴏᴡɴʟᴏᴀᴅ...")

        # Check if the URL contains 'instagram.com'
        PLATFORM_HANDLERS = {
            "instagram.com": download_from_lazy_instagram,
            "tiktok.com": download_from_lazy_tiktok_and_x,
            "twitter.com": download_from_lazy_tiktok_and_x,
            "x.com": download_from_lazy_tiktok_and_x,
            "pin.it": download_pintrest_vid,
            "pinterest.com": download_pintrest_vid,
            "facebook.com": download_from_lazy_tiktok_and_x,
            # "youtube.com": download_from_youtube,
            # "youtu.be": download_from_youtube
        }
        for platform, handler in PLATFORM_HANDLERS.items():
            if platform in url:
                lazydev = await ok.edit_text(f"Detected {platform} ᴜʀʟ!")
                await lazydev.delete()
                await handler(client, message, url)
                return

    except Exception as e:
        # Handle any errors
        await message.reply(f"❌ An error occurred: {e}")

