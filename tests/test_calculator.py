from unittest.mock import patch, MagicMock
from src.calculator import (
    build_discount_curve,
    build_implied_yield_curve,
    calculate_present_value,
    calculate_forward_value,
    calculate_interest_rate_swap_value,
    calculate_swap_value,
    calculate_interest_rate_forward_value
)
import QuantLib as ql
import pytest
import math

def test_build_discount_curve():
    spot_rates = [(0.5, 1.0), (1.0, 1.5), (2.0, 2.0)]
    curve = build_discount_curve(spot_rates)
    assert isinstance(curve, ql.YieldTermStructureHandle)

def test_build_implied_yield_curve():
    forward_rates = [(0.5, 1.0), (1.0, 1.5), (2.0, 2.0)]
    fx_rates = [(0.5, 1.1), (1.0, 1.2), (2.0, 1.3)]
    base_currency = "USD"
    target_currency = "EUR"
    
    # 修复参数错误
    curve = build_implied_yield_curve(forward_rates, base_currency, target_currency, fx_rates)
    assert isinstance(curve, ql.YieldTermStructureHandle)

def test_calculate_present_value():
    rate = 5.0
    years = 10
    future_value = 1000
    present_value = calculate_present_value(rate, years, future_value)
    assert math.isclose(present_value, 613.91, rel_tol=1e-2)

def test_calculate_forward_value():
    spot_rate = 1.2
    forward_rate = 1.3
    domestic_rate = 2.0
    foreign_rate = 1.5
    time_period = 1
    forward_value = calculate_forward_value(spot_rate, forward_rate, domestic_rate, foreign_rate, time_period)
    assert math.isclose(forward_value, 0.098, rel_tol=1e-2)

def test_calculate_interest_rate_swap_value():
    fixed_rate = 2.0
    floating_rate = 1.5
    time_period = 5
    notional_amount = 1000000
    payment_frequency = 1
    swap_value = calculate_interest_rate_swap_value(fixed_rate, floating_rate, time_period, notional_amount, payment_frequency)
    assert math.isclose(swap_value, 24500.0, rel_tol=1e-2)

def test_calculate_swap_value():
    spot_rate = 1.2
    forward_rate = 1.3
    domestic_rate = 2.0
    foreign_rate = 1.5
    time_period = 1
    notional_amount = 1000000
    swap_value = calculate_swap_value(spot_rate, forward_rate, domestic_rate, foreign_rate, time_period, notional_amount)
    assert math.isclose(swap_value, 98000.0, rel_tol=1e-2)

def test_calculate_interest_rate_forward_value():
    spot_rate = 2.0
    forward_rate = 2.5
    time_period = 1
    notional_amount = 1000000
    forward_value = calculate_interest_rate_forward_value(spot_rate, forward_rate, time_period, notional_amount)
    assert math.isclose(forward_value, 49000.0, rel_tol=1e-2)









