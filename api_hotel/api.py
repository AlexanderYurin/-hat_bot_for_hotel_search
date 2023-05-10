from typing import Dict
import requests
from config_data.config import RAPID_API_KEY
from loguru import logger

logger.add("connect.log", rotation="10 MB", level="INFO", format="{time} - {name} - {level} - {message}")


def request_to_api(url: str, querystring: Dict) -> str:
    """
    Функция отправляет GET-запрос на заданный URL с заданными параметрами и заголовками.
    :param url: Ссылка на сайт (строка).
    :param querystring: Параметры запроса (словарь).
    :return: Строка с ответом от сервера.
    """
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    try:
        with requests.get(url, headers=headers, params=querystring, timeout=30) as response:
            response.raise_for_status()
            logger.info(f'{url}: {response.status_code}!')
            return response.text
    except requests.exceptions.HTTPError as errh:
        logger.exception(f'HTTP-ошибка: {errh}')
    except requests.exceptions.ConnectionError as errc:
        logger.exception(f'Ошибка подключения: {errc}')
    except requests.exceptions.Timeout as errt:
        logger.exception(f'Ошибка тайм-аута: {errt}')
    except requests.exceptions.RequestException as err:
        logger.exception(f'Что-то пошло не так: {err}')
