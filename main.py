from command import help, hotels_commands, his
from config_data.config import BOT_TOKEN
import telebot

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(regexp=r'[Пп]ривет')
@bot.message_handler(commands=['start', 'help', 'history'])
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
    elif message.text == '/history':
        bot.send_message(message.from_user.id, f'История загружается...\n{his.history(message.from_user.id)}')

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


if __name__ == '__main__':
    bot.infinity_polling()
