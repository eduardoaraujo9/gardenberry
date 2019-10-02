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

url = "http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/" + config["api"]["id"] + "/hours/72?token=" + config["api"]["token"]

res = requests.get(url)
r = json.loads(res.text)
for dados in r["data"]:
	try:
		sql.execute("REPLACE INTO gardenberry.previsao (datahora,precipitacao,temperatura) VALUES ('" + str(dados["date"]) + "','" + str(dados["rain"]["precipitation"]) + "','" + str(dados["temperature"]["temperature"]) + "');")

	except sql.Error as error:
		print("Error: {}".format(error))

