#!/usr/bin/env python3
from datetime import datetime
from enum import Enum
import json
import nerdfonts as nf


class DataPoint:
    def __init__(self, json_datapoint):
        self.time = datetime.fromtimestamp(
            json_datapoint["dt"]).strftime('%H:%M')
        self.day = datetime.fromtimestamp(json_datapoint["dt"]).strftime('%d')
        self.temp = json_datapoint["feels_like"]
        self.weather = Weather(json_datapoint["weather"][0])


"""
Enum of different weather types
"""


class WeatherIcons(Enum):
    SUN = 0
    CLOUDY = 1
    CLOUDYRAIN = 2
    RAIN = 3
    THUNDER = 4
    SNOW = 5
    MIST = 6


class WeatherIcon:
    path = "./weather_icons/"
    icons = ["01_sunny.png", "02_cloudy.png", "03_cloudy_rain.png", "04_rain.png",\
             "05_thunder.png", "06_snow.png", "07_mist.png"]
    font_icons = ["", "", "", "", "", "", ""]

    def __init__(self, weather_type):
        self.icon = self.path + self.icons[weather_type.value]
        self.font_icon = self.font_icons[weather_type.value]


class Weather:
    def __init__(self, weather_json):
        self.weather_data = weather_json
        self.icons = {
            "01": nf.icons['weather_day_sunny'],
            "02": nf.icons["weather_day_cloudy"],
            "03": nf.icons["weather_cloud"],
            "04": nf.icons["weather_cloudy"],
            "09": nf.icons["weather_rain"],
            "10": nf.icons["weather_day_rain"],
            "11": nf.icons["weather_thunderstorm"],
            "13": nf.icons["weather_snow"],
            "50": nf.icons["weather_fog"],
        }

    def get_current_weather(self):
        current_time_json = weather_json["current"]
        current_weather_json = current_time_json["weather"][0]
        time = self.epoch_to_time(current_time_json["dt"])
        sunrise = self.epoch_to_time(current_time_json["sunrise"])
        sunset = self.epoch_to_time(current_time_json["sunset"])
        temp = (current_time_json["temp"], current_time_json["feels_like"])
        weather = current_weather_json["description"]
        icon = self.associate_id_to_icon(current_weather_json["icon"])
        return (time, sunrise, sunset, temp, weather, icon)

    def get_rest_of_day_hourly_weather(self):
        hourly_weather = weather_json["hourly"]
        find_index = 1
        while self.epoch_to_time(hourly_weather[find_index]["dt"]) != "00:00":
            find_index += 1

        rest_of_day = hourly_weather[:find_index]
        result = []
        for hour in rest_of_day:
            time = self.epoch_to_time(hour["dt"])
            temp = (hour["temp"], hour["feels_like"])
            weather = hour["weather"][0]["description"]
            icon = self.associate_id_to_icon(hour["weather"][0]["icon"])
            pop = hour["pop"]
            result.append((time, temp, weather, icon, pop))
        return result

    def get_tomorrow_hourly_weather(self):
        hourly_weather = weather_json["hourly"]
        find_index = 1
        while self.epoch_to_time(hourly_weather[find_index]["dt"]) != "00:00":
            find_index += 1

        tomorrow = hourly_weather[find_index:find_index+24]
        result = []
        for hour in tomorrow:
            time = self.epoch_to_time(hour["dt"])
            temp = (hour["temp"], hour["feels_like"])
            weather = hour["weather"][0]["description"]
            icon = self.associate_id_to_icon(hour["weather"][0]["icon"])
            pop = hour["pop"]
            result.append((time, temp, weather, icon, pop))
        return result
    
    def epoch_to_time(self, epoch):
        return datetime.fromtimestamp(epoch).strftime('%H:%M')

    def associate_id_to_icon(self, icon_code):
        """ Associates icons to the specified ids at
        https://openweathermap.org/weather-conditions
        """
        return self.icons[icon_code[0:2]]
    

weather_json = json.load(open("weather.json", "r"))
weather = Weather(weather_json)
# print(weather.get_current_weather())
print(weather.get_tomorrow_hourly_weather())
