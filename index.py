#!/usr/bin/python

import RPi.GPIO as GPIO
import cgi
import cgitb 

reles={
  "Natal": 23,
  "Rega": 24,
  "Luzinha": 25,
  "Terraco": 27,
}

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

f = open("assets/html/header.html", "r")
header=f.read()

form = cgi.FieldStorage() 

html="""
<!doctype html>
<html lang="en">
  <head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Gardenberry</title>
""" + header + """
  </head>
  <body>
  <div class="container">
  <div class="page-header text-center">
  <h1>Gardenberry <img src="assets/img/gardenberry.png" style="vertical-align:bottom"></h1>
  </div>
  <p class="lead">Controles dispon&iacute;veis</p>
  <form action="." method="POST">
  <input type="hidden" name="command" value="on">
"""

for rele in reles:
  status=""
  if GPIO.gpio_function(reles[rele]) == GPIO.OUT: # ja esta ligado
    status="checked"
    if form.getvalue('command'): # se recebeu comando de trocar
      if not form.getvalue(rele): # se recebeu comando de ficar off
        status=""
        GPIO.setup(reles[rele],GPIO.HIGH)
  else: # esta desligado
    status=""
    if form.getvalue('command'): # se recebeu comando de trocar
      if form.getvalue(rele): # se recebeu comando de ficar on
        status="checked"
        GPIO.setup(reles[rele],GPIO.OUT)
        GPIO.setup(reles[rele],GPIO.LOW)

  html+="""
  <p>
<label class="switch">
  <input type="checkbox" name='"""+rele+"""' onChange="this.form.submit()" """+status+""">
  <span class="slider round"></span>
</label>
<span class="h1">"""+rele+"""</span>
</p>
"""

html+="""</div> </body>
</html> """

print("Content-type:text/html\r\nContent-length:"+str(len(html))+"\r\n\r\n")
print(html)
