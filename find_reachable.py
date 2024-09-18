from myHttp import http
from airport_city_info import AIRPORT_TO_CITY, CITY_TO_AIRPORTS
from queue import Queue
from time import time, sleep
from typing import Tuple, Union, Literal
from _thread import start_new_thread
import traceback
from threading import Lock


FLIGHT_RADAR_URL = 'https://api.flightradar24.com/common/v1/airport.json?code=$airport$&plugin%5B%5D=schedule&plugin-setting%5Bschedule%5D%5Bmode%5D=departures&plugin-setting%5Bschedule%5D%5Btimestamp%5D=$time$&limit=100&page=$page$'


class RateLimitManager:
    def __init__(self, min_gap_second: float):
        self.min_gap_second = min_gap_second
        self.next_time = 0
        self.lock = Lock()

    def wait(self):
        current_time = time()
        sleep_time = 0
        with self.lock:
            if (current_time >= self.next_time):
                self.next_time = current_time + self.min_gap_second
                sleep_time = 0
            else:
                sleep_time = self.next_time - current_time
                self.next_time += self.min_gap_second
        sleep(sleep_time)


flight_radar_rate_limit = RateLimitManager(0.85)
city_caches = {}


def one_request(url: str) -> Tuple[bool, list[str], int]:
    '''
    Returns: (success, airports, page_num), but here success is always True. If fails, will encounter an error.

    No error handling.
    '''
    flight_radar_rate_limit.wait()
    resp = http(url)
    assert resp['status'] >= 0 and resp['code'] == 200
    results = resp['text']['result']['response']['airport']['pluginData']['schedule']['departures']
    page_num = results['page']['total']
    results = results['data']
    destinations = []
    for flight in results:
        destinations.append(flight['flight']['airport']['destination']['code']['iata'])
    return True, destinations, page_num


def one_page_flight(url: str) -> Tuple[bool, list[str], int]:
    '''
    Returns: (success, airports, page_num).

    Will not raise errors.
    '''
    max_trial = 5
    success = False
    while (success == False and max_trial > 0):
        try:
            _, airports, page_num = one_request(url)
            success = True
        except:
            max_trial -= 1
    if success == False:
        return (False, [], 0)
    return (True, airports, page_num)


def page_thread(url: str, result_queue: Queue) -> None:
    '''
    async, only process one request, and put the result into the queue.
    '''
    def tmp_func():
        success, airports, _ = one_page_flight(url)
        if (success == False):
            result_queue.put(False)
            return
        result_queue.put(airports)
    start_new_thread(tmp_func, ())


def get_flights(airport_code: str, result_queue: Queue, previous: bool) -> None:
    '''
    Get one type of flight destinations. type here means previous or future.

    async, put the result into the queue. If fails, put False into the queue.
    '''
    operator = ''
    if previous == True:
        operator = '-'
    current_time = str(int(time()))
    url = FLIGHT_RADAR_URL.replace('$airport$', airport_code).replace('$time$', current_time).replace('$page$', operator + '1')
    success, airports, page_num = one_page_flight(url)
    if (success == False):
        result_queue.put(False)
        return
    if (page_num <= 1):
        result_queue.put(airports)
        return
    waiting_num = page_num - 1
    queue = Queue()
    for i in range(2, page_num + 1):
        url = FLIGHT_RADAR_URL.replace('$airport$', airport_code).replace('$time$', current_time).replace('$page$', operator + str(i))
        page_thread(url, queue)
    while True:
        if (queue.qsize() == waiting_num):
            break
        sleep(0.1)
    results = [airports]
    while (queue.empty() == False):
        tmp = queue.get()
        if (tmp == False):
            result_queue.put(False)
            return
        results.append(tmp)
    results = sum(results, [])
    result_queue.put(results)


def find_airport_reachable_airports(airport_code: str) -> Union[Literal[False], list[str]]:
    '''
    Return False if fails. Return list[str] if success.

    If airport code not exists or no flights, will return an empty list.
    '''
    queue = Queue()
    start_new_thread(get_flights, (airport_code, queue, False))
    start_new_thread(get_flights, (airport_code, queue, True))
    while True:
        if (queue.qsize() == 2):
            break
        sleep(0.1)
    results = []
    while (queue.empty() == False):
        tmp = queue.get()
        if (tmp == False):
            return False
        results.append(tmp)
    results = sum(results, [])
    return list(set(results))


def find_city_reachable_cities(city_code: str) -> Union[Literal[False], list[str]]:
    '''
    Return False if fails. Return list[str] if success.
    '''
    if (city_code in city_caches):
        return city_caches[city_code]
    airports = CITY_TO_AIRPORTS[city_code]
    results = []
    for airport in airports:
        reachable_airports = find_airport_reachable_airports(airport)
        if (reachable_airports == False):
            return False
        results += reachable_airports
    results = list(set(results))
    cities = []
    for airport in results:
        if (airport not in AIRPORT_TO_CITY):
            # There may be some very small airports that are not in the database,
            # there are very few commercial flights in these airports, so it's safe to ignore them.
            continue
        cities.append(AIRPORT_TO_CITY[airport]['city_code'])
    city_caches[city_code] = list(set(cities))
    return list(set(cities))


if __name__ == '__main__':
    a = find_city_reachable_cities('TYO')
    print(a)
