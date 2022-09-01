import json
import re
from datetime import date, timedelta
from typing import Dict, Union

from telebot.types import Message

from api_hotel import api
from database.result import result_func
from loader import bot
from states.user_info import UserInfoState


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def hotel_commands(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.command, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if message.text == '/lowprice':
            data['output_result'] = message.text

        elif message.text == '/highprice':
            data['output_result'] = message.text

        else:
            data['output_result'] = message.text

    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите город, где будет проводится поиск.')


@bot.message_handler(state=UserInfoState.city)
def get_user_city(message: Message) -> None:
    if message.text.isalpha():
        url: str = "https://hotels4.p.rapidapi.com/locations/search"
        querystring: Dict[str: Union[int, str]] = {"query": message.text,
                                                   "locale": 'ru_RU'}
        response = api.request_to_api(url, querystring)

        try:
            pattern = r'(?<="CITY_GROUP",).+?[\]]'
            find = re.search(pattern, response)

            if find:
                result = json.loads(f"{{{find[0]}}}")
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['city_id'] = int(result['entities'][0]['destinationId'])

        except IndexError:
            bot.send_message(message.from_user.id,
                             'Ошибка! Такого города нету в списке.')
        else:
            bot.send_message(message.from_user.id,
                             'Введите количество отелей, которые необходимо вывести в результате.')
            bot.set_state(message.from_user.id, UserInfoState.count_city, message.chat.id)

    else:
        bot.send_message(message.from_user.id, 'Город может содержать только буквы!')


@bot.message_handler(state=UserInfoState.count_city)
def get_count_city(message: Message) -> None:
    if message.text.isdigit() and message.text in '12345':
        bot.send_message(message.from_user.id,
                         'Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»)')
        bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_city'] = int(message.text)

    else:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число от 1 до 5!')


@bot.message_handler(state=UserInfoState.photo)
def get_photo(message: Message) -> None:
    if message.text.lower() == 'да':
        bot.send_message(message.from_user.id,
                         'Введите количество фотографий, которые необходимо вывести в результате.')
        bot.set_state(message.from_user.id, UserInfoState.count_photo, message.chat.id)
    elif message.text.lower() == 'нет':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data['output_result'] in ('/lowprice', '/highprice'):
                bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
                result(message)
            else:
                bot.send_message(message.from_user.id, 'Введите диапазон цен отеля в формате "min-max".'
                                                       '\nПример: 3000-9999,'
                                                       'где 3000 - минимальная цена, а 9999 - максимальная.')
                bot.set_state(message.from_user.id, UserInfoState.price, message.chat.id)

    else:
        bot.send_message(message.from_user.id, 'В ответе должно быть только («Да/Нет»)')


@bot.message_handler(state=UserInfoState.count_photo)
def get_count_photo(message: Message) -> None:
    if message.text.isdigit() and message.text in '123':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_photo'] = int(message.text)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

            if data['output_result'] in ('/lowprice', '/highprice'):
                bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
                result(message)

            else:
                bot.send_message(message.from_user.id, 'Введите диапазон цен отеля в формате "min-max".'
                                                       '\nПример: 3000-9999,'
                                                       'где 3000 - минимальная цена, а 9999 - максимальная.')
                bot.set_state(message.from_user.id, UserInfoState.price, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'В ответе должно быть только число от 1 до 3!')


@bot.message_handler(state=UserInfoState.price)
def get_price(message: Message) -> None:
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price'] = (int(message.text.split('-')[0]), int(message.text.split('-')[1]))
            if data['price'][1] < data['price'][0]:
                raise ValueError

    except ValueError:
        bot.send_message(message.from_user.id, 'Максимальная цена должна быть больше минимальной!'
                                               '\nПример: 3000-9999')
        raise
    except Exception:
        bot.send_message(message.from_user.id, 'В ответе должно быть только числа! Смотри пример!'
                                               '\nПример: 3000-9999, '
                                               'где 3000 - минимальная цена, а 9999 - максимальная.')
    else:
        bot.send_message(message.from_user.id, 'Введите диапазон расстояния отеля от '
                                               'центра в формате "min-max" (в км). Пример: 0.5-2')
        bot.set_state(message.from_user.id, UserInfoState.distance, message.chat.id)


@bot.message_handler(state=UserInfoState.distance)
def get_distance(message: Message) -> None:
    try:
        min_distance, max_distance = message.text.split('-')
        min_distance, max_distance = re.sub(',', '.', min_distance), re.sub(',', '.', max_distance)
        min_distance, max_distance = float(min_distance), float(max_distance)
        if max_distance < min_distance:
            raise TypeError

    except TypeError:
        bot.send_message(message.from_user.id, 'Максимальное расстояние должно быть больше минимального!'
                                               '\nПример: 0.5-2!')
        raise
    except Exception:
        bot.send_message(message.from_user.id, 'В ответе должно быть только числа через дефис!'
                                               '\nПример: 0.5-2!'
                                               'где 0.5 - минимальное расстояние, а 2 - максимальное.')

    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['distance'] = (min_distance, max_distance)
        bot.send_message(message.from_user.id, 'Идет поиск отелей.  Это может занять несколько секунд...')
        result(message)


def result(message: Message) -> None:
    url = "https://hotels4.p.rapidapi.com/properties/list"

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

        querystring = {"adults1": "1", "pageNumber": "1", "destinationId": data['city_id'], "pageSize": "10",
                       "checkIn": str(date.today()),
                       "checkOut": str(date.today() + timedelta(days=1)),
                       "currency": "RUB", "locale": "ru_RU"}

        if data['output_result'] == '/lowprice':
            querystring["sortOrder"] = "PRICE"

        elif data['output_result'] == '/highprice':
            querystring["sortOrder"] = "PRICE_HIGHEST_FIRST"

        else:
            querystring["priceMin"] = data['price'][0]
            querystring["priceMax"] = data['price'][1]

        response = json.loads(api.request_to_api(url, querystring))

        if data['output_result'] == '/bestdeal':
            if len(response['data']['body']['searchResults']['results']) == 0:
                bot.send_message(message.from_user.id, 'Извините, но мы не нашли отеля, подходящего бы для Вас :(')
            else:
                total_indexes: int = 5
                if len(response['data']['body']['searchResults']['results']) < total_indexes:
                    total_indexes = len(response['data']['body']['searchResults']['results'])
                max_index = total_indexes
                for hotel in range(max_index):
                    actual_index = hotel - max_index + total_indexes
                    distance = response['data']['body']['searchResults']['results'][actual_index]['landmarks'][0][
                        'distance']
                    distance = re.findall(r'[\d,]+', distance)[0]
                    distance = float(re.sub(',', '.', distance))
                    if not data['distance'][0] <= distance <= data['distance'][1]:
                        response['data']['body']['searchResults']['results'].pop(actual_index)
                        total_indexes -= 1

        result_func(message, response, data['count_city'], data['output_result'], data.get('count_photo'))
        bot.set_state(message.from_user.id, message.chat.id)
