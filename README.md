# Gardenberry

Projeto simples para meu Raspberry efetuar regas automáticas no jardim com base na previsão do tempo (e no estado atual do tempo).

A temperatura futura funciona como um multiplicador que modifica o tempo de rega padrão, mais calor regará por mais tempo e um clima ameno regará por menos tempo. A umidade também causa o mesmo princípio.

Utiliza a api do climatempo, e tem a configuração definida no arquivo
.config.json
```
{
  "api":[
    { "id":"3477",
      "token":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" },
    { "id":"3791",
      "token":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" }
  ],

  "mysql":{
    "host":"127.0.0.1",
    "user":"gardenberry",
    "pass":"gardenberry",
    "db":"gardenberry"
  },
  "gpio":{
    "sensor":"3",
    "rele":[
      "2",
      "4"
    ]
  },
  "rega":{
    "tempo":"60",
    "maximo":"600",
    "temperatura":{
      "step":"3",
      "start":"0"
    },
    "umidade":{
      "step":"3",
      "start":"-15"
    }
  }
}
```

**api**: configurações da API do climatempo, (id) corresponde ao locale. Suporte a multiplos tokens.

**mysql**: configurações do banco de dados mysql

**gpio**: configurações do numero de porta do sensor de temperatura + umidade e das portas dos relés que serão ativados

**rega**: (tempo) tempo em segundos padrão de rega; (maximo) tempo limite para rega; (step) incremento no tempo com base na temperatura/umidade; (start) valor inicial para parametrização de variação temporal da rega com base na temperatura/umidade

**crontab:**
```
0 1 * * * /home/pi/gardenberry/previsao.py
1 * * * * /home/pi/gardenberry/tempo.py
5 6,18 * * * /home/pi/gardenberry/rega.log && /home/pi/gardenberry/rega.py
```
