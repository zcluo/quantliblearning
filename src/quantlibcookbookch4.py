import QuantLib as ql
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


today = ql.Date(17, ql.October, 2016)
ql.Settings.instance().evaluationDate = today

data = [(2, 0.02),  (4, 0.0225),  (6, 0.025),  (8, 0.0275),
        (10, 0.03), (12, 0.0325), (14, 0.035), (16, 0.0375),
        (18, 0.04), (20, 0.0425), (22, 0.045), (24, 0.0475),
        (26, 0.05), (28, 0.0525), (30, 0.055)]

print(data)

calendar = ql.TARGET()
settlement = calendar.advance(today, 3, ql.Days)  # today + 3 days

quotes = []
helpers = []

for length, coupon in data:
    # settlement + length years
    maturity = calendar.advance(settlement, length, ql.Years)
    schedule = ql.Schedule(
        settlement,
        maturity,
        ql.Period(ql.Annual),
        calendar,
        ql.ModifiedFollowing,
        ql.ModifiedFollowing,
        ql.DateGeneration.Backward,
        False)  # backward from maturity date
    quote = ql.SimpleQuote(100.0)
    quotes.append(quote)
    helpers.append(ql.FixedRateBondHelper(
        ql.QuoteHandle(quote),
        3,
        100.0,
        schedule,
        [coupon],
        ql.SimpleDayCounter(),
        ql.ModifiedFollowing))
    curve = ql.FittedBondDiscountCurve(
        0, calendar, helpers, ql.SimpleDayCounter(), ql.NelsonSiegelFitting())

print(curve)
sample_times = np.linspace(0.0, 30.0, 301)
sample_discounts = [curve.discount(t) for t in sample_times]
print(sample_discounts)

# 配置可视化
# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 根据系统实际字体选择
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.figure(figsize=(10, 6))
plt.plot(sample_times, sample_discounts, 'b-', linewidth=2)
plt.title('债券折现曲线', fontsize=14)
plt.xlabel('时间', fontsize=12)
plt.ylabel('折现因子', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

plt.legend()
plt.savefig('option_price_curve.png', dpi=300, bbox_inches='tight')
plt.show()

schedule = ql.Schedule(today, calendar.advance(today, 15, ql.Years),
                       ql.Period(ql.Semiannual), calendar,
                       ql.ModifiedFollowing, ql.ModifiedFollowing,
                       ql.DateGeneration.Backward, False)
bond = ql.FixedRateBond(3, 100.0, schedule, [0.04], ql.Actual360())
bond.setPricingEngine(
    ql.DiscountingBondEngine(ql.YieldTermStructureHandle(curve)))
print(bond.cleanPrice())

prices = []
def print_price():
    p = bond.cleanPrice()
    prices.append(p)
    print(p)

o = ql.Observer(print_price)
o.registerWith(bond)

quotes[2].setValue(101.0)