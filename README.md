Аналитика доходности портфеля Тиньков
======================================================

Для работы скрипта нужно настроить файл `run.sh`:
```
export TINKOFF_TOKEN=some_tinkoff_token
export TINKOFF_BROKER_ACCOUNT=some_broker_account
export TINKOFF_ACCOUNT_STARTED=01.06.2020
export PLAN_FILE=some_file_with_plan
```

`TINKOFF_TOKEN` - токен Тиньков инвестиций,
`TINKOFF_BROKER_ACCOUNT`- ID портфеля в Тинькове (его можно получить 
в `tinvest.UserApi(client).accounts_get().parse_json().payload`),
`TINKOFF_ACCOUNT_STARTED` это дата открытия портфеля в формате дд.мм.гггг,
от этой даты будут считаться пополнения.
`PLAN_FILE` - файл с планом по тикерам и процентам через таб 

Формат `PLAN_FILE`: `tiker(tab)weight`

Пример `PLAN_FILE`:
```
FXUS    25,00
TSPX    25,00
FXWO    25,00
FXCN    25,00
```

Использование:
```
chmod +x run.sh
./run.sh
```
