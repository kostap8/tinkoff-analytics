import os
import json
from pprint import pprint
from tinkoffapi import TinkoffApi
import locale
from decimal import Decimal
from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional, Tuple
from tabulate import tabulate
from utils import localize, get_now
from datetime import datetime

class Positions(BaseModel):
    """ Позиции в портфеле """
    """ Тикер """
    ticker: str = ''
    """ Стоимость """
    ticker_cost: Decimal = Decimal(0)
    """ Ожидаемый процент в портфеле """
    weigth_exp: Decimal = Decimal(0)
    """ Текущий процент в портфеле """
    weigth_cur: Decimal = Decimal(0)
    """ Разница между ожидаемым и текущим процентами """
    weigth_diff: Decimal = Decimal(0)

OPERATIONS_FROM = '2000-01-01T00:00:00.000000+03:00'
OPERATIONS_FROM_YEAR = '2020-01-01T00:00:00.000000+00:00'
OPERATIONS_TO_YEAR = '2021-01-01T00:00:00.000000+00:00'

TOKEN = os.getenv("TINKOFF_TOKEN")
#ACCOUNT_TYPE = 'TinkoffIis'
ACCOUNT_TYPE = os.getenv("TINKOFF_ACC_TYPE")
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
PLAN_FILE = os.getenv("PLAN_FILE")

tapi = TinkoffApi(TOKEN, ACCOUNT_TYPE)
usd_course = tapi.get_usd_course()
print(f"Текущий курс доллара в брокере: {usd_course} руб")
eur_course = tapi.get_eur_course()
print(f"Текущий курс евро в брокере: {eur_course} руб")


def get_etf_weigth() -> List[Positions]:
    """Возращает вес каждого ЕTF в ETF активах в рублях"""
    positions = tapi.get_portfolio_positions()

    etfs = list()
    etfs_sum = Decimal('0')
    for position in positions:
        if position.instrument_type == TinkoffApi.InstrumentType.etf:
            etf = Positions(ticker=position.ticker)
            #print(position)
            current_ticker_cost = (position.balance
                    * position.average_position_price.value
                    + position.expected_yield.value)
            if position.average_position_price.currency == TinkoffApi.Currency.usd:
                current_ticker_cost *= usd_course
            if position.average_position_price.currency == TinkoffApi.Currency.eur:
                #print(position)
                #print(eur_course)
                current_ticker_cost *= eur_course
            etf.ticker_cost = round(current_ticker_cost, 2)
            etfs_sum += etf.ticker_cost
            etfs.append(etf)
    print(f'Сумма в ETF: {etfs_sum} руб')

    for _etf in etfs:
        _etf.weigth_cur = round(_etf.ticker_cost * 100 / etfs_sum , 2)

    return etfs


def get_portfolio_positions_sum() -> int:
    """Возвращает текущую стоимость портфеля в рублях без учета
    просто лежащих на аккаунте рублей в деньгах"""
    positions = tapi.get_portfolio_positions()

    portfolio_sum = Decimal('0')
    for position in positions:
        #print(position)
        current_ticker_cost = (position.balance 
                * position.average_position_price.value 
                + position.expected_yield.value)
        if position.average_position_price.currency == TinkoffApi.Currency.usd:
            current_ticker_cost *= usd_course
        if position.average_position_price.currency == TinkoffApi.Currency.eur:
            current_ticker_cost *= eur_course
        portfolio_sum += current_ticker_cost
    return int(portfolio_sum)

def get_portfolio_currency_sum() -> int:
    """Возвращает сумму кэша(рубли) в портфеле"""
    currencies = tapi.get_portfolio_currencies()

    currencies_sum = Decimal('0')
    for currency in currencies:
        current_currency_cost = currency.balance
        if currency.currency == TinkoffApi.Currency.rub:
            currencies_sum += current_currency_cost
        #if currency.currency == TinkoffApi.Currency.usd:
        #    current_currency_cost *= usd_course
        #if currency.currency == TinkoffApi.Currency.eur:
        #    current_currency_cost *= eur_course
        #currencies_sum += current_currency_cost
    return int(currencies_sum)

def get_etf_plan(etfs: list):
    """Вставляет в etfs планируемый процентный состав портфеля"""
    with open(PLAN_FILE) as plan:
        for line in plan:
            sline = line.split('\t')
            for etf in etfs:
                if etf.ticker == sline[0]:
                    etf.weigth_exp = Decimal(sline[1].replace(',','.'))
                    break
            else:
                new_etf = Positions(ticker=sline[0])
                new_etf.ticker_cost = 0
                new_etf.weigth_cur = 0
                new_etf.weigth_exp = Decimal(sline[1].replace(',','.'))
                etfs.append(new_etf)


def get_operations_payin_sum(from_in: datetime = OPERATIONS_FROM, to_in: datetime = get_now()) -> int:
    """Возвращает сумму всех пополнений в рублях"""
    operations = tapi.get_all_operations(from_in, to_in)

    sum_pay_in = Decimal('0')
    for operation in operations:
        #print(operation.operation_type)
        if (operation.operation_type == TinkoffApi.OperationTypeWithCommission.pay_in \
            or operation.operation_type == TinkoffApi.OperationTypeWithCommission.pay_out) \
            and operation.status == TinkoffApi.OperationStatus.done:
            #print(operation)
            sum_pay = operation.payment
            if operation.currency == TinkoffApi.Currency.usd:
                sum_pay *= usd_course
            if operation.currency == TinkoffApi.Currency.eur:
                sum_pay *= eur_course
            sum_pay_in += sum_pay
    return int(sum_pay_in)

if __name__ ==  "__main__":
    portfolio_positions_sum = get_portfolio_positions_sum()
    print(f"\n")
    print(f"Стоимость активов: {portfolio_positions_sum:n} руб")
    portfolio_currencies_sum = get_portfolio_currency_sum()
    print(f"Стоимость кэша: {portfolio_currencies_sum:n} руб")
    portfolio_sum = portfolio_positions_sum + portfolio_currencies_sum
    print(f"Стоимость портфеля: {portfolio_sum:n} руб")

    sum_pay_in_year = get_operations_payin_sum(OPERATIONS_FROM_YEAR, OPERATIONS_TO_YEAR)
    print(f"Сумма пополнений за 2020: {sum_pay_in_year:n} руб")

    sum_pay_in = get_operations_payin_sum()
    print(f"Сумма пополнений: {sum_pay_in:n} руб")
    profit_in_rub = portfolio_sum - sum_pay_in
    profit_in_percent = round(profit_in_rub * 100 / sum_pay_in, 2)
    print(f"Рублёвая прибыль: {profit_in_rub:n} руб ({profit_in_percent:n}%)")
    print(f"\n")
    
    etfs = get_etf_weigth()
    get_etf_plan(etfs)
    for etf in etfs:
        etf.weigth_diff = etf.weigth_exp - etf.weigth_cur

    etfs.sort(key=lambda x: x.weigth_diff, reverse=True)
    print(tabulate([(etf.ticker, etf.ticker_cost, etf.weigth_cur, etf.weigth_exp, etf.weigth_diff) for etf in etfs], headers=['Тикер', 'Стоимость', 'Тек. доля', 'Ожид. доля', 'Разница долей']))

#    for _etf in etfs:
#        print(f"{_etf.ticker} : {_etf.ticker_cost} : {_etf.weigth_cur}")

    exit(0)


