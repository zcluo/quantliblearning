import QuantLib as ql
import numpy as np

class MonteCarloSimulator:
    """使用QuantLib进行蒙特卡洛模拟的类"""
    
    def __init__(self, spot_price, risk_free_rate, volatility, dividend_yield=0.0):
        """
        初始化蒙特卡洛模拟器
        
        参数:
            spot_price (float): 标的资产当前价格
            risk_free_rate (float): 无风险利率
            volatility (float): 波动率
            dividend_yield (float): 股息率，默认为0
        """
        self.spot_price = spot_price
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.dividend_yield = dividend_yield
        
    def simulate_paths(self, time_to_maturity, num_steps, num_paths):
        """
        模拟资产价格路径
        
        参数:
            time_to_maturity (float): 到期时间（年）
            num_steps (int): 时间步数
            num_paths (int): 模拟路径数
            
        返回:
            numpy.ndarray: 模拟的价格路径
        """
        # 设置日期和日历
        today = ql.Date().todaysDate()
        day_count = ql.Actual365Fixed()
        calendar = ql.NullCalendar()
        
        # 设置利率和波动率
        rate_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, self.risk_free_rate, day_count)
        )
        dividend_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, self.dividend_yield, day_count)
        )
        vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(today, calendar, self.volatility, day_count)
        )
        
        # 创建随机过程
        process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(self.spot_price)),
            dividend_ts,
            rate_ts,
            vol_ts
        )
        
        # 设置时间网格
        dt = time_to_maturity / num_steps
        
        # 创建路径生成器
        rng = ql.GaussianRandomSequenceGenerator(
            ql.UniformRandomSequenceGenerator(num_steps, ql.UniformRandomGenerator())
        )
        seq = ql.GaussianPathGenerator(process, time_to_maturity, num_steps, rng, False)
        
        # 生成路径
        paths = np.zeros((num_paths, num_steps + 1))
        paths[:, 0] = self.spot_price
        
        for i in range(num_paths):
            path = seq.next().value()
            for j in range(1, num_steps + 1):
                paths[i, j] = path[j-1]
                
        return paths
    
    def price_european_option(self, option_type, strike, time_to_maturity, num_paths=10000):
        """
        使用蒙特卡洛方法为欧式期权定价
        
        参数:
            option_type (str): 期权类型，'call' 或 'put'
            strike (float): 行权价
            time_to_maturity (float): 到期时间（年）
            num_paths (int): 模拟路径数
            
        返回:
            float: 期权价格
        """
        # 设置日期和日历
        today = ql.Date().todaysDate()
        day_count = ql.Actual365Fixed()
        calendar = ql.NullCalendar()
        
        # 设置利率和波动率
        rate_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, self.risk_free_rate, day_count)
        )
        dividend_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, self.dividend_yield, day_count)
        )
        vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(today, calendar, self.volatility, day_count)
        )
        
        # 创建随机过程
        process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(self.spot_price)),
            dividend_ts,
            rate_ts,
            vol_ts
        )
        
        # 设置期权参数
        maturity_date = today + int(time_to_maturity * 365)
        option_type_ql = ql.Option.Call if option_type.lower() == 'call' else ql.Option.Put
        payoff = ql.PlainVanillaPayoff(option_type_ql, strike)
        exercise = ql.EuropeanExercise(maturity_date)
        option = ql.VanillaOption(payoff, exercise)
        
        # 使用蒙特卡洛引擎
        engine = ql.MCEuropeanEngine(process, "pseudorandom", 
                                     timeSteps=100,
                                     requiredSamples=num_paths,
                                     seed=42)
        option.setPricingEngine(engine)
        
        return option.NPV()