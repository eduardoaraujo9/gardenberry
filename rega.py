#!/usr/bin/python

import json
import requests
import mysql.connector as mysql
import inspect
import os

filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))

configFile = open(path + "/.config.json")
config = json.loads(configFile.read())

conn = mysql.connect(host=config["mysql"]["host"],user=config["mysql"]["user"],password=config["mysql"]["pass"],database=config["mysql"]["db"])
sql = conn.cursor()

def rega(tempo):
	sql.execute("INSERT IGNORE INTO gardenberry.regas (datahora, tempo) VALUES (NOW(), " + tempo + ");")
	print("Regar: " + tempo + " seg")

try:
	sql.execute("SELECT SUM(precipitacao) AS precipitacoes,ROUND(AVG(temperatura),1) AS temperaturas, ROUND(AVG(umidade),0) AS umidades, \
		(SELECT SUM(precipitacao) FROM previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)) AS fut_precipitacoes, \
		(SELECT ROUND(AVG(temperatura),1) FROM previsao WHERE datahora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 12 HOUR)) AS fut_temperaturas, \
		(SELECT SUM(precipitacao) FROM previsao WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL IF(HOUR(NOW())<12,12,24) HOUR) AND NOW()) AS prev_precipitacoes, \
		(SELECT ROUND(AVG(temperatura),1) FROM previsao WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL IF(HOUR(NOW())<12,12,24) HOUR) AND NOW()) AS prev_temperaturas, \
		ROUND(IFNULL((SELECT SUM(tempo) FROM regas WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL 11 HOUR) AND NOW()),0),0) AS rega, \
		HOUR(NOW()) AS hora \
		FROM gardenberry.tempo WHERE datahora BETWEEN DATE_SUB(NOW(), INTERVAL IF(HOUR(NOW())<12,12,24) HOUR) AND NOW();")
	r = sql.fetchone()
	column_names = ["precipitacoes","temperaturas","umidades","fut_precipitacoes","fut_temperaturas","prev_precipitacoes","prev_temperaturas","rega","hora"]
	r = dict(zip(column_names,r))
	t = 0
	if int(r["hora"]) < 12:
		print("morning")
		if int(r["rega"]) == 0 and float(r["prev_precipitacoes"]) < 1.5 and float(r["umidades"]) < 80:
			t = int(int(config["rega"]["tempo"]) / 2)
	else:
		print("evening")
		if float(r["fut_precipitacoes"]) < 2:
			modf = float(2)
		elif float(r["fut_precipitacoes"]) < 5:
			modf = float(1)
		else:
			modf = 0
		if modf > 0:
			t = int(config["rega"]["tempo"])
			modt1 = float(config["rega"]["start"]) + (float(r["prev_temperaturas"]) *float(config["rega"]["step"]) *modf)
			modu1 = ((100 -float(r["umidades"]))* float(config["rega"]["step"]) * float(modf /2)) + float(config["rega"]["start"])
			modt2 = float(config["rega"]["start"]) + (float(r["fut_temperaturas"]) *float(config["rega"]["step"]) *modf)
			t = int(float(t) * float(modt1/100) * float(modu1/100) * float(modt2/100))
			t = t - int(r["rega"])
			print(str(t) + " " + str(modt1) + " " + str(modu1) + " " + str(modt2))
			print(str(config["rega"]["tempo"]) + " " + str(r["prev_temperaturas"]) + " " + str(r["umidades"]) + " " + str(r["fut_temperaturas"]))
	if t < 0:
		t = 0
	rega(str(t))
except sql.Error as error:
	print("Error: {}".format(error))

