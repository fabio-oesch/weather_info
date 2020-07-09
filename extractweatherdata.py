#!/usr/bin/env python3
from datetime import datetime
from enum import Enum

class DataPoint:
    def __init__(self, json_datapoint):
        self.time = datetime.fromtimestamp(json_datapoint["dt"]).strftime('%H:%M')
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
    def __init__(self, json_weather_datapoint):
        self.id = int(json_weather_datapoint["id"])
        self.description = json_weather_datapoint["description"]
        self.weather = WeatherIcon(self.associate_id_to_icon())

    def associate_id_to_icon(self):
        """ Associates icons to the specified ids at
        https://openweathermap.org/weather-conditions
        """
        if self.id < 300:
            return WeatherIcons.THUNDER
        elif 300 <= self.id < 400:
            return WeatherIcons.CLOUDYRAIN
        elif self.id == 511 or 600 <= self.id < 700:
            return WeatherIcons.SNOW
        elif 500 <= self.id < 600:
            return WeatherIcons.RAIN
        elif 700 <= self.id < 800:
            return WeatherIcons.MIST
        elif self.id == 800:
            return WeatherIcons.SUN
        else:
            return WeatherIcons.CLOUDY
