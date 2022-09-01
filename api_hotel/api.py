from typing import Dict

import requests

from config_data.config import RAPID_API_KEY


def request_to_api(url: str, querystring: Dict) -> str:

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"

    }
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            return response.text

    except Exception:
        print('Ошибка подключения к серверу!')
