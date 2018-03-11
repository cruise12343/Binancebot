#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import math
import sys
import threading
import time

from .xexception import StrategyError


class XController:
    INIT_WAIT_TIME = 30
    BUY_WAIT_TIME = 0.5
    SELL_WAIT_TIME = 1

    INIT_TIMES = sys.maxsize
    BUY_TIMES = 3
    SELL_TIMES = 3

    def __init__(self, robot, option):
        self._ctx = threading.local()
        self.robot = robot
        self.option = option

    def fire(self):
        for i in range(self.option.robot_count):
            trader = threading.Thread(target=self.run, name="XRobot{}({})".format(i, self.option.symbol))
            trader.start()

    def run(self):
        for i in range(self.option.transaction_count):
            logging.info("[Start]Transaction{} is started.".format(i))
            if self._init() is False:
                logging.error('[Init]Init failed, XTrader will exit.')
                return

            buy_order = None
            while buy_order is None:
                buy_order = self._buy()
                time.sleep(XController.BUY_WAIT_TIME)

            sell_order = None
            while sell_order is None:
                sell_order = self._sell()
                time.sleep(XController.SELL_WAIT_TIME)

            logging.info("[End]Transaction{} is ended.".format(i))

    def _init(self):
        for i in range(XController.INIT_TIMES):
            try:
                symbol_info = self.robot.get_symbol_info(self.option.symbol)
                if symbol_info is None:
                    logging.info("[Init]Symbol is not supported: {}".format(self.option.symbol))
                    return False

                self._ctx.symbol = symbol_info['symbol']

                symbol_info['filters'] = {item['filterType']: item for item in symbol_info['filters']}
                self._ctx.min_qty = float(symbol_info['filters']['LOT_SIZE']['minQty'])
                self._ctx.min_price = float(symbol_info['filters']['PRICE_FILTER']['minPrice'])
                self._ctx.min_notional = float(symbol_info['filters']['MIN_NOTIONAL']['minNotional'])
                self._ctx.step_size = float(symbol_info['filters']['LOT_SIZE']['stepSize'])
                self._ctx.tick_size = float(symbol_info['filters']['PRICE_FILTER']['tickSize'])

                quantity = self.option.quantity
                quantity = self._ctx.min_qty if quantity < self._ctx.min_qty else quantity
                quantity = float(self._ctx.step_size * math.floor(quantity / self._ctx.step_size))
                self._ctx.quantity = quantity

                self._ctx.fee = self.option.fee
                self._ctx.profit = self.option.profit
                self._ctx.price_adjust = self.option.price_adjust
                self._ctx.strategy = self.option.strategy

                return True
            except Exception as e:
                logging.error("[Init Exception {}]={}".format(i, e))
                time.sleep(XController.INIT_WAIT_TIME)
        return False

    def _buy(self):
        order = None
        if self.robot.can_buy(self._ctx, self._ctx.strategy):
            if hasattr(self._ctx, 'buy_price') is False:
                raise StrategyError("invalid strategy: ctx.buy_price is not be set in strategy.")

            buy_count = 0
            while buy_count < XController.BUY_TIMES:
                order = self.robot.buy(self._ctx.symbol, self._ctx.quantity, self._ctx.buy_price)

                if order is not None:
                    break

                buy_count += 1
        return order

    def _sell(self):
        order = None
        if self.robot.can_sell(self._ctx, self._ctx.strategy):
            if hasattr(self._ctx, 'sell_price') is False:
                raise StrategyError("invalid strategy: ctx.sell_price is not be set in strategy.")

            sell_count = 0
            while sell_count < XController.SELL_TIMES:
                order = self.robot.sell(self._ctx.symbol, self._ctx.quantity, self._ctx.sell_price)

                if order is not None:
                    break

                sell_count += 1
        return order
