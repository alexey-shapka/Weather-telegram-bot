import requests
import json
import datetime
from translate import Translator
from opencage.geocoder import OpenCageGeocode
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

translator_ru = Translator(to_lang="ru")
translator_en = Translator(to_lang="en")

token_weather = ''
token_geocoder = ''
geocoder = OpenCageGeocode(token_geocoder)

en_pattern = [("{} {}\n""Temperature : {} ℃\n""Wind : {} m/sec\n""Humidity : {} %\n""Pressure : {} hPa\n""***Location : {}***"),
    ("***Time : {}***\n""{} {}\n""Temperature : {} ℃\n""Wind : {} m/sec\n""Humidity : {} %\n"), 'Temperature ℃', 'Wind m/sec', 
        'Humidity %', 'Forecast']

ru_pattern = [("{} {}\n""Температура : {} ℃\n""Скорость ветра : {} м/сек\n""Влажность : {} %\n""Давление : {} гПа\n""***Местоположение : {}***"),
    ("***Время : {}***\n""{} {}\n""Температура : {}℃\n""Скорость ветра : {} м/сек\n""Влажность : {} %\n"), 'Температура ℃', 'Ветер м/сек', 
        'Влажность %', "Прогноз на"]

emoji_weather = {'01d' : '☀️', '02d' : '⛅️', '03d' : '☁️', '04d' : '☁️', '09d' : '🌧', '10d': '🌦', '11d' : '⛈', '13d': '🌨', '50d': '🌫'}

def GetNowWeather(lon, lat, lang):
    req = requests.get('http://api.openweathermap.org/data/2.5/weather?appid={}&mode=json&lat={}&lon={}&units=metric&lang={}'.format(token_weather, lat, lon, lang))
    jreq = json.loads(req.text)

    if lang == 'en':
        result = en_pattern[0]
        formating_city = jreq['name']
    else:
        result = ru_pattern[0]
        formating_city = translator_ru.translate(jreq['name'])

    return result.format(jreq['weather'][0]['description'].capitalize(), emoji_weather[jreq['weather'][0]['icon'].replace('n', 'd')],
                        jreq['main']['temp'], jreq['wind']['speed'], jreq['main']['humidity'],
                        jreq['main']['pressure'], formating_city).rstrip()

def GetDayWeather(lon, lat, lang):
    req = requests.get('http://api.openweathermap.org/data/2.5/forecast?appid={}&mode=json&lat={}&lon={}&units=metric&lang={}'.format(token_weather, lat, lon, lang))
    jreq = json.loads(req.text)
    now = datetime.datetime.now()
    day = '{}-{}-{}'.format(now.year, str(now.month).rjust(2, '0'), str(now.day).rjust(2, '0'))

    if lang == 'ru':
        mode = ru_pattern
    else:
        mode = en_pattern

    result = ""
    for i in jreq['list']:
        if day in i['dt_txt']:
            formating_pattern = [i['dt_txt'][11:-3], i['weather'][0]['description'].capitalize(),
                                emoji_weather[i['weather'][0]['icon'].replace('n', 'd')],
                                i['main']['temp'], i['wind']['speed'], i['main']['humidity']]
            result += mode[1].format(*formating_pattern) + '\n'
        else:
            break
            
    return result[95:].rstrip()

def GetWeatherOnXdays(lon, lat, days, lang, formating, id):
    req = requests.get('http://api.openweathermap.org/data/2.5/forecast?appid={}&mode=json&lat={}&lon={}&units=metric&lang={}'.format(token_weather, lat, lon, lang))
    jreq = json.loads(req.text)
    now = datetime.datetime.now()
    format_days = []
    for i in [now + datetime.timedelta(days=i) for i in range(1, days+1, 1)]:
        format_days.append('{}-{}-{}'.format(i.year, str(i.month).rjust(2, '0'), str(i.day).rjust(2, '0')))

    if lang == 'ru':
        mode = ru_pattern
    else:
        mode = en_pattern

    if formating == 'text':
        result = []
        part = ''
        for i in jreq['list']:
            if i['dt_txt'][:10] in format_days:
                if i['dt_txt'][:10] not in part:
                    if len(part) != 0: 
                        result.append(part)
                        part = ''
                    part += "***{}***\n".format(i['dt_txt'][:10])
                formating_pattern = [i['dt_txt'][11:-3], i['weather'][0]['description'].capitalize(),
                                    emoji_weather[i['weather'][0]['icon'].replace('n', 'd')],
                                    i['main']['temp'], i['wind']['speed'], i['main']['humidity']]
                part += mode[1].format(*formating_pattern) + '\n'
        result.append(part)
        return result 

    else:
        Values = [[], [], [], []]
        Colors = ['#ffc32d', '#54c2ff', '#011c70']

        for i in jreq['list']:
            if i['dt_txt'][:10] in format_days:
                Values[0].append(round(float(i['main']['temp']), 1))
                Values[1].append(round(float(i['wind']['speed']), 1))
                Values[2].append(round(float(i['main']['humidity']), 1))
                Values[3].append(i['dt_txt'][11:-3])

        plt.figure(figsize=(15, 6))
        ax = plt.gca()
        x_range = [j for j in range(len(Values[0]))]
        for i in range(len(Values)-1):
            plt.plot(x_range, Values[i], marker = 'o', label = mode[i + 2], color = Colors[i])
            plt.xticks(x_range, Values[3], rotation = 45)
            for i,j in zip(x_range, Values[i]):
                ax.annotate(str(j),xy = (i-0.5, j+1))
        plt.legend(bbox_to_anchor = (0., -0.2, 1., .102), loc = 8, ncol = 3, mode = "expand", borderaxespad = 0, framealpha = 0)
        if format_days[0] != format_days[-1:][0]:
            plt.title('{}  {} — {}'.format(mode[5], format_days[0][5:].replace('-', '.'), format_days[-1:][0][5:].replace('-', '.')))
        else:
            plt.title('{}  {}'.format(mode[5], format_days[0][5:].replace('-', '.')))
        plt.subplots_adjust(wspace = 0.1, hspace = 1, bottom = 0.2, top = 0.93, left = 0.04, right= 0.96)
        id_name = '{}.png'.format(id)
        plt.savefig(id_name)

        return id_name

def ConvertInput(text):
    g = geocoder.geocode(text)
    return (g[0]['geometry']['lng'], g[0]['geometry']['lat'])