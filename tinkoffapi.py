from datetime import datetime
from decimal import Decimal
from typing import List
import json
from pprint import pprint
from utils import localize, get_now

import tinvest

OPERATIONS_FROM='2000-01-01T00:00:00.000000+03:00'

#from utils import localize, get_now

class TinkoffApi:
    """Обёртка для работы с API Тинькова на основе библиотеки tinvest"""
    Currency = tinvest.Currency
    InstrumentType = tinvest.InstrumentType
    OperationTypeWithCommission = tinvest.OperationTypeWithCommission

    def __init__(self, api_token: str, account_type: str):
        self._client = tinvest.SyncClient(api_token)
        self._account_type = account_type
        self._account_id = None

        accounts = self._client.get_accounts().payload.accounts
        #pprint(accounts)

        for account in accounts:
            if account.broker_account_type == self._account_type:
                self._account_id = account.broker_account_id
                #pprint(account)


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


    def get_all_operations(self, from_in: datetime = OPERATIONS_FROM) \
                -> List[tinvest.schemas.Operation]:
        """Возвращает все операции в портфеле 'с' и 'по' указанные даты"""
        #from_ = localize(from_in)
        from_ = from_in
        now = get_now()

        operations = self._client.get_operations(broker_account_id=self._account_id, from_=from_, to=now)\
            .payload.operations
        return operations

