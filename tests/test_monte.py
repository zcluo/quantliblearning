import pytest
import numpy as np
from src.monte_carlo import MonteCarloSimulator
import QuantLib as ql


class TestMonteCarloSimulator:
    """测试蒙特卡洛模拟器"""
    
    def test_simulate_paths(self):
        """测试价格路径模拟"""
        # 设置参数
        spot = 100.0
        r = 0.05
        vol = 0.2
        T = 2.0
        steps = 360
        paths = 1000000
        
        # 创建模拟器
        simulator = MonteCarloSimulator(spot, r, vol)
        
        # 模拟路径
        simulated_paths = simulator.simulate_paths(T, steps, paths)
        
        # 验证结果
        assert simulated_paths.shape == (paths, steps + 1)
        assert np.all(simulated_paths[:, 0] == spot)
        assert np.all(simulated_paths > 0)  # 价格应该为正
    
    def test_european_option_pricing(self):
        """测试欧式期权定价"""
        # 设置参数
        spot = 100.0
        strike = 100.0
        r = 0.05
        vol = 0.2
        T = 1.0
        
        # 创建模拟器
        simulator = MonteCarloSimulator(spot, r, vol)
        
        # 使用蒙特卡洛方法计算期权价格
        mc_call_price = simulator.price_european_option('call', strike, T, num_paths=10000000)
        mc_put_price = simulator.price_european_option('put', strike, T, num_paths=10000000)
        
        # 使用Black-Scholes公式计算理论价格
        day_count = ql.Actual365Fixed()
        today = ql.Date().todaysDate()
        risk_free_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, r, day_count)
        )
        dividend_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, 0.0, day_count)
        )
        vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(today, ql.NullCalendar(), vol, day_count)
        )
        
        process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(spot)),
            dividend_ts,
            risk_free_ts,
            vol_ts
        )
        
        maturity_date = today + int(T * 365)
        exercise = ql.EuropeanExercise(maturity_date)
        
        call_payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
        put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, strike)
        
        call_option = ql.VanillaOption(call_payoff, exercise)
        put_option = ql.VanillaOption(put_payoff, exercise)
        
        engine = ql.AnalyticEuropeanEngine(process)
        call_option.setPricingEngine(engine)
        put_option.setPricingEngine(engine)
        
        bs_call_price = call_option.NPV()
        bs_put_price = put_option.NPV()
        print(bs_call_price, bs_put_price)
        print(mc_call_price, mc_put_price)
        
        # 验证蒙特卡洛价格与Black-Scholes价格接近
        assert abs(mc_call_price - bs_call_price) < 0.001
        assert abs(mc_put_price - bs_put_price) < 0.001
    
    def test_put_call_parity(self):
        """测试看涨看跌平价关系"""
        # 设置参数
        spot = 100.0
        strike = 100.0
        r = 0.05
        vol = 0.2
        T = 1.0
        
        # 创建模拟器
        simulator = MonteCarloSimulator(spot, r, vol)
        
        # 计算期权价格
        call_price = simulator.price_european_option('call', strike, T,1000000)
        put_price = simulator.price_european_option('put', strike, T,1000000)
        print(call_price,put_price)
        
        # 计算看涨看跌平价关系
        discount_factor = np.exp(-r * T)
        parity_call = put_price + spot - strike * discount_factor
        parity_put = call_price - spot + strike * discount_factor
        
        # 验证平价关系
        assert abs(call_price - parity_call) < 1.0
        assert abs(put_price - parity_put) < 1.0