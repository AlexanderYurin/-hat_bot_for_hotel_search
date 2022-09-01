from telebot.types import Message

from database import his
from loader import bot


@bot.message_handler(commands='history')
def history(message: Message) -> None:
    bot.send_message(message.from_user.id, f'История загружается...\n{his.history(message.from_user.id)}')
