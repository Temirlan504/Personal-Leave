def convert_dollars_to_days_hours(user, amount):
    daily_pay = user.base_salary / 260  # 260 workdays/year
    total_hours = (amount / daily_pay) * 8  # 8h per day

    days = int(total_hours // 8)
    hours = int(total_hours % 8)
    return days, hours
