import asyncio
import aiohttp
from aioconsole import ainput
from time import sleep
from TelegramParse.Telegram_Parse import main_parse_telegram
from WhatsAPPParse.WhatsAPP_Parse import main_parser_whatsapp
from telethon.sync import TelegramClient
from whatsapp_api_client_python import API
import multiprocessing
import signal


loopl = asyncio.get_event_loop()
session: aiohttp.ClientSession


# блок для Telegram
# api_id = 28384498
# api_hash = "cf3d04fa237a90699c4645852fb81e76"
# name_session = "new_app"
# client = TelegramClient(name_session, api_id, api_hash)
# client.start(password="chin3228")

# Ванины данные
api_id = 22288188
api_hash = "b08a61882df9d0aec4434fb88783257b"
name_session = "new_app"
client = TelegramClient(name_session, api_id, api_hash)
client.start()


# блок для WhatsApp
ID_INSTANCE = "1101792531"
API_TOKEN_INSTANCE = "eb938699e4f247f78be65e6c76c85abe0684ec79300e4fc09b"
greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
curr_account_name = greenAPI.account.getSettings().data["wid"][:-5]



# thread1 = multiprocessing.Process(target=main_loop)
# thread1.start()
# thread1.join()
# i = input()
# while True:
#     if int(i) == 2:
#         thread1.close()
#         break
#     i = input()

async def main():
    i = await ainput()
    while True:
        if int(i) == 2:
            loopl.stop()
            loopl.close()
            break
        i = await ainput()

        await asyncio.sleep(5)


async def new_parse():
    loopl.stop()

    global session
    session = aiohttp.ClientSession()
    async with session:
        tasks_lst = [loopl.create_task(main_parse_telegram(client)),
                     loopl.create_task(main_parser_whatsapp(greenAPI, curr_account_name)), loopl.create_task(main())]
        await asyncio.wait(tasks_lst)

if __name__ == "__main__":
    loopl.run_until_complete(new_parse())


