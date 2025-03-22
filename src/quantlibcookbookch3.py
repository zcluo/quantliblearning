import QuantLib as ql
today = ql.Date(8, ql.October, 2014)
ql.Settings.instance().evaluationDate = today

option = ql.BarrierOption(ql.Barrier.UpIn,
                 120.0,
                 0.0,
                 ql.PlainVanillaPayoff(ql.Option.Call, 100.0), # 创建看涨期权
                    ql.EuropeanExercise(ql.Date(8, ql.January, 2015)))
u = ql.SimpleQuote(100.0)
r = ql.SimpleQuote(0.01)
sigma = ql.SimpleQuote(0.20)

riskFreeCurve = ql.FlatForward(0,
                               ql.TARGET(),
                               ql.QuoteHandle(r),
                               ql.Actual360())
volatility = ql.BlackConstantVol(0,
                                 ql.TARGET(),
                                 ql.QuoteHandle(sigma),
                                 ql.Actual360())
process = ql.BlackScholesProcess(ql.QuoteHandle(u),
                                 ql.YieldTermStructureHandle(riskFreeCurve),
                                 ql.BlackVolTermStructureHandle(volatility))
engine = ql.AnalyticBarrierEngine(process)
option.setPricingEngine(engine)
print(option.NPV())
# print(option.delta())
u0 = u.value()
h = 0.01
P0 = option.NPV()
print(P0)
u.setValue(u0 + h)
P_plus = option.NPV()
print(P_plus)
u.setValue(u0 - h)
P_minus = option.NPV()
print(P_minus)
u.setValue(u0)
delta = (P_plus - P_minus) / (2 * h)
print(delta)    
gamma = (P_plus - 2 * P0 + P_minus) / (h * h)
print(gamma)   

r0 = r.value()
h = 0.0001
r.setValue(r0 + h)
P_plus = option.NPV()
r.setValue(r0)
Rho = (P_plus - P0) / h
print(Rho)

sigma0 = sigma.value()
h = 0.0001
sigma.setValue(sigma0 + h)
P_plus = option.NPV()
sigma.setValue(sigma0)
Vega = (P_plus - P0) / h
print(Vega)
 
ql.Settings.instance().evaluationDate = today + 1
P1 = option.NPV()
h = 1.0 / 365
Theta = (P1 - P0) / h
print(Theta)