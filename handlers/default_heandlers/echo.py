from telebot.types import Message
from logger.logger import logger_bot

from loader import bot


@bot.message_handler(state=None)
@logger_bot
def bot_echo(message: Message) -> None:
    """
    Эхо-хендлер для обработки текстовых сообщений без указанного состояния.

    Принимает объект сообщения message типа Message из библиотеки Telebot.
    Отвечает пользователю шаблонным сообщением, если не может понять запрос пользователя.

    :param message: Объект сообщения типа Message из библиотеки Telebot.
    :type message: telebot.types.Message
    :return: Функция ничего не возвращает, сообщение отправляется с помощью метода bot.reply_to
    :rtype: None
    """
    # Ответ на сообщение
    bot.reply_to(message, f'{message.from_user.first_name}, я тебя не понимаю.\nНажми /help')
