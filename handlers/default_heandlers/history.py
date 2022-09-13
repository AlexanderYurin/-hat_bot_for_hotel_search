from telebot.types import Message

from database import database
from loader import bot


@bot.message_handler(commands='history')
def history(message: Message) -> None:
    bot.send_message(message.from_user.id,
                     f'История загружается...\n{database.history(message.from_user.id)}',
                     disable_web_page_preview=True)
