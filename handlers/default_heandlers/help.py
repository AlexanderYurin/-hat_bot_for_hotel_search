from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot
from logger.logger import logger_bot


@bot.message_handler(commands=['help'])
@logger_bot
def bot_help(message: Message) -> None:
    """
       Хендлер помощи для вывода всех доступных команд пользователю.

       Принимает объект сообщения message типа Message из библиотеки Telebot.
       Отвечает пользователю списком всех доступных команд.

       :param message: Объект сообщения типа Message из библиотеки Telebot.
       :type message: telebot.types.Message
       :return: Функция ничего не возвращает, сообщение отправляется с помощью метода bot.reply_to
       :rtype: None
       """
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
