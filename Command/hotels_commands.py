import re
import requests
import json
from telebot import TeleBot
from typing import Dict, Union, Optional
from datetime import datetime
from Command import history

count_photo: Optional[int] = None
bot: Optional[TeleBot] = None

headers = {
    "X-RapidAPI-Key": "ac1b5818d5mshaca8453ad9e9c08p167539jsn8438d4f6f9aa",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def get_city(message, command: str, user_bot: TeleBot) -> None:
    """
    Начальная функция работы гостиничных команд.
    Отправляет запрос с указанием города пользователя и получает идентификатор назначения
    для продолжения дальнейшей работы с ним.
    Распределяет различные команды гостиничных команд по соответствующим функциям.
    :param message: message-object from an user
    :param command: command which user sent
    :param user_bot: TeleBot object
    """
    global bot
    bot = user_bot
    if message.text.isalpha():
        url: str = "https://hotels4.p.rapidapi.com/locations/search"
        querystring: Dict[str: Union[int, str]] = {"query": message.text,
                                                   "locale": 'ru_RU'}

        bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
        response: Union[requests.Response, Dict] = requests.request("GET", url, headers=headers, params=querystring)
        response = json.loads(response.text)
        destination_id: int = int(response['suggestions'][0]['entities'][0]['destinationId'])

        today: datetime = datetime.today()

        url = "https://hotels4.p.rapidapi.com/properties/list"

        querystring = {"adults1": "1", "pageNumber": "1", "destinationId": destination_id, "pageSize": "10",
                       "checkIn": str(today)[0:10],
                       "checkOut": f'{today.year}-{str(today)[5:7]}-{today.day + 1 if (today.day + 1) // 10 != 0 else "0" + str(today.day + 1)}',
                       "currency": "USD", "locale": "ru_RU"}

        if command == 'lowprice' or command == 'highprice':
            if command == 'lowprice':
                querystring["sortOrder"] = "PRICE"
            else:
                querystring["sortOrder"] = "PRICE_HIGHEST_FIRST"
            response = requests.request('GET', url=url, headers=headers, params=querystring)
            response = json.loads(response.text)

            bot.send_message(message.from_user.id,
                             'Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»)')

            @bot.message_handler(content_types=['text'])
            def answer_photo(message) -> None:
                if message.text.lower() == 'да':
                    bot.send_message(message.from_user.id,
                                     'Введите кол-во необходимых фотографий от 1 до 3)')
                    bot.register_next_step_handler(message, get_count, response)

                elif message.text.lower() == 'нет':
                    bot.send_message(message.from_user.id,
                                     'Введите количество отелей, которые необходимо вывести в результате.')
                    bot.register_next_step_handler(message, get_hotel_count, response,
                                                   len(response['data']['body']['searchResults']['results']))

                else:
                    bot.send_message(message.from_user.id,
                                     'Я тебя не понимаю=( Придется начать сначала=(')

        else:
            bot.send_message(message.from_user.id, 'Введите диапазон цен отеля в формате "min-max".\nПример: 3000-9999,'
                                                   'где 3000 - минимальная цена, а 9999 - максимальная.')
            bot.register_next_step_handler(message, price_range, querystring)
    else:
        bot.send_message(message.from_user.id, 'В ответе не должно быть символов, кроме символов текста.')


def get_count(message, response: Dict) -> None:
    """Эта функция для проверки значения запроса по фотографиям
    :param message: message-object
    :param response: response словарь
    """

    try:
        global count_photo
        if message.text.isdigit() or message.text in '123':
            count_photo = int(message.text)
        else:
            raise TypeError
    except TypeError:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число от 1 до 3!')

    else:
        bot.send_message(message.from_user.id,
                         'Введите количество отелей, которые необходимо вывести в результате.')
        bot.register_next_step_handler(message, get_hotel_count, response,
                                       len(response['data']['body']['searchResults']['results']))


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


def get_hotel_count(message, response: Dict, max_hotel_count: int) -> None:
    """
    Эта функция для подсчета максимального значение .
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
        result_func(message, response, max_hotel_count)


def price_range(message, querystring: Dict[str, Union[int, str]]) -> None:
    """
    Функция, которая получает от пользователя минимальную цену и максимальную цену отеля и отправляет запрос.
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
            bot.register_next_step_handler(message, distance_range, response)


def distance_range(message, response: Dict) -> None:
    """
    Функция, которая сортирует диктант с учетом distance_range.
    :param message: message-object from an user
    :param response: response from user's request
    """
    try:
        min_distance, max_distance = message.text.split('-')
        min_distance, max_distance = re.sub(',', '.', min_distance), re.sub(',', '.', max_distance)
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
            distance = float(re.sub(',', '.', distance))
            if not min_distance <= distance <= max_distance:
                response['data']['body']['searchResults']['results'].pop(actual_index)
                total_indexes -= 1
        bot.send_message(message.from_user.id, 'Введите количество отелей, которые необходимо вывести в результате.')
        bot.register_next_step_handler(message, get_hotel_count, response, total_indexes)


def result_func(message, response: Dict, hotel_count: int) -> None:
    """
    Функция результата.
    Отправляет результат ответов пользователю
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

    history.db_table_val(message.from_user.id, '\n'.join(result))

    bot.infinity_polling()
