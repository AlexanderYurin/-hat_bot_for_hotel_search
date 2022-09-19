from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    command = State()
    city = State()
    count_city = State()
    check_in = State()
    check_out = State()
    photo = State()
    count_photo = State()
    price = State()
    distance = State()



