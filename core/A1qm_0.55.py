user_question = '''
    核心问题:
    背景信息补充:
     


    '''

year, month, day = 2025, 7, 12
hour, minute = 7, 28   # 北京时间
lat, lon = 29.83, 106.40  # 坐标

41
from lunar_python import Solar, Lunar
from A2qm_base import QiMenCalculator# 调用奇门基本排盘函数
from A3qm_changsheng import ChangShengCalculator# 调用长生状态函数
from A4qm_shensha import ShenShaCalculator # 调用神煞函数
from A5qm_direction import DirectionCalculator # 调用方向函数

with open('role_content.txt', 'r', encoding='utf-8') as file:
    role = file.read()

with open('response_requirements.txt', 'r', encoding='utf-8') as file:
    response = file.read()




qimen = QiMenCalculator(year=year, month=month, day=day, hour=hour, minute=minute, latitude=lat, longitude=lon)

base_result = qimen.calculate_base()

# 计算日干长生状态
changsheng_calc = ChangShengCalculator(base_result)
changsheng_result = changsheng_calc.calculate()

# 整合到base_result
base_result['年干_月干_日干_时干_长生状态'] = changsheng_result
#计算神煞
shensha_calc = ShenShaCalculator(base_result)
shensha_calc.calculate_all_shensha()
#计算方向
direction_calculator = DirectionCalculator(base_result)
base_result = direction_calculator.enhance_pan_info()



#=============================

# print('系统角色扮演：')
# print(role)
#
# print("")
# print("奇门排盘信息：")

for key, value in base_result.items():
    print(f"{key}: {value}")


# print("")
# print("用户问题：")
# print(user_question)
#
# print('系统回答要求：')
# print(response)