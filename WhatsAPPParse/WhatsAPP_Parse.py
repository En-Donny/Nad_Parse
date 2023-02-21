from whatsapp_api_client_python import API
from datetime import datetime
import csv
import time
import asyncio
import aiohttp


# # блок данных для WhatsApp
# ID_INSTANCE = "1101792531"
# API_TOKEN_INSTANCE = "eb938699e4f247f78be65e6c76c85abe0684ec79300e4fc09b"
# greenAPI = API.GreenApi(ID_INSTANCE, API_TOKEN_INSTANCE)
# curr_account_name = greenAPI.account.getSettings().data["wid"][:-5]


async def main_parser_whatsapp(greenAPI, curr_account_name, list_of_words):
    """Getting all names and latest time of parsing for each group"""
    group_list = []
    with open("WhatsAPPParse/groups_file.txt", "r", encoding="utf-8") as f:
        for line in f:
            line_lst = line.replace("\n", "").split()
            group_list.append([line_lst[0], int(line_lst[1])])
    group_names_list = [group_list[i][0] for i in range(len(group_list))]

    number_of_mess = 100
    all_chats = greenAPI.serviceMethods.getContacts(chatId=None).data
    all_chats = list(filter(lambda x: x["type"] == 'group', all_chats))
    all_messages = set()
    i = 0
    while True:
        for chat in all_chats:
            group_title = chat["name"]
            if group_title in group_names_list:
                iter_of_current_group = group_names_list.index(group_title)
                all_messages_from_chat_data = greenAPI.journals.getChatHistory(chat["id"], number_of_mess)
                all_messages_from_chat = all_messages_from_chat_data.data
                if all_messages_from_chat:
                    all_messages_from_chat = all_messages_from_chat[::-1]
                    last_sended_time = int(all_messages_from_chat[-1]["timestamp"])
                    for mess in all_messages_from_chat:
                        if int(mess["timestamp"]) > group_list[iter_of_current_group][1]:
                            if mess["type"] == "outgoing":
                                user = curr_account_name
                            else:
                                user = mess["senderId"][:-5]
                            text_message = mess["textMessage"]
                            list_of_words_mess = text_message.split()
                            for word in list_of_words_mess:
                                if word.lower() in list_of_words:
                                    tup_for_str = (text_message, group_title, f'"{user}"',
                                                         datetime.utcfromtimestamp(int(mess["timestamp"])).strftime('%Y-%m-%d %H:%M:%S'))
                                    if tup_for_str not in all_messages:
                                        with open("WhatsAPPParse/chats.csv", "a", encoding="UTF-8") as f:
                                            writer = csv.writer(f, delimiter=",", lineterminator="\n")
                                            writer.writerow([text_message, group_title, f'"{user}"',
                                                         datetime.utcfromtimestamp(int(mess["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')])
                                        all_messages.add(tup_for_str)
                                    break
                    group_list[iter_of_current_group][1] = last_sended_time
        with open("WhatsAPPParse/groups_file.txt", "w", encoding="utf-8") as f:
            for g in group_list:
                f.write(f"{g[0]} {str(g[1])}\n")

        i += 1
        # time.sleep(5)
        await asyncio.sleep(15)
        print("iter closed")
