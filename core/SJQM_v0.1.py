from lunar_python import Solar, Lunar
import math

user_question = '''
    核心问题:手机到底去哪儿了？
    背景信息补充:
     我在单位，手机刚刚都还在，怎么突然就找不到了


    '''

year, month, day = 2025, 7, 7
hour, minute = 13, 3  # 北京时间
lat, lon = 29.83, 106.40  # 坐标



with open('role_content.txt', 'r', encoding='utf-8') as file:
    role = file.read()

with open('response_requirements.txt', 'r', encoding='utf-8') as file:
    response = file.read()


class QiMenCalculator:

    def __init__(self, year, month, day, hour,
                 minute=0, latitude=None, longitude=None,
                 use_ji_earth_kun=True, use_gui_separate=False,
                 strict_mode=False, use_threading=True,
                 use_futou_method=False):

        # use_futou_method=False 设置为拆补法
        # use_futou_method=True 设置为符头法


        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour = int(hour)
        self.minute = int(minute)
        self.latitude = float(lat)
        self.longitude = float(lon)
        self.use_futou_method = use_futou_method  #

    def calculate_sizhu_with_jieqi(self):
        """
        考虑经度影响的八字计算

        参数:
            longitude: 东经为正数（如北京116.4），西经为负数
            默认120.0（北京时间基准经度)
        """
        solar_year = self.year
        solar_month = self.month
        solar_day = self.day
        hour = self.hour
        minute = self.minute
        longitude = self.longitude

        # 计算时差（相对于东经120度）
        delta = (longitude - 120.0) * 4 / 60  # 每度4分钟，转换为小时

        # 调整后的时间（真太阳时）
        adjusted_hour = hour + delta
        adjusted_day = solar_day

        # 处理跨日情况
        if adjusted_hour >= 24:
            adjusted_hour -= 24
            adjusted_day += 1
        elif adjusted_hour < 0:
            adjusted_hour += 24
            adjusted_day -= 1

        # 创建公历对象（使用调整后的时间）
        solar = Solar.fromYmdHms(solar_year, solar_month, adjusted_day, int(adjusted_hour),
                                 int((adjusted_hour % 1) * 60),
                                 0)
        lunar = solar.getLunar()

        # 获取当前节气（兼容不同版本的 lunar_python）
        def get_jieqi_for_date(lunar):
            jieqi_list = lunar.getJieQiList()
            current_solar = lunar.getSolar()

            # 如果 jieqi_list 是字符串列表，则手动构造节气对象
            if isinstance(jieqi_list[0], str):
                # 需要手动计算节气日期（这里简化处理，实际应使用天文算法）
                # 此处仅作示例，实际应用需更精确的计算
                jieqi_dates = {
                    # 春季
                    "立春": Solar.fromYmdHms(solar_year, 2, 4, 0, 0, 0),
                    "雨水": Solar.fromYmdHms(solar_year, 2, 19, 0, 0, 0),
                    "惊蛰": Solar.fromYmdHms(solar_year, 3, 5, 0, 0, 0),
                    "春分": Solar.fromYmdHms(solar_year, 3, 20, 0, 0, 0),
                    "清明": Solar.fromYmdHms(solar_year, 4, 5, 0, 0, 0),
                    "谷雨": Solar.fromYmdHms(solar_year, 4, 20, 0, 0, 0),

                    # 夏季
                    "立夏": Solar.fromYmdHms(solar_year, 5, 5, 0, 0, 0),
                    "小满": Solar.fromYmdHms(solar_year, 5, 21, 0, 0, 0),
                    "芒种": Solar.fromYmdHms(solar_year, 6, 6, 0, 0, 0),
                    "夏至": Solar.fromYmdHms(solar_year, 6, 21, 0, 0, 0),
                    "小暑": Solar.fromYmdHms(solar_year, 7, 7, 0, 0, 0),
                    "大暑": Solar.fromYmdHms(solar_year, 7, 23, 0, 0, 0),

                    # 秋季
                    "立秋": Solar.fromYmdHms(solar_year, 8, 7, 0, 0, 0),
                    "处暑": Solar.fromYmdHms(solar_year, 8, 23, 0, 0, 0),
                    "白露": Solar.fromYmdHms(solar_year, 9, 7, 0, 0, 0),
                    "秋分": Solar.fromYmdHms(solar_year, 9, 23, 0, 0, 0),
                    "寒露": Solar.fromYmdHms(solar_year, 10, 8, 0, 0, 0),
                    "霜降": Solar.fromYmdHms(solar_year, 10, 23, 0, 0, 0),

                    # 冬季
                    "立冬": Solar.fromYmdHms(solar_year, 11, 7, 0, 0, 0),
                    "小雪": Solar.fromYmdHms(solar_year, 11, 22, 0, 0, 0),
                    "大雪": Solar.fromYmdHms(solar_year, 12, 7, 0, 0, 0),
                    "冬至": Solar.fromYmdHms(solar_year, 12, 22, 0, 0, 0),
                    "小寒": Solar.fromYmdHms(solar_year, 1, 5, 0, 0, 0),
                    "大寒": Solar.fromYmdHms(solar_year, 1, 20, 0, 0, 0)
                }

                closest_jieqi = None
                for jq_name in jieqi_list:
                    jq_solar = jieqi_dates.get(jq_name)
                    if jq_solar and jq_solar.toYmd() <= current_solar.toYmd():
                        closest_jieqi = jq_name
                return closest_jieqi if closest_jieqi else "无节气"

            # 如果 jieqi_list 是对象列表，则直接使用
            else:
                closest_jieqi = None
                for jq in jieqi_list:
                    jq_solar = jq.getSolar()
                    if jq_solar.toYmd() <= current_solar.toYmd():
                        closest_jieqi = jq.getName()
                return closest_jieqi if closest_jieqi else "无节气"

        jieqi = get_jieqi_for_date(lunar)

        return {
            '公历': solar.toYmdHms(),
            '农历': f"{lunar.getYear()}-{lunar.getMonth():02d}-{lunar.getDay():02d} {int(adjusted_hour):02d}:{int((adjusted_hour % 1) * 60):02d}:00",
            '四柱': {
                '年柱': lunar.getYearInGanZhi(),
                '月柱': lunar.getMonthInGanZhi(),
                '日柱': lunar.getDayInGanZhi(),
                '时柱': lunar.getTimeInGanZhi()
            },
            '当前节气': jieqi
        }

    def calculate_year_ganzhi(self):
        result=self.calculate_sizhu_with_jieqi()

        return result['四柱']['年柱']

    def calculate_hour_ganzhi(self):
        """时辰干支计算（五鼠遁全表版）"""
        result=self.calculate_sizhu_with_jieqi()

        return result['四柱']['时柱']

    def calculate_month_ganzhi(self):
        result = self.calculate_sizhu_with_jieqi()

        return result['四柱']['月柱']

    def calculate_day_ganzhi(self, date):
        result = self.calculate_sizhu_with_jieqi()

        return result['四柱']['日柱']

    def get_precise_solar_term(self):
        result = self.calculate_sizhu_with_jieqi()
        # 4. 返回当前最近的节气
        return result['当前节气']

    #计算旬首
    def get_xunshou(self, hour_ganzhi):
        """
        判断当前时柱的旬首（甲子、甲戌、甲申、甲午、甲辰、甲寅）

        返回:
            旬首 (如 "甲子") 或 None (如果时柱无效)
        """
        result = self.calculate_sizhu_with_jieqi()
        shizhu = result['四柱']['时柱']  # 格式如 "丙寅"

        if not shizhu or len(shizhu) != 2:
            return None

        # 天干地支表（60甲子顺序）
        ganzhi_order = [
            "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
            "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
            "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
            "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
            "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
            "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
        ]

        # 找到当前时柱在60甲子中的位置
        try:
            idx = ganzhi_order.index(shizhu)
        except ValueError:
            return None

        # 往前找最近的甲X旬首
        for i in range(idx, -1, -1):
            if ganzhi_order[i][0] == '甲':  # 找到天干是甲的组合
                return ganzhi_order[i]

        return None

    # 计算阴阳遁
    def determine_yinyang_dun(self):
        """
        判断当前节气是阴遁还是阳遁

        返回:
            "阳遁" 或 "阴遁" 或 None (如果节气无效)
        """
        result = self.calculate_sizhu_with_jieqi()
        jieqi = result['当前节气']

        # 阳遁节气列表（冬至到芒种）
        yang_dun_jieqi = [
            '冬至', '小寒', '大寒',
            '立春', '雨水', '惊蛰',
            '春分', '清明', '谷雨',
            '立夏', '小满', '芒种'
        ]

        # 阴遁节气列表（夏至到大雪）
        yin_dun_jieqi = [
            '夏至', '小暑', '大暑',
            '立秋', '处暑', '白露',
            '秋分', '寒露', '霜降',
            '立冬', '小雪', '大雪'
        ]

        if jieqi in yang_dun_jieqi:
            return "阳遁"
        elif jieqi in yin_dun_jieqi:
            return "阴遁"
        else:
            return None  # 无效节气

    # 计算马星
    def get_horse_star(self):
        """
        计算马星的地支和宫位数字

        返回:
            {
                "horse_branch": "申/巳/寅/亥" 或 None,  # 马星地支
                "horse_palace": 2/4/6/8 或 None        # 宫位数字（后天八卦数）
            }
        """
        result = self.calculate_sizhu_with_jieqi()
        shizhi = result['四柱']['时柱'][1]  # 提取时支（如 "寅"）

        # 马星规则字典 {时支: (马星地支, 宫位数字)}
        horse_rules = {
            "寅": ("申", 2),
            "午": ("申", 2),
            "戌": ("申", 2),
            "亥": ("巳", 4),
            "卯": ("巳", 4),
            "未": ("巳", 4),
            "申": ("寅", 8),
            "子": ("寅", 8),
            "辰": ("寅", 8),
            "巳": ("亥", 6),
            "酉": ("亥", 6),
            "丑": ("亥", 6),
        }


        horse_branch, horse_palace = horse_rules[shizhi]
        return horse_branch, horse_palace

    #计算局数
    def determine_ju(self):
        """
        根据四柱结果计算时家奇门局数（可选择拆补法或符头法）

        参数:
            use_futou_method: True使用符头法，False使用拆补法

        返回:
            局数 (1-9) 或 None (如果无法确定)
        """
        result = self.calculate_sizhu_with_jieqi()
        jieqi = result['当前节气']
        rizhu = result['四柱']['日柱']
        lunar_date_part = result['农历'].split(' ')[0]  # 提取 "年-月-日" 部分
        lunar_day = int(lunar_date_part.split('-')[2])  # 提取日

        # 节气到局数的映射 (上元、中元、下元)
        jieqi_ju_mapping = {
            # 阳遁
            '冬至': (1, 7, 4),
            '小寒': (2, 8, 5),
            '大寒': (3, 9, 6),
            '立春': (8, 5, 2),
            '雨水': (9, 6, 3),
            '惊蛰': (1, 7, 4),
            '春分': (3, 9, 6),
            '清明': (4, 1, 7),
            '谷雨': (5, 2, 8),
            '立夏': (4, 1, 7),
            '小满': (5, 2, 8),
            '芒种': (6, 3, 9),
            # 阴遁
            '夏至': (9, 3, 6),
            '小暑': (8, 2, 5),
            '大暑': (7, 1, 4),
            '立秋': (2, 5, 8),
            '处暑': (1, 4, 7),
            '白露': (9, 3, 6),
            '秋分': (7, 1, 4),
            '寒露': (6, 9, 3),
            '霜降': (5, 8, 2),
            '立冬': (6, 9, 3),
            '小雪': (5, 8, 2),
            '大雪': (4, 7, 1)
        }

        if jieqi not in jieqi_ju_mapping:
            return None

        # 拆补法（按农历日直接分三元）
        if lunar_day <= 5:
            yuan_chai = 0  # 上元
        elif lunar_day <= 10:
            yuan_chai = 1  # 中元
        else:
            yuan_chai = 2  # 下元

        # 符头法（日柱天干决定元）
        tiangan = rizhu[0]  # 日柱天干
        tiangan_yuan_mapping = {
            '甲': 0, '己': 0,  # 上元
            '乙': 1, '庚': 1, '丁': 1,  # 中元
            '丙': 2, '辛': 2, '戊': 2, '癸': 2  # 下元
        }
        yuan_futou = tiangan_yuan_mapping.get(tiangan, 2)  # 默认下元

        # 根据参数选择使用哪种方法
        if self.use_futou_method:
            yuan = yuan_futou
            method_name = '符头法'
        else:
            yuan = yuan_chai
            method_name = '拆补法'

        # 获取局数
        ju = jieqi_ju_mapping[jieqi][yuan]

        # 记录元名称和方法
        if yuan == 0:
            self.yuan_name = f'上元({method_name})'
        elif yuan == 1:
            self.yuan_name = f'中元({method_name})'
        else:
            self.yuan_name = f'下元({method_name})'
        self.yuan = yuan

        return ju

    def calculate_total(self):
        """
        整合所有计算结果，包括四柱信息和奇门遁甲参数

        返回:
            包含所有结果的字典:
            {
                '公历': str,
                '农历': str,
                '四柱': dict,
                '当前节气': str,
                '旬首': str,
                '阴阳遁': str,
                '局数': int,
                '元': str
            }
        """
        # 获取基础四柱和节气信息
        base_result = self.calculate_sizhu_with_jieqi()

        # 计算奇门遁甲相关参数
        hour_ganzhi = self.calculate_hour_ganzhi()
        xunshou = self.get_xunshou(hour_ganzhi)
        yinyang_dun = self.determine_yinyang_dun()
        ju = self.determine_ju()
        yuan_name = getattr(self, 'yuan_name', '未知')

        # 整合所有结果
        total_result = {
            '公历': base_result['公历'],
            '农历': base_result['农历'],
            '四柱': base_result['四柱'],
            '当前节气': base_result['当前节气'],
            '旬首': xunshou,
            '阴阳遁': yinyang_dun,
            '局数': ju,
            '元': yuan_name
        }

        return total_result


qimen = QiMenCalculator(year=year, month=month, day=day, hour=hour, minute=minute, latitude=lat, longitude=lon)

total_result = qimen.calculate_total()
print("奇门遁甲计算结果：")
for key, value in total_result.items():

    print(f"{key}: {value}")
