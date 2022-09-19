import re
from typing import Dict

from telebot.types import InputMediaPhoto, Message

from api_hotel import api
from database import database
from loader import bot


def get_hotel_photo(response: Dict, id_count: int) -> str:
    """Эта функция для генерации фотографий.
    Делается запрос к API после этого из текста, берутся все ссылки в формате списка.
       :param response: все данные по отелю в формате Словаря.
       :param id_count: индекс фото.
       :return: вощвращает ссылку на фото по индексу
    """

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": response}

    response = api.request_to_api(url, querystring)
    pattern = r'\bhttps://exp.cdn-hotels.com/hotels/\w+/\w+/\w+/\w+/\w+\b'
    try:
        result = re.findall(pattern, response)
        if result[id_count].count('_') == 1:
            photo = result[id_count].replace('_', '.jpg')
        else:
            raise
    except Exception:
        return 'https://gladston.ru/upload/iblock/b59/img_183363.jpg'

    else:
        return photo


def result_func(message: Message, response: Dict, hotel_count: int, user_filter: str, count_photo: int) -> None:
    """
    Функция результата.
    Записывает результат ответов в бд.
    :param count_photo: кол-во фотографий.
    :param user_filter: команда запроса от пользователя.
    :param message: сообщение от пользователя.
    :param response: response из hotels.com api_hotel
    :param hotel_count: кол-во отелей.
    :return:
    """
    result = []

    if response['result'] == 'ERROR':
        bot.send_message(message.from_user.id, 'Неизвестная ошибка.')
    elif hotel_count == 0:
        bot.send_message(message.from_user.id, 'Извините, но мы не нашли отеля, подходящего бы для Вас :(')
    else:
        for hotel in range(hotel_count):
            list_photo = []
            if count_photo is not None:
                try:
                    for photo in range(count_photo):
                        try:
                            list_photo.append(get_hotel_photo(
                                response['data']['body']['searchResults']['results'][hotel]['id'],
                                photo)
                            )


                        except IndexError:
                            print('Какая то ошибка')
                except IndexError:
                    print('Какая то ошибка')

                else:
                    medias = [InputMediaPhoto(url_photo) for url_photo in list_photo]
                    bot.send_media_group(message.from_user.id, medias)

            try:
                id_hotel = response['data']['body']['searchResults']['results'][hotel]['id']
                site = f'{hotel + 1}. Ссылка на отель: https://www.hotels.com/ho{id_hotel}'
                name = f'Название отеля: ' \
                       f"{response['data']['body']['searchResults']['results'][hotel]['name']}"
                if 'streetAddress' in response['data']['body']['searchResults']['results'][hotel]['address']:
                    address = f"Адрес: " \
                              f"{response['data']['body']['searchResults']['results'][hotel]['address']['streetAddress']}"
                else:
                    address = 'Адрес: отсутствует.'
                if 'distance' in response['data']['body']['searchResults']['results'][hotel]['landmarks'][0]:

                    distance_from_centre = f"Расстояние от центра: " \
                                           f"{response['data']['body']['searchResults']['results'][hotel]['landmarks'][0]['distance']}"
                else:
                    distance_from_centre = 'Расстояние от центра отсутствует'

                if 'ratePlan' in response['data']['body']['searchResults']['results'][hotel]:
                    price = f"Цена за ночь: " \
                            f"{response['data']['body']['searchResults']['results'][hotel]['ratePlan']['price']['current']}"
                else:
                    price = 'Стоимость отсутствует'
                answer = '\n'.join([site, name, address, distance_from_centre, price])
            except IndexError:
                bot.send_message(message.from_user.id, 'Отели не найдены')
                result.append('Отели не найдены')
                break

            else:
                result.append(answer)
                bot.send_message(message.from_user.id, answer, disable_web_page_preview=True)
    database.add_user_history(user_filter, message.from_user.id, '\n'.join(result))
