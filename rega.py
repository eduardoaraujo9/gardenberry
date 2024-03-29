#!/usr/bin/python

import json
import mysql.connector as mysql
import inspect
import os
import RPi.GPIO as GPIO
import time
import datetime
import argparse

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

configFile = open(path + "/.config.json")
config = json.loads(configFile.read())

conn = mysql.connect(host=config["mysql"]["host"],user=config["mysql"]["user"],password=config["mysql"]["pass"],database=config["mysql"]["db"])
sql = conn.cursor(buffered=True)

parser = argparse.ArgumentParser(description='Forcar tempo de rega')
parser.add_argument('-force', metavar='N', type=int, help='regar por N segundos')
args = parser.parse_args()

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
		sql.execute("SELECT IFNULL(ROUND(AVG(temperatura),3),22) AS media FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW();")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT IFNULL(ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2),0) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW() ) AS dp;")
		r = sql.fetchone()
		desvio_padrao = float(r[0])

		sql.execute("SELECT IFNULL(ROUND(AVG(temperatura),3),22) AS media FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND DATE_SUB(NOW(), INTERVAL 12 HOUR);")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT IFNULL(ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2),0) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND DATE_SUB(NOW(), INTERVAL 12 HOUR) ) AS dp;")
		r = sql.fetchone()
		desvio_padrao2 = float(r[0])

		sql.execute("SELECT IFNULL(ROUND(AVG(precipitacao),1),0) AS precipitacoes, \
			IFNULL((SELECT ROUND(AVG(temperatura) +" + str(desvio_padrao2) + ",1) FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND DATE_SUB(NOW(), INTERVAL 12 HOUR)),22) AS temperaturas, \
			IFNULL(ROUND(AVG(umidade),0),80) AS umidades, \
			IFNULL((SELECT ROUND(AVG(precipitacao),1) FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW()),0) AS fut_precipitacoes, \
			IFNULL((SELECT ROUND(AVG(temperatura) +" + str(desvio_padrao) + ",1) FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW()),22) AS fut_temperaturas, \
			ROUND(IFNULL((SELECT SUM(tempo) FROM gardenberry.regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 16 HOUR) AND NOW()),0),0) AS rega \
			FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 12 HOUR) AND NOW();")

	else:
		sql.execute("SELECT IFNULL(ROUND(AVG(temperatura),3),22) AS media FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR);")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT IFNULL(ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2),0) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR) ) AS dp;")
		r = sql.fetchone()
		desvio_padrao = float(r[0])

		sql.execute("SELECT IFNULL(ROUND(AVG(temperatura),3),22) AS media FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND NOW();")
		r = sql.fetchone()
		media = float(r[0])
		sql.execute("SELECT IFNULL(ROUND(SQRT(SUM(v)/(COUNT(v)-1)),2),0) AS desvio_padrao FROM ( SELECT temperatura, ROUND((" + str(media) + " -temperatura)*(" + str(media) + " -temperatura),2) AS v FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 24 HOUR) AND NOW() ) AS dp;")
		r = sql.fetchone()
		desvio_padrao2 = float(r[0])
		sql.execute("SELECT IFNULL(ROUND(AVG(precipitacao),1),0) AS precipitacoes,IFNULL(ROUND(AVG(temperatura) +" + str(desvio_padrao2) + ",1),22) AS temperaturas, IFNULL(ROUND(AVG(umidade),0),80) AS umidades, \
			IFNULL((SELECT ROUND(AVG(precipitacao),1) FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)),0) AS fut_precipitacoes, \
			IFNULL((SELECT ROUND(AVG(temperatura) +" + str(desvio_padrao) + ",1) FROM gardenberry.previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)),22) AS fut_temperaturas, \
			ROUND(IFNULL((SELECT SUM(tempo) FROM gardenberry.regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 10 HOUR) AND NOW()),0),0) AS rega \
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
		sql.execute("SELECT ROUND(IFNULL((SELECT SUM(tempo) FROM gardenberry.regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 47 HOUR) AND NOW()),0),0) AS rega;")
		r2 = sql.fetchone()
		if int(r2[0]) < 60:
			modf = 0.7
		else:
			modf = 0.4

	if modf > 0:
		t = int(config["rega"]["tempo"])
		modt1 = float(config["rega"]["temperatura"]["start"]) + (float(r["temperaturas"]) *float(config["rega"]["temperatura"]["step"]) *modf)
		modu1 = ((100 -float(r["umidades"]))* float(config["rega"]["umidade"]["step"]) *modf /2) + float(config["rega"]["umidade"]["start"])
		modt2 = float(config["rega"]["temperatura"]["start"]) + (float(r["fut_temperaturas"]) *float(config["rega"]["temperatura"]["step"]) *modf)
		t = int(float(t) * modt1/100 * modu1/100 * modt2/100)
		t = t - int(r["rega"])
		
		print("t\tconf.t\tm_t1\tm_u1\tm_t2\tm_f")
		print(str(t) + "\t" + str(config["rega"]["tempo"]) + "\t" + str(modt1) + "\t" + str(modu1) + "\t" + str(modt2) + "\t" + str(modf))
		print(r)

	if t < 5:
		t = 0
	try:
	        if args.force > 0:
			t = args.force
	except:
        	nothing = True

	rega(str(t))
except sql.Error as error:
	print("Error: {}".format(error))

