import json
import requests
import time
import vk_api
import datetime
from timeout import timeout
import os
import sys

#!!!!
#Надо изменить на свои данные!!!
vk = vk_api.VkApi(token = "TOKEN") #Токен ВК
peer_id = 199776748 # ID переписки, куда слать сообщения
mode = "buy" # Режим работы buy - покупка $/ sell - продажа доллара
#!!!!


def vk_send(text):
	print(text)
	try:
		vk.method("messages.send",{"random_id":0,"message":text,"peer_id":peer_id})
	except:
		time.sleep(10)
		vk.method("messages.send",{"random_id":0,"message":text,"peer_id":peer_id})

def vk_edit(text,message_id):
	print(text)
	try:
		vk.method("messages.edit",{"peer_id":peer_id,"message":text,"message_id": message_id})
	except:
		time.sleep(10)
		vk.method("messages.send",{"random_id":0,"message":text,"peer_id":peer_id})


@timeout(10)
def get_response():
	return requests.get("https://api.tinkoff.ru/v1/currency_rates")

def get_dollar_exchange():
	try:
		response = get_response()
		jsons = json.loads(response.text)
		buy = jsons["payload"]["rates"][1]["buy"]
		sell = jsons["payload"]["rates"][1]["sell"]
		for i in range(0,14):
			get_response()
		return buy,sell
	except Exception:
		return 0,0
	except KeyboardInterrupt:
		sys.exit()

def get_message():
	try:
		return vk.method("messages.getHistory", {"peer_id": peer_id, "count": 1})
	except Exception:
		time.sleep(10)
		return vk.method("messages.getHistory", {"peer_id": peer_id, "count": 1})


def send_message_in_zeros(buy):
	message = get_message()
	message_id = message.get("items")[0].get("id")
	message_text = message.get("items")[0].get("text")
	if "Курс $ на данный момент:" in message_text:
		vk_edit("Курс $ на данный момент: "+str(buy)+" руб.",message_id)
	else:
		vk_send("Курс $ на данный момент: "+str(buy)+" руб.")


sell, buy = get_dollar_exchange()
if mode == "buy":
	vk_send("Бот запущен. Включён режим покупки доллара. Все ценники будут показываться за покупку 1$")
	vk_send(f"Текущая цена покупки: {buy} руб.")
else:
	vk_send("Бот запущен. Включён режим продажи доллара. Все ценники будут показываться за продажу 1$")
	vk_send(f"Текущая цена продажи: {sell} руб.")

old = 0
lower = 0
upper = 0

while True:
	now = str(datetime.datetime.now())[:-7]
	sell, buy = get_dollar_exchange()
	if mode == "buy":
		if buy < old and old != 0 and buy != 0:
			if buy < lower and lower != 0 and buy != 0:
				vk_send(f"Цена покупки упала ниже локального минимума!\nКупить 1 $ можно за {buy} руб.")
				lower = buy
			else:
				vk_send(f"Цена покупки $ упала!\nНовая цена: {buy} руб.\nСтарая цена: {old} руб.")
				old = buy
		else:
			print(now+"|Цена не упала: "+str(buy)+" руб.")
		nowtime = now[11:].split(":")[2]
		if nowtime in ["00","01","02"]:
			send_message_in_zeros(buy)
		old = buy
	elif mode == "sell":
		if sell > old and old != 0 and sell != 0:
			if sell > upper and upper !=0 and sell != 0:
				vk_send(f"Цена продажи поднялась выше локального максимума!\nПродать 1 $ можно за {sell} руб.")
				upper = sell
			else:
				vk_send(f"Цена продажи $ поднялась!\nНовая цена: {sell} руб.\nСтарая цена: {sell} руб.")
				old = sell
		else:
			print(now+"|Цена не выросла: "+str(sell)+" руб.")
		nowtime = now[11:].split(":")[2]
		if nowtime in ["00","01","02"]:
			send_message_in_zeros(sell)
		old = sell

