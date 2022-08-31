from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f'{message.from_user.first_name}, добро пожаловать!\n'
                          f'Я помощник по подбору лучшего предложения в среде отелей для Вас!\n')
