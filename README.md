# Gardenberry

Projeto simples para meu Raspberry efetuar regas automáticas no jardim com base na previsão do tempo (e no estado atual do tempo).

Utiliza a api do climatempo, e tem a configuração definida no arquivo
.config.json
```
{
  "api":{
    "id":"3477",
    "token":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
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
    "tempo":"120",
    "step":"3",
    "start":"10"
  }
}
```

**api**: configurações da API do climatempo

**mysql**: configurações do banco de dados mysql

**gpio**: configurações do numero de porta do sensor de temperatura + umidade e das portas dos relés que serão ativados

**crontab:**
```
0 1 * * * /home/pi/gardenberry/previsao.py
1 * * * * /home/pi/gardenberry/tempo.py
```
