#!/usr/bin/env python3

import subprocess
import json
import os
import time
import logging
import traceback
import urllib.request
import sys
import argparse
from extractweatherdata import DataPoint


def get_weather_json():
    """
    Gets the weather data from openweather

    Requires the packages geoip, geoip extra data (for city) and api key from
    openweather. The API key can be generated free of charge. The packages
    geoip and the extra data can also be downloaded for free.

    First the local ip is being requested with which we lookup the current
    location. It should respond with the country and city and some additional
    information. We extract the country code and the city with which we send a
    request to the openweather API to return the weather data as a JSON.
    """
    counter = 0
    while not connect():
        if counter > 3:
            sys.exit(0)
        time.sleep(300)
    local_ip = subprocess.check_output(
        ["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"])
    # There seem to be issues sometimes with the above command. I do not know
    # what this is caused by. I might just replace it with the one below. I
    # don't know if it is more reliable though.
    if not local_ip:
        local_ip = subprocess.check_output([
            "dig", "TXT", "+short", "o-o.myaddr.l.google.com",
            "@ns1.google.com"
        ])[1:-2]
    logging.info("local IP:" + str(local_ip))
    # I think this should be replaced with the module ipinfo
    # (https://github.com/ipinfo/python)
    current_location = subprocess.check_output(["geoiplookup",
                                                local_ip]).decode("utf-8")
    logging.info("Current Location:" + str(current_location))
    latitude_pos = find_nth(current_location, ',', 7) + 2
    longitude_pos = current_location.find(',', latitude_pos) + 2
    latitude = current_location[latitude_pos:longitude_pos - 4]
    longitude = current_location[longitude_pos:current_location.
                                 find(',', longitude_pos) - 4]
    API_KEY = os.getenv("OPENWEATHER")
    api_call = "https://api.openweathermap.org/data/2.5/onecall?lat=" + \
        str(latitude) + "&lon=" + str(longitude) + \
        "&exclude=minutely&units=metric&appid=" + str(API_KEY)
    api_return = subprocess.check_output(["curl", api_call])
    logging.debug(api_return)
    return json.loads(api_return)


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def get_json(path_to_file="/tmp/weather",
             filename="weather.json",
             ttl=3600,
             force_poll=False):
    """
    Creates a file if no file exists, checks if the file needs to be updated 
    and return the JSON
    """
    file_descriptor = None
    if not os.path.exists(path_to_file):
        os.makedirs(path_to_file)
        file_descriptor = open(path_to_file + "/" + filename, 'w')
        ttl = -1  # just created the file we need to always poll the API
        logging.info('Created path and file')
    elif not os.path.exists(path_to_file + "/" + filename):
        file_descriptor = open(path_to_file + "/" + filename, 'w')
        ttl = -1  # just created the file we need to always poll the API
        logging.info('Created file')
    else:
        file_descriptor = open(path_to_file + "/" + filename, 'r+')
        logging.info('Opened file')

    return poll_API(ttl, file_descriptor, force_poll)


def poll_API(ttl, file_descriptor, force_poll):
    """
    Polls the API if the file is older than ttl
    """
    last_modified = os.stat(file_descriptor.name).st_mtime
    logging.info("Polling? lm: " + str(last_modified) + ", time: " +
                 str(int(time.time())))
    is_empty = os.stat(file_descriptor.name).st_size < 110
    weather_json = None
    if force_poll or last_modified + ttl < int(time.time()) or is_empty:
        file_descriptor.truncate()
        logging.info("Poll API")
        weather_json = get_weather_json()
        logging.info("Dumping JSON")
        json.dump(weather_json, file_descriptor)
    else:
        logging.info("Loading JSON")
        weather_json = json.load(file_descriptor)
    return weather_json


def connect(host='http://google.com'):
    """
    Check if connected to the internet
    (https://www.codespeedy.com/how-to-check-the-internet-connection-in-python/)
    """
    try:
        urllib.request.urlopen(host)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Return weather data depending on current IP")
    parser.add_argument(
        "-d",
        action='store_true',
        help="Returns the weather forcast of the current day at different times"
    )
    parser.add_argument("-w",
                        action='store_true',
                        help="Returns the weather forcast of the current week")
    parser.add_argument("-f",
                        action='store_true',
                        help="Force polling the OpenWeather API")
    args = parser.parse_args()

    logging.basicConfig(filename="weather.log",
                        level=logging.INFO,
                        format='%(asctime)s %(message)s')
    logging.info('Getting JSON')
    weather_json = None
    try:
        weather_json = get_json(ttl=1800, force_poll=args.f)
        print(weather_json)
        logging.info('Finished getting JSON')
    except Exception:
        logging.error(traceback.format_exc())
    print(weather_json)
    print(args)
    dp = DataPoint(weather_json["current"])
    print(dp.weather.weather.font_icon, str(dp.temp) + "C°")
