# FlightHopper

## Introduction

The purpose of this project is to find cheaper transfer flights. For example, if you want to go from A to B, sometimes A -> B -> C will be cheaper than A -> B, then you can buy A -> B -> C ticket and leave at B. The purpose of this project is to find the C cities that save money for you.

Consider this, I want to go from San Francisco to Detroit, but ...

<img src="resources/sfo_dtw.png" width="75%">
<img src="resources/sfo_dtw_cmh.png" width="75%">

&nbsp;

Name of this project is from ChatGPT:
https://chatgpt.com/share/66e89fd5-ed84-8009-b485-f33abff78ff7

## Installation

```bash
pip3 install FlightHopper
```

## Usage

```python
import FlightHopper

FlightHopper.search_transfer_flights('LAX', 'DTW', '20241119')
```

Date should be 8-digit string. Departure and destination can be 3-letter city code or 3-letter airport code.

## Data Source

Flight price data is from [trip.com](https://us.trip.com/).

Airport (city) and reachability data is from [flightradar24.com](https://www.flightradar24.com/).
