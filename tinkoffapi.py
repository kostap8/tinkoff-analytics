from datetime import datetime
from decimal import Decimal
from typing import List
import json
from pprint import pprint

import tinvest

#from utils import localize, get_now

class TinkoffApi:
    """Обёртка для работы с API Тинькова на основе библиотеки tinvest"""
    Currency = tinvest.Currency
    InstrumentType = tinvest.InstrumentType

    def __init__(self, api_token: str, account_type: str):
        self._client = tinvest.SyncClient(api_token)
        self._account_type = account_type
        self._account_id = None

        accounts = self._client.get_accounts().payload.accounts
        #pprint(accounts)

        for account in accounts:
            if account.broker_account_type == self._account_type:
                self._account_id = account.broker_account_id
                pprint(account)


    def get_usd_course(self) -> Decimal:
        """Отдаёт текущий курс доллара в брокере"""
        return self._client.get_market_orderbook(figi="BBG0013HGFT4", depth=1)\
                .payload.last_price


    def get_eur_course(self) -> Decimal:
        """Отдаёт текущий курс евро в брокере"""
        return self._client.get_market_orderbook(figi="BBG0013HJJ31", depth=1)\
                .payload.last_price


    def get_portfolio_positions(self) \
                -> List[tinvest.schemas.PortfolioPosition]:
        """Возвращает все позиции в портфеле"""
        positions = self._client.get_portfolio(broker_account_id=self._account_id)\
                .payload.positions
        return positions

    def get_portfolio_currencies(self) \
            -> List[tinvest.schemas.Currencies]:
        """Возвращает денежные позиции в портфеле"""
        positions = self._client.get_portfolio_currencies(broker_account_id=self._account_id)\
                .payload.currencies
        return positions


    def get_all_operations(self, broker_account_started_at: datetime) \
                -> List[tinvest.schemas.Operation]:
        """Возвращает все операции в портфеле с указанной даты"""
        from_ = localize(broker_account_started_at)
        now = get_now()

        operations = tinvest\
            .OperationsApi(self._client)\
            .operations_get(broker_account_id=self._broker_account_id, from_=from_, to=now)\
            .parse_json().payload.operations
        return operations

