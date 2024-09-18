# from airports import ALL_AIRPORTS
from myHttp import http
from airport_city_info import AIRPORT_TO_CITY, CITY_TO_AIRPORTS
from reachable_cities import REACHABLE_CITIES
import time
from utils import *
from copy import deepcopy
import json

# airports that cannot find city code on trip.com, these are all very small airports
NO_CITY_AIRPORTS = ['JRT', 'TKP']


SEARCH_URL = 'https://us.trip.com/restapi/soa2/27015/FlightListSearchSSE'


def search_flights(city1: str, city2: str, date: str, target_city: str):
    '''
    date: 8-digit string
    
    If city 2 is same as transfer city, only return direct flights.
    
    If different, only return 1-stop flights and the transfer city is the same as the transfer city.
    '''
    # y_int = int(date[:4])
    # m_int = int(date[4:6])
    # d_int = int(date[6:8])
    # today = (time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday)
    # today_unix_s = date_to_unix_s(*today)
    # search_unix_s = date_to_unix_s(y_int, m_int, d_int)
    # if (search_unix_s < today_unix_s - 24 * 3600):
    #     return 'Cannot search for past dates.'
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
    assert (json.loads(datas[0])['ResponseStatus']['Ack'] == None)
    # for data in datas:
    #     data = json.loads(data)
    #     print(json.dumps(data, indent=4, ensure_ascii=False))
    flights = []
    data = json.loads(datas[-1])
    for flight in data['itineraryList']:
        # print(json.dumps(flight, indent=4, ensure_ascii=False))
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
    return remove_duplicate_direct(flights)


if __name__ == '__main__':
    a = search_flights('SHA', 'BJS', '20241119', 'BJS')
    print(a)
