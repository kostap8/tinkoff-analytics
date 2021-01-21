import os
import json
from pprint import pprint
from tinkoffapi import TinkoffApi
import locale
from decimal import Decimal
from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional, Tuple
from tabulate import tabulate

class Positions(BaseModel):
    ticker: str = ''
    ticker_cost: Decimal = Decimal(0)
    weigth_exp: Decimal = Decimal(0)
    weigth_cur: Decimal = Decimal(0)
    weigth_diff: Decimal = Decimal(0)


TOKEN = os.getenv("TINKOFF_TOKEN")
ACCOUNT_TYPE = 'TinkoffIis'
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


if __name__ ==  "__main__":
    portfolio_positions_sum = get_portfolio_positions_sum()
    print(f"\n")
    print(f"Стоимость активов: {portfolio_positions_sum:n} руб")
    portfolio_currencies_sum = get_portfolio_currency_sum()
    print(f"Стоимость кэша: {portfolio_currencies_sum:n} руб")
    portfolio_sum = portfolio_positions_sum + portfolio_currencies_sum
    print(f"Стоимость портфеля: {portfolio_sum:n} руб")
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


