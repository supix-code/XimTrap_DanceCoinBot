from telebot import types
from telebot.apihelper import ApiTelegramException

import config
from utils.db_manager import *


admin_keyb = types.InlineKeyboardMarkup()
admin_keyb.add(types.InlineKeyboardButton(text=f'📤 Рассылка', callback_data='mailing'),
               types.InlineKeyboardButton(text=f'⚙️ Школы', callback_data='school_settings'))
admin_keyb.add(types.InlineKeyboardButton(text=f'🔎 Найти пользователя', callback_data='search_user'))


student_keyb = types.InlineKeyboardMarkup()
student_keyb.add(types.InlineKeyboardButton(text=f'📊 Статистика', callback_data='--'),
                 types.InlineKeyboardButton(text=f'🎓 Обучение', callback_data='--'))
student_keyb.add(types.InlineKeyboardButton(text=f'ℹ️ Информация', callback_data='faq'),
                 types.InlineKeyboardButton(text=f'🆘 Помощь', url='t.me/xantrue'))

mail_select_keyb = types.InlineKeyboardMarkup()
mail_select_keyb.add(types.InlineKeyboardButton(text='С кнопкой', callback_data=f'next_mailing:btn_yes'),
                     types.InlineKeyboardButton(text='Без кнопки', callback_data=f'next_mailing:btn_no'))
mail_select_keyb.add(types.InlineKeyboardButton(text='🔙', callback_data=f'back_to_main'))


def mail_link_keyb(flag):
    data = get_except(flag)[1]
    data = data.split('|')
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=data[1],      url=data[0]))
    keyboard.add(types.InlineKeyboardButton(text='✖️', callback_data='mail_del'))
    return keyboard


def back_to_main(data='back_to_main', text='🔙'):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=text, callback_data=data))
    return keyboard


def main_keyb(userid):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='📜 Информация', callback_data='info'),
                 types.InlineKeyboardButton(text='🛎 Поддержка', url=config.support_link))

    if int(userid) in config.admin: 
        keyboard.add(types.InlineKeyboardButton(text='🔐 Меню администратора', callback_data=f'admin_menu'))
    return keyboard    


def mail_confirm(btn_flag, userid, msg_id, data=None, except_id=None):
    keyboard = types.InlineKeyboardMarkup()
    if btn_flag:
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data=f'cancel_mail'),
                     (types.InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'mail_confirm:{userid}:{msg_id}:0')))
    else:
        keyboard.add(types.InlineKeyboardButton(text=data[1], url=data[0]))
        keyboard.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data=f'cancel_mail'),
                     (types.InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'mail_confirm:{userid}:{msg_id}:{except_id}')))
    return keyboard


def school_settings_keyb():
    schools = get_schools()

    keyboard = types.InlineKeyboardMarkup()
    if len(schools) > 0:
        keyboard.add(types.InlineKeyboardButton(text='➕ Добавить', callback_data=f'add_school'),
                     types.InlineKeyboardButton(text='➖ Удалить', callback_data=f'del_school'))
    else:
        keyboard.add(types.InlineKeyboardButton(text='➕ Добавить школу', callback_data=f'add_school'))
    keyboard.add(types.InlineKeyboardButton(text='🔙', callback_data=f'back_to_main'))
    return keyboard
















