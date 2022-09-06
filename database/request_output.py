import re
from typing import Dict

from api_hotel import api
from database import database
from loader import bot
from telebot.types import Message, InputMediaPhoto

def get_hotel_photo(response: Dict, id_count: int) -> str:
    """Эта функция для генерации фотографий
       :param response: response словарь
       :param id_count: id photo
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
    Отправляет результат ответов пользователю
    :param count_photo: parameter number of photos
    :param user_filter: user filter from output_result
    :param message: message object from user
    :param response: response from hotels.com api_hotel
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
                    price = f"Цена: " \
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
