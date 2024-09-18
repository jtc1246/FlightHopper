# from airports import ALL_AIRPORTS
from myHttp import http
from airport_city_info import AIRPORT_TO_CITY, CITY_TO_AIRPORTS
from reachable_cities import REACHABLE_CITIES
import time
from utils import *
from copy import deepcopy
import json
from typing import Union
from queue import Queue
from _thread import start_new_thread

# airports that cannot find city code on trip.com, these are all very small airports
NO_CITY_AIRPORTS = ['JRT', 'TKP']


SEARCH_URL = 'https://us.trip.com/restapi/soa2/27015/FlightListSearchSSE'


def search_flights(city1: str, city2: str, date: str, target_city: str) -> list:
    '''
    date: 8-digit string, all city should 3-letter city code, NOT airport code.

    If city 2 is same as transfer city, only return direct flights.

    If different, only return 1-stop flights and the transfer city is the same as the target city.
    '''
    data = REQUEST_BODY.replace('$YYYY$', date[:4]).replace('$MM$', date[4:6]).replace('$DD$', date[6:8])
    city_airports = [city1, city2, '', '']
    if (city1 in NO_CITY_AIRPORTS):
        city_airports[0] = ''
        city_airports[2] = city1
    if (city2 in NO_CITY_AIRPORTS):
        city_airports[1] = ''
        city_airports[3] = city2
    data = data.replace('$CITY1$', city_airports[0]).replace('$CITY2$', city_airports[1]).replace('$AIRPORT1$', city_airports[2]).replace('$AIRPORT2$', city_airports[3])
    header = deepcopy(REQUEST_HEADER)
    header['Content-Length'] = str(len(data.encode('utf-8')))
    resp = http(SEARCH_URL, Method='POST', Body=data, Header=header, Timeout=10000, Retry=False, ToJson=False)
    datas = resp['text'].split('data:')[1:]
    assert (resp['code'] == 200)
    assert (json.loads(datas[0])['ResponseStatus']['Ack'] == None)
    flights = []
    data = json.loads(datas[-1])
    for flight in data['itineraryList']:
        if (target_city == city2 and len(flight["journeyList"][0]['transSectionList']) == 1):
            price = flight['policies'][0]['price']['totalPrice']
            info = flight["journeyList"][0]['transSectionList'][0]
            flight_number = info['flightInfo']['flightNo']
            if (info['flightInfo']['shareFlightNo'] != None):
                flight_number = info['flightInfo']['shareFlightNo']
            src_airport = info['departPoint']["airportCode"]
            src_city_name = info['departPoint']['cityName']
            dest_airport = info['arrivePoint']["airportCode"]
            dest_city_name = info['arrivePoint']['cityName']
            start_time = info['departDateTime'][5:-3]
            end_time = info['arriveDateTime'][5:-3]
            flights.append({
                'price': price,
                'segments': [{
                    'flight_number': flight_number,
                    'src_airport': src_airport,
                    'src_city_name': src_city_name,
                    'dest_airport': dest_airport,
                    'dest_city_name': dest_city_name,
                    'start_time': start_time,
                    'end_time': end_time
                }]
            })
        if (target_city == city2):
            continue
        if (len(flight["journeyList"][0]['transSectionList']) != 2):
            continue
        middle_city_code = flight["journeyList"][0]['transSectionList'][0]['arrivePoint']['cityCode']
        if (middle_city_code != target_city):
            continue
        price = flight['policies'][0]['price']['totalPrice']
        this_flight = {
            'price': price,
            'segments': []
        }
        info = flight["journeyList"][0]['transSectionList'][0]
        flight_number = info['flightInfo']['flightNo']
        if (info['flightInfo']['shareFlightNo'] != None):
            flight_number = info['flightInfo']['shareFlightNo']
        src_airport = info['departPoint']["airportCode"]
        src_city_name = info['departPoint']['cityName']
        dest_airport = info['arrivePoint']["airportCode"]
        dest_city_name = info['arrivePoint']['cityName']
        start_time = info['departDateTime'][5:-3]
        end_time = info['arriveDateTime'][5:-3]
        this_flight['segments'].append({
            'flight_number': flight_number,
            'src_airport': src_airport,
            'src_city_name': src_city_name,
            'dest_airport': dest_airport,
            'dest_city_name': dest_city_name,
            'start_time': start_time,
            'end_time': end_time
        })
        info = flight["journeyList"][0]['transSectionList'][1]
        flight_number = info['flightInfo']['flightNo']
        if (info['flightInfo']['shareFlightNo'] != None):
            flight_number = info['flightInfo']['shareFlightNo']
        src_airport = info['departPoint']["airportCode"]
        src_city_name = info['departPoint']['cityName']
        dest_airport = info['arrivePoint']["airportCode"]
        dest_city_name = info['arrivePoint']['cityName']
        start_time = info['departDateTime'][5:-3]
        end_time = info['arriveDateTime'][5:-3]
        this_flight['segments'].append({
            'flight_number': flight_number,
            'src_airport': src_airport,
            'src_city_name': src_city_name,
            'dest_airport': dest_airport,
            'dest_city_name': dest_city_name,
            'start_time': start_time,
            'end_time': end_time
        })
        flights.append(this_flight)
    if (target_city == city2):
        return remove_duplicate_direct(flights)
    return flights


def search_flights_wrapper(city1: str, city2: str, date: str, target_city: str, result_queue: Queue) -> None:
    '''
    Have retry and error handling.
    '''
    max_trial = 5
    success = False
    while (success == False and max_trial > 0):
        try:
            flights = search_flights(city1, city2, date, target_city)
            result_queue.put(flights)
            return
        except:
            max_trial -= 1
            time.sleep(1)
    print(f'Searching for {city1} -> {city2} failed after max retries.')
    result_queue.put(False)


def search_transfer_flights(src: str, dest: str, date: str) -> None:
    '''
    src and dest: 3-letter city code or airport code. But if a city has multiple airports, it will
    still search for all airports in that city, even if you specify airport code.

    date: 8-digit string

    Will not return anything, will print the results.
    '''
    if (len(date) != 8):
        raise Exception('Date should be 8-digit string.')
    y_int = int(date[:4])
    m_int = int(date[4:6])
    d_int = int(date[6:8])
    today = (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
    today_unix_s = date_to_unix_s(*today)
    search_unix_s = date_to_unix_s(y_int, m_int, d_int)
    err_msg = ''
    if (search_unix_s < today_unix_s - 24 * 3600):
        err_msg += 'Cannot search for past dates. '
    if (search_unix_s > today_unix_s + 24 * 3600 * 365 * 2):
        err_msg += 'Date incorrect. '
    if (src not in CITY_TO_AIRPORTS and src not in AIRPORT_TO_CITY):
        err_msg += f'Airport or city {src} not found. '
    if (dest not in CITY_TO_AIRPORTS and dest not in AIRPORT_TO_CITY):
        err_msg += f'Airport or city {dest} not found.'
    if (err_msg != ''):
        raise Exception(err_msg)
    src_city = ''
    dest_city = ''
    src_city_name = ''
    dest_city_name = ''
    if (src in AIRPORT_TO_CITY):
        src_city = AIRPORT_TO_CITY[src]['city_code']
    else:
        src_city = src
    if (dest in AIRPORT_TO_CITY):
        dest_city = AIRPORT_TO_CITY[dest]['city_code']
    else:
        dest_city = dest
    src_city_name = AIRPORT_TO_CITY[CITY_TO_AIRPORTS[src_city][0]]['city_name']
    dest_city_name = AIRPORT_TO_CITY[CITY_TO_AIRPORTS[dest_city][0]]['city_name']
    print(f'Searching for flights from {src_city_name} to {dest_city_name}.')
    print(f'Searching direct flights ...')
    direct_flights = search_flights(src_city, dest_city, date, dest_city)
    if (len(direct_flights) == 0):
        print('Error: No direct flights found. You cannot search for transfer flights.\nStop.')
        return
    print('+--------+----------------------------------------------+---------------------------+----------+')
    for f in direct_flights:
        print(format_direct_flight(f))
        print('+--------+----------------------------------------------+---------------------------+----------+')
    transfer_cities = REACHABLE_CITIES[dest_city]
    queue = Queue()
    waiting_num = len(transfer_cities)
    print(f'Searching {waiting_num} transfer cities ...')
    for i in range(0, waiting_num):
        start_new_thread(search_flights_wrapper, (src_city, transfer_cities[i], date, dest_city, queue))
        time.sleep(0.5)
    while (queue.qsize() < waiting_num):
        time.sleep(0.1)
    transfer_flights = []
    while (queue.empty() == False):
        result = queue.get()
        if (result == False):
            print('Error: Some flight search failed.')
            continue
        transfer_flights += result
    transfer_flight_num = len(transfer_flights)
    for i in range(transfer_flight_num - 1, -1, -1):
        this_price = transfer_flights[i]['price']
        this_flight_number = transfer_flights[i]['segments'][0]['flight_number']
        for j in range(0, len(direct_flights)):
            if (this_flight_number == direct_flights[j]['segments'][0]['flight_number']):
                if (this_price >= direct_flights[j]['price']):
                    transfer_flights.pop(i)
                break
    if (len(transfer_flights) == 0):
        print('No cheaper transfer flights found.')
        return
    print('Found following cheaper transfer flights: ')
    print('+--------+-------------+----------------------------------------------------------------------+----------+')
    for f in transfer_flights:
        print(format_transfer_flight(f))
        print('+--------+-------------+----------------------------------------------------------------------+----------+')


if __name__ == '__main__':
    search_transfer_flights('LAX', 'DTW', '20241119')
