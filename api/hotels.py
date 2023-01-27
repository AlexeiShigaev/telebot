import json
import sys
from logs import logger
import requests
from api.queries import url_city, headers_city, get_query_city
from api.queries import url_hotels, headers_hotels, get_query_hotels
from api.queries import url_photos, headers_photos, get_query_photos
from config import MAX_HOTEL_PHOTOS


def find_city(city: str) -> dict:
    """Пользователь ввел строку имени города. Сделаем запрос, на выходе или пустой {} - нет такого города,
    или будут варианты совпадений имен. Отбираем из запроса только города."""
    cities = {}
    logger.info('Запрос на поиск gaiaId города {}'.format(city))
    try:
        response = requests.request("GET", url_city, headers=headers_city, params=get_query_city(city))
        # logger.debug()
        data = json.loads(response.text)
        for elem in data['sr']:
            if elem['type'] == 'CITY':
                cities.update({elem['gaiaId']: elem['regionNames']['displayName']})
    except Exception as ex:
        logger.error(ex.with_traceback(sys.exc_info()[2]))
    logger.debug('Запрос прошел удачно.\nНа выходе {}'.format(cities))
    return cities


def find_hotels(user_state: dict) -> list:
    logger.info('Запрос на поиск отелей в городе {}:{}\nНа входе {}'.format(
        user_state['city_gaiaId'], user_state['city'], user_state)
    )
    hotels = []
    try:
        response = requests.request("POST", url_hotels, json=get_query_hotels(user_state), headers=headers_hotels)
        ret_hotels = json.loads(response.text)['data']['propertySearch']
        # logger.debug('Запрос прошел удачно.\n{}'.format(ret_hotels))
        logger.debug('Запрос прошел удачно.')

        hotels_list = ret_hotels['properties']

        """В запросе сортировка PRICE_LOW_TO_HIGH дает список отелей от дешевых к дорогим, 
        нужно его отсортировать в обратном порядке для команды highprice."""
        if user_state['command'] == 'highprice':
            hotels_list = reversed(hotels_list)

        """Для команды bestdeal,
        Нужно убрать отели которые не подходят под фильтр min_distance - max_distance"""
        ret_hotels_list = []
        if user_state['command'] == 'bestdeal':
            for hotel in hotels_list:
                distance = int(hotel['destinationInfo']['distanceFromDestination']['value'])
                if int(user_state['min_distance']) < distance < int(user_state['max_distance']):
                    ret_hotels_list.append(hotel)
            hotels_list = ret_hotels_list

        hotels_counter = 0
        """ограничим выборку"""
        max_hotels_counter = int(user_state['hotels_count'])

        for i_hotel in hotels_list:
            hotels_counter += 1
            current_hotel = {}
            current_hotel.update(
                {'id': i_hotel['id'],
                 'name': i_hotel['name'],
                 'distance': i_hotel['destinationInfo']['distanceFromDestination']['value'],
                 'price': i_hotel['price']['displayMessages'][0]['lineItems'][0]['price']['formatted'],
                 'price_total': i_hotel['price']['displayMessages'][1]['lineItems'][0]['value'],
                 'hotel_img_url': i_hotel['propertyImage']['image']['url']
                 }
            )
            hotels.append(current_hotel)
            if hotels_counter >= max_hotels_counter:
                break
    except Exception as ex:
        logger.error(ex.with_traceback(sys.exc_info()[2]))
    logger.debug('Результат выполнения запроса:\n{}'.format(hotels))
    return hotels


def find_hotel_photos(hotel_id: str, photos_cnt:int = MAX_HOTEL_PHOTOS) -> list:
    photos_urls = []
    logger.info('Запрос на поиск фотографий отеля {}'.format(hotel_id))
    try:
        response = requests.request("POST", url_photos, json=get_query_photos(hotel_id), headers=headers_photos)
        ret_photos = json.loads(response.text)['data']['propertyInfo']['propertyGallery']
        for index in range(photos_cnt):
            photos_urls.append({
                'desc': ret_photos['images'][index]['image']['description'],
                'url': ret_photos['images'][index]['image']['url']
            })
    except Exception as ex:
        logger.error(ex.with_traceback(sys.exc_info()[2]))
        return []
    logger.debug('Запрос прошел удачно.\nНа выходе {}'.format(photos_urls))
    return photos_urls
