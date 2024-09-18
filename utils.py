import datetime
import calendar
import math

__all__ = ['date_to_unix_s', 'REQUEST_BODY', 'REQUEST_HEADER', 'remove_duplicate_direct',
           'format_direct_flight', 'format_transfer_flight']


def date_to_unix_s(year, month, day):
    '''
    Get the unix timestamp of the given date in GMT+0, independent of system timezone.
    '''
    dt = datetime.datetime(year, month, day, 0, 0, 0, tzinfo=datetime.timezone.utc)
    result = calendar.timegm(dt.utctimetuple())
    assert (result % (24 * 3600) == 0)
    return result


REQUEST_BODY = '''{
  "mode": 0,
  "searchCriteria": {
    "grade": 3,
    "tripType": 1,
    "journeyNo": 1,
    "passengerInfoType": {
      "adultCount": 1,
      "childCount": 0,
      "infantCount": 0
    },
    "journeyInfoTypes": [
      {
        "journeyNo": 1,
        "departDate": "$YYYY$-$MM$-$DD$",
        "departCode": "$CITY1$",
        "arriveCode": "$CITY2$",
        "departAirport": "$AIRPORT1$",
        "arriveAirport": "$AIRPORT2$"
      }
    ],
    "policyId": null,
    "productId": ""
  },
  "sortInfoType": {
    "direction": true,
    "orderBy": "Direct",
    "topList": []
  },
  "tagList": [],
  "filterType": {
    "filterFlagTypes": [],
    "queryItemSettings": [],
    "studentsSelectedStatus": true
  },
  "abtList": [
    {
      "abCode": "240319_IBU_ollrc",
      "abVersion": "B"
    },
    {
      "abCode": "240509_IBU_RFUO",
      "abVersion": "B"
    }
  ],
  "head": {
    "cid": "09031105115243857021",
    "ctok": "",
    "cver": "3",
    "lang": "01",
    "sid": "8888",
    "syscode": "40",
    "auth": "",
    "xsid": "",
    "extension": [
      {
        "name": "abTesting",
        "value": "M:-1,231213_IBU_OSPCL:A;M:52,240308_IBU_olrp:B;M:65,240319_IBU_ollrc:B;M:-1,240425_IBU_OMPA:A;M:40,240417_IBU_Ohtwl:A;M:19,240418_IBU_zfsxo:B;M:13,240509_IBU_RFUO:B;M:0,240614_IBU_ofapi:B;M:26,240701_IBU_OL071:A;M:84,240731_IBU_olusp:D;M:72,240730_IBU_CTMMA:A;M:85,240820_IBU_MCCTR:A;M:26,240701_IBU_OL071:A;M:26,240701_IBU_OL071:A;M:26,240701_IBU_OL071:A;M:26,240701_IBU_OL071:A;M:26,240701_IBU_OL071:A;"
      },
      {
        "name": "source",
        "value": "ONLINE"
      },
      {
        "name": "sotpGroup",
        "value": "Trip"
      },
      {
        "name": "sotpLocale",
        "value": "en-US"
      },
      {
        "name": "sotpCurrency",
        "value": "USD"
      },
      {
        "name": "allianceID",
        "value": "0"
      },
      {
        "name": "sid",
        "value": "0"
      },
      {
        "name": "ouid",
        "value": ""
      },
      {
        "name": "uuid"
      },
      {
        "name": "useDistributionType",
        "value": "1"
      },
      {
        "name": "flt_app_session_transactionId",
        "value": "53b70d2f-72ed-4c20-8771-cd511edda0d9"
      },
      {
        "name": "vid",
        "value": "1726527039151.9773wh5iFZDi"
      },
      {
        "name": "pvid",
        "value": "8"
      },
      {
        "name": "Flt_SessionId",
        "value": "1"
      },
      {
        "name": "channel"
      },
      {
        "name": "x-ua",
        "value": "v=3_os=ONLINE_osv=10.15.7"
      },
      {
        "name": "PageId",
        "value": "10320667452"
      },
      {
        "name": "clientTime",
        "value": "2024-09-16T18:53:41-04:00"
      },
      {
        "name": "SpecialSupply",
        "value": "false"
      },
      {
        "name": "LowPriceSource",
        "value": "searchForm"
      },
      {
        "name": "Flt_BatchId",
        "value": "1983cc24-6e1f-4e3e-a2e9-284ff84602e1"
      },
      {
        "name": "BlockTokenTimeout",
        "value": "0"
      }
    ],
    "appid": "700020"
  }
}'''

REQUEST_HEADER = {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'text/event-stream',
    'Content-Length': ''
}


def remove_duplicate_direct(flights):
    lowest_price = {}
    lowest_index = {}
    for i in range(0, len(flights)):
        flight = flights[i]
        flight_number = flight['segments'][0]['flight_number']
        price = flight['price']
        if (flight_number not in lowest_price):
            lowest_price[flight_number] = price
            lowest_index[flight_number] = i
            continue
        if (price < lowest_price[flight_number]):
            lowest_price[flight_number] = price
            lowest_index[flight_number] = i
    new_flights = []
    for _, v in lowest_index.items():
        new_flights.append(flights[v])
    return new_flights


def pad_space(s: str, length: int) -> str:
    end = (length - len(s)) // 2
    front = length - len(s) - end
    return ' ' * front + s + ' ' * end


def format_direct_flight(flight) -> str:
    price = flight['price']
    flight = flight['segments'][0]
    flight_number = flight['flight_number']
    src_airport = flight['src_airport']
    src_city_name = flight['src_city_name']
    dest_airport = flight['dest_airport']
    dest_city_name = flight['dest_city_name']
    start_time = flight['start_time']
    end_time = flight['end_time']
    flight_number = pad_space(flight_number, 6)
    src_display = f'{src_city_name} ({src_airport})'
    dest_display = f'{dest_city_name} ({dest_airport})'
    src_display = src_display[:20]
    dest_display = dest_display[:20]
    src_display = pad_space(src_display, 20)
    dest_display = pad_space(dest_display, 20)
    price = f'{price} USD'
    price = price[:8]
    price = pad_space(price, 8)
    return f'| {flight_number} | {src_display} -> {dest_display} | {start_time} ~ {end_time} | {price} |'


def format_transfer_flight(flight) -> str:
    origin_flight = flight
    price = flight['price']
    price = f'{price} USD'
    price = price[:8]
    price = pad_space(price, 8)
    flight = flight['segments'][0]
    flight_number = flight['flight_number']
    flight_number = pad_space(flight_number, 6)
    src_airport = flight['src_airport']
    src_city_name = flight['src_city_name']
    dest_airport = flight['dest_airport']
    dest_city_name = flight['dest_city_name']
    start_time = flight['start_time']
    second_flight = origin_flight['segments'][1]
    third_airport = second_flight['dest_airport']
    third_city_name = second_flight['dest_city_name']
    src_display = f'{src_city_name} ({src_airport})'
    dest_display = f'{dest_city_name} ({dest_airport})'
    third_display = f'{third_city_name} ({third_airport})'
    src_display = src_display[:20]
    dest_display = dest_display[:20]
    third_display = third_display[:20]
    src_display = pad_space(src_display, 20)
    dest_display = pad_space(dest_display, 20)
    third_display = pad_space(third_display, 20)
    return f'| {flight_number} | {start_time} | {src_display} -> {dest_display} -> {third_display} | {price} |'
