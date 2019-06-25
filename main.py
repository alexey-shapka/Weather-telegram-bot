import telebot
import weather
from os import remove

token_bot = ''
bot = telebot.TeleBot(token_bot)

print("Weather bot was started..")

#{id : [(long, lat), language, input_flag, format_forecast]}
global d
d = dict()

answers = {'en' : ["Send location", "Press button to send location.", "Choose the language :", "You need to send your location.",
                   "Choose the number of days to forecast :", "Your location was successfully saved!",
                    "Language was successfully changed!", 'Write location', 'Choose the variant :', 'Input location :', 'Not found.',
                    'Change language', 'Change formating forecast', 'Picture', 'Text', 'Changes have been successfully saved!', 
                    'The day is coming over.\nYou can use \'now\' command.'],
           'ru' : ["Отправить местоположение", "Нажмите кнопку для отправки местоположения", "Выберите язык :",
                   "Вам нужно отправить ваше местоположение.", "Выберите количество дней для прогноза :",
                   "Ваше местоположение было успешно сохранено!", "Язык был успешно изменен!", "Ввести населенный пункт", 'Выберите вариант :',
                   'Введите населенный пункт :', 'Местоположение не найдено.', 'Изменить язык', 'Изменить вид прогноза',
                   'Картинка', 'Текст', 'Изменения были успешно сохранены!', 'День подходит к концу.\nВы можете использовать команду \'now\'.']}

def Saved_dict():
    global d
    f = open('data.txt', 'w')
    for key, values in d.items():
        f.write("{} {} {} {}\n".format(str(key), "{} {} {}".format(str(values[0][0]), str(values[0][1]), str(values[1])), str(values[2]), str(values[3])))
    f.close()

def Load_dict():
    global d
    f = open('data.txt', 'r').readlines()
    for i in f:
        k = i.split(" ")
        d[int(k[0])] = [(float(k[1]), float(k[2])), k[3], bool(k[4]), str(k[5]).replace('\n', '')]

try:
    Load_dict()
except:
    pass

def CheckFunction(message):
    global d
    if message.chat.id not in d:
        d[message.chat.id] = [(0, 0), 'en', False, 'text']
        Saved_dict()

@bot.message_handler(commands = ['start'])
def start(message):
    CheckFunction(message)
    bot.send_message(message.chat.id, "I am weather bot. My list of commands will help you!")

@bot.message_handler(commands = ['location'])
def location(message):
    global d
    CheckFunction(message)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton(text = answers[d[message.chat.id][1]][0], callback_data = "geo_button"),
               telebot.types.InlineKeyboardButton(text = answers[d[message.chat.id][1]][7], callback_data = "geo_text"))
    bot.send_message(message.chat.id, answers[d[message.chat.id][1]][8], reply_markup = markup)

@bot.message_handler(commands = ['settings'])
def settings(message):
    global d
    CheckFunction(message)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text = answers[d[message.chat.id][1]][11], callback_data = "lang"))
    markup.add(telebot.types.InlineKeyboardButton(text = answers[d[message.chat.id][1]][12], callback_data = "format"))

    bot.send_message(message.chat.id, answers[d[message.chat.id][1]][8], parse_mode = 'markdown', reply_markup = markup)

@bot.message_handler(commands = ['now'])
def now(message):
    global d
    CheckFunction(message)

    if sum(d[message.chat.id][0]) == 0:
        bot.send_message(message.chat.id, answers[d[message.chat.id][1]][3])
    else:
        bot.send_message(message.chat.id, weather.GetNowWeather(*d[message.chat.id][0], d[message.chat.id][1]), parse_mode = 'markdown')

@bot.message_handler(commands = ['today'])
def today(message):
    global d
    CheckFunction(message)

    if sum(d[message.chat.id][0]) == 0:
        bot.send_message(message.chat.id, answers[d[message.chat.id][1]][3])
    else:
        text = weather.GetDayWeather(*d[message.chat.id][0], d[message.chat.id][1])
        if len(text) == 0:
            bot.send_message(message.chat.id,  answers[d[message.chat.id][1]][16], parse_mode = 'markdown')
        else:
            bot.send_message(message.chat.id, text, parse_mode = 'markdown')

@bot.message_handler(commands = ['forecast'])
def forecast(message):
    global d
    CheckFunction(message)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(*[telebot.types.InlineKeyboardButton(text = str(i+1), callback_data = "{}days".format(str(i+1))) for i in range(5)])

    if sum(d[message.chat.id][0]) == 0:
        bot.send_message(message.chat.id, answers[d[message.chat.id][1]][3])
    else:
        bot.send_message(message.chat.id, answers[d[message.chat.id][1]][4], parse_mode = 'markdown', reply_markup=markup)


@bot.message_handler(func = lambda message: True, content_types = ['location'])
def location(message):
    global d
    if message.location is not None:
        longitude, latitude = message.location.longitude, message.location.latitude
        if message.chat.id not in d:
            d[message.chat.id] = [(longitude, latitude), 'en', False, 'text']
            Saved_dict()
        else:
            d[message.chat.id][0] = (longitude, latitude)
            Saved_dict()
        bot.send_message(message.chat.id, text = answers[d[message.chat.id][1]][5], reply_markup = telebot.types.ReplyKeyboardRemove())

@bot.callback_query_handler(func = lambda call:True)
def inlin(call):
    global d
    if 'days' in call.data:
        text = weather.GetWeatherOnXdays(*d[call.message.chat.id][0], int(call.data[0]), d[call.message.chat.id][1], d[call.message.chat.id][3], call.message.chat.id)
        if d[call.message.chat.id][3] == 'text':
            for i in text:
                bot.send_message(chat_id = call.message.chat.id, text = i, parse_mode = 'markdown')
        elif d[call.message.chat.id][3] == 'picture':
            bot.send_photo(chat_id = call.message.chat.id, photo = open(text, 'rb'))
            remove(text)

    elif call.data == 'lang':
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton(text = 'en', callback_data = "en_lg"), 
                   telebot.types.InlineKeyboardButton(text = 'ru', callback_data = "ru_lg"))
        bot.send_message(call.message.chat.id, answers[d[call.message.chat.id][1]][2], parse_mode = 'markdown', reply_markup = markup)

    elif call.data == 'format':
        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(telebot.types.InlineKeyboardButton(text = answers[d[call.message.chat.id][1]][14], callback_data = "f_text"),
                   telebot.types.InlineKeyboardButton(text = answers[d[call.message.chat.id][1]][13], callback_data = "f_picture"))
        bot.send_message(call.message.chat.id, answers[d[call.message.chat.id][1]][8], parse_mode = 'markdown', reply_markup = markup)

    elif call.data == 'f_text':
        d[call.message.chat.id][3] = 'text'
        Saved_dict()
        bot.send_message(chat_id = call.message.chat.id, text = answers[d[call.message.chat.id][1]][15], parse_mode = 'markdown')

    elif call.data == 'f_picture':
        d[call.message.chat.id][3] = 'picture'
        Saved_dict()
        bot.send_message(chat_id = call.message.chat.id, text = answers[d[call.message.chat.id][1]][15], parse_mode = 'markdown')

    elif call.data == 'en_lg':
        d[call.message.chat.id][1] = 'en'
        Saved_dict()
        bot.send_message(chat_id = call.message.chat.id, text = answers[d[call.message.chat.id][1]][6], parse_mode = 'markdown')

    elif call.data == 'ru_lg':
        d[call.message.chat.id][1] = 'ru'
        Saved_dict()
        bot.send_message(chat_id=call.message.chat.id, text = answers[d[call.message.chat.id][1]][6], parse_mode = 'markdown')

    elif call.data == 'geo_button':
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        button_geo = telebot.types.KeyboardButton(text = answers[d[call.message.chat.id][1]][0], request_location = True)
        keyboard.add(button_geo)
        bot.send_message(call.message.chat.id, answers[d[call.message.chat.id][1]][1], reply_markup = keyboard)
        
    elif call.data == 'geo_text':
        d[call.message.chat.id][2] = True
        Saved_dict()
        bot.send_message(call.message.chat.id, answers[d[call.message.chat.id][1]][9])

@bot.message_handler(func = lambda message: True, content_types = ['text'])
def input(message):
    global d
    if d[message.chat.id][2] == True:
        result = weather.ConvertInput(message.text)
        if sum(result) > 0:
            d[message.chat.id][0] = result 
            bot.send_message(message.chat.id, answers[d[message.chat.id][1]][5])
        else:
            bot.send_message(message.chat.id, answers[d[message.chat.id][1]][10])
        d[message.chat.id][2] = False
        Saved_dict()
        
bot.polling(none_stop = True)