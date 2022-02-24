import json
import requests
import time
import vk_api
import datetime
from timeout import timeout
import os

#!!!!
#Надо изменить на свои данные!!!
vk = vk_api.VkApi(token = "TOKEN VK") #Токен ВК
peer_id = 2000000014 #ID Беседы куда бот будет писать уведомления
#!!!!


def vk_send(text):
	print(text)
	try:
		vk.method("messages.send",{"random_id":0,"message":text,"peer_id":peer_id})
	except:
		time.sleep(10)
		vk.method("messages.send",{"random_id":0,"message":text,"peer_id":peer_id})

def vk_edit(text):
	print(text)
	try:
		vk.method("messages.edit",{"peer_id":peer_id,"message":text,"message_id": message_id,},)
	except:
		time.sleep(10)
		vk.method("messages.edit",{"peer_id":peer_id,"message":text,"message_id": message_id,},)

@timeout(10)
def get_response():
	return requests.get("https://api.tinkoff.ru/v1/currency_rates")

def get_dollar_exchange():
	try:
		response = get_response()
		status = response.status_code
		jsons = json.loads(response.text)
		buy = jsons["payload"]["rates"][1]["buy"]
		sell = jsons["payload"]["rates"][1]["sell"]
		return buy,sell
	except:
		return 0,0

def get_message():
	try:
		return vk.method("messages.getHistory", {"peer_id": peer_id, "count": 1})
	except:
		time.sleep(10)
		return vk.method("messages.getHistory", {"peer_id": peer_id, "count": 1})

def send_message_in_zeros(buy):
	message = get_message()
	message_id = message.get("items")[0].get("id")
	message_text = message.get("items")[0].get("text")
	if "Курс $ на данный момент:" in message_text:
		vk_edit("Курс $ на данный момент: "+str(buy)+" руб.")
	else:
		vk_send("Курс $ на данный момент: "+str(buy)+" руб.")
old_buy = 0
oldest_buy = 0
highest = 86.50	
while True:
	now = str(datetime.datetime.now())[:-7]
	buy,sell = get_dollar_exchange()
	if buy > old_buy and old_buy != 0 and buy != oldest_buy:
		first_new = str(buy).split(".")[0]
		second_new = str(buy).split(".")[1]
		first_old = str(old_buy).split(".")[0]
		second_old = str(old_buy).split(".")[1]
		if int(first_new)> 87:
			vk_send("Цена $ выше 87 руб. Уведомляю о изменении и копеек:\nНовая цена: "+str(buy)+" руб. \nСтарая цена: "+str(old_buy)+" руб.")
		if int(first_new) > int(first_old):
			minus_rub = str(int(first_new) - int(first_old))
			minus_kop = str(int(second_new) - int(second_old))
			if buy > highest:
				vk_send("Внимание!\n@all")
				vk_send("Цена выше локальной вершины!\nНовая цена: "+str(buy)+" руб.\n Старая цена: "+str(old_buy)+" руб.")
				highest = buy
			else:
				vk_send("Цена $ выросла на "+minus_rub+" руб.\nНовая цена: "+str(buy)+" руб.\n Старая цена: "+str(old_buy)+" руб.") 
			for i in range(0,7):
				get_response()
			time.sleep(10)
	else:
		print(now+"|Цена не выросла: "+str(buy)+" руб.")
	nowtime = now[11:].split(":")[2]
	if nowtime == "00":
		send_message_in_zeros(buy)
	oldest_buy = old_buy
	old_buy = buy
	time.sleep(0.7)
