#!/usr/bin/python

import json
import mysql.connector as mysql
import inspect
import os
import RPi.GPIO as GPIO
import time
import datetime

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

configFile = open(path + "/.config.json")
config = json.loads(configFile.read())

conn = mysql.connect(host=config["mysql"]["host"],user=config["mysql"]["user"],password=config["mysql"]["pass"],database=config["mysql"]["db"])
sql = conn.cursor(buffered=True)

dt = datetime.datetime.now()

def rega(tempo):
	if int(tempo) > 0:
		GPIO.setmode(GPIO.BCM)
		for rele in config["gpio"]["rele"]:
			GPIO.setup(int(rele),GPIO.OUT)
			GPIO.setup(int(rele),GPIO.LOW)
		time.sleep(int(tempo))
		for rele in config["gpio"]["rele"]:
			GPIO.setup(int(rele),GPIO.HIGH)
	sql.execute("INSERT IGNORE INTO gardenberry.regas (datahora, tempo) VALUES (NOW(), " + tempo + ");")
	print("Regou: " + tempo + " seg")

try:
	if dt.hour < 12:
		sql.execute("SELECT ROUND(AVG(temperatura),3) AS media FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW();")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW() ) AS dp;")
		r = sql.fetchone()
		desvio_padrao = float(r[0])

		sql.execute("SELECT ROUND(AVG(temperatura),3) AS media FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND DATE_SUB(NOW(), INTERVAL 12 HOUR);")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND DATE_SUB(NOW(), INTERVAL 12 HOUR) ) AS dp;")
		r = sql.fetchone()
		desvio_padrao2 = float(r[0])

		sql.execute("SELECT ROUND(AVG(precipitacao),1) AS precipitacoes, \
			(SELECT ROUND(AVG(temperatura) +" + str(desvio_padrao2) + ",1) FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND DATE_SUB(NOW(), INTERVAL 12 HOUR)) AS temperaturas, \
			ROUND(AVG(umidade),0) AS umidades, \
			(SELECT ROUND(AVG(precipitacao),1) FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW()) AS fut_precipitacoes, \
			(SELECT ROUND(AVG(temperatura) +" + str(desvio_padrao) + ",1) FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW()) AS fut_temperaturas, \
			ROUND(IFNULL((SELECT SUM(tempo) FROM gardenberry.regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 16 HOUR) AND NOW()),0),0) AS rega \
			FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW();")

	else:
		sql.execute("SELECT ROUND(AVG(temperatura),3) AS media FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR);")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR) ) AS dp;")
		r = sql.fetchone()
		desvio_padrao = float(r[0])

		sql.execute("SELECT ROUND(AVG(temperatura),3) AS media FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND NOW();")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND NOW() ) AS dp;")
		r = sql.fetchone()
		desvio_padrao2 = float(r[0])
		sql.execute("SELECT ROUND(AVG(precipitacao),1) AS precipitacoes,ROUND(AVG(temperatura) +" + str(desvio_padrao2) + ",1) AS temperaturas, ROUND(AVG(umidade),0) AS umidades, \
			(SELECT ROUND(AVG(precipitacao),1) FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)) AS fut_precipitacoes, \
			(SELECT ROUND(AVG(temperatura) +" + str(desvio_padrao) + ",1) FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)) AS fut_temperaturas, \
			ROUND(IFNULL((SELECT SUM(tempo) FROM gardenberry.regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 8 HOUR) AND NOW()),0),0) AS rega \
			FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND NOW();")

	r = sql.fetchone()
	column_names = ["precipitacoes","temperaturas","umidades","fut_precipitacoes","fut_temperaturas","rega"]
	r = dict(zip(column_names,r))
	t = 0
	modf = 0

	if float(r["fut_precipitacoes"]) < 0.6 and float(r["precipitacoes"]) < 1.6:
		modf = float(2)
	elif float(r["fut_precipitacoes"]) < 1.6 and float(r["precipitacoes"]) < 1.6:
		modf = float(1)
	else:
		sql.execute("SELECT ROUND(IFNULL((SELECT SUM(tempo) FROM gardenberry.regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 71 HOUR) AND NOW()),0),0) AS rega;")
		r = sql.fetchone()
		if int(r[0]) == 0:
			modf = 0.7

	if modf > 0:
		t = int(config["rega"]["tempo"])
		modt1 = float(config["rega"]["temperatura"]["start"]) + (float(r["temperaturas"]) *float(config["rega"]["temperatura"]["step"]) *modf)
		modu1 = ((100 -float(r["umidades"]))* float(config["rega"]["umidade"]["step"]) *modf /2) + float(config["rega"]["umidade"]["start"])
		modt2 = float(config["rega"]["temperatura"]["start"]) + (float(r["fut_temperaturas"]) *float(config["rega"]["temperatura"]["step"]) *modf)
		t = int(float(t) * modt1/100 * modu1/100 * modt2/100)
		t = t - int(r["rega"])
		
		print("debug")
		print("t\tconf.t\tm_t1\tm_u1\tm_t2\tm_f")
		print(str(t) + "\t" + str(config["rega"]["tempo"]) + "\t" + str(modt1) + "\t" + str(modu1) + "\t" + str(modt2) + "\t" + str(modf))
		print(r)
	if t < 5:
		t = 0
	rega(str(t))
except sql.Error as error:
	print("Error: {}".format(error))

