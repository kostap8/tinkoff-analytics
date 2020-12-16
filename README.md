Аналитика доходности инвестиционного портфеля Тиньков
======================================================

Для работы скрипта нужно установить три переменных окружения:
```
export TINKOFF_TOKEN=some_tinkoff_token
export TINKOFF_BROKER_ACCOUNT=some_broker_account
export TINKOFF_ACCOUNT_STARTED=01.06.2020
```

Здесь `TINKOFF_TOKEN` это токен Тиньков инвестиций,
`TINKOFF_BROKER_ACCOUNT` это ID портфеля в Тинькове,
`TINKOFF_ACCOUNT_STARTED` это дата открытия портфеля в формате дд.мм.гггг,
от этой даты будут считаться пополнения.

Использование:

```
python go.py
```
