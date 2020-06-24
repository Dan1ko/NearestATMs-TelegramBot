import telebot
from telebot import types
from config import my_token, connection
import csv
import folium
import pandas as pd

token = my_token
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение", reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def get_location(message):
# getting location from user____________________________________________________________________________________________
    if get_location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        msg = bot.reply_to(message, 'Одну секунду')
# connection to database________________________________________________________________________________________________
        with connection.cursor() as cursor:
# Read 5 closest objects________________________________________________________________________________________________
            sql1 = "SELECT object_latitude, object_longitude, object_address,  SQRT(POW(69.1 * (object_latitude - {}), 2) + POW" \
                  "(69.1 * ({} - object_longitude) * COS(object_latitude / 57.3), 2)) AS distance FROM optima_bank " \
                  "HAVING distance < 1 ORDER BY distance LIMIT 0,5;".format(latitude, longitude)

            sql2 = "SELECT object_type, object_address, SQRT(POW(69.1 * (object_latitude - {}), 2) + POW" \
                   "(69.1 * ({} - object_longitude) * COS(object_latitude / 57.3), 2)) AS distance FROM optima_bank " \
                   "HAVING distance < 1 ORDER BY distance LIMIT 0,5;".format(latitude, longitude)
            cursor.execute(sql1)
            results = cursor.fetchall()
# saving results of query to csv file
            with open('adresa.csv', 'w+', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f, fieldnames=list(results[0].keys()), quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
# pin the addresses to a map in html
            addresses = pd.read_csv('adresa.csv')
            addresses.head()
            map1 = folium.Map([latitude, longitude], zoom_start=70)
            for index, row in addresses.iterrows():
                folium.CircleMarker([row['object_latitude'], row['object_longitude']],
                                    radius=10,
                                    popup=row['object_address'],
                                    fill_color='#3db7e4',).add_to(map1)
            map1.save('map.html')
            # Read 5 closest objects________________________________________________________________________________________________

            cursor.execute(sql2)
            results = cursor.fetchall()
            bot.send_message(message.chat.id, text='Ближайшие филиалы/терминалы:')
            for result in results:
                type = result['object_type']
                addr = result['object_address']
                bot.send_message(message.chat.id, text=f'{type}  {addr}')

            f = open('/home/daniko/Desktop/locabot/map.html', 'rb')
            bot.send_document(message.chat.id, f)

if __name__=='__main__':
    bot.polling(none_stop=True)
