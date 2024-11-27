
import contextlib
import json
import logging
import random
import re
import tempfile
import threading
import time
import traceback
from io import BytesIO
from typing import Any
import pathlib
import filetype



import psutil
import pyrogram.errors
import yt_dlp
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client, enums, filters, types
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.raw import functions
from pyrogram.raw import types as raw_types
from config import *
from youtubesearchpython import VideosSearch
import typing
from typing import Any
from plugins.lazyprogress import tqdm_progress
import ffmpeg
import uuid
import yt_dlp as ytdl

def remove_bash_color(text):
    return re.sub(r"\u001b|\[0;94m|\u001b\[0m|\[0;32m|\[0m|\[0;33m", "", text)


def download_hook(d: dict, bot_msg):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        if total > TG_PREMIUM_MAX_SIZE:
            raise Exception(f"There's no way to handle a file of {sizeof_fmt(total)}.")
        if total > TG_NORMAL_MAX_SIZE:
            msg = f"Your download file size {sizeof_fmt(total)} is too large for Telegram."
            # if PREMIUM_USER:
            #     raise FileTooBig(msg)
        else:
            raise Exception(msg)

        # percent = remove_bash_color(d.get("_percent_str", "N/A"))
        speed = remove_bash_color(d.get("_speed_str", "N/A"))
        eta = remove_bash_color(d.get("_eta_str", d.get("eta")))
        text = tqdm_progress("Downloading...", total, downloaded, speed, eta)
        # debounce in here
        edit_text(bot_msg, text)


async def get_metadata(video_path):
    width, height, duration = 1280, 720, 0
    try:
        video_streams = ffmpeg.probe(video_path, select_streams="v")
        for item in video_streams.get("streams", []):
            height = item["height"]
            width = item["width"]
        duration = int(float(video_streams["format"]["duration"]))
    except Exception as e:
        logging.error(e)
    
    try:
        # Generate thumbnail at the middle of the video
        thumb = pathlib.Path(video_path).parent.joinpath(f"{uuid.uuid4().hex}-thumbnail.png").as_posix()
        ffmpeg.input(video_path, ss=duration / 2).filter("scale", width, -1).output(thumb, vframes=1).run()
    except ffmpeg._run.Error:
        thumb = None

    return dict(height=height, width=width, duration=duration, thumb=thumb)

def sizeof_fmt(num: int, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)

def shorten_url(url, CAPTION_URL_LENGTH_LIMIT):
    # Shortens a URL by cutting it to a specified length.
    shortened_url = url[: CAPTION_URL_LENGTH_LIMIT - 3] + "..."

    return shortened_url

def gen_cap(bm, url, video_path):
    # payment = Payment()
    chat_id = bm.chat.id
    user = bm.chat
    try:
        user_info = "@{}({})-{}".format(user.username or "N/A", user.first_name or "" + user.last_name or "", user.id)
    except Exception:
        user_info = ""

    if isinstance(video_path, pathlib.Path):
        meta = get_metadata(video_path)
        file_name = video_path.name
        file_size = sizeof_fmt(os.stat(video_path).st_size)
    else:
        file_name = getattr(video_path, "file_name", "")
        file_size = sizeof_fmt(getattr(video_path, "file_size", (2 << 2) + ((2 << 2) + 1) + (2 << 5)))
        meta = dict(
            width=getattr(video_path, "width", 0),
            height=getattr(video_path, "height", 0),
            duration=getattr(video_path, "duration", 0),
            thumb=getattr(video_path, "thumb", None),
        )
    # free = payment.get_free_token(chat_id)
    # pay = payment.get_pay_token(chat_id)
    
    remain = ".."

    if worker_name := os.getenv("WORKER_NAME"):
        worker = f"Downloaded by  {worker_name}"
    else:
        worker = ""
    # Shorten the URL if necessary
    try:
        if len(url) > CAPTION_URL_LENGTH_LIMIT:
            url_for_cap = shorten_url(url, CAPTION_URL_LENGTH_LIMIT)
        else:
            url_for_cap = url
    except Exception as e:
        logging.warning(f"Error shortening URL: {e}")
        url_for_cap = url
    
    cap = (
        f"{user_info}\n{file_name}\n\n{url_for_cap}\n\nInfo: {meta['width']}x{meta['height']} {file_size}\t"
        f"{meta['duration']}s\n{remain}\n{worker}\nwith ❤ @LazyDeveloperr"
    )

    offset = len(f"{user_info}\n`{file_name}`\n\n")

    entities = [
        # For the filename
        types.MessageEntity(
            type=enums.MessageEntityType.CODE,
            offset=len(f"{user_info}\n"),
            length=len(file_name)
        ),
        # For the URL
        types.MessageEntity(
            type=enums.MessageEntityType.URL,
            offset=offset,
            length=len(url_for_cap)
        )
    ]

    return cap, entities, meta

def generate_input_media(file_paths: list, cap: str, entities: list) -> list:
    input_media = []
    for path in file_paths:
        mime = filetype.guess_mime(path)
        if "video" in mime:
            input_media.append(pyrogram.types.InputMediaVideo(media=path))
        elif "image" in mime:
            input_media.append(pyrogram.types.InputMediaPhoto(media=path))
        elif "audio" in mime:
            input_media.append(pyrogram.types.InputMediaAudio(media=path))
        else:
            input_media.append(pyrogram.types.InputMediaDocument(media=path))

    # Add caption and entities of the first media
    input_media[0].caption = cap
    input_media[0].caption_entities = entities

    return input_media

def edit_text(bot_msg: types.Message, text: str):
    bot_msg.edit_text(text)

def upload_hook(current, total, bot_msg):
    text = tqdm_progress("Uploading...", total, current)
    edit_text(bot_msg, text)

def gen_video_markup():
    markup = types.InlineKeyboardMarkup(
        [
            [  # First row
                types.InlineKeyboardButton(  # Generates a callback query when pressed
                    "convert to audio", callback_data="convert"
                )
            ]
        ]
    )
    return markup

async def upload_processor(client: Client, bot_msg: types.Message, url: str, vp_or_fid: str | list):
    # redis = Redis()
    # raise pyrogram.errors.exceptions.FloodWait(13)
    # if is str, it's a file id; else it's a list of paths
    # payment = Payment()
    chat_id = bot_msg.chat.id
    markup = gen_video_markup()
    if isinstance(vp_or_fid, list) and len(vp_or_fid) > 1:
        # just generate the first for simplicity, send as media group(2-20)
        cap, entities, meta = gen_cap(bot_msg, url, vp_or_fid[0])
        res_msg: list["types.Message"] | Any = client.send_media_group(chat_id, generate_input_media(vp_or_fid, cap, entities))
        # T ODO no cache for now 
        return res_msg[0]
    elif isinstance(vp_or_fid, list) and len(vp_or_fid) == 1:
        # normal download, just contains one file in video_paths
        vp_or_fid = vp_or_fid[0]
        cap, entities, meta = gen_cap(bot_msg, url, vp_or_fid)
    else:
        # just a file id as string
        cap, entities, meta = gen_cap(bot_msg, url, vp_or_fid)

    logging.info("Sending as video")
    try:
        res_msg =await client.send_video(
            chat_id,
            vp_or_fid,
            supports_streaming=True,
            caption=cap,
            caption_entities=entities,
            progress=upload_hook,
            progress_args=(bot_msg,),
            reply_markup=markup,
            **meta,
        )
    except Exception:
        # try to send as annimation, photo
        try:
            logging.warning("Retry to send as animation")
            res_msg =await client.send_animation(
                chat_id,
                vp_or_fid,
                caption=cap,
                caption_entities=entities,
                progress=upload_hook,
                progress_args=(bot_msg,),
                reply_markup=markup,
                **meta,
            )
        except Exception:
            # this is likely a photo
            logging.warning("Retry to send as photo")
            res_msg =await client.send_photo(
                chat_id,
                vp_or_fid,
                caption=cap,
                caption_entities=entities,
                progress=upload_hook,
                progress_args=(bot_msg,),
            )

    if ARCHIVE_ID and isinstance(vp_or_fid, pathlib.Path):
        await client.forward_messages(bot_msg.chat.id, ARCHIVE_ID, res_msg.id)
    return res_msg


def ytdl_download(url: str, tempdir: str, bm, **kwargs) -> list:
    # payment = Payment()
    chat_id = bm.chat.id
    # hijack = kwargs.get("hijack")
    # output = pathlib.Path(tempdir, "%(title).70s.%(ext)s").as_posix()
    # OUT_DIRECTORY = f"{DOWNLOAD_LOCATION}/{chat_id}/{time.time()}"
    # if not os.path.isdir(OUT_DIRECTORY):
    #     os.makedirs(OUT_DIRECTORY)

    # ydl_opts = {
    #     "progress_hooks": [lambda d: download_hook(d, bm)],
    #     "outtmpl": output,
    #     "restrictfilenames": False,
    #     "quiet": True,
    # }

    # TEMP_DOWNLOAD_FOLDER = f"./downloads/{chat_id}/{time.time()}"
    # if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
    #     os.makedirs(TEMP_DOWNLOAD_FOLDER)
    # destination_folder = TEMP_DOWNLOAD_FOLDER 
    
    cookies_path = './cookies.txt'  # Path to the cookies.txt file

    ydl_opts = {
            # Use the video ID to avoid filename issues
            'outtmpl': f'{tempdir}/%(id)s.%(ext)s',
            'restrictfilenames': True,  # Limit special characters
            # Hook to show real-time progress
            "progress_hooks": [lambda d: download_hook(d, bm)],
            "quiet": True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            },
            'cookies': cookies_path,  # Directly using the cookies file
            'geo_bypass': True,        # Bypass geo-restrictions
            'nocheckcertificate': True,  # If SSL errors occur
            'verbose': True, 

        }
    
    if url.startswith("https://drive.google.com"):
        # Always use the `source` format for Google Drive URLs.
        formats = ["source"]
    else:
        # Use the default formats for other URLs.
        formats = [
            # webm , vp9 and av01 are not streamable on telegram, so we'll extract only mp4
            "bestvideo[ext=mp4][vcodec!*=av01][vcodec!*=vp09]+bestaudio[ext=m4a]/bestvideo+bestaudio",
            "bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[vcodec^=avc]/best",
            None,
        ]
    # This method will alter formats if necessary
    # adjust_formats(chat_id, url, formats, hijack)
    address = ["::", "0.0.0.0"] if IPv6 else [None]
    error = None
    video_paths = None
#     formats = [
#     "bestvideo[ext=mp4][height=1080]+bestaudio[ext=m4a]/best",
#     "bestvideo[ext=mp4][height=720]+bestaudio[ext=m4a]/best",
#     "bestvideo[ext=mp4][height=480]+bestaudio[ext=m4a]/best",
#     "bestaudio[ext=m4a]"
# ]
    for format_ in formats:
        ydl_opts["format"] = format_
        for addr in address:
            # IPv6 goes first in each format
            ydl_opts["source_address"] = addr
            try:
                logging.info("Downloading for %s with format %s", url, format_)
                with ytdl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                # video_paths = list(pathlib.Path(tempdir).glob("*"))
                video_paths = [os.path.join(tempdir, f) for f in os.listdir(tempdir)]
                break
            # except FileTooBig as e:
            #     raise e
            except Exception:
                error = traceback.format_exc()
                logging.error("Download failed for %s - %s, try another way", format_, url)
        if error is None:
            break

    if not video_paths:
        print("no path found")
        raise Exception(error)

    # convert format if necessary
    # settings = payment.get_user_settings(chat_id)
    # if settings[2] == "video" or isinstance(settings[2], MagicMock):
    #     # only convert if send type is video
    #     convert_to_mp4(video_paths, bm)
    # if settings[2] == "audio" or hijack == "bestaudio[ext=m4a]":
    #     convert_audio_format(video_paths, bm)
    # split_large_video(video_paths)
    return video_paths

def ytdl_normal_download(client: Client, bot_msg: types.Message | typing.Any, url: str):
    chat_id = bot_msg.chat.id
    # temp_dir = tempfile.TemporaryDirectory(prefix="ytdl-", dir=TMPFILE_PATH)
    # if not os.path.isdir(temp_dir):
    #     os.makedirs(temp_dir)
    TEMP_DOWNLOAD_FOLDER = f"./downloads/{chat_id}/{time.time()}"
    if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
        os.makedirs(TEMP_DOWNLOAD_FOLDER)
    temp_dir = TEMP_DOWNLOAD_FOLDER

    print(f"temp_dir : => {temp_dir}")
    client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    video_paths = ytdl_download(url, temp_dir, bot_msg)
    logging.info("Download complete.")
    client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_DOCUMENT)
    bot_msg.edit_text("Download complete. Sending now...")
    try:
        upload_processor(client, bot_msg, url, video_paths)
    except pyrogram.errors.Flood as e:
        logging.critical("FloodWait from Telegram: %s", e)
        client.send_message(
            chat_id,
            f"I'm being rate limited by Telegram. Your video will come after {e} seconds. Please wait patiently.",
        )
        client.send_message(bot_msg.chat.id, f"CRITICAL INFO: {e}")
        time.sleep(e.value)
        upload_processor(client, bot_msg, url, video_paths)

    bot_msg.edit_text("Download success!✅")

def ytdl_download_entrance(client: Client, bot_msg: types.Message, url: str, mode=None):
    # in Local node and forward mode, we pass client from main
    # in celery mode, we need to use our own client called bot
    try:
        ytdl_normal_download(client, bot_msg, url)
    except Exception as e:
        logging.error("Failed to download %s, error: %s", url, e)
        error_msg = traceback.format_exc().split("yt_dlp.utils.DownloadError: ERROR: ")
        if len(error_msg) > 1:
            bot_msg.edit_text(f"Download failed!❌\n\n`{error_msg[-1]}", disable_web_page_preview=True)
        else:
            bot_msg.edit_text(f"Download failed!❌\n\n`{traceback.format_exc()[-2000:]}`", disable_web_page_preview=True)

def link_checker(url: str) -> str:
    if url.startswith("https://www.instagram.com"):
        return ""
    ytdl = yt_dlp.YoutubeDL()

    if not PLAYLIST_SUPPORT and (
        re.findall(r"^https://www\.youtube\.com/channel/") or "list" in url
    ):
        return "Playlist or channel links are disabled."

    if not M3U8_SUPPORT and (re.findall(r"m3u8|\.m3u8|\.m3u$", url.lower())):
        return "m3u8 links are disabled."

    with contextlib.suppress(yt_dlp.utils.DownloadError):
        if ytdl.extract_info(url, download=False).get("live_status") == "is_live":
            return "Live stream links are disabled. Please download it after the stream ends."

def search_ytb(kw: str):
    videos_search = VideosSearch(kw, limit=10)
    text = ""
    results = videos_search.result()["result"]
    for item in results:
        title = item.get("title")
        link = item.get("link")
        index = results.index(item) + 1
        text += f"{index}. {title}\n{link}\n\n"
    return text

def extract_url_and_name(message_text):
    # Regular expression to match the URL
    url_pattern = r'(https?://[^\s]+)'
    # Regular expression to match the new name after '-n'
    name_pattern = r'-n\s+([^\s]+)'

    # Find the URL in the message_text
    url_match = re.search(url_pattern, message_text)
    url = url_match.group(0) if url_match else None

    # Find the new name in the message_text
    name_match = re.search(name_pattern, message_text)
    new_name = name_match.group(1) if name_match else None

    return url, new_name

async def download_from_youtube(client, message, url):
    urls = url
    logging.info("start %s", urls)
    chat_id = message.from_user.id
    await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    message_text = message.text
    url, new_name = extract_url_and_name(message_text)
    logging.info("ytdl start %s", url)
    if url is None or not re.findall(r"^https?://", url.lower()):
        await message.reply_text("Something wrong 🤔.\nCheck your URL and send me again.", quote=True)
        return

    bot_msg = await message.reply_text("Request received.", quote=True)
    ytdl_download_entrance(client, bot_msg, url)
    
    
    
    # for url in urls:
    #     # check url
    #     if not re.findall(r"^https?://", url.lower()):
    #         text = search_ytb(url)
    #         await message.reply_text(text, quote=True, disable_web_page_preview=True)
    #         return

    #     if text := link_checker(url):
    #         await message.reply_text(text, quote=True)
    #         return
        
    #     try:
    #         # raise pyrogram.errors.exceptions.FloodWait(10)
    #         bot_msg: types.Message | Any = await message.reply_text(text, quote=True)
    #     except pyrogram.errors.Flood as e:
    #         f = BytesIO()
    #         f.write(str(e).encode())
    #         f.write(b"Your job will be done soon. Just wait! Don't rush.")
    #         f.name = "Please don't flood me.txt"
    #         bot_msg = await message.reply_document(
    #             f, caption=f"Flood wait! Please wait {e} seconds...." f"Your job will start automatically", quote=True
    #         )
    #         f.close()
    #         await client.send_message(message.chat.id, f"Flood wait! 🙁 {e} seconds....")
    #         time.sleep(e.value)

    #     await client.send_chat_action(chat_id, enums.ChatAction.UPLOAD_VIDEO)
    #     bot_msg.chat = message.chat
    #     ytdl_download_entrance(client, bot_msg, url)









    
@Client.on_message(filters.command(["ytdl"]))
def ytdl_handler(client: Client, message: types.Message):
    # redis = Redis()
    chat_id = message.from_user.id
    client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    message_text = message.text
    url, new_name = extract_url_and_name(message_text)
    logging.info("ytdl start %s", url)
    if url is None or not re.findall(r"^https?://", url.lower()):
        message.reply_text("Something wrong 🤔.\nCheck your URL and send me again.", quote=True)
        return

    bot_msg =  message.reply_text("Request received.", quote=True)
    ytdl_download_entrance(client, bot_msg, url)
