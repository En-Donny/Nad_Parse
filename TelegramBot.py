# import time
# import logging
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
import emoji
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import aiohttp
from TelegramParse.Telegram_Parse import main_parse_telegram
from WhatsAPPParse.WhatsAPP_Parse import main_parser_whatsapp
from telethon.sync import TelegramClient
from whatsapp_api_client_python import API
from aiogram.types import InputFile
# import os
import pandas as pd


# def is_non_zero_file(fpath):
#     return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


loopl = asyncio.get_event_loop()
session: aiohttp.ClientSession

TOKEN = '6075847320:AAHVRFnQU60nS0YJ1CETBJcIR52buyXAJPs'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

# блок данных для Телеграма
# api_id = 22866821
# api_hash = "4dcc3fa36638e13044afad6c538e35d4"
# name_session = "new_app"
# client = TelegramClient(name_session, api_id, api_hash)
# client.start()
# +79938921078


# api_id = 28384498
# api_hash = "cf3d04fa237a90699c4645852fb81e76"
# name_session = "new_app"
# client = TelegramClient(name_session, api_id, api_hash)
# client.start(password="chin3228")


# # блок данных для WhatsApp (Надежда)
# ID_INSTANCE = "1101797078"
# API_TOKEN_INSTANCE = "7c2055d423de4f8aa41be4e313cb6037ffb14928c3d84c7895"
# greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
# curr_account_name = greenAPI.account.getSettings().data["wid"][:-5]

# блок данных для WhatsApp (Моё)
ID_INSTANCE = "1101794868"
API_TOKEN_INSTANCE = "fb83b702cf0e45d9b25e781b0fe5daa10488ab88e744439b8d"
greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
curr_account_name = greenAPI.account.getSettings().data["wid"][:-5]

telegram_groups = []
whatsapp_groups = []
all_words = []


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message, state: FSMContext):
    global user_id
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    msg = f'''Привет, {user_full_name}!
Это главное меню! Выбирай, что хочешь{emoji.emojize(":backhand_index_pointing_down:")}'''
    # logging.info(f'{user_id} {user_full_name} {time.asctime()}')

    key1 = types.InlineKeyboardButton(text=f'Запустить парсер', callback_data='parse')
    key2 = types.InlineKeyboardButton(text=f'Изменить список групп для Telegram', callback_data='edit_tele_group')
    key3 = types.InlineKeyboardButton(text=f'Изменить список групп для WhatsApp', callback_data='edit_whats_group')
    key4 = types.InlineKeyboardButton(text=f'Изменить список слов для парсинга', callback_data='edit_words_list')
    key5 = types.InlineKeyboardButton(text=f'Остановить парсер', callback_data='stopping_parse')
    key6 = types.InlineKeyboardButton(text=f'Получить результаты парсинга', callback_data='get_files')

    keyboard_main = types.InlineKeyboardMarkup(row_width=1).add(key1, key2, key3, key4, key5, key6)
    await bot.send_message(user_id, msg, reply_markup=keyboard_main)
    await state.set_state("Nothing")


current_keyboard_markup: types.InlineKeyboardMarkup

# Данное меню используется много раз, сохраним его заранее
key1 = types.InlineKeyboardButton(text=f'Запустить парсер', callback_data='parse')
key2 = types.InlineKeyboardButton(text=f'Изменить список групп для Telegram', callback_data='edit_tele_group')
key3 = types.InlineKeyboardButton(text=f'Изменить список групп для WhatsApp', callback_data='edit_whats_group')
key4 = types.InlineKeyboardButton(text=f'Изменить список слов для парсинга', callback_data='edit_words_list')
key5 = types.InlineKeyboardButton(text=f'Остановить парсер', callback_data='stopping_parse')
key6 = types.InlineKeyboardButton(text=f'Получить результаты парсинга', callback_data='get_files')
root_menu = types.InlineKeyboardMarkup(row_width=1).add(key1, key2, key3, key4, key5, key6)

current_text, current_id_mess = "", 0
current_image_list = []
current_label_for_pay: str
used_labels = []


@dp.callback_query_handler(
    text=['parse', 'edit_tele_group', 'root_menu', 'edit_whats_group', 'edit_words_list', 'working_parse',
          'stopping_parse', 'add_tele_group', 'del_tele_group', 'add_whats_group', 'del_whats_group',
          'edit_whats_group', 'edit_words_list', 'add_parse_word', 'del_parse_word', 'get_files'],
    state=["Nothing", "send_image", 'send_text', 'on_working'])
async def callback_telegram_bot(call: types.CallbackQuery, state: FSMContext):
    global user_id, current_text, current_id_mess, current_bill, bill, used_labels, current_label_for_pay, channel_ids
    command = call.data
    user_id = call.from_user.id
    got_status = await state.get_state()
    data_in_status = await state.get_data()
    if got_status == "send_image" or got_status == "send_text" or got_status == "on_editing":
        await state.set_state("Nothing")

    if command == 'root_menu':
        msg = f"""Вы в главном меню. Выберите действие {emoji.emojize(":backhand_index_pointing_down:")}"""
        await bot.send_message(user_id, msg, reply_markup=root_menu)

    elif command == 'parse':
        await parse_main(call, state)

    elif command == 'working_parse':
        key1 = types.InlineKeyboardButton(text=f'Остановить парсер', callback_data='stopping_parse')
        keyboard_channels = types.InlineKeyboardMarkup(row_width=1).add(key1)

        msg = f"""Парсер был успешно запущен {emoji.emojize(":winking_face:")}. 
Ты можешь остановить его для изменения данных для парсинга."""
        await bot.send_message(user_id, msg, reply_markup=keyboard_channels)

    elif command == 'stopping_parse':
        if got_status == "on_working":
            await state.set_state("Nothing")
            for task in asyncio.all_tasks():
                if "main_parse_telegram" in str(task.get_coro()) or "main_parser_whatsapp" in str(task.get_coro()):
                    task.cancel()
            msg = f'''Парсер был успешно остановлен'''
            await bot.send_message(user_id, msg, reply_markup=root_menu)

    elif command == 'edit_tele_group':
        file_str = ""
        global telegram_groups
        with open("TelegramParse/groups_file.txt", "r", encoding="utf-8") as f:
            telegram_groups = f.readlines()
        if not telegram_groups:
            key1 = types.InlineKeyboardButton(text=f'Добавить имя группы', callback_data='add_tele_group')
            key2 = types.InlineKeyboardButton(text=f'Назад', callback_data='root_menu')
            keyboard_add_group = types.InlineKeyboardMarkup(row_width=1).add(key1, key2)
            msg = f"""Список групп Telegram пока пуст. Добавьте в список группы для парсинга."""
            await bot.send_message(user_id, msg, reply_markup=keyboard_add_group)
        else:
            for j, line in enumerate(telegram_groups):
                group = line.replace('\n', '').split()[0]
                file_str += f"{j+1}: {group}\n"

            key1 = types.InlineKeyboardButton(text=f'Добавить имя группы', callback_data='add_tele_group')
            key2 = types.InlineKeyboardButton(text=f'Удалить группу из списка', callback_data='del_tele_group')
            key3 = types.InlineKeyboardButton(text=f'Назад', callback_data='root_menu')
            keyboard_tele_menu = types.InlineKeyboardMarkup(row_width=1).add(key1, key2, key3)
            msg = f"""Текущий список групп выглядит так:"""
            await bot.send_message(user_id, msg)
            msg = file_str
            await bot.send_message(user_id, msg)
            msg = f"""Выберите действие со списком групп"""
            await bot.send_message(user_id, msg, reply_markup=keyboard_tele_menu)

    elif command == 'add_tele_group':
        key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_tele_group')
        keyboard_send_image = types.InlineKeyboardMarkup(row_width=1).add(key1)
        msg = f'''Введите название группы Telegram, которую
хотите добавить в список парсинга'''
        await bot.send_message(user_id, msg, reply_markup=keyboard_send_image)
        await state.set_state("send_text")
        await state.update_data(messanger="telegram")

    elif command == 'del_tele_group':
        key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_tele_group')
        keyboard_send_image = types.InlineKeyboardMarkup(row_width=1).add(key1)
        msg = f'''Введите номер группы из списка, которую Вы хотите удалить'''
        await bot.send_message(user_id, msg, reply_markup=keyboard_send_image)
        await state.set_state("send_number")
        await state.update_data(messanger="telegram")

    elif command == 'edit_whats_group':
        file_str = ""
        global whatsapp_groups
        with open("WhatsAPPParse/groups_file.txt", "r", encoding="utf-8") as f:
            whatsapp_groups = f.readlines()
        if not whatsapp_groups:
            key1 = types.InlineKeyboardButton(text=f'Добавить имя группы', callback_data='add_whats_group')
            key2 = types.InlineKeyboardButton(text=f'Назад', callback_data='root_menu')
            keyboard_add_group = types.InlineKeyboardMarkup(row_width=1).add(key1, key2)
            msg = f"""Список групп WhatsApp пока пуст. Добавьте в список группы для парсинга."""
            await bot.send_message(user_id, msg, reply_markup=keyboard_add_group)
        else:
            for j, line in enumerate(whatsapp_groups):
                group = line.replace('\n', '').split()[0]
                file_str += f"{j+1}: {group}\n"

            key1 = types.InlineKeyboardButton(text=f'Добавить имя группы', callback_data='add_whats_group')
            key2 = types.InlineKeyboardButton(text=f'Удалить группу из списка', callback_data='del_whats_group')
            key3 = types.InlineKeyboardButton(text=f'Назад', callback_data='root_menu')
            keyboard_tele_menu = types.InlineKeyboardMarkup(row_width=1).add(key1, key2, key3)
            msg = f"""Текущий список групп выглядит так:"""
            await bot.send_message(user_id, msg)
            msg = file_str
            await bot.send_message(user_id, msg)
            msg = f"""Выберите действие со списком групп"""
            await bot.send_message(user_id, msg, reply_markup=keyboard_tele_menu)

    elif command == 'add_whats_group':
        key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_whats_group')
        keyboard_send_image = types.InlineKeyboardMarkup(row_width=1).add(key1)
        msg = f'''Введите название группы WhatsAPP, которую
хотите добавить в список парсинга'''
        await bot.send_message(user_id, msg, reply_markup=keyboard_send_image)
        await state.set_state("send_text")
        await state.update_data(messanger="whatsapp")

    elif command == 'del_whats_group':
        key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_whats_group')
        keyboard_send_image = types.InlineKeyboardMarkup(row_width=1).add(key1)
        msg = f'''Введите номер группы из списка, которую Вы хотите удалить'''
        await bot.send_message(user_id, msg, reply_markup=keyboard_send_image)
        await state.set_state("send_number")
        await state.update_data(messanger="whatsapp")

    elif command == 'edit_words_list':
        file_str = ""
        global all_words
        with open("words_for_parse.txt", "r", encoding="utf-8") as f:
            all_words = f.readlines()
        if not all_words:
            key1 = types.InlineKeyboardButton(text=f'Добавить слово', callback_data='add_parse_word')
            key2 = types.InlineKeyboardButton(text=f'Назад', callback_data='root_menu')
            keyboard_add_group = types.InlineKeyboardMarkup(row_width=1).add(key1, key2)
            msg = f"""Список слов для парсинга пока пуст. Добавьте слова для парсинга в список."""
            await bot.send_message(user_id, msg, reply_markup=keyboard_add_group)
        else:
            for j, line in enumerate(all_words):
                word = line.replace('\n', '')
                file_str += f"{j + 1}: {word}\n"
            key1 = types.InlineKeyboardButton(text=f'Добавить слово', callback_data='add_parse_word')
            key2 = types.InlineKeyboardButton(text=f'Удалить слово', callback_data='del_parse_word')
            key3 = types.InlineKeyboardButton(text=f'Назад', callback_data='root_menu')
            keyboard_tele_menu = types.InlineKeyboardMarkup(row_width=1).add(key1, key2, key3)
            msg = f"""Текущий список слов парсинга выглядит так:"""
            await bot.send_message(user_id, msg)
            msg = file_str
            await bot.send_message(user_id, msg)
            msg = f"""Выберите действие со списком слов"""
            await bot.send_message(user_id, msg, reply_markup=keyboard_tele_menu)

    elif command == 'add_parse_word':
        key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_words_list')
        keyboard_send_image = types.InlineKeyboardMarkup(row_width=1).add(key1)
        msg = f'''Введите новое слово для парсинга'''
        await bot.send_message(user_id, msg, reply_markup=keyboard_send_image)
        await state.set_state("send_text")
        await state.update_data(messanger="for_words")

    elif command == 'del_parse_word':
        key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_words_list')
        keyboard_send_image = types.InlineKeyboardMarkup(row_width=1).add(key1)
        msg = f'''Введите номер слов из списка, которое Вы хотите удалить'''
        await bot.send_message(user_id, msg, reply_markup=keyboard_send_image)
        await state.set_state("send_number")
        await state.update_data(messanger="for_words")

    elif command == 'get_files':
        msg = f'''Вот результаты парсинга сообщений'''
        await bot.send_message(user_id, msg)
        with open("TelegramParse/chats.csv", "r", encoding="utf-8") as f:
            tele_doc = f.read()
        with open("WhatsAPPParse/chats.csv", "r", encoding="utf-8") as f:
            whats_doc = f.read()
        if tele_doc:
            df_tele = pd.read_csv("TelegramParse/chats.csv")
            df_tele.to_excel("chatsTelegram.xls", index=False)
            tele_parse = InputFile("chatsTelegram.xls")
            await bot.send_document(chat_id=user_id, document=tele_parse)
        else:
            await bot.send_message(user_id, "Файл для Telegram пока пуст")
        if whats_doc:
            df_whats = pd.read_csv("WhatsAPPParse/chats.csv")
            df_whats.to_excel("chatsWhatsApp.xls", index=False)
            whats_parse = InputFile("chatsWhatsApp.xls")
            await bot.send_document(chat_id=user_id, document=whats_parse)
        else:
            await bot.send_message(user_id, "Файл для WhatsApp пока пуст")
        await bot.send_message(user_id, text="Выберите действие из меню ниже", reply_markup=root_menu)


@dp.message_handler(state="send_text", content_types=types.ContentTypes.ANY)
async def get_add_something(message: types.Message, state: FSMContext):
    key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_tele_group')
    keyboard_send_tele = types.InlineKeyboardMarkup(row_width=1).add(key1)
    if message.text:
        new_call = types.CallbackQuery()
        await state.set_state("Nothing")
        text_mess = message.text
        new_call.from_user = message.from_user
        msg = ""
        async with state.proxy() as data:
            messanger = data.get("messanger")
        if messanger == "telegram":
            new_call.data = "edit_tele_group"
            msg = f'Группа {text_mess} была успешно добавлена в список'
            with open("TelegramParse/groups_file.txt", "a", encoding="utf-8") as f:
                f.write(f"{text_mess} {0}\n")
        elif messanger == "whatsapp":
            new_call.data = "edit_whats_group"
            msg = f'Группа {text_mess} была успешно добавлена в список'
            with open("WhatsAPPParse/groups_file.txt", "a", encoding="utf-8") as f:
                f.write(f"{text_mess} {0}\n")
        elif messanger == "for_words":
            new_call.data = "edit_words_list"
            msg = f'Слово {text_mess} было успешно добавлено в список'
            with open("words_for_parse.txt", "a", encoding="utf-8") as f:
                f.write(text_mess + "\n")
        await bot.send_message(message.from_user.id, msg)
        await callback_telegram_bot(call=new_call, state=state)
    else:
        msg = f'Вы ввели что-то не то. Повторите ввод названия группы.'
        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard_send_tele)


@dp.message_handler(state="send_number", content_types=types.ContentTypes.ANY)
async def get_add_something(message: types.Message, state: FSMContext):
    key1 = types.InlineKeyboardButton(text=f'Назад', callback_data='edit_tele_group')
    keyboard_send_tele = types.InlineKeyboardMarkup(row_width=1).add(key1)
    if message.text:
        new_call = types.CallbackQuery()
        new_call.from_user = message.from_user
        await state.set_state("Nothing")
        text_mess = message.text
        group_name = ""
        if text_mess.isdigit():
            async with state.proxy() as data:
                messanger = data.get("messanger")
            if messanger == "telegram":
                new_call.data = "edit_tele_group"
                group_name = telegram_groups[int(text_mess) - 1].split()[0]
                with open("TelegramParse/groups_file.txt", "w", encoding="utf-8") as f:
                    del telegram_groups[int(text_mess) - 1]
                    f.write(f"{''.join(telegram_groups)}")
                    msg = f'Группа {group_name} была успешно удалена из списка'
            elif messanger == "whatsapp":
                new_call.data = "edit_whats_group"
                group_name = whatsapp_groups[int(text_mess) - 1].split()[0]
                with open("WhatsAPPParse/groups_file.txt", "w", encoding="utf-8") as f:
                    del whatsapp_groups[int(text_mess) - 1]
                    f.write(f"{''.join(whatsapp_groups)}")
                    msg = f'Группа {group_name} была успешно удалена из списка'
            elif messanger == "for_words":
                new_call.data = "edit_words_list"
                word_name = all_words[int(text_mess) - 1].replace("\n", "")
                with open("words_for_parse.txt", "w", encoding="utf-8") as f:
                    del all_words[int(text_mess) - 1]
                    f.write(f"{''.join(all_words)}")
                    msg = f'Слово {word_name} было успешно удалено из списка'
            await bot.send_message(message.from_user.id, msg)
            await callback_telegram_bot(call=new_call, state=state)
        else:
            msg = f'Вы ввели не число. Повторите ввод номера.'
            await bot.send_message(message.from_user.id, msg, reply_markup=keyboard_send_tele)
    else:
        msg = f'Вы ввели что-то не то. Повторите ввод номера.'
        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard_send_tele)


async def parse_main(call, state):
    new_call = call
    new_call.data = "working_parse"
    await state.set_state("on_working")
    with open("words_for_parse.txt", "r", encoding="utf-8") as f:
        list_of_words = [word.replace("\n", "") for word in f]
    tasks_lst = [
        # loopl.create_task(main_parse_telegram(client, list_of_words)),
                 loopl.create_task(main_parser_whatsapp(greenAPI, curr_account_name, list_of_words)),
                 loopl.create_task(callback_telegram_bot(call=new_call, state=state))]
    loopl.run_until_complete(asyncio.wait(tasks_lst))
    # loopl.run_until_complete(new_parse())


if __name__ == "__main__":
    executor.start_polling(dp)
