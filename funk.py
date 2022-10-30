# # -*- coding: utf-8 -*- 
import threading
from datetime import datetime

from loguru import logger

from source.text_dict import text_dict as td
from utils.keyboards import *
import config


logger.add("log/log_file.log", rotation="1 week")


def main_bot(bot):
    bot.infinity_polling(timeout=5, skip_pending=True)


def rounding(data, degree=2):
    try: 
        data = int(float(data) * 10**degree) / 10**degree
    except ValueError: 
        ...
    return data


def del_msg(message, bot):
    try: 
        bot.delete_message(chat_id=message.chat.id, 
                           message_id=message.message_id)
    except ApiTelegramException: 
        ...


def call_del_msg(call, bot):
    try: 
        bot.delete_message(chat_id=call.message.chat.id, 
                           message_id=call.message.message_id)
    except ApiTelegramException: 
        ...


def call_helper(call):
    call_chat_id = call.message.chat.id
    call_msg_id = call.message.message_id
    userid = str(call.message.chat.id)
    first_name = str(call.from_user.first_name)
    return call_chat_id, call_msg_id, userid, first_name


def clear_handler(bot, call):
    try: 
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    except ApiTelegramException: 
        ...


def get_username(bot, userid):
    try:
        username = bot.get_chat_member(userid, userid).user.username
        return f'<a href="tg://user?id={userid}">{userid}</a>' if username is None else f'@{username}'
    except ApiTelegramException:
        return f'<a href="tg://user?id={userid}">{userid}</a>'


def admin_send_mail_result(success, unsuccess, users_count, msg, bot, flag=False):
    if flag:
        for _ in range(30):
            try:
                text = td['full_mailing_progress']
                text = text.format(success + unsuccess, users_count,
                                   success, unsuccess)

                bot.edit_message_text(chat_id=msg.chat.id, 
                                      message_id=msg.message_id, 
                                      text=text)

                userid = msg.chat.id
                main_data_list = main_menu_data(userid, bot)
                bot.send_photo(userid, main_data_list[0], 
                               caption=main_data_list[1],
                               reply_markup=main_data_list[2])
                break
            except ApiTelegramException: 
                time.sleep(30)
    else:
        try:
            text = td['full_mailing_progress']
            text = text.format(success + unsuccess, users_count,
                               success, unsuccess)
            bot.edit_message_text(chat_id=msg.chat.id, 
                                  message_id=msg.message_id, 
                                  text=text)
        except ApiTelegramException: 
            ...


def mail_funk(bot, admin, msg_id, flag):
    all_users = get_users()
    users_count = len(all_users)
    success, unsuccess = 1, 0

    if flag == '0':    
        del_keyb = back_to_main('mail_del', '✖️')
    else: 
        del_keyb = mail_link_keyb(flag)

    bot.copy_message(admin, admin, msg_id, reply_markup=del_keyb)
    msg = bot.send_message(admin, td['mailing_progress'].format(users_count))

    for user in all_users:
        uid = user[0]
        if str(uid) == str(admin): 
            continue

        try:
            bot.copy_message(uid, admin, msg_id, reply_markup=del_keyb)
            success += 1
        except ApiTelegramException: 
            unsuccess += 1

        if (success + unsuccess) % 30 == 0:
            admin_send_mail_result(success, unsuccess, users_count, msg, bot)
    admin_send_mail_result(success, unsuccess, users_count, msg, bot, True)


def register_text(userid, bot):
    text = '''
⭐️ Добро пожаловать, <b>{}</b>

<i>📌 Введите регистрационный код:</i>
    '''
    text = text.format(get_username(bot, userid))
    return text


def date_parser_loop(data, indexes, pay=False):    # indexes = [userid_index, date_index]
    all_time_list, month_time_list, day_time_list = [], [], []
    timestamp = int(time.time())

    if len(indexes) == 2:
        for user in data:
            userid = user[indexes[0]]
            date = int(user[indexes[1]])
            all_time_list.append(userid)
            
            if date + 2592000 > timestamp:
                month_time_list.append(userid)
                if date + 86400 > timestamp:
                    day_time_list.append(userid)
        return [len(all_time_list), len(month_time_list), len(day_time_list)]
    else:
        for user in data:
            userid = user[indexes[0]]
            date = int(user[indexes[1]])
            amount = int(user[indexes[2]])
            all_time_list.append(amount)
            
            if date + 2592000 > timestamp:
                month_time_list.append(amount)
                if date + 86400 > timestamp:
                    day_time_list.append(amount)

        return [sum(all_time_list), sum(month_time_list), sum(day_time_list)]



def main_menu_data(userid, bot):
    user = get_user(userid)
    user_type = user[1]
    photo_list = config.photo_file_list

    if user_type == 'admin':
        photo = photo_list[3]
        dates_list = date_parser_loop(get_users(), [0, 6])
        text = td['admin_text']
        text = text.format(dates_list[0], dates_list[1], 
                           dates_list[2], len(get_schools()))
        keyboard = admin_keyb

    elif user_type == 'teacher':
        photo = photo_list[5]
        text = td['teacher_text']

    elif user_type == 'student':
        photo = photo_list[8]
        text = td['student_text']
        keyboard = student_keyb

    return [photo, text, keyboard]


def school_settings_text():
    schools = get_schools()
    if len(schools) == 0:
        text = '<b>😕 Нет доступных школ</b>'
    else:
        text = f'🏫 <b>Школы:</b>\n'
        counter = 1
        for school in schools:
            if counter == len(schools):
                edit_text = '     └ <b>{}.</b> <i>{}</i> [code: <code>{}</code>]\n'
                text += edit_text.format(school[0], school[1], school[2])
            else:
                edit_text = '     ├ <b>{}.</b> <i>{}</i> [code: <code>{}</code>]\n'
                text += edit_text.format(school[0], school[1], school[2])
            counter += 1

    return text
















