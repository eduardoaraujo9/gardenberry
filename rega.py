#!/usr/bin/python

import json
import requests
import mysql.connector as mysql
import inspect
import os
import RPi.GPIO as GPIO
import time

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

configFile = open(path + "/.config.json")
config = json.loads(configFile.read())

conn = mysql.connect(host=config["mysql"]["host"],user=config["mysql"]["user"],password=config["mysql"]["pass"],database=config["mysql"]["db"])
sql = conn.cursor()

def rega(tempo):
	if int(tempo) > 0:
		GPIO.setmode(GPIO.BCM)
		for rele in config["gpio"]["rele"]:
			GPIO.setup(rele,GPIO.OUT)
			GPIO.setup(rele,GPIO.LOW)
		time.sleep(int(tempo))
		for rele in config["gpio"]["rele"]:
			GPIO.setup(rele,GPIO.HIGH)
	sql.execute("INSERT IGNORE INTO gardenberry.regas (datahora, tempo) VALUES (NOW(), " + tempo + ");")
	print("Regou: " + tempo + " seg")

try:
	sql.execute("SELECT ROUND(SUM(precipitacao)/" + str(len(config["api"])) + ",1) AS precipitacoes,ROUND(AVG(temperatura),1) AS temperaturas, ROUND(AVG(umidade),0) AS umidades, \
		(SELECT ROUND(SUM(precipitacao)/" + str(len(config["api"])) + ",1) FROM previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)) AS fut_precipitacoes, \
		(SELECT ROUND(AVG(temperatura),1) FROM previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)) AS fut_temperaturas, \
		(SELECT ROUND(SUM(precipitacao)/" + str(len(config["api"])) + ",1) FROM previsao WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL IF(HOUR(NOW())<12,12,24) HOUR) AND NOW()) AS prev_precipitacoes, \
		(SELECT ROUND(AVG(temperatura),1) FROM previsao WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL IF(HOUR(NOW())<12,12,24) HOUR) AND NOW()) AS prev_temperaturas, \
		ROUND(IFNULL((SELECT SUM(tempo) FROM regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 11 HOUR) AND NOW()),0),0) AS rega, \
		HOUR(NOW()) AS hora \
		FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL IF(HOUR(NOW())<12,12,24) HOUR) AND NOW();")
	r = sql.fetchone()
	column_names = ["precipitacoes","temperaturas","umidades","fut_precipitacoes","fut_temperaturas","prev_precipitacoes","prev_temperaturas","rega","hora"]
	r = dict(zip(column_names,r))
	t = 0
	modf = 0
	if int(r["hora"]) < 12:
		print("morning")
		if int(r["rega"]) == 0 and float(r["prev_precipitacoes"]) < 1.5 and float(r["umidades"]) < 80:
			modf = float(1)
	else:
		print("evening")
		if float(r["fut_precipitacoes"]) < (2 *len(config["api"])):
			modf = float(2)
		elif float(r["fut_precipitacoes"]) < (5 *len(config["api"])):
			modf = float(1)
	if modf > 0:
		t = int(config["rega"]["tempo"])
		modt1 = float(config["rega"]["temperatura"]["start"]) + (float(r["prev_temperaturas"]) *float(config["rega"]["temperatura"]["step"]) *modf)
		modu1 = ((100 -float(r["umidades"]))* float(config["rega"]["umidade"]["step"]) *modf /2) + float(config["rega"]["umidade"]["start"])
		modu1 = float(100)
		modt2 = float(config["rega"]["temperatura"]["start"]) + (float(r["fut_temperaturas"]) *float(config["rega"]["temperatura"]["step"]) *modf)
		t = int(float(t) * modt1/100 * modu1/100 * modt2/100)
		t = t - int(r["rega"])
		print("t\tconf.t\tm_t1\tm_u1\tm_t2\tm_f")
		print(str(t) + "\t" + str(config["rega"]["tempo"]) + "\t" + str(modt1) + "\t" + str(modu1) + "\t" + str(modt2) + "\t" + str(modf))
	if t < 5:
		t = 0
# ideia futura, reduzir o tempo da rega matinal (validar acompanhando os logs)
#	elif int(r["hora"]) < 12:
#		t = t /2
	rega(str(t))
except sql.Error as error:
	print("Error: {}".format(error))

