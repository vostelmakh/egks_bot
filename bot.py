# ! /usr/bin/python
# -*- coding: utf-8 -*-

"""This script starts bot and sends info about egds."""

import requests
from bs4 import BeautifulSoup
import logging
import time
import telebot
import os

API_TOKEN = ''

BOT_INTERVAL = 10
BOT_TIMEOUT = 5

current_path = os.path.dirname(os.path.realpath(__file__))

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)

error_logger = logging.FileHandler(os.path.join(current_path, 'error.log'))
error_logger.setLevel(logging.ERROR)
error_logger.setFormatter(formatter)

info_logger = logging.FileHandler(os.path.join(current_path, 'info.log'))
info_logger.setLevel(logging.INFO)
info_logger.setFormatter(formatter)

logger.addHandler(error_logger)
logger.addHandler(info_logger)

def bot_polling():
    global bot
    logger.info('Starting bot polling now')
    while True:
        try:
            logger.info('New bot instance started')
            bot = telebot.TeleBot(API_TOKEN)
            bot_actions()
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except Exception as ex:
            logger.info(f'Bot polling failed, restarting in {BOT_TIMEOUT} sec. Error: {ex}')
            bot.stop_polling()
            time.sleep(BOT_TIMEOUT)
        else:
            bot.stop_polling()
            logger.info('Bot polling loop finished')
            break

def bot_actions():

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, 'Привет, чтобы получить данные о карте ЕГКС просто отправь боту ее номер.')
        logger.info(f'Said hi to user [{message.from_user.username}] with id: [{message.chat.id}]')
    
    @bot.message_handler(content_types=['text'])
    def get_egks_info(message):
        
        card_number = message.text
        chat_id = message.chat.id
        first_name = message.from_user.first_name 
        last_name = message.from_user.last_name
        username = message.from_user.username

        inline_message = message.text.replace("\n", " | ")
        logger.info(f'{first_name} {last_name} [{username}] [{chat_id}] send message: [{inline_message}].')

        if (not card_number.isdecimal()):
            logger.info(f'Not valid card number [{card_number}] from user [{chat_id}].')
            bot.send_message(chat_id=chat_id, text='Номер карты должен состоять только из чисел')
            return
        
        if (len(card_number) != 6 and len(card_number) != 9):
            logger.info(f'Not valid card number [{card_number}] from user [{chat_id}].')
            bot.send_message(chat_id=chat_id, text='Номер карты должен состоять из 6 либо 9 символов')
            return

        response = requests.post(f'https://www.egks.ru/card?number={card_number}', verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        result_message = str(soup.find('p')).replace('<br/>', '\n').replace('<p>', '').replace('</p>', '')
        if (len(result_message) == 0):
            bot.send_message(chat_id=chat_id, text=f'Карта с номером {card_number} не найдена либо неактивна')
        else:
            bot.send_message(chat_id=chat_id, text=result_message)

        result_message = result_message.replace("\n", " | ")
        logger.info(f'Send message: [{result_message}] to user [{username}] [{chat_id}]')

if __name__ == '__main__':
    bot_polling()