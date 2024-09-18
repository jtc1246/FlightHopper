from myHttp import http
from typing import Tuple
import json
from airports import ALL_AIRPORTS
from random import randint
from queue import Queue
from _thread import start_new_thread
from time import sleep
import traceback


def get_airport_city(airport_code: str) -> Tuple[str, str]:
    '''
    3-letter airport code -> (3-letter city code, city name)
    '''
    airport_code = airport_code.upper()
    url = 'https://us.trip.com/flights/graphql/poiSearch'
    data = {
        "operationName": "poiSearch",
        "variables": {
            "key": airport_code,
            "mode": "0",
            "tripType": "OW"
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "a04f920da8c6c0545bab401b5c2f3488878430a73c4b23aed9fda2156c7044d8"
            }
        }
    }
    data = json.dumps(data, ensure_ascii=False)
    header = {
        'Content-Length': str(len(data.encode('utf-8'))),
        'content-type': 'application/json'
    }
    resp = http(url, Method='POST', Body=data, Header=header)
    # print(resp)
    assert (resp['text']['data']['poiSearch']['ResponseStatus']['Ack'] == 'Success')
    result = resp['text']['data']['poiSearch']['results']
    # print(json.dumps(result, ensure_ascii=False, indent=4))
    for r in result:
        if ((r['dataType'] == 5 and r['airportCode'] == airport_code)):
            assert (len(r['cityCode']) == 3 or r['cityCode'] == '')
            if (r['cityCode'] == ''):
                r['cityCode'] = airport_code
            return (r['cityCode'], r['cityEName'])
    for r in result:
        if (r['dataType'] != 3):
            continue
        child_results = r['childResults']
        for child in child_results:
            if (child['dataType'] == 5 and child['airportCode'] == airport_code):
                assert (len(child['cityCode']) == 3 or child['cityCode'] == '')
                if (child['cityCode'] == ''):
                    child['cityCode'] = airport_code
                return (child['cityCode'], child['cityEName'])
    return False


def worker(start: int, end_plus_1: int):
    for i in range(start, end_plus_1):
        airport = ALL_AIRPORTS[i]['iata']
        success = False
        max_retry = 5
        while (not success and max_retry > 0):
            try:
                city = get_airport_city(airport)
                if (city == False):
                    failed_queue.put(airport)
                else:
                    success_queue.put((airport, city))
                success = True
            except:
                traceback.print_exc()
                max_retry -= 1
        if (success == False):
            assert (False), f"Failed to get city for airport {airport}"


success_queue = Queue()
failed_queue = Queue()


if __name__ == '__main__':
    per_worker_tasks = 150
    task_num = len(ALL_AIRPORTS)
    result_dict = {}
    worker_num = (task_num + per_worker_tasks - 1) // per_worker_tasks
    for i in range(0, worker_num):
        start = i * per_worker_tasks
        tasks = per_worker_tasks if i != worker_num - 1 else task_num - (worker_num - 1) * per_worker_tasks
        end = start + tasks
        start_new_thread(worker, (start, end))
    while (True):
        sleep(1)
        success = success_queue.qsize()
        failed = failed_queue.qsize()
        print(f'Success: {success}, Failed: {failed}, Total: {success + failed}')
        if (success + failed == task_num):
            print('All tasks finished')
            break
    print(f'Success: {success}, Failed: {failed}')
    while (not success_queue.empty()):
        info = success_queue.get()
        airport = info[0]
        city_code = info[1][0]
        city_name = info[1][1]
        result_dict[airport] = {
            'city_code': city_code,
            'city_name': city_name
        }
    result = json.dumps(result_dict, ensure_ascii=False)
    print(len(result))
    print(result)
    with open('./airport_city.json', 'w') as f:
        f.write(result)
    
