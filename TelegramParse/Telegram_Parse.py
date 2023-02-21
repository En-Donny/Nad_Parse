from xmlrpc.client import DateTime
from telethon.sync import TelegramClient
import time
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import csv
import asyncio
import aiohttp



# with TelegramClient(phone, api_id, api_hash) as client:
#     for message in client.iter_messages(-1001878338439):
#         print(message.sender_id, ':', message.text)


# print("Сохраняем данные в файл...")
# with open("members.csv", "w", encoding="UTF-8") as f:
#     writer = csv.writer(f, delimiter=",", lineterminator="\n")
#     writer.writerow(["username", "name", "group"])
#     for user in all_participants:
#         if user.username:
#             username = user.username
#         else:
#             username = ""
#         if user.first_name:
#             first_name = user.first_name
#         else:
#             first_name = ""
#         if user.last_name:
#             last_name = user.last_name
#         else:
#             last_name = ""
#         name = (first_name + ' ' + last_name).strip()
#         writer.writerow([username, name, target_group.title])
# print("Парсинг участников группы успешно выполнен.")


async def main_parse_telegram(client, list_of_words):
    """
    Get all groups of client
    """
    chats = []
    last_date = None
    chunk_size = 200
    groups = []
    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)
    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except:
            continue

    """Get all chat history from telegram chats of all groups"""
    limit = 100
    all_messages = set()
    total_messages = 0
    total_count_limit = 0
    i = 0
    group_list = []
    with open("TelegramParse/groups_file.txt", "r") as f:
        for line in f:
            line_lst = line.replace("\n", "").split()
            group_list.append([line_lst[0], int(line_lst[1])])

    group_names_list = [group_list[i][0] for i in range(len(group_list))]
    while True:
        for g in groups:
            if g.title in group_names_list:
                iter_of_current_group = group_names_list.index(g.title)
                offset_id = 0
                while True:
                    history = await client(GetHistoryRequest(
                        peer=g,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=limit,
                        max_id=0,
                        min_id=group_list[iter_of_current_group][1],
                        hash=0
                    ))
                    if not history.messages:
                        break
                    messages = history.messages
                    messages = messages[::-1]
                    for message in messages:
                        if not message.message:
                            continue
                        text_message = message.message
                        list_of_words_mess = text_message.split()
                        for word in list_of_words_mess:
                            if word.lower() in list_of_words:
                                user_sended = await client.get_entity(message.from_id)
                                if not user_sended.last_name:
                                    tup_for_str = (
                                    text_message, g.title, (user_sended.username, user_sended.first_name), message.date)
                                    if tup_for_str not in all_messages:
                                        with open("TelegramParse/chats.csv", "a", encoding="UTF-8") as f:
                                            writer = csv.writer(f, delimiter=",", lineterminator="\n")
                                            writer.writerow([text_message, g.title, user_sended.username,
                                                             user_sended.first_name, message.date])
                                        all_messages.add(tup_for_str)
                                else:
                                    tup_for_str = (
                                        text_message, g.title, (user_sended.username, user_sended.first_name),
                                        message.date)
                                    if tup_for_str not in all_messages:
                                        with open("TelegramParse/chats.csv", "a", encoding="UTF-8") as f:
                                            writer = csv.writer(f, delimiter=",", lineterminator="\n")
                                            writer.writerow([text_message, g.title,
                                                      user_sended.username, user_sended.first_name,
                                                          user_sended.last_name, message.date])
                                        all_messages.add(tup_for_str)
                                break
                    offset_id = messages[0].id
                    group_list[iter_of_current_group][1] = messages[-1].id
                    if total_count_limit != 0 and total_messages >= total_count_limit:
                        break
        with open("TelegramParse/groups_file.txt", "w") as f:
            for g in group_list:
                f.write(f"{g[0]} {str(g[1])}\n")
        # print("Сохраняем данные в файл...")
        # with open("TelegramParse/chats.csv", "a", encoding="UTF-8") as f:
        #     writer = csv.writer(f, delimiter=",", lineterminator="\n")
        #     for message in all_messages:
        #         writer.writerow([message[0], message[1], f'{message[2][0]} ({" ".join(message[2][1:])})', message[3]])
        # print('Парсинг сообщений групп успешно выполнен.')

        i += 1
        await asyncio.sleep(15)
        print("Итерация закончилась!")


