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

for api in config["api"]:
	url = "http://apiadvisor.climatempo.com.br/api/v1/weather/locale/" + str(api["id"]) + "/current?token=" + str(api["token"])

	res = requests.get(url)
	r = json.loads(res.text)
	try:
		sql.execute("REPLACE INTO gardenberry.tempo (datahora,umidade,temperatura,precipitacao,fonte) VALUES (CONCAT(LEFT(NOW(),14),'00:00'),'" + str(r["data"]["humidity"]) + "','" + str(r["data"]["temperature"]) + "',IF(LEFT('3n',1)>2 AND LEFT('8n',1)<9,(SELECT precipitacao FROM gardenberry.previsao WHERE datahora = CONCAT(LEFT(NOW(),14),'00:00')),0)," + str(api["id"]) + ");")
	except sql.Error as error:
		print("Error: {}".format(error))

