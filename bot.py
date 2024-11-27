from pyrogram import Client 
from config import API_ID, API_HASH, BOT_TOKEN, LOGGER, PORT
from aiohttp import web
from route import web_server
import pyromod.listen
import os

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="savexbot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins=dict(root="plugins"),
            sleep_threshold=15,
            max_concurrent_transmissions=5,
        )
        self.LOGGER = LOGGER
    # the one and only - LazyDeveloperr ❤
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username 
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"       
        await web.TCPSite(app, bind_address, PORT).start()
        self.LOGGER(__name__).info(f"Bot Running..!\n\n❤ with love  \n ıllıllı🚀🌟 L͙a͙z͙y͙D͙e͙v͙e͙l͙o͙p͙e͙r͙r͙ 🌟🚀ıllıllı")
     
        print(f"{me.first_name} 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 ⚡️⚡️⚡️")
      

    async def stop(self, *args):
        await super().stop()      
        print("Bot Stopped")
       

bot=Bot()
bot.run()
