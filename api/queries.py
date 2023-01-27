from config import RAPID_KEY
from logs import logger

"""
Блок с url_city и headers_city и get_query_city().
Касается запроса-поиска кода города по имени.
"""
url_city = "https://hotels4.p.rapidapi.com/locations/v3/search"

headers_city = {
    "X-RapidAPI-Key": RAPID_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def get_query_city(city: str) -> dict:
    """Возвращает строку запроса на поиск города"""
    return {"q": city, "type": "CITY", "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}


"""
Блок для запроса отелей. url_hotels, headers_hotels, get_query_hotels
"""

url_hotels = "https://hotels4.p.rapidapi.com/properties/v2/list"

headers_hotels = {
    "content-type": "application/json",
    "X-RapidAPI-Key": RAPID_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def get_query_hotels(user_state: dict) -> dict:
    """Возвращает словарь с запросом для поиска отелей на основе кода города gaiaId"""
    check_in = user_state['date_check_in'].split('.')
    check_out = user_state['date_check_out'].split('.')

    query_hotels = {
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": user_state['city_gaiaId']},
        "checkInDate": {
            "day": int(check_in[0]), "month": int(check_in[1]), "year": int(check_in[2])
        },
        "checkOutDate": {
            "day": int(check_out[0]), "month": int(check_out[1]), "year": int(check_out[2])
        },
        "rooms": [{"adults": 1,  "children": []}],
        "resultsStartingIndex": 0,
        "resultsSize": int(user_state['hotels_count']),
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {"max": 150000, "min": 10}}
    }

    """Изменим выборку, чтоб выдал больше дорогих отелей, если команда highprice."""
    if user_state['command'] == 'highprice':
        query_hotels.update({"filters": {"price": {"max": 150000, "min": 150}}, "resultsSize": 200})

    """Команда bestdeal требует уточнить фильтр по ценам. И отсортируем по расстоянию от центра.
    Расстояние от центра нужно фильтровать вручную после получения результата. Нет фильтра про дистанс.
    Здесь могут быть вопросы. Если вдруг количество отелей в фильтре получится больше 200
    (а больше апи не выдает, дальше след. страница), может случиться что результат будет не совсем корректен."""
    if user_state['command'] == 'bestdeal':
        query_hotels.update(
            {"filters": {"price": {"max": int(user_state['max_price']), "min": int(user_state['min_price'])}},
             "sort": "DISTANCE", "resultsSize": 200}
        )
    logger.debug('Сформирован запрос\n{}'.format(query_hotels))
    return query_hotels


"""
Блок объявлений для поиска фотографий отеля.
url_photos, headers_photos, get_query_photos
"""

url_photos = "https://hotels4.p.rapidapi.com/properties/v2/detail"

headers_photos = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }


def get_query_photos(hotel_id: str):
    return {"eapid": 1, "locale": "ru_RU", "siteId": 300000001, "propertyId": hotel_id}
