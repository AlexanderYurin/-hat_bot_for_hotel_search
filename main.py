import telebot
from Command import help, hotels_commands, history

bot = telebot.TeleBot('5536563248:AAFXGeg_TGu2i-6r-FGHZgaXIqHbz2Vsocg')


@bot.message_handler(commands=['help', 'start'])
def main_commands_catcher(message) -> None:
    """
    Отправляет ответ на команды пользователю в Telegram-чате: /start и /help.
    :param message: message-object from user
    """
    result: str = ''
    if message.text == '/start':
        bot.send_animation(message.chat.id, r'https://gifer.com/ru/Geu2')
        result = f'{message.from_user.first_name}, добро пожаловать!\n' \
                 f'Я помощник по подбору лучшего предложения в среде отелей для Вас!\n'
    else:
        help.help()
    result += help.help()
    bot.send_message(message.from_user.id, result)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def hotel_commands(message) -> None:
    """
    Отправляет ответ на команды пользователю в Telegram-чате: /lowprice, /highprice, /bestdeal.
    :param message: message-object from user
    """
    bot.send_message(message.from_user.id, 'Введите город, где будет проводится поиск.')
    bot.register_next_step_handler(message, hotels_commands.get_city, message.text[1:], bot)


@bot.message_handler(commands='history')
def history(message) -> None:
    """
    Отправляет ответ на команды пользователю в Telegram-чате: /history.
    :param
    message: message - object from user
    """
    bot.send_message(message.from_user.id, 'История загружается...')
    bot.register_next_step_handler(message, history.search, bot)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
