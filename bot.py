#coding:utf-8

import telebot, config
import requests
import datetime

bot = telebot.TeleBot(config.TOKEN)

urlForStop = "https://lad.lviv.ua/api/stops/"
hour = datetime.datetime.now().hour # for recommendation

vechiles = {"bus": "Авт.", "trol": "Трл.", "tram": "Трм."}
n = 57 # number of "-" symbols


# start bot
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Щоб дізнатися коли приїде транспорт, введіть номер зупинки.")


# help menu
@bot.message_handler(commands=["help"])
def help(message):
    info = "Позначення:\nАвт. - автобус(маршрутка)\nТрл. - тролейбус\nТрм. - трамвай\n"
    info += "\nВідображення маршруту:\n" + n*"-" + "\nТип    Маршрут    Кінцева    Час\n" + n*"-" + "\n"
    info += "\nФункції:\nЩоб дізнатися час прибуття транспорту, введіть номер зупинки."
    bot.send_message(message.chat.id, info)


# get data by stop id
@bot.message_handler(regexp="^[0-9]+$")
def dataByStop(message):
    stopId = message.text # bus stop code
    stopUrl = urlForStop + stopId

    data = requests.get(stopUrl) # recieved data
    if data:
        data = data.json()
        information = "Зупинка №{}\n{}\n".format(data["code"], data["name"])
        if len(data["timetable"]) == 0: # if there is no transport
            information += "\nНа жаль, на потрібному маршруті зараз немає транспорту. Будь ласка, виберіть інший маршрут."
            bot.send_message(message.chat.id, information)
            if hour == 23 or 0 <= hour <= 6: # if night time
                bot.send_message(message.chat.id, "І ще одне... Надворі вже ніч, тому краще їдьте додому заради Вашої безпеки.")

        else: # ok
            information += "\nМаршрути:\n"
            information += n*"-" + "\n"
            for row in data["timetable"]:
                # route data
                transportType = vechiles[row["vehicle_type"]]
                route_name = row["route"]
                end_stop = row["end_stop"]
                mins = row["time_left"]

                information += "{}   \"{}\"   {}   {}\n".format(transportType, route_name, end_stop, mins)
                information += n*"-" + "\n"
            bot.send_message(message.chat.id, information)

    else: # bus stop not found
        bot.send_message(message.chat.id, "Такої зупинки не існує. Введіть правильний номер зупинки.")


# anything else except bus stop number
@bot.message_handler()
def tryAgain(message):
    bot.send_message(message.chat.id, "Будь ласка, введіть номер зупинки.")


if __name__ == "__main__":
    bot.polling()