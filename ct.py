import asyncio
import configparser
import os

import googletrans
from environs import Env
from telethon import TelegramClient
from telethon import events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import UpdateShortMessage

if not os.path.isfile(r'data\.env'):
    os.startfile('inputer.py')
    os._exit(0)

commands_mas = ['/help', '/set_lang', '/pause', '/shutdown', '/format', '/mode', '/synch',
                '/clear', '/delete']  # массив с командами для бота
config_options = {"Settings": ["to_chat_id", "from_chat_id", "from_chat_username", "from_chat_first_name", "my_id",
                               "is_pause", "mode", "my_lang", "2_lang", "format"],
                  "MSG_DATA": ["msg_id_string"]}

# словарь с основными полями файла config.ini

translator = googletrans.Translator()
langs_mas = googletrans.LANGUAGES.keys()

file_config = r"data\config.ini"
file_bkp = r"data\debug_program\config.bkp"
config = configparser.ConfigParser()
config.read(file_config)

env = Env()
env.read_env(r"data\.env")
API_ID = int(env.int("api_id"))
API_HASH = env.str("api_hash")

client = TelegramClient(r'data\session\my_session', API_ID, API_HASH)


# функция сохранения данных в config.ini
def saver_config():
    with open(file_config, 'w+') as configfile:
        config.write(configfile)


# функция перевода сервисных сообщений на любой язык
def help_translate(msg, lang):
    lang = 'en' if lang == 'enn' else lang
    mas = msg.split("\"")
    text = ""
    while len(mas) != 0:
        if mas[0] == "":
            mas.pop(0)
            continue
        if "\t" in mas[0] or "\n" in mas[0] or "/" in mas[0]:
            text += mas[0] + ""
        elif "$$" in mas[0]:
            text += str(mas[0])[2:] + ""
        else:
            text += translator.translate(str(mas[0]), dest=lang).text + ""
        mas.pop(0)
    return text


# invalid command
@client.on(events.NewMessage(chats=(int(config["Settings"]["to_chat_id"])), incoming=False, pattern='/'))
async def invalid(event):
    msg_mas = event.text.split(' ')
    msg_id = event.id
    entity = event.chat_id
    if msg_mas[0] not in commands_mas:
        await client.delete_messages(message_ids=msg_id, entity=entity)


# delete connection
@client.on(events.NewMessage(chats=(int(config["Settings"]["to_chat_id"])), incoming=False, pattern='/delete'))
async def delete_connection(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    config.set('Settings', 'from_chat_id', str(config['Settings']['my_id']))
    saver_config()
    msg = help_translate(msg="Удаление соединения",
                         lang=config['Settings']['my_lang'])
    service_msg_delete = await client.send_message(message=msg, entity=entity)
    await asyncio.sleep(3)
    # удаляем сервисное сообщение
    await client.delete_messages(message_ids=service_msg_delete.id, entity=entity)


# clear
@client.on(events.NewMessage(incoming=False, pattern='/clear'))
async def clear(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    mas_ids = str(config['MSG_DATA']['msg_id_string']).split(';')
    mas_ids.pop(len(mas_ids) - 1)
    for i in mas_ids:
        await client.delete_messages(message_ids=int(i), entity=int(config['Settings']['to_chat_id']))
    config.set('MSG_DATA', 'msg_id_string', '')
    saver_config()


# help
@client.on(events.NewMessage(incoming=False, pattern='/help'))
async def help_funk(event):
    msg_mas = event.text.split(' ')
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    service_message = ''
    if len(msg_mas) == 1:
        msg_help = "\"\n/shutdown - \" полное отключение программы \"\n" \
                   "\" \"/pause - \"включить или выключить режим паузы\"\n" \
                   "\" \"/format - \" изменить формат вывода ника \"\n" \
                   "\" \"/set_lang my en - \" изменить своя язык на нужный \"\n" \
                   "\" \"/set_lang 2 en - \" изменить язык перевода \"\n" \
                   "\" \"/set_lang en-en - \" изменить языки \"\n" \
                   "\" \"/mode 0 - \" выбрать режим вывода перевода (0 - только перевод, " \
                   "1 - для себя перевод и оригинал, 2 - перевод и оригинал для обоих) \"\n" \
                   "\" \"/synch - \" настроить ручную синхронизацию, в случае, если автоматическая не сработала \"\n" \
                   "\" для автоматической синхронизации, перешлите в избранное сообщение от человека, с которым " \
                   "собираетесь общаться \"\n" \
                   "\"\"/clear - \"команда удаления последних отправленных сообщений \"\n" \
                   "\"\"/delete - \"удаление соединения (переадресации)"
        service_message_text = help_translate(
            msg="/help: " + msg_help, lang=config['Settings']['my_lang'])
        service_message = await client.send_message(message=service_message_text, entity=entity)

    elif msg_mas[1] == '/set_lang':
        langs_dict = googletrans.LANGUAGES
        text = ''
        for i in langs_dict:
            text += str(i) + " - " + str(langs_dict[i]) + "\n"
        text = text[:-2]
        service_message = await client.send_message(message=text, entity=entity)

    config.set('MSG_DATA', 'msg_id_string',
               config['MSG_DATA']["msg_id_string"] + str(service_message.id) + ";")
    saver_config()


# выключение бота
@client.on(events.NewMessage(incoming=False, pattern='/shutdown'))
async def shutdown(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    msg = help_translate(
        msg="Полное отключение бота, через 3 секунды", lang=config['Settings']['my_lang'])
    service_msg_shutdown = await client.send_message(message=msg, entity=entity)
    await asyncio.sleep(3)
    # удаляем сервисное сообщение
    await client.delete_messages(message_ids=service_msg_shutdown.id, entity=entity)
    os._exit(0)


# включение/выключение паузы
@client.on(events.NewMessage(incoming=False, pattern='/pause'))
async def pause(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    is_pause = bool(int((config["Settings"]["is_pause"])))
    if not is_pause:
        config.set("Settings", "is_pause", "1")
        msg = help_translate(msg="Остановка работы бота, для включения пропишите \" /pause\"",
                             lang=config['Settings']["my_lang"])
        service_msg_pause = await client.send_message(message=msg, entity=entity)
        await asyncio.sleep(3)
        # удаляем сервисное сообщение
        await client.delete_messages(message_ids=service_msg_pause.id, entity=entity)

    else:
        config.set("Settings", "is_pause", "0")
        msg = help_translate(msg="Включение бота, для остановки пропишите \" /pause\"",
                             lang=config['Settings']["my_lang"])
        service_msg_pause = await client.send_message(message=msg, entity=entity)
        await asyncio.sleep(3)
        # удаляем сервисное сообщение
        await client.delete_messages(message_ids=service_msg_pause.id, entity=entity)

    saver_config()


# изменение формата вывода ника
@client.on(events.NewMessage(incoming=False, pattern='/format'))
async def format_func(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    format_name = config['Settings']['format']
    if format_name == 'first_name':
        config.set("Settings", "format", "username")
        saver_config()
        msg = help_translate(
            msg="Изменение формата вывода имени на username", lang=config['Settings']["my_lang"])
        service_msg_format = await client.send_message(message=msg, entity=entity)
        await asyncio.sleep(3)
        # удаляем сервисное сообщение
        await client.delete_messages(message_ids=service_msg_format.id, entity=entity)

    else:
        config.set("Settings", "format", "first_name")
        saver_config()
        msg = help_translate(msg="Изменение формата вывода имени на first_name",
                             lang=config['Settings']["my_lang"])
        service_msg_format = await client.send_message(message=msg, entity=entity)
        await asyncio.sleep(3)
        # удаляем сервисное сообщение
        await client.delete_messages(message_ids=service_msg_format.id, entity=entity)


# переинициализация языков
@client.on(events.NewMessage(incoming=False, pattern='/set_lang'))
async def set_lang(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    text_msg_orig = event.text
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    if len(text_msg_orig.split(' ')) != 1:
        text_msg_orig_2 = text_msg_orig.split(' ')[1]
        if text_msg_orig_2 in ["my", "2"]:
            if text_msg_orig_2 == "my":
                if len(text_msg_orig.split(' ')) > 2:
                    first_lang = text_msg_orig.split(' ')[2]
                    if first_lang in langs_mas:
                        config.set('Settings', 'my_lang', first_lang)
                    else:
                        msg = help_translate(
                            msg='Вы указали неверный язык, полный список языков можно получить по команде \"'
                                ' /help set_lang \"',
                            lang=config['Settings']['my_lang'])
                        service_msg_set_lang = await client.send_message(message=msg, entity=entity)
                        await asyncio.sleep(3)
                        await client.delete_messages(message_ids=service_msg_set_lang.id,
                                                     entity=entity)  # удаляем сервисное сообщение
                else:
                    msg = help_translate(
                        msg='Вы не указали язык, полный список языков можно получить по команде \" /help set_lang \"',
                        lang=config['Settings']['my_lang'])
                    service_msg_set_lang = await client.send_message(message=msg, entity=entity)
                    await asyncio.sleep(3)
                    await client.delete_messages(message_ids=service_msg_set_lang.id,
                                                 entity=entity)  # удаляем сервисное сообщение

            if text_msg_orig_2 == "2":
                if len(text_msg_orig.split(' ')) > 2:
                    second_lang = text_msg_orig.split(' ')[2]
                    if second_lang in langs_mas:
                        config.set('Settings', '2_lang', second_lang)
                    else:
                        msg = help_translate(
                            msg='Вы указали неверный язык, полный список языков можно получить по команде \"'
                                ' /help set_lang \"',
                            lang=config['Settings']['my_lang'])
                        service_msg_set_lang = await client.send_message(message=msg, entity=entity)
                        await asyncio.sleep(3)
                        await client.delete_messages(message_ids=service_msg_set_lang.id,
                                                     entity=entity)  # удаляем сервисное сообщение
                else:
                    msg = help_translate(
                        msg='Вы не указали язык, полный список языков можно получить по команде \"'
                            ' /help set_lang \"',
                        lang=config['Settings']['my_lang'])
                    service_msg_set_lang = await client.send_message(message=msg, entity=entity)
                    await asyncio.sleep(3)
                    await client.delete_messages(message_ids=service_msg_set_lang.id,
                                                 entity=entity)  # удаляем сервисное сообщение
        else:
            if '-' in text_msg_orig_2:
                first_lang = text_msg_orig_2.split('-')[0]
                second_lang = text_msg_orig_2.split('-')[1]
                if first_lang in langs_mas and second_lang in langs_mas:
                    config.set('Settings', 'my_lang', first_lang)
                    config.set('Settings', '2_lang', second_lang)
                    saver_config()
                else:
                    msg = help_translate(
                        msg='Вы указали неверный язык, полный список языков можно получить по команде \"'
                            ' /help set_lang \"',
                        lang=config['Settings']['my_lang'])
                    service_msg_set_lang = await client.send_message(message=msg, entity=entity)
                    await asyncio.sleep(3)
                    await client.delete_messages(message_ids=service_msg_set_lang.id,
                                                 entity=entity)  # удаляем сервисное сообщение
    else:
        msg = help_translate(
            msg='Вы не указали параметры, полный список языков можно получить по команде \"'
                ' /help set_lang \"',
            lang=config['Settings']['my_lang'])
        service_msg_set_lang = await client.send_message(message=msg, entity=entity)
        await asyncio.sleep(3)
        await client.delete_messages(message_ids=service_msg_set_lang.id,
                                     entity=entity)  # удаляем сервисное сообщение

    saver_config()


# выбор режима работы (0 - только перевод, 1 - для юзера перевод и оригинал, 2 - для всех перевод и оригинал)
@client.on(events.NewMessage(incoming=False, pattern='/mode'))
async def mode(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    command = event.text.split(" ")
    if len(command) == 1:
        msg = help_translate(msg='Вы не указали режим работы, пример \" /mode 1\"',
                             lang=config['Settings']['my_lang'])
        service_msg_mode = await client.send_message(message=msg, entity=entity)
        await asyncio.sleep(3)
        # удаляем сервисное сообщение
        await client.delete_messages(message_ids=service_msg_mode.id, entity=entity)
    else:
        command = command[1]
        if command in ["0", "1", "2"]:
            config.set("Settings", "mode", command)
            saver_config()
            msg = help_translate(msg=f"Вы указали {command} режим работы",
                                 lang=config['Settings']['my_lang'])
            service_msg_mode = await client.send_message(message=msg, entity=entity)
            await asyncio.sleep(3)
            # удаляем сервисное сообщение
            await client.delete_messages(message_ids=service_msg_mode.id, entity=entity)
        else:
            msg = help_translate(msg="Вы указали неверный режим работы",
                                 lang=config['Settings']['my_lang'])
            service_msg_mode = await client.send_message(message=msg, entity=entity)
            await asyncio.sleep(3)
            # удаляем сервисное сообщение
            await client.delete_messages(message_ids=service_msg_mode.id, entity=entity)


# синхронизация второй способ
@client.on(events.NewMessage(incoming=False, pattern='/synch'))
async def synch(event):
    msg_id = event.id  # id сообщения
    entity = event.chat_id
    to_chat_id = int(config['Settings']['to_chat_id'])
    # удаляем сообщение с командой
    await client.delete_messages(message_ids=msg_id, entity=entity)
    if isinstance(event.original_update, UpdateShortMessage):
        if entity != int(config['Settings']['my_id']):
            from_user = await client.get_entity(entity)
            config.set("Settings", "from_chat_username",
                       str(from_user.username))
            config.set("Settings", "from_chat_first_name",
                       str(from_user.first_name))
            config.set("Settings", "from_chat_id", str(abs(entity)))
            msg = help_translate(msg="Включен режим синхронизации\"\n\"Сообщение удалится через 5 секунд",
                                 lang=config['Settings']["my_lang"])
            service_msg_synch = await client.send_message(message=msg, entity=to_chat_id)
            await asyncio.sleep(3)
            await client.delete_messages(message_ids=service_msg_synch.id, entity=to_chat_id)
            # удаляем сервисное сообщение
            saver_config()
        else:
            msg = help_translate(
                msg="Данную команду, надо прописать в чате с человеком, с которым вы хотите пообщаться",
                lang=config['Settings']["my_lang"])
            service_msg_synch = await client.send_message(message=msg, entity=to_chat_id)
            await asyncio.sleep(3)
            await client.delete_messages(message_ids=service_msg_synch.id, entity=to_chat_id)
            # удаляем сервисное сообщение

    else:
        msg = help_translate(msg="Данную команду, надо прописать в чате с человеком, а не в группе",
                             lang=config['Settings']["my_lang"])
        service_msg_synch = await client.send_message(message=msg, entity=to_chat_id)
        await asyncio.sleep(3)
        # удаляем сервисное сообщение
        await client.delete_messages(message_ids=service_msg_synch.id, entity=to_chat_id)


# Синхронизация первый способ
@client.on(events.NewMessage(incoming=True, from_users=(int(config["Settings"]["to_chat_id"]))))
async def init_from(event):
    to_chat_id = int(config["Settings"]["to_chat_id"])
    config.set('Settings', 'from_chat_id', str(to_chat_id))
    if event.peer_id.user_id == to_chat_id:
        text_msg_orig = event.text
        msg_id = event.id  # id сообщения
        # удаляем сообщение с командой
        await client.delete_messages(message_ids=msg_id, entity=to_chat_id)
        tranlate_text_info = translator.detect(text_msg_orig)
        config.set('Settings', '2_lang', tranlate_text_info.lang)
        config.set('MSG_DATA', 'msg_id_string', "")
        saver_config()
        from_chat_id = event.original_update.message.fwd_from.from_id  # id отправителя
        if from_chat_id:
            from_chat_id = event.original_update.message.fwd_from.from_id.user_id  # id отправителя
            if from_chat_id != to_chat_id:
                from_user = await client.get_entity(from_chat_id)
                config.set("Settings", "from_chat_username",
                           str(from_user.username))
                config.set("Settings", "from_chat_first_name",
                           str(from_user.first_name))
                config.set("Settings", "from_chat_id", str(abs(from_chat_id)))
                saver_config()
                print(
                    f'from_chat_id={from_chat_id}\t'
                    f'from_chat_username={from_user.username}\t'
                    f'from_chat_username={from_user.first_name}')

                msg = help_translate(msg="Включен режим синхронизации\"\n\"Сообщение удалится через 5 секунд",
                                     lang=config['Settings']['my_lang'])
                service_msg_synch_init = await client.send_message(
                    message=msg,
                    entity=to_chat_id)
                await asyncio.sleep(5)
                await client.delete_messages(message_ids=service_msg_synch_init.id,
                                             entity=to_chat_id)  # удаляем сервисное сообщение
                translate_text_info = translator.translate(
                    text_msg_orig, dest=config['Settings']['my_lang'])
                translate_text = translate_text_info.text
                # определение нужного формата вывода ника
                if str(from_user.username) == 'None' or config['Settings']['format'] == "first_name":
                    if str(from_user.first_name) == 'None':
                        username = translator.translate(
                            'Second user', dest=config['Settings']['my_lang']).text
                    else:
                        username = from_user.first_name
                else:
                    username = from_user.username
                if config['Settings']['mode'] != "0" and translate_text != text_msg_orig:
                    text_msg_new = f"{username}:\nTranslate:\n{translate_text}\nOrig:\n{text_msg_orig}"
                else:
                    text_msg_new = f"{username}:\n{translate_text}"
                msg_redirected = await client.send_message(message=text_msg_new,
                                                           entity=to_chat_id)
                msg_id = msg_redirected.id
                config.set('MSG_DATA', 'msg_id_string',
                           config['MSG_DATA']["msg_id_string"] + str(msg_id) + ";")
                saver_config()

            else:
                msg = help_translate(
                    msg="Надо переслать чужое сообщение, а не своё",
                    lang=config['Settings']['my_lang'])
                service_msg_synch_init = await client.send_message(
                    message=msg,
                    entity=to_chat_id)
                await asyncio.sleep(5)
                await client.delete_messages(message_ids=service_msg_synch_init.id,
                                             entity=to_chat_id)  # удаляем сервисное сообщение

        else:
            msg = help_translate(msg="Прости, не могу получить id, пожалуйста напиши\" /synch \"в чате с пользователем",
                                 lang=config['Settings']['my_lang'])
            service_msg_synch_init = await client.send_message(
                message=msg,
                entity=to_chat_id)
            await asyncio.sleep(5)
            await client.delete_messages(message_ids=service_msg_synch_init.id, entity=to_chat_id)
            # удаляем сервисное сообщение


# пересылка от 2 юзера
@client.on(events.NewMessage(incoming=True))
async def send_from_second_user(event):
    # проверка режима паузы
    if not bool(int(config["Settings"]["is_pause"])):
        # запрос данных из бд о id получателя
        from_chat_id = int(config["Settings"]["from_chat_id"])
        # запрос данных из бд о username получателя
        from_chat_username = config["Settings"]["from_chat_username"]
        # запрос данных из бд о first_name получателя
        from_chat_first_name = config["Settings"]["from_chat_first_name"]
        # проверка откуда пришло сообщение и пересланное ли оно
        if event.chat_id == from_chat_id and not event.fwd_from:
            # запрос данных из бд о id лички
            to_chat_id = int(config["Settings"]["to_chat_id"])
            text_msg_orig = event.text  # текст сообщения
            # проверка на наличие текста в сообщении (не картинка, не видео, не аудио и т.д.)
            if len(text_msg_orig) != 0:
                translate_text_info = translator.translate(
                    text_msg_orig, dest=config['Settings']['my_lang'])
                translate_text = translate_text_info.text
                # определение нужного формата вывода ника
                if str(from_chat_username) == 'None' or config['Settings']['format'] == "first_name":
                    if str(from_chat_first_name) == 'None':
                        username = translator.translate(
                            'Second user', dest=config['Settings']['my_lang']).text
                    else:
                        username = from_chat_first_name
                else:
                    username = from_chat_username
                if config['Settings']['mode'] != "0" and translate_text != text_msg_orig:
                    text_msg_new = f"{username}:\nTranslate:\n{translate_text}\nOrig:\n{text_msg_orig}"
                else:
                    text_msg_new = f"{username}:\n{translate_text}"
                msg_from_second_user = await client.send_message(message=text_msg_new,
                                                                 entity=to_chat_id)
                msg_id = msg_from_second_user.id
                config.set('MSG_DATA', 'msg_id_string',
                           config['MSG_DATA']["msg_id_string"] + str(msg_id) + ";")
                saver_config()


# пересылка от 1 юзера
@client.on(events.NewMessage(chats=(int(config["Settings"]["to_chat_id"])), incoming=False))
async def send_from_second_user(event):
    # запрос данных из бд о id лички
    to_chat_id = int(config["Settings"]["to_chat_id"])
    # запрос данных из бд о id получателя
    from_chat_id = int(config["Settings"]["from_chat_id"])
    text_msg_orig = event.text  # тест сообщения
    msg_id = event.id  # id сообщения
    # определение языка юзера
    if config["Settings"]["my_lang"] == 'enn' and text_msg_orig[0] != '/':
        tranlate_text_info = translator.detect(text_msg_orig)
        config.set('Settings', 'my_lang', tranlate_text_info.lang)
        print(tranlate_text_info.lang)
        saver_config()
    # проверка есть ли чат для прослушивания и переадресации
    if from_chat_id == to_chat_id and not bool(int(config["Settings"]["is_pause"])):
        await client.delete_messages(message_ids=msg_id, entity=to_chat_id)
        msg = help_translate(
            msg='Вы не инициализировали переадресацию сообщения', lang=config['Settings']['my_lang'])
        service_msg_send_from_1 = await client.send_message(message=msg, entity=to_chat_id)
        await asyncio.sleep(1.5)
        await client.delete_messages(message_ids=service_msg_send_from_1.id, entity=to_chat_id)
        # удаляем сервисное сообщение
    # основной блок обработки и переадресации
    elif not bool(int(config["Settings"]["is_pause"])):
        from_chat_id = int(config["Settings"]["from_chat_id"])
        # проверка содержания текста в сообщении (отсеивание картинок, видео, аудио и т.д.)
        if len(text_msg_orig) != 0:
            # проверка команда ли это
            if text_msg_orig[0] != '/':
                config.set('MSG_DATA', 'msg_id_string',
                           config['MSG_DATA']["msg_id_string"] + str(msg_id) + ";")
                saver_config()
                translate_text_info = translator.translate(
                    text_msg_orig, dest=config['Settings']['2_lang'])
                translate_text = translate_text_info.text
                # выбранный режим отправки текса
                if config['Settings']['mode'] == "2" and translate_text != text_msg_orig:
                    text_msg_new = f"Translate:\n{translate_text}\nOrig:\n{text_msg_orig}"
                else:
                    text_msg_new = f"{translate_text}"
                await client.send_message(message=text_msg_new,
                                          entity=from_chat_id)

    # сервисное сообщение о включенной паузе
    elif text_msg_orig[0] != '/':
        config.set('MSG_DATA', 'msg_id_string',
                   config['MSG_DATA']["msg_id_string"] + str(msg_id) + ";")
        saver_config()
        msg = help_translate(msg='У вас включен режим паузы',
                             lang=config['Settings']['my_lang'])
        service_msg_send_from_1 = await client.send_message(
            message=msg,
            entity=to_chat_id)
        await asyncio.sleep(1.5)
        await client.delete_messages(message_ids=service_msg_send_from_1.id, entity=to_chat_id)
        # удаляем сервисное сообщение


# основной блок кода, все первоначальные действия здесь
if __name__ == '__main__':
    line_preview = "   ______                                      __  _            \n  / ____/___  ____ _   _____  _" \
                   "_____________ _/ /_(_)___  ____  \n / /   / __ \/ __ \ | / / _ \/ ___/ ___/ __ `/ __/ / __ \/ __" \
                   " \ \n/ /___/ /_/ / / / / |/ /  __/ /  (__  ) /_/ / /_/ / /_/ / / / / \n\____/\____/_/ /_/|___/\__" \
                   "_/_/  /____/\__,_/\__/_/\____/_/ /_/  \n                                                         " \
                   "       \n   __                        __      __             \n  / /__________ _____  _____/ /__" \
                   "_ _/ /_____  _____ \n / __/ ___/ __ `/ __ \/ ___/ / __ `/ __/ __ \/ ___/ \n/ /_/ /  / /_/ / / / (" \
                   "__  ) / /_/ / /_/ /_/ / /     \n\__/_/   \__,_/_/ /_/____/_/\__,_/\__/\____/_/      \n        " \
                   "                                            \n"
    print(line_preview)
    client.connect()
    if not client.is_user_authorized():
        try:
            client.send_code_request(input('Enter your phone: '))
            client.sign_in(code=input('Enter code: '))
        except SessionPasswordNeededError:
            print('Enter your password: ', end='')
            client.sign_in(password=input(''))

    print('connected')
    client.start()
    # проверка совместимости файла config.ini
    config_options_in_file = dict()
    for section_name in config.sections():
        config_options_in_file[section_name] = config.options(section_name)
    with open(file_config, "r+") as fl_conf, open(file_bkp, "r+") as fl_bkp:
        fl_bkp.write(fl_conf.read(
        )) if config_options_in_file == config_options else fl_conf.write(fl_bkp.read())
    config.read(file_config)

    # проверка содержания файлом id
    if config["Settings"]["to_chat_id"] == "-1" or config["Settings"]["from_chat_id"] == "-1":
        service_msg = client.send_message("me", "Connect")
        my_id = service_msg.peer_id.user_id
        client.delete_messages(message_ids=service_msg.id, entity=my_id)
        config.set("Settings", "to_chat_id", str(abs(my_id)))
        config.set("Settings", "from_chat_id", str(abs(my_id)))
        config.set("Settings", "my_id", str(abs(my_id)))
        saver_config()
        os.startfile("ct.exe")
    else:
        client.run_until_disconnected()
