# Gardenberry

## Propósito

Compor um projeto simples para meu Raspberry efetuar regas automáticas no jardim com base na previsão do tempo (e no estado atual do tempo).

A temperatura futura funciona como um multiplicador que modifica o tempo de rega padrão, mais calor regará por mais tempo e um clima ameno regará por menos tempo. A umidade também causa o mesmo princípio.

A parte complexa, alem de definir o tempo padrao de rega, e efetuar o ajuste fino do step e valor de start dos modificadores, para auxiliar a simulacao montei uma planilha `rega regra.xls` que simula o calculo e a visualizacao dos valores que serao obtidos para cada faixa de temperatura / umidade.

## Configuração

Utiliza a api do climatempo (aceitando multiplos ids/tokens) para triangular as temperaturas e previsões próximas de casa, e tem a configuração definida no arquivo `.config.json`
```json
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

**gpio**: configurações do numero de porta do sensor de temperatura + umidade e das portas dos relés que serão ativados.

**rega**: (tempo) tempo em segundos padrão de rega; (maximo) tempo limite para rega; (step) incremento no tempo com base na temperatura/umidade; (start) valor inicial para parametrização de variação temporal da rega com base na temperatura/umidade. Para desabilitar os modificadores é só utilizar `start 100` e `step 0`

**crontab:** é preciso configurar os scripts para execução na crontab.
```
0 1 * * * /home/pi/gardenberry/previsao.py
1 * * * * /home/pi/gardenberry/tempo.py
5 6,18 * * * /home/pi/gardenberry/rega.py
```

## Fotos do projeto

Com o Raspberry PI (zero W) conectado à placa de relés:

![Rasbperry PI](https://github.com/eduardoaraujo9/gardenberry/raw/master/gardenberry.gif)

Ativar o relé (luz vermelha) com base nos cálculos em Python/SQL liga a solenóide e permite a vazão da água na mangueira:

![Solenoide](https://github.com/eduardoaraujo9/gardenberry/raw/master/solenoide.PNG)

E os micro-aspersores com controle de fluxo enfiados na mangueira são responsáveis pela rega das plantas!

![micro-aspersores](https://github.com/eduardoaraujo9/gardenberry/raw/master/rega.gif)
