import QuantLib as ql
import math

from typing import List, Tuple

def build_discount_curve(spot_rates: List[Tuple[float, float]]) -> ql.YieldTermStructure:
    """
    构建折现曲线
    
    参数:
        spot_rates: 即期利率列表，每个元素为(期限(年), 利率(百分比))元组
    
    返回:
        ql.YieldTermStructure: QuantLib折现曲线对象
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 创建日期和利率列表
    if not spot_rates or len(spot_rates) < 2:
        raise ValueError("spot_rates must contain at least two elements with valid data")
    dates = [today + ql.Period(int(t * 365), ql.Days) for t, _ in spot_rates]
    rates = [r / 100 for _, r in spot_rates]
    
    # 构建折现曲线
    day_count = ql.Actual360()
    interpolation = ql.Linear()
    compounding = ql.Compounded
    compounding_frequency = ql.Annual
    
    curve = ql.ZeroCurve(dates, rates, day_count, ql.NullCalendar(),
                        interpolation, compounding, compounding_frequency)
    
    return ql.YieldTermStructureHandle(curve)

def build_implied_yield_curve(forward_rates: List[Tuple[float, float]], base_currency: str, target_currency: str, fx_rates: List[Tuple[float, float]]) -> ql.YieldTermStructure:
    """
    构建隐含收益率曲线，考虑汇率转换
    
    参数:
        forward_rates: 远期利率列表，每个元素为(期限(年), 利率(百分比))元组
        base_currency: 基础货币
        target_currency: 目标货币
        fx_rates: 汇率列表，每个元素为(期限(年), 汇率)元组
    
    返回:
        ql.YieldTermStructure: QuantLib隐含收益率曲线对象
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 创建日期和利率列表
    if not forward_rates or len(forward_rates) < 2:
        raise ValueError("forward_rates must contain at least two elements with valid data")
    if not fx_rates or len(fx_rates) < 2:
        raise ValueError("fx_rates must contain at least two elements with valid data")
    
    dates = [today + ql.Period(int(t * 365), ql.Days) for t, _ in forward_rates]
    rates = [r / 100 for _, r in forward_rates]
    
    # 创建汇率日期和汇率列表
    fx_dates = [today + ql.Period(int(t * 365), ql.Days) for t, _ in fx_rates]
    fx_values = [r for _, r in fx_rates]
    
    # 构建汇率曲线
    fx_curve = ql.ForwardCurve(fx_dates, fx_values, ql.Actual360())
    
    # 构建隐含收益率曲线
    day_count = ql.Actual360()
    interpolation = ql.Linear()
    compounding = ql.Compounded
    compounding_frequency = ql.Annual
    
    curve = ql.ForwardCurve(dates, rates, day_count)
    
    # 考虑汇率转换
    implied_rates = []
    for i in range(len(dates)):
        fx_rate = fx_curve.forwardRate(dates[i], dates[i], day_count, compounding).rate()
        implied_rate = rates[i] + fx_rate
        implied_rates.append(implied_rate)
    
    implied_curve = ql.ForwardCurve(dates, implied_rates, day_count)
    
    return ql.YieldTermStructureHandle(implied_curve)

# 保留其他现有函数
def calculate_present_value(rate, years, future_value):
    """
    使用QuantLib计算现值。
    
    :param rate: 年利率（百分比）
    :param years: 投资年限
    :param future_value: 未来值
    :return: 现值
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 设置利率曲线
    interest_rate = ql.InterestRate(rate / 100, ql.Actual360(), ql.Simple, ql.Annual)
    
    # 计算现值
    present_value = future_value / (1 + interest_rate.rate()) ** years
    return present_value

def calculate_forward_value(spot_rate, forward_rate, domestic_rate, foreign_rate, time_period):
    """
    计算外汇远期现值
    
    :param spot_rate: 即期汇率
    :param forward_rate: 远期汇率
    :param domestic_rate: 本币利率（百分比）
    :param foreign_rate: 外币利率（百分比） 
    :param time_period: 期限（年）
    :return: 远期现值
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 创建折现曲线
    domestic_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(domestic_rate / 100)), ql.Actual360())
    )
    foreign_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(foreign_rate / 100)), ql.Actual360())
    )
    
    # 计算折现因子
    discount_factor_domestic = domestic_rate_handle.discount(time_period)
    discount_factor_foreign = foreign_rate_handle.discount(time_period)
    
    # 计算远期现值
    forward_value = (forward_rate - spot_rate) * discount_factor_domestic / discount_factor_foreign
    return forward_value

def calculate_interest_rate_swap_value(fixed_rate, floating_rate, time_period, notional_amount, payment_frequency=1):
    """
    计算利率掉期现值
    
    :param fixed_rate: 固定利率（百分比）
    :param floating_rate: 浮动利率（百分比）
    :param time_period: 期限（年）
    :param notional_amount: 名义本金
    :param payment_frequency: 支付频率（每年支付次数，默认为1）
    :return: 利率掉期现值
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 创建折现曲线
    fixed_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(fixed_rate / 100)), ql.Actual360())
    )
    floating_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(floating_rate / 100)), ql.Actual360())
    )
    
    # 计算折现因子
    discount_factor_fixed = fixed_rate_handle.discount(time_period)
    discount_factor_floating = floating_rate_handle.discount(time_period)
    
    # 计算利率掉期现值
    if floating_rate == 0:
        swap_value = notional_amount * (fixed_rate - floating_rate) * time_period
    else:
        swap_value = (notional_amount * (fixed_rate - floating_rate) *
                     (1 - math.exp(-floating_rate * time_period))) / floating_rate
    
    # 考虑支付频率
    swap_value *= payment_frequency
    
    return swap_value

def calculate_swap_value(spot_rate, forward_rate, domestic_rate, foreign_rate, time_period, notional_amount):
    """
    计算外汇掉期现值
    
    :param spot_rate: 即期汇率
    :param forward_rate: 远期汇率
    :param domestic_rate: 本币利率（百分比）
    :param foreign_rate: 外币利率（百分比）
    :param time_period: 期限（年）
    :param notional_amount: 名义本金
    :return: 掉期现值
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 创建折现曲线
    domestic_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(domestic_rate / 100)), ql.Actual360())
    )
    foreign_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(foreign_rate / 100)), ql.Actual360())
    )
    
    # 计算折现因子
    discount_factor_domestic = domestic_rate_handle.discount(time_period)
    discount_factor_foreign = foreign_rate_handle.discount(time_period)
    
    # 计算掉期现值
    swap_value = notional_amount * (forward_rate - spot_rate) * discount_factor_domestic / discount_factor_foreign
    return swap_value

def calculate_interest_rate_forward_value(spot_rate, forward_rate, time_period, notional_amount):
    """
    计算利率远期现值
    
    :param spot_rate: 即期利率（百分比）
    :param forward_rate: 远期利率（百分比）
    :param time_period: 期限（年）
    :param notional_amount: 名义本金
    :return: 利率远期现值
    """
    # 设置日期
    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    
    # 创建折现曲线
    spot_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(spot_rate / 100)), ql.Actual360())
    )
    forward_rate_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(forward_rate / 100)), ql.Actual360())
    )
    
    # 计算折现因子
    discount_factor_spot = spot_rate_handle.discount(time_period)
    discount_factor_forward = forward_rate_handle.discount(time_period)
    
    # 计算利率远期现值
    forward_value = notional_amount * (forward_rate - spot_rate) * discount_factor_spot / discount_factor_forward
    return forward_value
