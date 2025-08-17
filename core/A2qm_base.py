
from lunar_python import Solar, Lunar
import math
from datetime import datetime, timedelta  # 添加datetime模块导入


class QiMenCalculator:

    def __init__(self, year, month, day, hour,
                 minute=0 ,latitude=None, longitude=None,
                 use_futou_method=False):

        # use_futou_method=False 设置为拆补法
        # use_futou_method=True 设置为符头法


        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour = int(hour)
        self.minute = int(minute)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
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

        # === 修正时间计算（保持输出格式不变）===
        # 1. 计算总分钟数（避免浮点数误差）
        # 时间计算部分（必须包含这段）
        total_minutes = hour * 60 + minute + (longitude - 120.0) * 4

        # === 新增：日柱切换点处理（23:00后属于下一天） ===
        # 创建基准日期时间
        base_dt = datetime(solar_year, solar_month, solar_day)
        adjusted_dt = base_dt + timedelta(minutes=total_minutes)

        # 处理日柱切换点（23:00）
        if adjusted_dt.hour >= 23:
            # 23:00后属于下一天的日柱
            adjusted_dt = adjusted_dt - timedelta(hours=23) + timedelta(days=1)

        # 提取调整后的日期时间
        solar_year = adjusted_dt.year
        solar_month = adjusted_dt.month
        solar_day = adjusted_dt.day
        adjusted_hour = adjusted_dt.hour
        adjusted_minute = adjusted_dt.minute

        solar = Solar.fromYmdHms(
            solar_year, solar_month, solar_day,
            int(adjusted_hour),
            int(adjusted_minute),
            0
        )

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
            '农历': f"{lunar.getYear()}-{int(lunar.getMonth()):02d}-{int(lunar.getDay()):02d} {int(adjusted_hour):02d}:{int(adjusted_minute):02d}:00",
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

     # 计算旬首
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

            # 向前找最近的甲X旬首（处理边界情况）
            for i in range(idx, idx - 11, -1):  # 最多搜索10个位置（一旬的长度）
                adjusted_idx = i % 60  # 处理循环边界
                if ganzhi_order[adjusted_idx][0] == '甲':  # 找到天干是甲的组合
                    return ganzhi_order[adjusted_idx]

            # 如果循环结束都没找到（理论上不可能，但安全处理）
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
    def get_futou(self, rizhu):
        """
        根据日柱确定符头 - 修复表格数据缺失问题
        规则：
        1. 如果日柱天干是甲或己，直接返回日柱作为符头
        2. 否则使用标准60甲子序列向前查找最近的符头
        """
        # 1. 检查日柱本身是否为符头
        if rizhu[0] in ['甲', '己']:
            return rizhu  # 日柱本身就是符头

        # 2. 使用标准60甲子序列（确保包含所有干支）
        ganzhi_order = [
            "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
            "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
            "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
            "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
            "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
            "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
        ]

        # 找到当前日柱在序列中的位置
        try:
            current_idx = ganzhi_order.index(rizhu)
        except ValueError:
            return None

        # 向左查找最近的符头（甲或己）
        futou = None
        for i in range(current_idx, -1, -1):
            gan = ganzhi_order[i][0]
            if gan in ['甲', '己']:
                futou = ganzhi_order[i]
                break

        return futou

    def  determine_ju(self):
        """
        根据符头法确定局数
        1. 先根据日柱确定符头
        2. 根据符头的地支确定上中下元：
            上元：子、午、卯、酉
            中元：寅、申、巳、亥
            下元：辰、戌、丑、未
        """
        # 确保已计算四柱
        if '四柱' not in self.base_result:
            return None

        # 获取日柱
        rizhu = self.base_result['四柱']['日柱']

        # 获取符头
        futou = self.get_futou(rizhu)
        if not futou:
            return None

        # 提取符头的地支
        dizhi = futou[1]

        # 地支到元的映射
        dizhi_to_yuan = {
            '子': 0, '午': 0, '卯': 0, '酉': 0,  # 上元
            '寅': 1, '申': 1, '巳': 1, '亥': 1,  # 中元
            '辰': 2, '戌': 2, '丑': 2, '未': 2  # 下元
        }

        # 获取元编号
        yuan = dizhi_to_yuan.get(dizhi, 2)

        # 节气到局数的映射
        jieqi = self.base_result['当前节气']
        jieqi_ju_mapping = {
            '冬至': (1, 7, 4), '小寒': (2, 8, 5), '大寒': (3, 9, 6),
            '立春': (8, 5, 2), '雨水': (9, 6, 3), '惊蛰': (1, 7, 4),
            '春分': (3, 9, 6), '清明': (4, 1, 7), '谷雨': (5, 2, 8),
            '立夏': (4, 1, 7), '小满': (5, 2, 8), '芒种': (6, 3, 9),
            '夏至': (9, 3, 6), '小暑': (8, 2, 5), '大暑': (7, 1, 4),
            '立秋': (2, 5, 8), '处暑': (1, 4, 7), '白露': (9, 3, 6),
            '秋分': (7, 1, 4), '寒露': (6, 9, 3), '霜降': (5, 8, 2),
            '立冬': (6, 9, 3), '小雪': (5, 8, 2), '大雪': (4, 7, 1)
        }

        if jieqi not in jieqi_ju_mapping:
            return None

        # 获取局数
        ju = jieqi_ju_mapping[jieqi][yuan]

        # 记录元名称
        if yuan == 0:
            yuan_name = '上元(符头法)'
        elif yuan == 1:
            yuan_name = '中元(符头法)'
        else:
            yuan_name = '下元(符头法)'

        # 将结果存入 base_result
        self.base_result['符头法'] = {
            '日柱': rizhu,
            '符头': futou,
            '符头地支': dizhi,
            '元': yuan,
            '元名称': yuan_name,
            '局数': ju
        }

        # 兼容旧代码
        self.yuan = yuan
        self.yuan_name = yuan_name

        return ju






    # 计算地盘
    def arrange_di_pan(self):
        """排列地盘三奇六仪并打印九宫格 - 完善5宫寄坤2宫逻辑"""
        # 提取关键参数
        yinyang_dun = self.base_result['阴阳遁']
        ju = self.base_result['局数']

        # 三奇六仪固定顺序
        san_qi_liu_yi = ['戊', '己', '庚', '辛', '壬', '癸', '丁', '丙', '乙']

        # 九宫位置映射（宫位数字:位置索引）
        palace_order = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        # 确定起始位置（局数对应的宫位）
        start_index = palace_order.index(ju)

        # 创建空九宫
        di_pan = [''] * 9

        # 根据阴阳遁排列
        if yinyang_dun == "阳遁":
            # 阳遁：顺布
            for i in range(9):
                pos = (start_index + i) % 9
                di_pan[pos] = san_qi_liu_yi[i]
        else:
            # 阴遁：逆布
            for i in range(9):
                pos = (start_index - i + 9) % 9
                di_pan[pos] = san_qi_liu_yi[i]

        # 格式化为九宫布局 - 保持原始结构
        di_pan_layout = {
            1: di_pan[0],
            2: di_pan[1],  # 2宫原有地盘干
            3: di_pan[2],
            4: di_pan[3],
            5: di_pan[4],  # 5宫地盘干
            6: di_pan[5],
            7: di_pan[6],
            8: di_pan[7],
            9: di_pan[8]
        }

        # === 创建寄宫后的布局 ===
        di_pan_layout_with_ji = di_pan_layout.copy()

        # 5宫寄坤2宫逻辑：5宫干添加到2宫，但不覆盖2宫原有干
        if di_pan_layout[5]:  # 确保5宫有地盘干
            # 如果2宫已经是列表，直接追加
            if isinstance(di_pan_layout_with_ji[2], list):
                di_pan_layout_with_ji[2].append(di_pan_layout[5])
            # 如果2宫是字符串，转为列表并添加（保留原有干）
            elif di_pan_layout_with_ji[2]:
                di_pan_layout_with_ji[2] = [di_pan_layout_with_ji[2], di_pan_layout[5]]
            # 如果2宫为空，创建列表
            else:
                di_pan_layout_with_ji[2] = [di_pan_layout[5]]

        # 打印九宫格（使用寄宫布局）
        print("\n地盘九宫格布局：")
        print("┌─────┬─────┬─────┐")
        print(
            f"│ {di_pan_layout_with_ji[4]} │ {di_pan_layout_with_ji[9]} │ {self.format_palace_2(di_pan_layout_with_ji[2])} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {di_pan_layout_with_ji[3]} │ {di_pan_layout_with_ji[5]} │ {di_pan_layout_with_ji[7]} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {di_pan_layout_with_ji[8]} │ {di_pan_layout_with_ji[1]} │ {di_pan_layout_with_ji[6]} │")
        print("└─────┴─────┴─────┘")

        # 保存两种布局
        self.base_result['地盘'] = di_pan_layout  # 原始布局
        self.base_result['地盘带寄宫'] = di_pan_layout_with_ji  # 寄宫布局

    def format_palace_2(self, value):
        """格式化2宫显示（处理可能包含两个地盘干的情况）"""
        if isinstance(value, list):
            return f"{value[0]}/{value[1]}"
        return value

    #错  #值符计算
    def calculate_zhi_fu(self):
        """
        独立计算值符（八神之首）的位置 - 修复甲时问题和值符定位问题
        规则：
        1. 甲时使用映射规则（甲子→戊等）
        2. 正确处理2宫包含多个地盘干的情况
        3. 中五宫寄坤二宫
        """
        # 确保base_result已初始化
        if not hasattr(self, 'base_result') or not self.base_result:
            print("错误：base_result未初始化")
            return

        # 获取必要信息
        di_pan = self.base_result.get('地盘')
        if not di_pan:
            print("错误：地盘数据缺失")
            return

        shi_zhu = self.base_result.get('四柱', {}).get('时柱', '')
        if not shi_zhu or len(shi_zhu) < 2:
            print("错误：时柱信息缺失或格式不正确")
            return

        # 提取时干和时支
        shi_gan = shi_zhu[0]
        shi_zhi = shi_zhu[1]

        # 甲时映射规则（六仪藏甲）
        jia_mapping = {
            '子': '戊',  # 甲子→戊
            '戌': '己',  # 甲戌→己
            '申': '庚',  # 甲申→庚
            '午': '辛',  # 甲午→辛
            '辰': '壬',  # 甲辰→壬
            '寅': '癸'  # 甲寅→癸
        }

        # 处理甲时：使用时支映射到隐藏天干
        if shi_gan == '甲':
            if shi_zhi in jia_mapping:
                target_gan = jia_mapping[shi_zhi]
                print(f"时柱为甲{shi_zhi}，映射为{target_gan}")
            else:
                # 如果时支不在映射表中，保持原有时干
                target_gan = shi_gan
                print(f"警告：甲时支{shi_zhi}不在映射表中，使用原时干")
        else:
            target_gan = shi_gan

        print(f"用于定位值符的天干: {target_gan}")

        # 特殊处理：当target_gan为甲时，使用原始时干
        if target_gan == '甲':
            target_gan = shi_gan
            print(f"目标天干为甲，使用原始时干: {shi_gan}")

        # 找到目标天干在地盘中的位置
        zhi_fu_palace = None

        # 1. 遍历所有宫位
        for palace, gan in di_pan.items():
            # 特殊处理2宫（列表形式）
            if palace == 2 and isinstance(gan, list):
                if target_gan in gan:
                    zhi_fu_palace = 2
                    print(f"在坤二宫(含中五宫)找到天干 {target_gan}")
                    break
            # 普通情况
            elif gan == target_gan:
                zhi_fu_palace = palace
                # 中五宫寄坤二宫
                if zhi_fu_palace == 5:
                    zhi_fu_palace = 2
                    print(f"值符在中五宫，寄坤二宫")
                break

        # 2. 如果没找到，检查中五宫（寄坤二宫）
        if zhi_fu_palace is None:
            if di_pan.get(5) == target_gan:
                zhi_fu_palace = 2  # 中五宫寄坤二宫
                print(f"值符在中五宫，寄坤二宫")
            else:
                # 检查坤二宫本身
                if di_pan.get(2) == target_gan:
                    zhi_fu_palace = 2

        # 3. 如果还没找到，尝试在坤二宫查找（因为中五宫寄此宫）
        if zhi_fu_palace is None:
            # 坤二宫可能有中五宫寄来的干
            if di_pan.get(5) == target_gan:
                zhi_fu_palace = 2
                print(f"值符在中五宫，寄坤二宫")

        # 4. 特殊处理：坤二宫可能包含中五宫的地盘干
        if zhi_fu_palace is None and di_pan.get(2) is not None:
            # 坤二宫的地盘干可能包含中五宫的天干
            if di_pan[2] == target_gan:
                zhi_fu_palace = 2

        if zhi_fu_palace is None:
            print(f"错误：未找到天干 {target_gan} 在地盘的位置")
            # 打印当前地盘布局以便调试
            print("当前地盘布局:")
            for palace in range(1, 10):
                print(f"宫位 {palace}: {di_pan.get(palace, '')}")
            return

        # 保存结果
        self.base_result['值符宫位'] = zhi_fu_palace
        print(f"值符宫位: {zhi_fu_palace}")

        return zhi_fu_palace

    #计算天干
    def arrange_tian_pan(self):
        if not hasattr(self, 'base_result') or not self.base_result:
            return

        # 初始化天盘（中五宫设为'wu'）
        tian_pan = {i: 'wu' if i == 5 else '' for i in range(1, 10)}
        self.base_result['天盘'] = tian_pan

        # 获取必要参数
        di_pan = self.base_result.get('地盘', {})
        if not di_pan:
            print("错误：地盘数据缺失")
            return

        # 获取旬首并确定值符天干
        xunshou = self.base_result['旬首']
        xunshou_to_fu_gan = {
            '甲子': '戊', '甲戌': '己', '甲申': '庚',
            '甲午': '辛', '甲辰': '壬', '甲寅': '癸'
        }
        fu_gan = xunshou_to_fu_gan.get(xunshou)
        if not fu_gan:
            print(f"错误：无效的旬首 {xunshou}")
            return

        # 获取值符宫位（时干位置）
        fu_palace = self.base_result['值符宫位']
        if fu_palace == 5:  # 中五宫寄坤二宫
            fu_palace = 2
            print("值符宫位寄坤二宫")

        # 固定宫位顺序（1→8→3→4→9→2→7→6）
        palace_order = [1, 8, 3, 4, 9, 2, 7, 6]

        # 构建地盘序列（处理坤二宫双干情况）
        di_sequence = []
        for palace in palace_order:
            if palace == 2:  # 坤二宫特殊处理
                gan_2 = di_pan.get(2, '')
                if isinstance(gan_2, list) and len(gan_2) > 0:
                    # 坤二宫原有干 + 中五宫寄宫干
                    di_sequence.append(gan_2[0])  # 2宫本宫干
                    di_sequence.append(gan_2[1])  # 5宫寄宫干
                elif isinstance(gan_2, str) and '/' in gan_2:
                    # 处理字符串格式的"辛/戊"
                    parts = gan_2.split('/')
                    di_sequence.append(parts[0])
                    if len(parts) > 1:
                        di_sequence.append(parts[1])
                else:
                    di_sequence.append(gan_2)
            else:
                di_sequence.append(di_pan.get(palace, ''))

        # 查找值符天干在地盘序列中的位置
        try:
            start_index = di_sequence.index(fu_gan)
            print(f"值符天干 {fu_gan} 在地盘序列位置: {start_index}")
        except ValueError:
            print(f"错误：未找到值符天干 {fu_gan}")
            print(f"地盘序列: {di_sequence}")
            return

        # 值符落宫设置值符天干
        tian_pan[fu_palace] = fu_gan

        # 确定起始位置（值符宫位在顺序中的索引）
        try:
            palace_start_idx = palace_order.index(fu_palace)
        except ValueError:
            palace_start_idx = palace_order.index(2)  # 寄宫情况默认坤二宫

        # 填充剩余宫位（跳过值符宫位）
        current_gan_idx = (start_index + 1) % len(di_sequence)
        current_palace_idx = (palace_start_idx + 1) % len(palace_order)

        # 需要填充的宫位数：总宫位数-1（因为值符宫位已经设置）
        for _ in range(len(palace_order) - 1):
            target_palace = palace_order[current_palace_idx]

            # 跳过已设置的值符宫位（如果值符宫位在顺序中，且当前正好指向它，则跳过）
            if target_palace == fu_palace:
                current_palace_idx = (current_palace_idx + 1) % len(palace_order)
                target_palace = palace_order[current_palace_idx]

            # 设置天盘干
            tian_pan[target_palace] = di_sequence[current_gan_idx]

            # 移动到下一个位置
            current_gan_idx = (current_gan_idx + 1) % len(di_sequence)
            current_palace_idx = (current_palace_idx + 1) % len(palace_order)

        # 关键修改：确定天盘5宫的寄宫位置
        # 1. 获取地盘2宫的地盘干
        di_gan_2 = di_pan.get(2, '')
        if isinstance(di_gan_2, list) and len(di_gan_2) > 0:
            di_gan_2 = di_gan_2[0]  # 取坤二宫的本宫干
        elif isinstance(di_gan_2, str) and '/' in di_gan_2:
            di_gan_2 = di_gan_2.split('/')[0]  # 取斜杠前的部分

        # 2. 找到地盘2宫地盘干对应的天盘干所在的宫位
        ji_palace = None
        for palace, gan in tian_pan.items():
            if gan == di_gan_2 and palace != 5:  # 排除中五宫本身
                ji_palace = palace
                break

        # 3. 设置天盘5宫的寄宫位置
        if ji_palace is not None:
            # 获取5宫的地盘干
            di_gan_5 = di_pan.get(5, '')
            if isinstance(di_gan_5, list) and len(di_gan_5) > 0:
                di_gan_5 = di_gan_5[0]
            elif isinstance(di_gan_5, str) and '/' in di_gan_5:
                di_gan_5 = di_gan_5.split('/')[0]

            # 在寄宫位置显示双干格式
            if tian_pan[ji_palace] and di_gan_5:
                tian_pan[ji_palace] = f"{tian_pan[ji_palace]}/{di_gan_5}"
            elif di_gan_5:
                tian_pan[ji_palace] = f"{tian_pan[ji_palace]}/{di_gan_5}"
            elif tian_pan[ji_palace]:
                tian_pan[ji_palace] = f"{tian_pan[ji_palace]}/"

            print(f"天盘5宫寄于{ji_palace}宫（地盘2宫干'{di_gan_2}'所在天盘干宫位）")
        else:
            print(f"警告：未找到地盘2宫干'{di_gan_2}'对应的天盘干宫位")

        # 保存结果
        self.base_result['天盘'] = tian_pan
        self.base_result['值符落宫'] = fu_palace

        # 打印天盘布局（保持原格式）
        print("\n【天盘布局】")
        print(f"旬首: {xunshou} => 值符天干: {fu_gan}")
        print(f"值符位置: {fu_palace}宫")
        print(f"地盘序列: {di_sequence}")
        print("┌─────┬─────┬─────┐")
        print(f"│ {tian_pan[4]} │ {tian_pan[9]} │ {tian_pan[2]} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {tian_pan[3]} │ {tian_pan[5]} │ {tian_pan[7]} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {tian_pan[8]} │ {tian_pan[1]} │ {tian_pan[6]} │")
        print("└─────┴─────┴─────┘")

    def arrange_stars_and_doors(self):
        """
        根据旬首地盘干落宫确定值符星和值使门，并排布八神、八门、九星
        """
        # 首先设置默认极值，防止后续KeyError
        self.base_result['值符星'] = "未知"
        self.base_result['值使门'] = "未知"

        # 获取必要数据
        if not hasattr(self, 'base_result') or not self.base_result:
            print("错误：base_result未初始化")
            return

        di_pan = self.base_result.get('地盘', {})
        shi_zhu = self.base_result.get('四柱', {}).get('时柱', '')
        is_yang = self.base_result.get('阴阳遁') == '阳遁'
        xunshou = self.base_result['旬首']  # 获取旬首，如"甲戌"

        # 使用值符宫位（来自calculate_zhi_fu）
        zhi_fu_palace = self.base_result['值符宫位']  # 使用值符宫位

        # 获取旬首对应的值符天干
        xunshou_to_fu_gan = {
            '甲子': '戊',
            '甲戌': '己',
            '甲申': '庚',
            '甲午': '辛',
            '甲辰': '壬',
            '甲寅': '癸'
        }
        fu_gan = xunshou_to_fu_gan.get(xunshou)
        if not fu_gan:
            print(f"错误：无效的旬首 {xunshou}")
            return

        # 在地盘中查找旬首值符天干的位置
        xunshou_palace = None
        for palace, gan in di_pan.items():
            if gan == fu_gan:
                xunshou_palace = palace
                break

        # 处理中五宫寄坤二的情况
        if xunshou_palace is None:
            if di_pan.get(5) == fu_gan:
                xunshou_palace = 2
            else:
                print(f"错误：未找到旬首值符天干 {fu_gan} 在地盘的位置")
                return

        print(f"旬首值符天干: {fu_gan} 落宫: {xunshou_palace}宫")

        # 1. 确定值符星和值使门（处理中五宫寄坤二宫）
        palace = xunshou_palace
        if palace == 5:  # 中五宫寄坤二宫
            palace = 2

        # 宫位到值符星和值使门的映射
        palace_to_star_door = {
            1: ('天蓬', '休门'),
            8: ('天任', '生门'),
            3: ('天冲', '伤门'),
            4: ('天辅', '杜门'),
            9: ('天英', '景门'),
            2: ('天芮', '死门'),
            7: ('天柱', '惊门'),
            6: ('天心', '开门')
        }

        if palace not in palace_to_star_door:
            print(f"错误：无效宫位 {palace}")
            return

        # 修复变量名拼写错误
        zhi_fu_star, zhi_shi_door = palace_to_star_door[palace]  # 正确变量名
        print(f"值符星: {zhi_fu_star}, 值使门: {zhi_shi_door}")

        # 2. 确定值使门起始宫位（根据时辰差计算）
        # 获取旬首干支和时柱干支
        xunshou_ganzhi = self.base_result['旬首']  # 如"甲戌"
        shizhu_ganzhi = self.base_result['四柱']['时柱']  # 如"壬午"

        # 地支顺序
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

        # 计算旬首地支位置
        xunshou_zhi = xunshou_ganzhi[1]  # 如"戌"
        try:
            xunshou_idx = zhi_order.index(xunshou_zhi)
        except ValueError:
            print(f"错误：无效的旬首地支 {xunshou_zhi}")
            return

        # 计算时柱地支位置
        shizhu_zhi = shizhu_ganzhi[1]  # 如"午"
        try:
            shizhu_idx = zhi_order.index(shizhu_zhi)
        except ValueError:
            print(f"错误：无效的时柱地支 {shizhu_zhi}")
            return

        # 计算时辰差（从旬首到当前时柱的时辰数）
        # 处理地支循环：如果当前地支小于旬首地支，则加12
        if shizhu_idx < xunshou_idx:
            steps = (shizhu_idx + 12) - xunshou_idx
        else:
            steps = shizhu_idx - xunshou_idx

        print(f"从旬首({xunshou_ganzhi})到时柱({shizhu_ganzhi})的时辰差: {steps}个时辰")

        # 确定值使门起始宫位（从旬首宫位开始移动）
        # 使用洛书宫位顺序：1, 2, 3, 4, 5, 6, 7, 8, 9
        palace_order_yang = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 阳遁顺序
        palace_order_yin = [9, 8, 7, 6, 5, 4, 3, 2, 1]  # 阴遁顺序

        # 找到旬首宫位在顺序中的位置
        start_palace = palace
        if is_yang:
            order = palace_order_yang
        else:
            order = palace_order_yin

        try:
            start_idx = order.index(start_palace)
        except ValueError:
            print(f"错误：宫位{start_palace}不在顺序中")
            return

        # 计算移动后的宫位索引
        new_idx = (start_idx + steps) % len(order)
        zhi_shi_start_palace = order[new_idx]

        # 处理中五宫寄坤二宫
        if zhi_shi_start_palace == 5:
            zhi_shi_start_palace = 2

        print(f"值使门起始宫位: {zhi_shi_start_palace} (从旬首宫位{start_palace}移动{steps}步)")

        # 3. 固定顺序定义
        # 八神固定顺序（始终不变）
        shen_order = ['值符', '腾蛇', '太阴', '六合', '白虎', '玄武', '九地', '九天']

        # 八门固定顺序（始终不变）
        men_order = ['休门', '生门', '伤门', '杜门', '景门', '死门', '惊门', '开门']

        # 九星固定顺序（始终顺时针）
        star_order = ['天蓬', '天任', '天冲', '天辅', '天英', '天芮', '天柱', '天心']

        # 宫位顺序（顺时针：1-8-3-4-9-2-7-6）
        clockwise_order = [1, 8, 3, 4, 9, 2, 7, 6]
        # 宫位顺序（逆时针：6-7-2-9-4-3-8-1）
        counterclockwise_order = [6, 7, 2, 9, 4, 3, 8, 1]

        # 初始化分布
        shen_distribution = {}
        men_distribution = {}
        star_distribution = {}

        # 4. 排布九星（始终顺时针）
        # 找到值符星在九星顺序中的位置
        try:
            star_start_idx = star_order.index(zhi_fu_star)  # 使用正确变量名
        except ValueError:
            star_start_idx = 0

        # 使用值符宫位（zhi_fu_palace）而不是旬首位置
        try:
            palace_start_idx = clockwise_order.index(zhi_fu_palace)
        except ValueError:
            palace_start_idx = 0

        # 按固定九星顺序顺时针排布
        for i in range(8):
            # 计算九星索引
            star_idx = (star_start_idx + i) % 8

            # 计算宫位索引（始终顺时针）
            palace_idx = (palace_start_idx + i) % 8
            palace_num = clockwise_order[palace_idx]

            star_distribution[palace_num] = star_order[star_idx]

        # 5. 排布八神
        # 找到值符宫在顺序中的索引
        if is_yang:  # 阳遁用顺时针顺序
            order = clockwise_order
        else:  # 阴遁用逆时针顺序
            order = counterclockwise_order

        # 使用值符宫位（zhi_fu_palace）而不是旬首位置
        try:
            start_idx = order.index(zhi_fu_palace)
        except ValueError:
            start_idx = 0

        for i, shen in enumerate(shen_order):
            # 计算宫位索引
            idx = (start_idx + i) % 8
            palace_num = order[idx]
            shen_distribution[palace_num] = shen

        # 6. 排布八门
        # 找到值使门在八门顺序中的位置
        door_start_idx = men_order.index(zhi_shi_door)

        # 找到起始宫位在顺序中的索引
        if is_yang:  # 阳遁用顺时针顺序
            order = clockwise_order
        else:  # 阴遁用逆时针顺序
            order = clockwise_order

        try:
            # 使用计算出的值使门起始宫位
            start_idx = order.index(zhi_shi_start_palace)
        except ValueError:
            print(f"警告：值使门起始宫位 {zhi_shi_start_palace} 不在顺序中，使用0索引")
            start_idx = 0

        # 确保八门分布覆盖所有8个宫位
        for i in range(8):
            # 计算八门索引
            men_idx = (door_start_idx + i) % 8

            # 计算宫位索引
            palace_idx = (start_idx + i) % 8
            palace_num = order[palace_idx]

            men_distribution[palace_num] = men_order[men_idx]

        # 7. 处理中五宫（不分配八神、八门和九星）
        shen_distribution[5] = '中五'
        men_distribution[5] = '中五'
        star_distribution[5] = '中五'

        # 保存结果
        self.base_result['值符星'] = zhi_fu_star  # 使用正确变量名
        self.base_result['值使门'] = zhi_shi_door
        self.base_result['八神分布'] = shen_distribution
        self.base_result['八门分布'] = men_distribution
        self.base_result['九星分布'] = star_distribution
        self.base_result['值符落宫'] = palace  # 保存值符落宫位置
        self.base_result['旬首值符天干宫位'] = xunshou_palace

        # 打印结果
        print("\n【值符星与值使门】")
        print(f"旬首: {xunshou} => 值符天干: {fu_gan} 落宫: {xunshou_palace}宫")
        print(f"值符星: {zhi_fu_star}, 值使门: {zhi_shi_door}")
        print(f"值使门起始宫位: {zhi_shi_start_palace} (从旬首宫位{start_palace}移动{steps}步)")
        print(f"值符宫位: {zhi_fu_palace}宫")

        print("\n【九星分布】")
        self.print_palace_distribution(star_distribution)

        print("\n【八神分布】")
        self.print_palace_distribution(shen_distribution)

        print("\n【八门分布】")
        self.print_palace_distribution(men_distribution)

        return shen_distribution, men_distribution, star_distribution

    def print_palace_distribution(self, distribution):
        """打印九宫格分布"""
        print("┌─────┬─────┬─────┐")
        print(f"│ {distribution.get(4, ' ')} │ {distribution.get(9, ' ')} │ {distribution.get(2, ' ')} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {distribution.get(3, ' ')} │ {distribution.get(5, ' ')} │ {distribution.get(7, ' ')} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {distribution.get(8, ' ')} │ {distribution.get(1, ' ')} │ {distribution.get(6, ' ')} │")
        print("└─────┴─────┴─────┘")

    def print_palace_distribution(self, distribution):
        """打印九宫格分布（与self.calculate完全一致）"""
        print("┌─────┬─────┬─────┐")
        print(f"│ {distribution.get(4, ' ')} │ {distribution.get(9, ' ')} │ {distribution.get(2, ' ')} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {distribution.get(3, ' ')} │ {distribution.get(5, ' ')} │ {distribution.get(7, ' ')} │")
        print("├─────┼─────┼─────┤")
        print(f"│ {distribution.get(8, ' ')} │ {distribution.get(1, ' ')} │ {distribution.get(6, ' ')} │")
        print("└─────┴─────┴─────┘")

    # 错误
    def generate_human_pan_doors(self):
        """生成人盘八门布局（值使门随时支转动）
        规则：
        1. 值使门原始宫位 = 值符星原始宫位（已处理寄坤）
        2. 值使门随时支转动：找到时支对应的宫位，将值使门移动至该宫位
        3. 其他七门按八门顺序（休生伤杜景死惊开）和阴阳遁顺逆规则排布
        4. 中五宫寄坤二宫（阳遁）或寄艮八宫（阴遁）
        """
        # --- 1. 准备基础数据 ---
        yinyang_dun = self.base_result['阴阳遁']
        shizhi = self.base_result['四柱']['时柱'][1]  # 时柱地支
        doors = ['休门', '生门', '伤门', '杜门', '景门', '死门', '惊门', '开门']  # 八门固定顺序

        # 值使门信息
        zhi_shi_door = self.base_result['值使门名称']  # 如"休门"
        zhi_shi_original_palace = self.base_result['值符星宫位']  # 值使门原始宫位（同值符宫位）

        # --- 2. 地支与宫位映射（固定）---
        # 子(1), 丑寅(8), 卯(3), 辰巳(4), 午(9), 未申(2), 酉(7), 戌亥(6)
        zhi_palace_map = {
            '子': 1, '丑': 8, '寅': 8, '卯': 3,
            '辰': 4, '巳': 4, '午': 9, '未': 2,
            '申': 2, '酉': 7, '戌': 6, '亥': 6
        }

        # --- 3. 确定时支宫位（值使门目标位置）---
        shizhi_palace = zhi_palace_map.get(shizhi)
        if shizhi_palace is None:
            raise ValueError(f"无效时支: {shizhi}")

        # --- 4. 初始化人盘布局 ---
        human_pan = {i: '' for i in range(1, 10)}
        human_pan[shizhi_palace] = zhi_shi_door  # 值使门随时支转动

        # --- 5. 定义宫位移动顺序（洛书轨迹）---
        # 阳遁顺行：1→2→3→4→5→6→7→8→9
        # 阴遁逆行：9→8→7→6→5→4→3→2→1
        palace_sequence = {
            '阳遁': [1, 2, 3, 4, 5, 6, 7, 8, 9],
            '阴遁': [9, 8, 7, 6, 5, 4, 3, 2, 1]
        }[yinyang_dun]

        # --- 6. 从值使门开始排布其他门 ---
        current_door_index = doors.index(zhi_shi_door)
        current_palace_index = palace_sequence.index(shizhi_palace)

        # 跳过已放置的值使门
        doors_to_place = doors[current_door_index + 1:] + doors[:current_door_index]

        for door in doors_to_place:
            # 移动到下一宫位（循环洛书序列）
            current_palace_index = (current_palace_index + 1) % 9
            target_palace = palace_sequence[current_palace_index]

            # 中五宫寄宫处理
            if target_palace == 5:
                target_palace = 2 if yinyang_dun == '阳遁' else 8  # 修正了这里的语法错误

            # 确保不覆盖已放置的门
            if human_pan[target_palace] == '':  # 修正了变量名中的拼写错误
                human_pan[target_palace] = door
            else:
                # 若宫位被占，继续找下一可用位置
                for _ in range(8):
                    current_palace_index = (current_palace_index + 1) % 9  # 修正了变量名中的拼写错误
                    target_palace = palace_sequence[current_palace_index]
                    if target_palace == 5:
                        target_palace = 2 if yinyang_dun == '阳遁' else 8
                    if human_pan[target_palace] == '':
                        human_pan[target_palace] = door
                        break

        # --- 7. 打印和保存结果 ---
        # print("\n【人盘八门布局】")
        # print(f"值使门: {zhi_shi_door} | 时支: {shizhi}（宫位: {shizhi_palace}） | 阴阳遁: {yinyang_dun}")
        # print("┌──────┬──────┬──────┐")
        # print(f"│ {human_pan[4]:<4} │ {human_pan[9]:<4} │ {human_pan[2]:<4} │")
        # print("├──────┼──────┼──────┤")
        # print(f"│ {human_pan[3]:<4} │ {human_pan[5]:<4} │ {human_pan[7]:<4} │")
        # print("├──────┼──────┼──────┤")
        # print(f"│ {human_pan[8]:<4} │ {human_pan[1]:<4} │ {human_pan[6]:<4} │")
        # print("└──────┴──────┴──────┘")

        # 保存结果
        self.base_result['人盘八门'] = {
            '布局': human_pan,
            '值使门位置': shizhi_palace,
            '中五寄宫': '坤二' if yinyang_dun == '阳遁' else '艮八'
        }

    def generate_god_pan(self):
        """生成神盘八神布局（强化错误处理）"""
        # --- 1. 准备基础数据 ---
        gods = ['值符', '腾蛇', '太阴', '六合', '勾陈', '朱雀', '九地', '九天']  # 八神固定顺序
        yinyang_dun = self.base_result.get('阴阳遁', '阳遁')  # 添加默认值

        # 定义宫位移动序列（提前定义，确保在任何分支都可用）
        palace_sequence = {
            '阳遁': [1, 2, 3, 4, 6, 7, 8, 9],
            '阴遁': [9, 8, 7, 6, 4, 3, 2, 1]
        }.get(yinyang_dun, [1, 2, 3, 4, 6, 7, 8, 9])  # 默认阳遁序列

        # --- 2. 获取值符星位置（多重来源）---
        zhi_fu_palace = None

        # 优先从天盘九星信息获取
        if '天盘九星' in self.base_result:
            zhi_fu_palace = self.base_result['天盘九星'].get('值符星位置')

        # 其次从值符星宫位字段获取
        if zhi_fu_palace is None:
            zhi_fu_palace = self.base_result.get('值符星宫位')

        # 最后从值符原始宫位获取
        if zhi_fu_palace is None:
            zhi_fu_palace = self.base_result.get('值符原始宫位', 1)  # 默认1宫

        # 处理中五宫寄坤
        if zhi_fu_palace == 5:
            zhi_fu_palace = 2

        # --- 3. 初始化神盘布局 ---
        god_pan = {i: '' for i in range(1, 10)}
        god_pan[zhi_fu_palace] = '值符'  # 值符始终在值符星位置

        # --- 4. 找到值符宫在序列中的起始位置 ---
        try:
            start_index = palace_sequence.index(zhi_fu_palace)
        except ValueError:
            # 处理值符宫不在序列中的情况
            start_index = 0
            print(f"警告：值符宫位{zhi_fu_palace}不在宫位序列中，使用起始位置")

        # --- 5. 从值符后开始排布其他七神 ---
        current_index = start_index
        for god in gods[1:]:  # 跳过已放置的值符
            # 移动到下一宫位（循环序列）
            current_index = (current_index + 1) % len(palace_sequence)
            target_palace = palace_sequence[current_index]

            # 确保不覆盖已放置的神
            if god_pan[target_palace] == '':
                god_pan[target_palace] = god
            else:
                # 如果宫位被占（理论上不会发生），找下一可用位置
                for _ in range(len(palace_sequence) - 1):
                    current_index = (current_index + 1) % len(palace_sequence)
                    target_palace = palace_sequence[current_index]
                    if god_pan[target_palace] == '':
                        god_pan[target_palace] = god
                        break

        # 中五宫留空
        god_pan[5] = ''

        # --- 6. 打印和保存结果 ---
        # print("\n【神盘八神布局】")
        # print(f"值符位置: {zhi_fu_palace}宫 | 阴阳遁: {yinyang_dun}")
        # print("┌──────┬──────┬──────┐")
        # print(f"│ {god_pan[4]:<4} │ {god_pan[9]:<4} │ {god_pan[2]:<4} │")
        # print("├──────┼──────┼──────┤")
        # print(f"│ {god_pan[3]:<4} │ {'':<4} │ {god_pan[7]:<4} │")  # 中五宫留空
        # print("├──────┼──────┼──────┤")
        # print(f"│ {god_pan[8]:<4} │ {god_pan[1]:<4} │ {god_pan[6]:<4} │")
        # print("└──────┴──────┴──────┘")

        # 保存结果
        self.base_result['神盘八神'] = {
            '布局': god_pan,
            '值符位置': zhi_fu_palace,
            '排法': f"{yinyang_dun}遁{'顺' if yinyang_dun == '阳遁' else '逆'}布"
        }
        return god_pan

    def get_zhi_fu_palace_tian_gan(self):
        """获取值符所在宫的天盘天干（值符星携带的天干）
        规则：
        1. 值符星在转动前的位置（原始宫位）的地盘干，就是值符星携带的天干
        2. 这个天干会随着值符星移动到新位置，成为新位置的天盘干
        3. 因此值符宫的天盘干 = 值符星原始宫位的地盘干
        """
        # 1. 获取值符星名称和原始宫位
        zhi_fu_star_name = self.base_result['值符星'].replace('星', '')  # 如"天辅"
        initial_star_palace = self.get_initial_star_palace(zhi_fu_star_name)

        # 2. 处理中五宫寄宫情况
        actual_palace = initial_star_palace
        if initial_star_palace == 5:  # 天禽星特殊处理
            actual_palace = 2  # 天禽星始终寄坤二宫

        # 3. 从地盘获取原始宫位的地盘干（这就是值符星携带的天干）
        di_pan = self.base_result['地盘']
        carried_gan = di_pan.get(actual_palace)

        if not carried_gan:
            raise ValueError(f"地盘宫位 {actual_palace} 未找到天干数据")

        # 4. 保存并返回结果
        self.base_result['值符宫天盘干'] = {
            '值符星': zhi_fu_star_name,
            '天盘干': carried_gan
        }


        return carried_gan

    def get_initial_star_palace(self, star_name):
        """获取九星原始宫位（地盘位置）"""
        star_palace_map = {
            '天蓬': 1, '天芮': 2, '天冲': 3, '天辅': 4,
            '天禽': 5, '天心': 6, '天柱': 7, '天任': 8, '天英': 9
        }
        return star_palace_map.get(star_name)

    # 暗干计算
    def generate_an_gan(self):
        """排暗干（八门暗干）
        规则（拆补法）：
        1. 以值使门为起点，值使门所在宫位的暗干为"值符宫天干"
        2. 阳遁顺排（1→2→3→4→6→7→8→9），阴遁逆排（9→8→7→6→4→3→2→1）
        3. 中五宫寄坤二宫（与坤二宫相同）
        4. 天干顺序：乙、丙、丁、戊、己、庚、辛、壬、癸（循环使用）
        5. 排布在八门所在宫位
        """
        # --- 1. 准备基础数据 ---
        # 获取阴阳遁
        yinyang_dun = self.base_result['阴阳遁']

        # 获取值使门名称和位置
        zhi_shi_men = self.base_result['值使门名称']
        men_pan = self.base_result['人盘八门']['布局']

        # 找到值使门所在宫位（处理中五宫寄坤二）
        zhi_shi_palace = None
        for palace, men in men_pan.items():
            if men == zhi_shi_men:
                zhi_shi_palace = palace
                break

        if zhi_shi_palace is None:
            raise ValueError("值使门位置未找到！")

        # 处理中五宫寄坤二
        if zhi_shi_palace == 5:
            actual_zhi_shi_palace = 2
        else:
            actual_zhi_shi_palace = zhi_shi_palace

        # 获取值符宫天干（之前函数的结果）
        zhi_fu_gan = self.base_result['值符宫天盘干']['天盘干']

        # 暗干顺序（乙→丙→丁→戊→己→庚→辛→壬→癸，循环）
        an_gan_order = ['乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

        # --- 2. 确定宫位移动序列 ---
        # 阳遁序列：1→2→3→4→6→7→8→9（跳过5）
        # 阴遁序列：9→8→7→6→4→3→2→1（跳过5）
        palace_sequence = {
            '阳遁': [1, 2, 3, 4, 6, 7, 8, 9],
            '阴遁': [9, 8, 7, 6, 4, 3, 2, 1]
        }[yinyang_dun]

        # --- 3. 找到值使门在序列中的位置 ---
        try:
            start_index = palace_sequence.index(actual_zhi_shi_palace)
        except ValueError:
            # 处理中五宫寄坤二的情况
            start_index = palace_sequence.index(2) if yinyang_dun == '阳遁' else palace_sequence.index(8)

        # --- 4. 生成暗干布局 ---
        an_gan_dict = {}

        # 值使门宫位的暗干是值符宫天干
        an_gan_dict[actual_zhi_shi_palace] = zhi_fu_gan

        # 获取天干起始位置
        try:
            gan_index = an_gan_order.index(zhi_fu_gan)
        except ValueError:
            gan_index = 0  # 如果值符天干不在列表中（理论上不会），从乙开始

        # 从值使门位置开始，按阴阳遁顺序排布暗干
        current_index = start_index
        for _ in range(7):  # 剩下7个宫位
            # 移动到下一宫位
            if yinyang_dun == '阳遁':
                current_index = (current_index + 1) % 8
            else:
                current_index = (current_index - 1) % 8
                if current_index < 0:
                    current_index = 7

            target_palace = palace_sequence[current_index]

            # 获取下一个天干
            gan_index = (gan_index + 1) % 9
            next_gan = an_gan_order[gan_index]

            # 设置暗干
            an_gan_dict[target_palace] = next_gan

        # --- 5. 处理中五宫（寄坤二）---
        an_gan_dict[5] = an_gan_dict.get(2, '')  # 中五宫暗干与坤二宫相同

        # 确保所有宫位都有暗干（即使为空）
        full_an_gan = {i: an_gan_dict.get(i, '') for i in range(1, 10)}

        # --- 6. 打印和保存结果 ---
        # print("\n【暗干布局】")
        # print(f"值使门: {zhi_shi_men} | 位置: {zhi_shi_palace}宫 | 起始暗干: {zhi_fu_gan}")
        # print("┌──────┬──────┬──────┐")
        # print(f"│ {full_an_gan[4]:<4} │ {full_an_gan[9]:<4} │ {full_an_gan[2]:<4} │")
        # print("├──────┼──────┼──────┤")
        # print(f"│ {full_an_gan[3]:<4} │ {full_an_gan[5]:<4} │ {full_an_gan[7]:<4} │")
        # print("├──────┼──────┼──────┤")
        # print(f"│ {full_an_gan[8]:<4} │ {full_an_gan[1]:<4} │ {full_an_gan[6]:<4} │")
        # print("└──────┴──────┴──────┘")

        # 保存结果
        self.base_result['暗干'] = {
            '布局': full_an_gan,
            '值使门位置': zhi_shi_palace,
            '起始暗干': zhi_fu_gan,
            '排法': f"值使门起({zhi_shi_men}),寄坤宫流"
        }
#计算空亡
    def mark_kong_wang_for_sizhu(self):
        """标注四柱的空亡情况（基于宫位地支规则）"""
        # --- 1. 获取基础数据 ---
        sizhu = self.base_result['四柱']
        xunshou = self.base_result['旬首']  # 直接使用已计算的旬首

        # --- 2. 根据旬首确定空亡地支 ---
        kong_wang_map = {
            "甲子": ("戌", "亥"),  # 甲子旬中空戌亥
            "甲戌": ("申", "酉"),  # 甲戌旬中空申酉
            "甲申": ("午", "未"),  # 甲申旬中空午未
            "甲午": ("辰", "巳"),  # 甲午旬中空辰巳
            "甲辰": ("寅", "卯"),  # 甲辰旬中空寅卯
            "甲寅": ("子", "丑")  # 甲寅旬中空子丑
        }

        # 获取空亡地支
        kong_wang_zhi = list(kong_wang_map.get(xunshou, ()))
        print(f"\n【空亡计算】")
        print(f"旬首: {xunshou} → 空亡地支: {kong_wang_zhi}")

        # --- 3. 宫位地支映射 ---
        palace_zhi_map = {
            1: ["子"],
            8: ["丑", "寅"],
            3: ["卯"],
            4: ["辰", "巳"],
            9: ["午"],
            2: ["未", "申"],
            7: ["酉"],
            6: ["戌", "亥"]
        }

        # --- 4. 准备四柱地支列表 ---
        zhu_list = ['年柱', '月柱', '日柱', '时柱']
        zhi_list = [sizhu[zhu][1] for zhu in zhu_list]  # 各地支

        # --- 5. 标注四柱空亡情况 ---
        kong_wang_results = {}
        for zhu in zhu_list:
            zhi = sizhu[zhu][1]
            is_kong = zhi in kong_wang_zhi
            kong_wang_results[zhu] = {
                '空亡': is_kong,
                '地支': zhi
            }

        # 打印四柱空亡情况
        print("\n【四柱空亡】")
        for zhu in zhu_list:
            info = kong_wang_results[zhu]
            status = "空亡" if info['空亡'] else "不空"
            print(f"{zhu} ({info['地支']}): {status}")

        # --- 6. 标注宫位空亡情况 ---
        kong_wang_palaces = {}
        kong_palaces = []  # 存储空亡宫位编号

        print("\n【宫位空亡】")
        for palace, zhi_list in palace_zhi_map.items():
            # 检查宫位中是否有空亡地支
            has_kong = any(zhi in kong_wang_zhi for zhi in zhi_list)
            kong_wang_palaces[palace] = {
                '空亡': has_kong,
                '地支': zhi_list
            }

            # 打印宫位空亡状态
            status = "空亡" if has_kong else "不空"
            zhi_str = "/".join(zhi_list)
            print(f"宫位 {palace} ({zhi_str}): {status}")

            # 记录空亡宫位
            if has_kong:
                kong_palaces.append(palace)

        # 打印空亡宫位汇总
        if kong_palaces:
            print(f"\n空亡宫位: {', '.join(map(str, sorted(kong_palaces)))}宫")
        else:
            print("\n无空亡宫位")

        # --- 7. 保存结果 ---
        self.base_result['四柱空亡'] = {
            '旬空地支': kong_wang_zhi,
            '四柱状态': kong_wang_results,
            '宫位状态': kong_wang_palaces
        }

        return kong_wang_results

    def get_month_element(self, yue_zhi):
        """获取月令五行属性"""
        # 月支 -> 季节 -> 当令五行
        season_map = {
            '寅': '木', '卯': '木', '辰': '土',  # 春
            '巳': '火', '午': '火', '未': '土',  # 夏
            '申': '金', '酉': '金', '戌': '土',  # 秋
            '亥': '水', '子': '水', '丑': '土'  # 冬
        }
        return season_map.get(yue_zhi, '')

    def check_element_strength(self, di_zhi, yue_element):
        """检查地支在月令是否旺相"""
        # 地支五行属性
        zhi_element_map = {
            '寅': '木', '卯': '木',
            '巳': '火', '午': '火',
            '申': '金', '酉': '金',
            '亥': '水', '子': '水',
            '辰': '土', '戌': '土', '丑': '土', '未': '土'
        }

        element = zhi_element_map.get(di_zhi, '')
        if not element or not yue_element:
            return False

        # 当令者旺，令生者相
        if element == yue_element:  # 旺
            return True
        if (yue_element == '木' and element == '火') or \
                (yue_element == '火' and element == '土') or \
                (yue_element == '土' and element == '金') or \
                (yue_element == '金' and element == '水') or \
                (yue_element == '水' and element == '木'):  # 相
            return True
        return False

    def check_he(self, target_zhi, zhi_list):
        """检查地支是否有合（六合或三合）"""
        # 六合关系
        liu_he = [
            ('子', '丑'), ('寅', '亥'), ('卯', '戌'),
            ('辰', '酉'), ('巳', '申'), ('午', '未')
        ]

        # 三合关系（半合也算）
        san_he = [
            ('申', '子'), ('子', '辰'),  # 水局半合
            ('巳', '酉'), ('酉', '丑'),  # 金局半合
            ('寅', '午'), ('午', '戌'),  # 火局半合
            ('亥', '卯'), ('卯', '未')  # 木局半合
        ]

        # 检查六合
        for zhi in zhi_list:
            if zhi == target_zhi:
                continue  # 跳过自身

            # 检查六合
            for he_pair in liu_he:
                if (target_zhi == he_pair[0] and zhi == he_pair[1]) or \
                        (target_zhi == he_pair[1] and zhi == he_pair[0]):
                    return True

            # 检查三合（半合）
            for he_pair in san_he:
                if (target_zhi == he_pair[0] and zhi == he_pair[1]) or \
                        (target_zhi == he_pair[1] and zhi == he_pair[0]):
                    return True

        return False

    def check_men_po(self):
        """
        检查门迫情况
        门迫逻辑：
        - 开门在震三宫(3)或巽四宫(4)为门迫
        - 惊门在震三宫(3)或巽四宫(4)为门迫
        - 生门在坎一宫(1)为门迫
        - 死门在坎一宫(1)为门迫
        - 休门在离九宫(9)为门迫
        - 伤门在艮八宫(8)或坤二宫(2)为门迫
        - 杜门在艮八宫(8)或坤二宫(2)为门迫
        """
        men_po_info = {}
        men_distribution = self.base_result.get('八门分布', {})

        for palace, men in men_distribution.items():
            if men == '开门' and palace in [3, 4]:
                men_po_info[palace] = f"开门门迫（落{self.get_palace_name(palace)}宫）"
            elif men == '惊门' and palace in [3, 4]:
                men_po_info[palace] = f"惊门门迫（落{self.get_palace_name(palace)}宫）"
            elif men == '生门' and palace == 1:
                men_po_info[palace] = "生门门迫（落坎一宫）"
            elif men == '死门' and palace == 1:
                men_po_info[palace] = "死门门迫（落坎一宫）"
            elif men == '休门' and palace == 9:
                men_po_info[palace] = "休门门迫（落离九宫）"
            elif men == '伤门' and palace in [2, 8]:
                men_po_info[palace] = f"伤门门迫（落{self.get_palace_name(palace)}宫）"
            elif men == '杜门' and palace in [2, 8]:
                men_po_info[palace] = f"杜门门迫（落{self.get_palace_name(palace)}宫）"

        # 保存门迫信息
        self.base_result['门迫信息'] = men_po_info

        # 打印门迫情况
        if men_po_info:
            print("\n【门迫情况】")
            for palace, info in men_po_info.items():
                print(f"宫位 {palace} ({self.get_palace_name(palace)}): {info}")
        else:
            print("\n无门迫情况")

        return men_po_info

    def check_jixing(self):
        """
        检查天盘干和地盘干的击刑情况
        击刑逻辑：
        - 戊在震三宫（3）为击刑
        - 己在坤二宫（2）为击刑
        - 庚在艮八宫（8）为击刑
        - 辛在离九宫（9）为击刑
        - 壬在巽四宫（4）为击刑
        - 癸在巽极宫（4）为击刑
        """
        jixing_info = {}
        tian_pan = self.base_result.get('天盘', {})
        di_pan = self.base_result.get('地盘带寄宫', {})

        # 检查天盘干击刑
        for palace, gan in tian_pan.items():
            if gan == '戊' and palace == 3:
                jixing_info[palace] = "戊击刑(天盘)"
            elif gan == '己' and palace == 2:
                jixing_info[palace] = "己击刑(天盘)"
            elif gan == '庚' and palace == 8:
                jixing_info[palace] = "庚击刑(天盘)"
            elif gan == '辛' and palace == 9:
                jixing_info[palace] = "辛击刑(天盘)"
            elif gan == '壬' and palace == 4:
                jixing_info[palace] = "壬击刑(天盘)"
            elif gan == '癸' and palace == 4:
                jixing_info[palace] = "癸击刑(天盘)"

        # 检查地盘干击刑（处理坤二宫的特殊情况）
        for palace, gan in di_pan.items():
            # 处理坤二宫的多干情况
            if palace == 2:
                if isinstance(gan, list):
                    for g in gan:
                        if g == '己':
                            jixing_info[palace] = "己击刑(地盘)"
                        elif g == '戊' and palace == 3:
                            jixing_info[palace] = "戊击刑(地盘)"
                        elif g == '庚' and palace == 8:
                            jixing_info[palace] = "庚击刑(地盘)"
                        elif g == '辛' and palace == 9:
                            jixing_info[palace] = "辛击刑(地盘)"
                        elif g == '壬' and palace == 4:
                            jixing_info[palace] = "壬击刑(地盘)"
                        elif g == '癸' and palace == 4:
                            jixing_info[palace] = "癸击刑(地盘)"
                elif gan == '己':
                    jixing_info[palace] = "己击刑(地盘)"
                elif gan == '戊' and palace == 3:
                    jixing_info[palace] = "戊击刑(地盘)"
                elif gan == '庚' and palace == 8:
                    jixing_info[palace] = "庚击刑(地盘)"
                elif gan == '辛' and palace == 9:
                    jixing_info[palace] = "辛击刑(地盘)"
                elif gan == '壬' and palace == 4:
                    jixing_info[palace] = "壬击刑(地盘)"
                elif gan == '癸' and palace == 4:
                    jixing_info[palace] = "癸击刑(地盘)"
            else:
                if gan == '戊' and palace == 3:
                    jixing_info[palace] = "戊击刑(地盘)"
                elif gan == '己' and palace == 2:
                    jixing_info[palace] = "己击刑(地盘)"
                elif gan == '庚' and palace == 8:
                    jixing_info[palace] = "庚击刑(地盘)"
                elif gan == '辛' and palace == 9:
                    jixing_info[palace] = "辛击刑(地盘)"
                elif gan == '壬' and palace == 4:
                    jixing_info[palace] = "壬击刑(地盘)"
                elif gan == '癸' and palace == 4:
                    jixing_info[palace] = "癸击刑(地盘)"

        # 保存击刑信息
        self.base_result['击刑信息'] = jixing_info

        # 打印击刑情况
        if jixing_info:
            print("\n【击刑情况】")
            for palace, info in jixing_info.items():
                print(f"宫位 {palace} ({self.get_palace_name(palace)}): {info}")
        else:
            print("\n无击刑情况")

        return jixing_info

    def get_palace_name(self, palace):
        """获取宫位名称"""
        palace_names = {
            1: "坎一宫",
            2: "坤二宫",
            3: "震三宫",
            4: "巽四宫",
            5: "中五宫",
            6: "乾六宫",
            7: "兑七宫",
            8: "艮八宫",
            9: "离九宫"
        }
        return palace_names.get(palace, f"{palace}宫")

    def print_integrated_pan(self):
        """以表格形式打印整合的奇门盘信息（包含门迫信息）"""
        if not hasattr(self, 'base_result'):
            print("错误：请先调用calculate_base方法")
            return

        # 获取各组件数据
        di_pan = self.base_result.get('地盘带寄宫', {})
        tian_pan = self.base_result.get('天盘', {})
        stars = self.base_result.get('九星分布', {})
        doors = self.base_result.get('八门分布', {})
        shens = self.base_result.get('八神分布', {})
        an_gan = self.base_result.get('暗干', {}).get('布局', {})
        horse_palace = self.base_result.get('马星宫位', None)
        kong_wang_zhi = self.base_result.get('四柱空亡', {}).get('旬空地支', [])
        men_po_info = self.base_result.get('门迫信息', {})  # 获取门迫信息
        jixing_info = self.base_result.get('击刑信息', {})  # 获取击刑信息

        # 获取寄宫信息
        ji_gong_info = self.base_result.get('寄宫信息', {})
        ji_gong_gan = ji_gong_info.get('5宫地盘干', '')

        # 修复后的宫位地支映射（符合传统规则）
        palace_zhi_map = {
            1: ['子'],  # 坎一宫
            2: ['未', '申'],  # 坤二宫（含寄宫）
            3: ['卯'],  # 震三宫
            4: ['辰', '巳'],  # 巽四宫
            5: [],  # 中五宫（寄坤二宫）
            6: ['戌', '亥'],  # 乾六极
            7: ['酉'],  # 兑七宫
            8: ['丑', '寅'],  # 艮八宫
            9: ['午']  # 离九宫
        }

        # 获取击刑信息
        jixing_info = self.base_result.get('击刑信息', {})

        # 准备9宫格数据 - 确保所有宫位都有数据
        palace_data = {}
        for palace in range(1, 10):  # 1到9宫
            # 确保每个宫位都有基础数据
            di_gan = di_pan.get(palace, '')
            tian_gan = tian_pan.get(palace, '')

            # 处理地盘干（2宫特殊处理）
            if palace == 2:
                # 如果是坤二宫，显示本宫干+寄宫干
                if isinstance(di_gan, list) and len(di_gan) > 1:
                    di_str = f"{di_gan[0]}/{di_gan[1]}"
                else:
                    di_str = str(di_gan)
                    # 添加寄宫干（如果中五宫有地盘干）
                    if ji_gong_gan and palace == 2:
                        di_str += f"/{ji_gong_gan}"
            else:
                di_str = str(di_gan)

            # 天盘干（中五宫特殊处理）
            if palace == 5:
                tian_str = "中五"  # 中五宫特殊标记
            else:
                tian_str = str(tian_gan)

            # 检查空亡（只在空亡宫位标注"空"）
            is_kong = False
            zhi_list = palace_zhi_map.get(palace, [])
            for zhi in zhi_list:
                if zhi in kong_wang_zhi:
                    is_kong = True
                    break

            # 检查马星
            ma_str = "马" if palace == horse_palace else ""

            # 检查门迫
            po_str = "迫" if palace in men_po_info else ""
            # 检查击刑（新添加）
            ji_str = "击" if palace in jixing_info else ""

            # 创建标记字符串（包含空亡、马星和门迫）
            marks = []
            if is_kong:
                marks.append("空")
            if ma_str:
                marks.append("马")
            if po_str:
                marks.append("迫")
            if ji_str:
                marks.append("击")

            marks_str = "".join(marks)  # 组合所有标记

            # 确保每个字段都有值
            palace_data[palace] = {
                'tian': tian_str if tian_str else ' ',
                'di': di_str if di_str else ' ',
                'star': stars.get(palace, ' ') if stars else ' ',
                'door': doors.get(palace, ' ') if doors else ' ',
                'shen': shens.get(palace, ' ') if shens else ' ',
                'an': an_gan.get(palace, ' ') if an_gan else ' ',
                'marks': marks_str if marks_str else ' '  # 使用新字段，包含所有标记
            }

        # 打印表格形式的整合盘
        print("\n整合奇门盘（表格布局）:")
        print("┌───────────┬───────────┬───────────┐")
        print("│ 巽四宫    │ 离九宫    │ 坤二宫    │")
        line4 = palace_data.get(4, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        line9 = palace_data.get(9, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        line2 = palace_data.get(2, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})

        # 使用固定宽度格式
        print(f"│ 天盘: {line4['tian']:<2} │ 天盘: {line9['tian']:<2} │ 天盘: {line2['tian']:<2} │")
        print(f"│ 地盘: {line4['di']:<3} │ 地盘: {line9['di']:<3} │ 地盘: {line2['di']:<3} │")
        print(f"│ 九星: {line4['star']:<3} │ 九星: {line9['star']:<3} │ 九星: {line2['star']:<3} │")
        print(f"│ 八门: {line4['door']:<3} │ 八门: {line9['door']:<3} │ 八门: {line2['door']:<3} │")
        print(f"│ 八神: {line4['shen']:<3} │ 八神: {line9['shen']:<3} │ 八神: {line2['shen']:<3} │")
        print(f"│ 暗干: {line4['an']:<2} │ 暗干: {line9['an']:<2} │ 暗干: {line2['an']:<2} │")

        # 标记行使用固定宽度（4字符）
        print(f"│ {line4['marks']:<4} │ {line9['marks']:<4} │ {line2['marks']:<4} │")
        print("├───────────┼───────────┼───────────┤")

        print("│ 震三宫    │ 中五宫    │ 兑七宫    │")
        line3 = palace_data.get(3, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        line5 = palace_data.get(5, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        line7 = palace_data.get(7, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        print(f"│ 天盘: {line3['tian']:<2} │ 天盘: {line5['tian']:<2} │ 天盘: {line7['tian']:<2} │")
        print(f"│ 地盘: {line3['di']:<3} │ 地盘: {line5['di']:<3} │ 地盘: {line7['di']:<3} │")
        print(f"│ 九星: {line3['star']:<3} │ 九星: {line5['star']:<3} │ 九星: {line7['star']:<3} │")
        print(f"│ 八门: {line3['door']:<3} │ 八门: {line5['door']:<3} │ 八门: {line7['door']:<3} │")
        print(f"│ 八神: {line3['shen']:<3} │ 八神: {line5['shen']:<3} │ 八神: {line7['shen']:<3} │")
        print(f"│ 暗干: {line3['an']:<2} │ 暗干: {line5['an']:<2} │ 暗干: {line7['an']:<2} │")

        # 标记行使用固定宽度（4字符）
        print(f"│ {line3['marks']:<4} │ {line5['marks']:<4} │ {line7['marks']:<4} │")
        print("├───────────┼───────────┼───────────┤")

        print("│ 艮八宫    │ 坎一宫    │ 乾六宫    │")
        line8 = palace_data.get(8, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        line1 = palace_data.get(1, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        line6 = palace_data.get(6, {'tian': ' ', 'di': ' ', 'star': ' ', 'door': ' ', 'shen': ' ', 'an': ' ',
                                    'marks': ' '})
        print(f"│ 天盘: {line8['tian']:<2} │ 天盘: {line1['tian']:<2} │ 天盘: {line6['tian']:<2} │")
        print(f"│ 地盘: {line8['di']:<3} │ 地盘: {line1['di']:<3} │ 地盘: {line6['di']:<3} │")
        print(f"│ 九星: {line8['star']:<3} │ 九星: {line1['star']:<3} │ 九星: {line6['star']:<3} │")
        print(f"│ 八门: {line8['door']:<3} │ 八门: {line1['door']:<3} │ 八门: {line6['door']:<3} │")
        print(f"│ 八神: {line8['shen']:<3} │ 八神: {line1['shen']:<3} │ 八神: {line6['shen']:<3} │")
        print(f"│ 暗干: {line8['an']:<2} │ 暗干: {line1['an']:<2} │ 暗干: {line6['an']:<2} │")

        # 标记行使用固定宽度（4字符）
        print(f"│ {line8['marks']:<4} │ {line1['marks']:<4} │ {line6['marks']:<4} │")
        print("└───────────┴───────────┴───────────┘")

        # 基础整合方法
    def calculate_base(self):
            """整合所有计算结果"""
            # 获取基础四柱和节气信息
            base_result = self.calculate_sizhu_with_jieqi()

            # 先初始化base_result
            self.base_result = {
                '公历': base_result['公历'],
                '农历': base_result['农历'],
                '四柱': base_result['四柱'],
                '当前节气': base_result['当前节气']
            }

            # 计算关键信息并打印
            jieqi = self.base_result['当前节气']
            print(f"节气: {jieqi}")

            yuan_name = getattr(self, 'yuan_name', '未知')
            print(f"元: {yuan_name}")

            yinyang_dun = self.determine_yinyang_dun()
            print(f"阴/阳遁: {yinyang_dun}")

            ju = self.determine_ju()
            print(f"局数: {ju}局")

            horse_branch, horse_palace = self.get_horse_star()
            print(f"马星位置: 地支:{horse_branch} 宫位:{horse_palace}")

            hour_ganzhi = self.calculate_hour_ganzhi()
            xunshou = self.get_xunshou(hour_ganzhi)
            print(f"旬首: {xunshou}")
            # 获取上/中/下元信息并打印
            yuan_name = getattr(self, 'yuan_name', '未知')
            print(f"元: {yuan_name}")

            # 获取符头并打印
            rizhu = self.base_result['四柱']['日柱']
            futou = self.get_futou(rizhu)
            print(f"符头: {futou}")

            horse_branch, horse_palace = self.get_horse_star()
            print(f"马星位置: 地支:{horse_branch} 宫位:{horse_palace}")

            hour_ganzhi = self.calculate_hour_ganzhi()
            xunshou = self.get_xunshou(hour_ganzhi)
            print(f"旬首: {xunshou}")

            # 更新base_result
            self.base_result.update({
                '旬首': xunshou,
                '阴阳遁': yinyang_dun,
                '局数': ju,
                '元': yuan_name,
                '符头': futou
            })
            # 现在可以安全调用determine_ju
            hour_ganzhi = self.calculate_hour_ganzhi()
            xunshou = self.get_xunshou(hour_ganzhi)
            yinyang_dun = self.determine_yinyang_dun()
            ju = self.determine_ju()  # 此时base_result已存在
            yuan_name = getattr(self, 'yuan_name', '未知')



            # 计算地盘布局
            self.arrange_di_pan()
            # 新增：计算值符宫位（基于时干在地盘中的位置）
            self.calculate_zhi_fu()  # 添加这行
            self.arrange_tian_pan()  # 新增：天盘干

            # === 修改开始 ===
            # 调用 arrange_stars_and_doors 方法计算值符星和值使门
            self.arrange_stars_and_doors()



            # 值使门信息已经在方法内部保存到 base_result
            # 无需额外处理
            # === 修改结束 ===
            self.get_zhi_fu_palace_tian_gan()  # 值符宫天干
            # 计算马星
            horse_branch, horse_palace = self.get_horse_star()
            self.base_result['马星'] = horse_branch
            self.base_result['马星宫位'] = horse_palace
            self.mark_kong_wang_for_sizhu()  # 新增：四柱空亡判断
            self.print_integrated_pan()
            self.check_men_po()  # 新增门迫检查
            self.check_jixing()  # 新增击刑检查
            return self.base_result















