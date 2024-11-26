import instaloader
import re
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
insta = instaloader.Instaloader()

async def download_from_lazy_instagram(client, message, url):
    # Extract shortcode from Instagram URL (assuming this is a function you implemented)
    post_shortcode = get_post_or_reel_shortcode_from_link(url)
    
    if not post_shortcode:
        print(f"log:\n\nuser: {message.chat.id}\n\nerror in getting post_shortcode")
        return  # Post shortcode not found, stop processing
    
    progress_message2 = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ ᴛᴏ ꜰᴇᴛᴄʜ ᴄᴀᴘᴛɪᴏɴ...</i>")
    await asyncio.sleep(1)
    
    # Get an instance of Instaloader (assuming this function initializes it)
    L = get_ready_to_work_insta_instance()        
    post = instaloader.Post.from_shortcode(L.context, post_shortcode)

    # Caption handling (ensure the caption does not exceed Telegram's limit)
    bot_username = client.username if client.username else TEL_USERNAME
    caption_trail = "\n\n\n" + f"ᴡɪᴛʜ ❤ @{bot_username}"

    new_caption = post.caption
    while len(new_caption) + len(caption_trail) > 1024:
        new_caption = new_caption[:-1]  # Trim caption if it's too long
    new_caption = new_caption + caption_trail  # Add bot username at the end
     # Initialize media list
    
    progress_message3 = await progress_message2.edit_text("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>")
    # await asyncio.sleep(1)
    
    media_list = []
    # Handle sidecars (multiple media in a post)
    if post.mediacount > 1:
        sidecars = post.get_sidecar_nodes()
        for s in sidecars:
            if s.is_video:
                url = s.video_url
                media = InputMediaVideo(url)
                if not media_list:  # Add caption to the first media
                    media = InputMediaVideo(url, caption=new_caption)
            else:
                url = s.display_url
                media = InputMediaPhoto(url)
                if not media_list:  # Add caption to the first media
                    media = InputMediaPhoto(url, caption=new_caption)
            media_list.append(media)

        # Send media group
        await client.send_media_group(message.chat.id, media_list)

    else:
        # Single media handling
        if post.is_video:
            await client.send_video(message.chat.id, post.video_url, caption=new_caption)
        else:
            await client.send_photo(message.chat.id, post.url, caption=new_caption)

    await progress_message3.delete()
    lazydeveloper = await client.send_message(chat_id=message.chat.id, text=f"❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ...")
    await asyncio.sleep(100)
    await lazydeveloper.delete()

# regex
insta_post_or_reel_reg = r'(?:https?://www\.)?instagram\.com\S*?/(p|reel)/([a-zA-Z0-9_-]{11})/?'

def get_post_or_reel_shortcode_from_link(link):
    match = re.search(insta_post_or_reel_reg, link)
    if match:
        return match.group(2)
    else:
        return False

def get_ready_to_work_insta_instance():
    L = instaloader.Instaloader()
    return L
