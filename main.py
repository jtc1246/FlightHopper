# from airports import ALL_AIRPORTS
from myHttp import http
from airport_city_info import AIRPORT_TO_CITY, CITY_TO_AIRPORTS
from reachable_cities import REACHABLE_CITIES

 # airports that cannot find city code on trip.com, these are all very small airports
NO_CITY_AIRPORTS = ['JRT', 'TKP']

print(len(REACHABLE_CITIES))


URL2 = 'https://us.trip.com/restapi/soa2/27015/FlightListSearchSSE'

body = '''{
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
        "departAirport": "",
        "arriveAirport": ""
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

HEADER = {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'text/event-stream',
    'Content-Length': ''
}

