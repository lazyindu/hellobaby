
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
from plugins.insta_lazydeveloper import download_from_lazy_instagram 
from plugins.tiktok_x_lazydeveloper import download_from_lazy_tiktok_and_x
from plugins.pintrest_lazydeveloepr import download_pintrest_vid
from plugins.youtube_downloader_lazydeveloper import youtube_and_other_download_lazy
from pyrogram import Client, filters
from pyrogram.types import Message
import re
from pyrogram import enums

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

user_tasks = {}


@Client.on_message(filters.private & filters.text & ~filters.command(['start','users','broadcast']))
async def handle_incoming_message(client: Client, message: Message):
    try:
        user_id = message.from_user.id  # Get user ID dynamically

        # Extract the message text and user ID
        if user_id not in ADMIN:
            await client.send_message(chat_id=message.chat.id, text=f"Sorry Sweetheart! cant talk to you \nTake permission from my Lover @LazyDeveloperr")
        # Initialize task list for the user if not already present
        if user_id not in user_tasks:
            user_tasks[user_id] = []

        # Check if the user already has 3 active tasks
        if len(user_tasks[user_id]) >= 1:
            await message.reply("⏳ You already have 2 active downloads. Please wait for one to finish before adding more.")
            return

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
                lazydev = await ok.edit_text(f"Detected {platform} URL!")
                await lazydev.delete()
                # Create a task for the handler function
                task = asyncio.create_task(handler(client, message, url))
                # Create a task and add it to the user's task list
                user_tasks[user_id].append(task)
                
                # while not task.done():
                #     await asyncio.sleep(3)  # Sleep for 3 seconds before sending the next action
                #     await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)  # Show the 'upload document' action

                # When the task finishes, remove it from the user's task list
                # task.add_done_callback(lambda t: user_tasks[user_id].remove(t))                
                async def task_done_callback(t):
                    user_tasks[user_id].remove(t)  # Remove the task from the user's task list
                    workdonemsg = asyncio.create_task(client.send_message(
                        chat_id=message.chat.id,
                        text="✅ Your task is completed. You can send a new URL now!"
                    ))
                    await asyncio.sleep(300)
                    await workdonemsg.delete()

                task.add_done_callback(task_done_callback)
                
                return #await task  # Wait for the task to finish before proceeding

        # for platform, handler in PLATFORM_HANDLERS.items():
        #     if platform in url:
        #         lazydev = await ok.edit_text(f"Detected {platform} ᴜʀʟ!")
        #         await lazydev.delete()
        #         await handler(client, message, url)
        #         return

    except Exception as e:
        # Handle any errors
        await message.reply(f"❌ An error occurred: {e}")

