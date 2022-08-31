from loader import bot
from telebot.types import Message
from output_result import his


@bot.message_handler(commands='history')
def history(message: Message) -> None:
    bot.send_message(message.from_user.id, f'История загружается...\n{his.history(message.from_user.id)}')
