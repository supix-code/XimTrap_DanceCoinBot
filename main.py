# -*- coding: utf-8 -*- 
from telebot import TeleBot

from source.banner import main_banner
from funk import *
import config


bot = TeleBot(config.token, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start(message):
    userid = int(message.chat.id)
    logger.info(f"Start user: {get_username(bot, userid)} [{userid}]")
    if message.chat.type != 'private': 
        return

    user = get_user(userid)
    if user is None: 
        if userid in config.admin:
            add_user(userid, 'admin')
        else:
            msg = bot.send_photo(userid, config.photo_file_list[0],
                                 caption=register_text(userid, bot))
            bot.register_next_step_handler(msg, code_enter)
            return

    main_data_list = main_menu_data(userid, bot)
    bot.send_photo(userid, main_data_list[0], 
                   caption=main_data_list[1],
                   reply_markup=main_data_list[2])
    username_update(message, userid)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    call_chat_id, call_msg_id, userid, first_name = call_helper(call)
    logger.info(f"CallBack: {call.data} | {get_username(bot, userid)} [{userid}]")
    clear_handler(bot, call)

    
    if call.data == 'back_to_main':   
        try:
            main_data_list = main_menu_data(userid, bot)
            file_id = main_data_list[0]
            bot.edit_message_media(types.InputMediaPhoto(file_id),
                                   call_chat_id, call_msg_id)

            bot.edit_message_caption(main_data_list[1], 
                                     call_chat_id, call_msg_id,
                                     reply_markup=main_data_list[2])
        except ApiTelegramException:           
            main_data_list = main_menu_data(userid, bot)
            bot.send_photo(userid, main_data_list[0], 
                           caption=main_data_list[1],
                           reply_markup=main_data_list[2])
    
    elif call.data == 'school_settings':
        call_del_msg(call, bot)
        bot.send_message(userid, school_settings_text(),
                         reply_markup=school_settings_keyb())

    elif call.data == 'add_school':
        msg = bot.edit_message_text(td['add_school_text'], 
                                    call_chat_id, call_msg_id, 
                                    reply_markup=back_to_main('school_settings')) 
        bot.register_next_step_handler(msg, add_school_funk, msg)

    elif call.data == 'del_school':
        msg = bot.edit_message_text(td['del_school_text'], 
                                    call_chat_id, call_msg_id, 
                                    reply_markup=back_to_main('school_settings')) 
        bot.register_next_step_handler(msg, del_school_funk, msg)

    elif call.data == 'faq':
        file_id = config.photo_file_list[4]
        bot.edit_message_media(types.InputMediaPhoto(file_id),
                               call_chat_id, call_msg_id)
        bot.edit_message_caption(td['faq_text'], 
                                 call_chat_id, call_msg_id,
                                 reply_markup=back_to_main())


    elif call.data == 'cancel_mail':
        call_del_msg(call, bot)
        bot.send_message(userid, td['mailing_cancel'])

        main_data_list = main_menu_data(userid, bot)
        bot.send_photo(userid, main_data_list[0], 
                       caption=main_data_list[1],
                       reply_markup=main_data_list[2])

    elif 'mail_confirm' in call.data:
        call_del_msg(call, bot)
        mail_data = str(call.data).split(':')
        userid, msg_id, flag = mail_data[1], mail_data[2], mail_data[3]
        threading.Thread(target=mail_funk, 
                         args=(bot, userid, msg_id, flag, )).start()    

    elif call.data == 'mail_del':
        bot.answer_callback_query(call.id, text=td['hide_msg'])
        call_del_msg(call, bot)

    elif call.data == 'mailing':
        if int(userid) not in config.admin:
            return

        file_id = config.photo_file_list[7]
        bot.edit_message_media(types.InputMediaPhoto(file_id),
                               call_chat_id, call_msg_id)

        bot.edit_message_caption(td['mailing_type'], 
                                 call_chat_id, call_msg_id,
                                 reply_markup=mail_select_keyb)

    elif 'next_mailing:' in call.data:
        if int(userid) not in config.admin:
            return
        btn_flag = call.data.split(':')[1]
        keyboard = back_to_main('cancel_mail', '❌ Отмена')
        call_del_msg(call, bot)

        if btn_flag == 'btn_yes':
            msg = bot.send_message(userid, td['button_link'], 
                             reply_markup=keyboard)
            bot.register_next_step_handler(msg, forward_link, msg)

        elif btn_flag == 'btn_no':
            msg = bot.send_message(userid, td['wait_msg'], 
                             reply_markup=keyboard)
            bot.register_next_step_handler(msg, forward_sms, msg)


def code_enter(message):
    userid = message.chat.id
    code = message.text
    if message.text == '/start':
        start(message)
        return

    data = get_reg_code(code)
    if True:
    # if data is None:
        msg = bot.send_message(userid, '<b>⚠️ Код активации не принят, повторите ввод:</b>')
        bot.register_next_step_handler(msg, code_enter)

    elif data[0] == 'teacher':
        ...

    elif data[0] == 'student':
        ...


def add_school_funk(message, msg_for_del):
    del_msg(msg_for_del, bot)
    userid = message.chat.id
    name = message.text
    if message.text == '/start':
        start(message)
        return
    
    add_school(name, userid)
    bot.send_message(userid, td['add_school_complete'].format(name), 
                     reply_markup=back_to_main('school_settings'))


def del_school_funk(message, msg_for_del):
    del_msg(msg_for_del, bot)
    userid = message.chat.id
    data = message.text
    if message.text == '/start':
        start(message)
        return

    if data.isdigit():
        school_id = data
        school = get_school(school_id)
        if school is None:
            bot.send_message(userid, td['school_not_exist'], 
                             reply_markup=back_to_main())
        else:
            del_school(school_id)
            del_reg_code(school[2])
            bot.send_message(userid, td['school_del_compl'].format(school[1]), 
                             reply_markup=back_to_main('school_settings'))
        return

    bot.send_message(userid, td['format_error'], 
                     reply_markup=back_to_main())


def forward_link(message, msg_for_del):
    del_msg(msg_for_del, bot)
    userid = message.chat.id
    data = message.text
    if message.text == '/start': 
        bot.send_message(userid, td['mailing_cancel'], reply_markup=admin_keyb)
        return

    data = data.split('|')
    if len(data) != 2:
        bot.send_message(userid, td['format_error'], 
                         reply_markup=back_to_main('cancel_mail'))
        return

    text = td['mailing_with_btn'].format(data[1], data[0])
    keyboard = back_to_main('cancel_mail', '❌ Отмена')
    msg = bot.send_message(userid, text, 
                           reply_markup=keyboard, 
                           disable_web_page_preview=True)
    bot.register_next_step_handler(msg, forward_sms, msg, data)


def forward_sms(message, msg_for_del, data=None):
    del_msg(msg_for_del, bot)
    userid = message.chat.id
    msg_id = message.message_id
    if message.text == '/start': 
        bot.send_message(userid, td['mailing_cancel'], reply_markup=admin_keyb)
        return

    if data is None:
        keyboard = mail_confirm(True, userid, msg_id)
    else:
        except_id = add_except(f'{data[0]}|{data[1]}')
        keyboard = mail_confirm(False, userid, msg_id, data, except_id)
    bot.copy_message(userid, userid, msg_id, reply_markup=keyboard)


main_banner()
main_bot(bot)
