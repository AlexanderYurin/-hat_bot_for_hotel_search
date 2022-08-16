import re
import requests
import json
from requests import Response
from telebot import TeleBot
from typing import Dict, Union, Optional
from datetime import datetime

bot: Optional[TeleBot] = None

headers = {
    "X-RapidAPI-Key": "ac1b5818d5mshaca8453ad9e9c08p167539jsn8438d4f6f9aa",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def get_city(message, command: str, user_bot: TeleBot) -> None:
    """
    Initial function of hotel commands work.
    Sends a request with user's city and gets destinationId to continue future work with it.
    Distributes different commands of hotel commands to corresponding functions.
    :param message: message-object from an user
    :param command: command which user sent
    :param user_bot: TeleBot object
    """

    bot = user_bot
    if message.text.isalpha():
        url: str = "https://hotels4.p.rapidapi.com/locations/search"
        querystring: Dict[str: Union[int, str]] = {"query": message.text,
                                                   "locale": 'ru_RU'}

        bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
        response: Union[Response, Dict] = requests.request("GET", url, headers=headers, params=querystring)
        response = json.loads(response.text)
        destination_id: int = int(response['suggestions'][0]['entities'][0]['destinationId'])

        today: datetime = datetime.today()

        url = "https://hotels4.p.rapidapi.com/properties/list"

        querystring = {"adults1": "1", "pageNumber": "1", "destinationId": destination_id, "pageSize": "10",
                       "checkIn": str(today)[0:10],
                       "checkOut": f'{today.year}-{str(today)[5:7]}-{today.day + 1 if (today.day + 1) // 10 != 0 else "0" + str(today.day + 1)}',
                       "currency": "RUB", "locale": "ru_RU"}

        if command == 'lowprice' or command == 'highprice':
            if command == 'lowprice':
                querystring["sortOrder"] = "PRICE"
            else:
                querystring["sortOrder"] = "PRICE_HIGHEST_FIRST"
            response = requests.request('GET', url=url, headers=headers, params=querystring)
            response = json.loads(response.text)

            bot.send_message(message.from_user.id,
                             'Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»)')
            if message.text.lower() == 'да':

                bot.send_message(message.from_user.id,
                                 'Введите кол-во необходимых фотографий (1-3)')
                if message.text not in ['1', '2', '3']:
                    bot.send_message(message.from_user.id,
                                     'Введите кол-во необходимых фотографий (1-3)')

                count_photo = message.text

                bot.send_message(message.from_user.id,
                                 'Введите количество отелей, которые необходимо вывести в результате.')
                bot.register_next_step_handler(message, get_hotel_count, response,
                                               len(response['data']['body']['searchResults']['results']),
                                               int(count_photo))



        else:
            bot.send_message(message.from_user.id, 'Введите диапазон цен отеля в формате "min-max".\nПример: 3000-9999,'
                                                   'где 3000 - минимальная цена, а 9999 - максимальная.')
            bot.register_next_step_handler(message, price_range, querystring)
    else:
        bot.send_message(message.from_user.id, 'В ответе не должно быть символов, кроме символов текста.')


def get_hotel_photo(response: Dict, count: int) -> str:
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": response['data']['body']['searchResults']['results'][0]['id']}

    response = requests.request("GET", url, headers=headers, params=querystring)

    response = json.loads(response.text)
    return response['hotelImages'][count]['baseUrl'] + '.jpg'


def get_hotel_count(message, response: Dict, max_hotel_count: int, count_photo: int) -> None:
    """
    Gets hotel count which user want to see and compares it with maximal hotel count.
    :param message: message-object from an user
    :param response: response from user's request
    :param max_hotel_count: conditional maximal hotel count
    """
    try:
        user_hotel_count: int = int(message.text)
    except TypeError:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число.')
    else:
        if user_hotel_count > max_hotel_count:
            bot.send_message(message.from_user.id,
                             f'Вы запрашиваете слишком много отелей.\n'
                             f'Кол-во отелей, которое будет выведено: {max_hotel_count}')
        else:
            max_hotel_count = user_hotel_count
        result_func(message, response, max_hotel_count, count_photo)


def price_range(message, querystring: Dict[str, Union[int, str]]) -> None:
    """
    Function which gets from user minimal price and maximal price of a hotel and sends a request.
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
    Function which sorts a dict considering distance_range.
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
            distance = re.findall(r'[0-9,]+', distance)[0]
            distance = float(re.sub(',', '.', distance))
            if not min_distance <= distance <= max_distance:
                response['data']['body']['searchResults']['results'].pop(actual_index)
                total_indexes -= 1
        bot.send_message(message.from_user.id, 'Введите количество отелей, которые необходимо вывести в результате.')
        bot.register_next_step_handler(message, get_hotel_count, response, total_indexes)


def result_func(message, response: Dict, hotel_count: int, count_photo: int) -> None:
    """
    Result function.
    Sends a result of responses to an user.
    :param message: message object from user
    :param response: response from hotels.com API
    :param hotel_count: num of hotels which will be sent to an user
    :return:
    """

    if response['result'] == 'ERROR':
        bot.send_message(message.from_user.id, 'Неизвестная ошибка.')
        print(response['error_message'])
    elif hotel_count == 0:
        bot.send_message(message.from_user.id, 'Извините, но мы не нашли отеля, подходящего бы для Вас :(')
    else:
        if count_photo is not None:
            for hotel in range(hotel_count):
                for photo in range(count_photo):
                    bot.send_animation(message.chat.id, get_hotel_count(response, photo))

                name = f"{hotel + 1}. Название отеля: {response['data']['body']['searchResults']['results'][hotel]['name']}"
                if 'streetAddress' in response['data']['body']['searchResults']['results'][hotel]['address']:
                    address = f"Адрес: {response['data']['body']['searchResults']['results'][hotel]['address']['streetAddress']}"
                else:
                    address = 'Адрес: отсутствует.'
                distance_from_centre = f"Расстояние от центра: " \
                                       f"{response['data']['body']['searchResults']['results'][hotel]['landmarks'][0]['distance']}"
                price = f"Цена: {response['data']['body']['searchResults']['results'][hotel]['ratePlan']['price']['current']} "
                answer = '\n'.join([name, address, distance_from_centre, price])
                bot.send_message(message.from_user.id, answer)


