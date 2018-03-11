#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
from argparse import ArgumentTypeError


def quantity_float(value):
    quantity = float(value)
    if quantity <= 0:
        raise ArgumentTypeError("invalid quantity: {}, and quantity must be greater than 0!".format(quantity))
    return quantity


def profit_float(value):
    profit = float(value)
    if profit < 0.3:
        raise ArgumentTypeError("invalid profit: {}, and profit must be greater than or equal to 0.3!".format(profit))
    return profit


def fee_float(value):
    fee = float(value)
    if fee < 0:
        raise ArgumentTypeError("invalid fee: {}, and fee must be greater than or equal to 0!".format(fee))
    return fee


def price_adjust_int(value):
    price_adjust = int(value)
    if price_adjust < 1:
        raise ArgumentTypeError(
            "invalid price_adjust: {}, and price_adjust must be greater than or equal to 1!".format(price_adjust))
    return price_adjust


def count_int(value):
    count = int(value)
    if count < 1:
        raise ArgumentTypeError("invalid count: {}, and count must be greater than or equal to 1!".format(count))
    return count


def strategy(value):
    values = value.split('.')
    if len(values) < 2:
        raise ArgumentTypeError("invalid strategy: {}, and strategy's format is module_name.class_name!".format(value))

    strategy_module_name, strategy_class_name = ".".join(values[:-1]), values[-1]

    try:
        strategy_module = importlib.import_module("strategy.{}".format(strategy_module_name))
    except Exception as e:
        raise ArgumentTypeError("invalid strategy: {}".format(e))

    if hasattr(strategy_module, strategy_class_name) is False:
        raise ArgumentTypeError("invalid strategy: No class named {}".format(value))

    strategy_class = getattr(strategy_module, strategy_class_name)
    strategy_obj = strategy_class()

    buy_method_name = "consult_buy_strategy"
    if hasattr(strategy_obj, buy_method_name) is False:
        raise ArgumentTypeError("invalid strategy: No method named {}".format(buy_method_name))

    sell_method_name = "consult_buy_strategy"
    if hasattr(strategy_obj, sell_method_name) is False:
        raise ArgumentTypeError("invalid strategy: No method named {}".format(sell_method_name))

    return strategy_obj
