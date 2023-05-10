from telebot.types import Message
from logger.logger import logger_bot

from loader import bot


@bot.message_handler(commands=['start'])
@logger_bot
def bot_start(message: Message) -> None:
    """
    Стартовый хендлер с привествием и информацией о боте.

    Принимает объект сообщения message типа Message из библиотеки Telebot.
    Отвечает пользователю шаблонным сообщением, если не может понять запрос пользователя.

    :param message: Объект сообщения типа Message из библиотеки Telebot.
    :type message: telebot.types.Message
    :return: Функция ничего не возвращает, сообщение отправляется с помощью метода bot.reply_to
    :rtype: None
    """
    bot.reply_to(message, f'{message.from_user.first_name}, добро пожаловать!\n'
                          f'Я помощник по подбору лучшего предложения в среде отелей для Вас!\n'
                          f'Введи /help я расскажу что умею!')
