import QuantLib as ql
#import matplotlib
#matplotlib.use('Agg')  # 必须在导入 pyplot 之前设置
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display



today = ql.Date(7, ql.March, 2014)

ql.Settings.instance().evaluationDate = today # 设置当前日期
print(ql.Settings.instance().evaluationDate) # 输出当前日期
option = ql.EuropeanOption(ql.PlainVanillaPayoff(ql.Option.Call, 100.0), ql.EuropeanExercise(ql.Date(7, ql.June, 2014))) # 创建欧式看涨期权

u = ql.SimpleQuote(100.0) # 标的资产价格
r = ql.SimpleQuote(0.01)    # 无风险利率
sigma = ql.SimpleQuote(0.20) # 波动率

riskFreeCurve = ql.FlatForward(0, ql.TARGET(), ql.QuoteHandle(r), ql.Actual360())  # 无风险利率曲线
volatility = ql.BlackConstantVol(0, ql.TARGET(), ql.QuoteHandle(sigma), ql.Actual360())  # 波动率曲线

process = ql.BlackScholesProcess(ql.QuoteHandle(u), ql.YieldTermStructureHandle(riskFreeCurve), ql.BlackVolTermStructureHandle(volatility))  # Black-Scholes过程

engine = ql.AnalyticEuropeanEngine(process) # 欧式期权定价引擎
option.setPricingEngine(engine) # 设置定价引擎
print(option.NPV()) # 输出期权价格
print(option.delta()) # 输出期权的Delta值
print(option.gamma()) # 输出期权的Gamma值
print(option.vega())    # 输出期权的Vega值
print(option.rho())   # 输出期权的Rho值
print(option.theta()) # 输出期权的Theta值
print(option.dividendRho()) # 输出期权的分红Rho值



# 生成标的资产价格区间
spot_prices = np.linspace(80, 120, 50)
npvs = []

# 遍历计算不同标的价对应的期权价值
original_value = u.value()  # 保存原始值
for price in spot_prices:
    u.setValue(price)
    npvs.append(option.NPV())
u.setValue(original_value)  # 恢复原始值

# 配置可视化
# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 根据系统实际字体选择
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.figure(figsize=(10, 6))
plt.plot(spot_prices, npvs, 'b-', linewidth=2)
plt.title('欧式看涨期权价格曲线', fontsize=14)
plt.xlabel('标的资产价格', fontsize=12)
plt.ylabel('期权价格(NPV)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.axvline(x=100, color='r', linestyle='--', label='行权价')
plt.legend()
plt.savefig('option_price_curve.png', dpi=300, bbox_inches='tight')
# plt.show()

ql.Settings.instance().evaluationDate = ql.Date(7, ql.April, 2014)
print(option.NPV())
ys = []
for price in spot_prices:
    u.setValue(price)
    ys.append(option.NPV())
plt.plot(spot_prices, ys, 'r--', linewidth=2)
plt.show()
ql.Settings.instance().evaluationDate = today
u.setValue(105.0)
r.setValue(0.01)
sigma.setValue(0.20)
print(option.NPV())

model = ql.HestonModel(
    ql.HestonProcess(
        ql.YieldTermStructureHandle(riskFreeCurve),
        ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), ql.QuoteHandle(r), ql.Actual360())),
        ql.QuoteHandle(u),
        0.04,
        0.1,
        0.01,
        0.05,
        -0.75
    )
)

engine = ql.AnalyticHestonEngine(model)
option.setPricingEngine(engine)

print(option.NPV())

engine = ql.MCEuropeanEngine(
    process,
    "pseudorandom",
    timeSteps=10,
    requiredSamples=250000)
option.setPricingEngine(engine)
print(option.NPV())

engine = ql.MCEuropeanHestonEngine(
    ql.HestonProcess(
        ql.YieldTermStructureHandle(riskFreeCurve),
        ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), ql.QuoteHandle(r), ql.Actual360())),
        ql.QuoteHandle(u),
        0.04,
        0.1,
        0.01,
        0.05,
        -0.75
    ),
    "pseudorandom",
    timeSteps=10,
    requiredSamples=250000)
option.setPricingEngine(engine)
print(option.NPV())

engine = ql.MCEuropeanGJRGARCHEngine(
    ql.GJRGARCHProcess(
        ql.YieldTermStructureHandle(riskFreeCurve),
        ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), ql.QuoteHandle(r), ql.Actual360())),
        ql.QuoteHandle(u),
        0.04,
        0.1,
        0.01,
        0.05,
        0.02,
        0.01,
        0.01
    ),
    "pseudorandom",
    timeSteps=10,
    requiredSamples=2500000)
option.setPricingEngine(engine)
print(option.NPV())





