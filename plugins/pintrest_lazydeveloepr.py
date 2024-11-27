import asyncio
import logging
import math
import os
import time
from typing import List
from urllib import request
from script import Script
import pymongo
import requests
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


TMP_DOWNLOAD_DIRECTORY = os.environ.get(
    "TMP_DOWNLOAD_DIRECTORY", "./DOWNLOADS/")


def expand_url(short_url):
    try:
        response = requests.get(short_url, allow_redirects=True)
        return response.url  # Returns the expanded URL
    except requests.exceptions.RequestException as e:
        print(f"Error expanding URL: {e}")
        return None



# Example Usage:
# pinterest_url = input("Enter Pinterest URL (short URL like https://pin.it/...): ")
# video_url = get_pinterest_video_url(pinterest_url)

# async def lazy_get_download_url(link):
#     try:
#         # Send POST request to the downloader service
#         post_request = requests.post(
#             'https://www.expertsphp.com/download.php',
#             data={'url': link},
#         )

#         # Parse the response content
#         response_content = post_request.content.decode('utf-8')
#         document = pq(response_content)

#         # Extract all download links
#         download_links = document('table.table-condensed tbody td a').items()
#         video_link = None
#         fallback_link = None

#         for link in download_links:
#             href = link.attr('href')
#             if href:
#                 if '.mp4' in href:
#                     video_link = href
#                     break
#                 elif not fallback_link:  # Store the first link as fallback
#                     fallback_link = href

#         # Prioritize video links, fallback to the first link if no video
#         return video_link or fallback_link

#     except Exception as e:
#         print(f"Error in lazy_get_download_url: {e}")
#         return None

async def lazy_get_download_url(link):
    # Make request to website 
    post_request = requests.post('https://www.expertsphp.com/download.php', data={'url': link})

    # Get content from post request
    request_content = post_request.content
    str_request_content = str(request_content, 'utf-8')
    download_url = pq(str_request_content)('table.table-condensed')('tbody')('td')('a').attr('href')
    print(download_url)
    return download_url

async def download_pintrest_vid(client, message, url):
    try:
        full_url = expand_url(url)
        # print(f"expand url => {full_url}")
        if full_url:
            ms = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ ᴛᴏ download...</i>")
            down = await lazy_get_download_url(full_url)
            # print(f"Final link => {down}")
            if '.mp4' in (down):
                await ms.edit_text("⚡Found video - Sending you video...")
                await message.reply_video(down)
            elif '.gif' in (down):
                await ms.edit_text("⚡Found GIF - Sending you GIF...")
                await message.reply_animation(down)
            else:
                await ms.edit_text("⚡Found Photo - Sending you photo...")
                await message.reply_photo(down)
            await ms.delete()
            lazydeveloper = await client.send_message(chat_id=message.chat.id, text=f"❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ...")
            await asyncio.sleep(100)
            await lazydeveloper.delete()
        else:
            await message.reply("Send me the correct link !")
    except FileNotFoundError:
        return

# Function to get download url
def get_download_url(link):
    # Make request to website
    post_request = requests.post(
        'https://www.expertsphp.com/download.php', data={'url': link})

    # Get content from post request
    request_content = post_request.content
    str_request_content = str(request_content, 'utf-8')
    return pq(str_request_content)('table.table-condensed')('tbody')('td')(
        'a'
    ).attr('href')

# Function to download video
def download_video(url):
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    video_to_download = request.urlopen(url).read()

    with open(TMP_DOWNLOAD_DIRECTORY + 'pinterest_video.mp4', 'wb') as video_stream:
        video_stream.write(video_to_download)
    return TMP_DOWNLOAD_DIRECTORY + 'pinterest_video.mp4'

# Function to download image
def download_image(url):
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    image_to_download = request.urlopen(url).read()
    with open(TMP_DOWNLOAD_DIRECTORY + 'pinterest_iamge.jpg', 'wb') as photo_stream:
        photo_stream.write(image_to_download)
    return TMP_DOWNLOAD_DIRECTORY + 'pinterest_iamge.jpg'



# Command to make an announcement to users using the bot
# credit  https://github.com/kamronbek29/pinterst_downloader/blob/master/pinterest-downloader.py thanks for create this repository!
# async def lazy_get_download_url(link):
#     # Make request to website 
#     post_request = requests.post('https://www.expertsphp.com/download.php', data={'url': link})

#     # Get content from post request
#     request_content = post_request.content
#     str_request_content = str(request_content, 'utf-8')
#     download_url = pq(str_request_content)('table.table-condensed')('tbody')('td')('a').attr('href')
#     print(download_url)
#     return download_url

# @bot.on(events.NewMessage(pattern="/pimg ?(.*)", func=lambda e: e.is_private))
# async def img(event):
#     await log_yolla(event)
#     j = await event.client(
#         GetFullUserRequest(
#             event.chat_id
#         )
#     )
#     mesaj = f"Gönderen [{j.user.first_name}](tg://user?id={event.chat_id})\nMesaj: {event.message.message}"
#     await bot.send_message(
#         "By_Azade",
#         mesaj
#     )
#     markup = bot.build_reply_markup([Button.url(
#         text='📍 Channel', url="t.me/rioprojects"),
#         Button.url(
#         text='👤 Rio', url="t.me/fckualot")
#     ])
#     url = event.pattern_match.group(1)
#     if url:
#         x = await event.reply("`İşlem yapılıyor lütfen bekleyiniz...`\n\nProcessing please wait ...")
#         get_url = get_download_url(url)
#         j = download_image(get_url)

#         if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
#             os.makedirs(TMP_DOWNLOAD_DIRECTORY)
#         c_time = time.time()
#         await event.client.send_file(
#             event.chat_id,
#             j,
#             caption="**@pinterestriobot** tarafından indirilmiştir\n\nDownloaded by **@pinterestriobot**",
#             force_document=False,
#             allow_cache=False,
#             reply_to=event.message.id,
#             buttons=markup,
#             progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
#                 progress(d, t, event, c_time, "yükleniyor...")
#             )
#         )
#         await event.delete()
#         await x.delete()
#         os.remove(TMP_DOWNLOAD_DIRECTORY + 'pinterest_iamge.jpg')
#     else:
#         await event.reply("**bana komutla beraber link gönder.**\n\n`send me the link with the command.`")

# async def take_screen_shot(video_file, output_directory, ttl):
#     # https://stackoverflow.com/a/13891070/4723940
#     out_put_file_name = output_directory + \
#         "/" + str(time.time()) + ".jpg"
#     file_genertor_command = [
#         "ffmpeg",
#         "-ss",
#         str(ttl),
#         "-i",
#         video_file,
#         "-vframes",
#         "1",
#         out_put_file_name
#     ]
#     # width = "90"
#     # t_response, e_response = await run_command(file_genertor_command)
#     if os.path.lexists(out_put_file_name):
#         return out_put_file_name
#     # logger.info(e_response)
#     # logger.info(t_response)
#     return None


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    return None


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def progress_for_pyrogram(current, total, ud_type, message, start):

    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]))

        tmp = progress + Script.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text="{}\n\n{}".format(ud_type, tmp),               
                
            )
        except:
            pass



