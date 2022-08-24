from typing import Dict, Union, Optional
from datetime import datetime
from config_data.config import RAPID_API_KEY
from command import his
import telebot
import re
import requests
import json
import time

bot: Optional[telebot.TeleBot] = None

headers = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def get_city(message, command: str, user_bot: telebot.TeleBot) -> None:
    """
    Начальная функция работы гостиничных команд.
    Отправляет запрос с указанием города пользователя и получает идентификатор назначения
    для продолжения дальнейшей работы с ним.
    Распределяет различные команды гостиничных команд по соответствующим функциям.
    :param message: message-object from an user
    :param command: command1 which user sent
    :param user_bot: TeleBot object
    """
    global bot
    bot = user_bot
    user_filter: str = ''
    count_photo: Optional[int] = None
    if message.text.isalpha():
        url: str = "https://hotels4.p.rapidapi.com/locations/search"
        querystring: Dict[str: Union[int, str]] = {"query": message.text,
                                                   "locale": 'ru_RU'}

        bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
        response: Union[requests.Response, Dict] = requests.request("GET", url,
                                                                    headers=headers,
                                                                    params=querystring)
        response = json.loads(response.text)
        destination_id: int = int(response['suggestions'][0]['entities'][0]['destinationId'])

        today: datetime = datetime.now()

        url = "https://hotels4.p.rapidapi.com/properties/list"

        querystring = {"adults1": "1", "pageNumber": "1", "destinationId": destination_id, "pageSize": "10",
                       "checkIn": str(today)[0:10],
                       "checkOut": f'{today.year}-'
                                   f'{str(today)[5:7]}-'
                                   f'{today.day + 1 if (today.day + 1) // 10 != 0 else "0" + str(today.day + 1)}',
                       "currency": "RUB", "locale": "ru_RU"}

        bot.send_message(message.from_user.id,
                         'Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»)')

        @bot.message_handler(content_types=['text'])
        def answer_photo(message):
            if message.text.lower() == 'да':
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text='1', callback_data=1))
                markup.add(telebot.types.InlineKeyboardButton(text='2', callback_data=2))
                markup.add(telebot.types.InlineKeyboardButton(text='3', callback_data=3))
                bot.send_message(message.chat.id, 'Выбери кол-во фотографий', reply_markup=markup)

                @bot.callback_query_handler(func=lambda call: True)
                def query_handler(call):
                    nonlocal count_photo
                    if call.data == '1':
                        count_photo = 1
                    elif call.data == '2':
                        count_photo = 2
                    elif call.data == '3':
                        count_photo = 3
                    else:
                        bot.send_message(message.chat.id, 'Будет выведено 3 фото')

            else:
                bot.send_message(message.chat.id, 'Вывод будет без фотографий')
                nonlocal count_photo
                count_photo = None

        time.sleep(5)

        if command == 'lowprice' or command == 'highprice':
            if command == 'lowprice':
                querystring["sortOrder"] = "PRICE"
                user_filter = 'lowprice'
            else:
                querystring["sortOrder"] = "PRICE_HIGHEST_FIRST"
                user_filter = 'highprice'

            response = requests.request('GET', url=url, headers=headers, params=querystring)
            response = json.loads(response.text)

            bot.send_message(message.from_user.id,
                             'Введите количество отелей, которые необходимо вывести в результате.')
            bot.register_next_step_handler(message, get_hotel_count, response,
                                           len(response['data']['body']['searchResults']['results']),
                                           user_filter, count_photo)

        else:
            user_filter = 'bestdeal'
            bot.send_message(message.from_user.id, 'Введите диапазон цен отеля в формате "min-max".'
                                                   '\nПример: 3000-9999,'
                                                   'где 3000 - минимальная цена, а 9999 - максимальная.')
            bot.register_next_step_handler(message, price_range, querystring,
                                           user_filter, count_photo)
    else:
        bot.send_message(message.from_user.id, 'В ответе не должно быть символов, кроме символов текста.')


def get_hotel_photo(response: Dict, id_count: int) -> str:
    """Эта функция для генерации фотографий
       :param response: response словарь
       :param id_count: id photo
    """

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": response}

    response = requests.request("GET", url, headers=headers, params=querystring)

    response = json.loads(response.text)
    return response['hotelImages'][id_count]['baseUrl'].replace('_{size}', '')


def get_hotel_count(message, response: Dict, max_hotel_count: int, user_filter: str, count_photo: int) -> None:
    """
    Эта функция для подсчета максимального значение .
    :param count_photo: parameter number of photos
    :param user_filter: user_filter: user filter from command
    :param message: message-object
    :param response: response словарь
    :param max_hotel_count: максимальное кол-во отелей
    """

    try:
        user_hotel_count: int = int(message.text)
    except ValueError:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число.')
    else:
        if user_hotel_count > max_hotel_count:
            bot.send_message(message.from_user.id,
                             f'Вы запрашиваете слишком много отелей.\n'
                             f'Кол-во отелей, которое будет выведено: {max_hotel_count}')
        else:
            max_hotel_count = user_hotel_count
        result_func(message, response, max_hotel_count, user_filter, count_photo)


def price_range(message, querystring: Dict[str, Union[int, str]], user_filter: str, count_photo: int) -> None:
    """
    Функция, которая получает от пользователя минимальную цену и максимальную цену отеля и отправляет запрос.
    :param count_photo: parameter number of photos
    :param user_filter: user_filter: user filter from command
    :param message: message-object from an user
    :param querystring: querystring for request
    """
    try:
        querystring["priceMin"] = int(message.text.split('-')[0])
        querystring["priceMax"] = int(message.text.split('-')[1])
    except ValueError:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число.')
    else:
        url = "https://hotels4.p.rapidapi.com/properties/list"
        bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
        response = requests.request('GET', url=url, headers=headers, params=querystring)
        response = json.loads(response.text)
        if len(response['data']['body']['searchResults']['results']) == 0:
            bot.send_message(message.from_user.id, 'Извините, но мы не нашли отеля, подходящего бы для Вас :(')
        else:
            bot.send_message(message.from_user.id,
                             'Введите диапазон расстояния отеля от центра в формате "min-max" (в км). Пример: 0.5-2')
            bot.register_next_step_handler(message, distance_range, response, user_filter, count_photo)


def distance_range(message, response: Dict, user_filter: str, count_photo: int) -> None:
    """
    Функция, которая сортирует диктант с учетом distance_range.
    :param count_photo: parameter number of photos
    :param user_filter: user_filter: user filter from command
    :param message: message-object from an user
    :param response: response from user's request
    """
    try:
        min_distance, max_distance = message.text.split('-')
        min_distance, max_distance = re.sub(',', '../command1', min_distance), re.sub(',', '../command1', max_distance)
        min_distance, max_distance = float(min_distance), float(max_distance)
    except ValueError:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число.')
    else:
        total_indexes: int = 10
        if len(response['data']['body']['searchResults']['results']) < total_indexes:
            total_indexes = len(response['data']['body']['searchResults']['results'])
        max_index = total_indexes
        for hotel in range(max_index):
            actual_index = hotel - max_index + total_indexes
            distance = response['data']['body']['searchResults']['results'][actual_index]['landmarks'][0]['distance']
            distance = re.findall(r'[\d,]+', distance)[0]
            distance = float(re.sub(',', '../command1', distance))
            if not min_distance <= distance <= max_distance:
                response['data']['body']['searchResults']['results'].pop(actual_index)
                total_indexes -= 1
        bot.send_message(message.from_user.id, 'Введите количество отелей, которые необходимо вывести в результате.')
        bot.register_next_step_handler(message, get_hotel_count, response, total_indexes, user_filter, count_photo)


def result_func(message, response: Dict, hotel_count: int, user_filter: str, count_photo: int) -> None:
    """
    Функция результата.
    Отправляет результат ответов пользователю
    :param count_photo: parameter number of photos
    :param user_filter: user filter from command
    :param message: message object from user
    :param response: response from hotels.com API
    :param hotel_count: num of hotels which will be sent to an user
    :return:
    """
    result = []
    if response['result'] == 'ERROR':
        bot.send_message(message.from_user.id, 'Неизвестная ошибка.')
        print(response['error_message'])
    elif hotel_count == 0:
        bot.send_message(message.from_user.id, 'Извините, но мы не нашли отеля, подходящего бы для Вас :(')
    else:
        for hotel in range(hotel_count):
            if count_photo is not None:
                for photo in range(count_photo):
                    bot.send_photo(message.chat.id,
                                   get_hotel_photo(response['data']['body']['searchResults']['results'][hotel]['id'],
                                                   photo
                                                   )
                                   )

            name = f"{hotel + 1}. Название отеля: " \
                   f"{response['data']['body']['searchResults']['results'][hotel]['name']}"
            if 'streetAddress' in response['data']['body']['searchResults']['results'][hotel]['address']:
                address = f"Адрес: " \
                          f"{response['data']['body']['searchResults']['results'][hotel]['address']['streetAddress']}"
            else:
                address = 'Адрес: отсутствует.'
            distance_from_centre = f"Расстояние от центра: " \
                                   f"{response['data']['body']['searchResults']['results'][hotel]['landmarks'][0]['distance']}"
            price = f"Цена: {response['data']['body']['searchResults']['results'][hotel]['ratePlan']['price']['current']} "
            answer = '\n'.join([name, address, distance_from_centre, price])

            result.append(answer)
            bot.send_message(message.from_user.id, answer)
    his.add_user_history(user_filter, message.from_user.id, '\n'.join(result))
