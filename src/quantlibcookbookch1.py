import QuantLib as ql
import pandas as pd
import numpy as np

date = ql.Date(31,3,2015)
print(date)

print("%d-%d-%d" % (date.dayOfMonth(), date.month(), date.year()))

print(date.weekday() == ql.Tuesday)

print(type(date + 1))

print("Add a day: {0}".format(date + 1))
print("Subtract a day: {0}".format(date - 1))
print("Add a week: {0}".format(date + ql.Period(1, ql.Weeks)))
print("Add a month: {0}".format(date + ql.Period(1, ql.Months)))
print("Add a year: {0}".format(date + ql.Period(1, ql.Years)))

print(date == ql.Date(31,3,2015))
print(date > ql.Date(30,3,2015))
print(date < ql.Date(1,4,2015))
print(date != ql.Date(1,4,2015))

us_calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
italy_calendar = ql.Italy()

period = ql.Period(60, ql.Days)
raw_date = date + period
us_date = us_calendar.advance(date, period) # 美国日历
italy_date = italy_calendar.advance(date, period) # 意大利日历

print("Add 60 days: {0}".format(raw_date))
print("Add 60 days (US calendar): {0}".format(us_date))
print("Add 60 days (Italy calendar): {0}".format(italy_date))

us_busdays = us_calendar.businessDaysBetween(date, us_date)
italy_busdays = italy_calendar.businessDaysBetween(date, italy_date)
print("Business days between {0} and {1} (US calendar): {2}".format(date, us_date, us_busdays))
print("Business days between {0} and {1} (Italy calendar): {2}".format(date, italy_date, italy_busdays))

joint_calendar = ql.JointCalendar(us_calendar, italy_calendar)
joint_date = joint_calendar.advance(date, period)
print("Add 60 days (joint calendar): {0}".format(joint_date))
joint_busdays = joint_calendar.businessDaysBetween(date, joint_date)
print("Business days between {0} and {1} (joint calendar): {2}".format(date, joint_date, joint_busdays))


effective_date = ql.Date(1,1,2015)
termination_date = ql.Date(1,1,2016)
ternor = ql.Period(1, ql.Months)
calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
business_convention = ql.Following
termination_business_convention = ql.Following
date_generation = ql.DateGeneration.Forward
end_of_month = False

schedule = ql.Schedule(effective_date, termination_date, ternor, calendar, business_convention, termination_business_convention, date_generation, end_of_month)
print(pd.DataFrame({'date': list(schedule)}))

annual_rate = 0.05
day_count = ql.ActualActual(ql.ActualActual.ISDA)
compound_type = ql.Compounded
frequency = ql.Annual
interest_rate = ql.InterestRate(annual_rate, day_count, compound_type, frequency)
print("Compound type: {0}".format(compound_type))
print("Frequency: {0}".format(interest_rate.frequency()))
print("Annual rate: {0}".format(interest_rate.rate()))
print("Interest rate: {0}".format(interest_rate.rate()))
print("Day count: {0}".format(interest_rate.dayCounter()))
print(interest_rate)

t = 2.0
print(interest_rate.compoundFactor(t))
print((1+annual_rate)**t)

print(interest_rate.discountFactor(t))
print(1.0/interest_rate.compoundFactor(t))

new_freqency = ql.Semiannual
new_interest_rate = interest_rate.equivalentRate(compound_type, new_freqency, t)
print("New frequency: {0}".format(new_interest_rate.frequency()))
print("New annual rate: {0}".format(new_interest_rate.rate()))
print("New interest rate: {0}".format(new_interest_rate.rate()))

print(new_interest_rate)

print(interest_rate.discountFactor(t))
print(new_interest_rate.discountFactor(t))








