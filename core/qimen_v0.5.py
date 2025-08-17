

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
from skyfield.api import Loader


load = Loader('~/skyfield-data')  # 数据存储路径，可自定义
eph = load('de421.bsp')  # 加载 JPL DE421 历表
ts = load.timescale()    # 时间系统
from datetime import datetime, timedelta
import datetime
import math
from timezonefinder import TimezoneFinder
import pytz
import ephem
import re
from shensha_calculator import ShenShaCalculator# 调用神煞函数
from lunar_python import Solar, Lunar

class QiMenCalculator:
    """完整的奇门遁甲计算器，加入经纬度功能"""

    # 基础数据定义
    PALACE_NAMES = ["坎一宫", "坤二宫", "震三宫", "巽四宫", "中五宫", "乾六宫", "兑七宫", "艮八宫", "离九宫"]
    GODS = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
    GATES = ["休门", "死门", "伤门", "杜门", "", "开门", "惊门", "生门", "景门"]
    STARS = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 24节气对应的太阳黄经角度（春分为0度，每个节气间隔15度）
    SOLAR_TERM_ANGLES = {
        '立春': 315,  # 315°
        '雨水': 330,  # 330°
        '惊蛰': 345,  # 345°
        '春分': 0,  # 0°
        '清明': 15,  # 15°
        '谷雨': 30,  # 30°
        '立夏': 45,  # 45°
        '小满': 60,  # 60°
        '芒种': 75,  # 75°
        '夏至': 90,  # 90°
        '小暑': 105,  # 105°
        '大暑': 120,  # 120°
        '立秋': 135,  # 135°
        '处暑': 150,  # 150°
        '白露': 165,  # 165°
        '秋分': 180,  # 180°
        '寒露': 195,  # 195°
        '霜降': 210,  # 210°
        '立冬': 225,  # 225°
        '小雪': 240,  # 240°
        '大雪': 255,  # 255°
        '冬至': 270,  # 270°
        '小寒': 285,  # 285°
        '大寒': 300,  # 300°
    }

    MOUNTAINS_24 = {
        1: ["壬(337.5-352.5°)", "子(352.5-7.5°)", "癸(7.5-22.5°)"],  # 坎宫
        2: ["未(202.5-217.5°)", "坤(217.5-232.5°)", "申(232.5-247.5°)"],  # 坤宫
        3: ["甲(67.5-82.5°)", "卯(82.5-97.5°)", "乙(97.5-112.5°)"],  # 震宫
        4: ["辰(112.5-127.5°)", "巽(127.5-142.5°)", "巳(142.5-157.5°)"],  # 巽宫
        6: ["戌(292.5-307.5°)", "乾(307.5-322.5°)", "亥(322.5-337.5°)"],  # 乾宫
        7: ["庚(247.5-262.5°)", "酉(262.5-277.5°)", "辛(277.5-292.5°)"],  # 兑宫
        8: ["丑(22.5-37.5°)", "艮(37.5-52.5°)", "寅(52.5-67.5°)"],  # 艮宫
        9: ["丙(157.5-172.5°)", "午(172.5-187.5°)", "丁(187.5-202.5°)"],  # 离宫
    }
    # 增加光行差参数
    SOLAR_ABERRATION = 20.49552  # 单位：角秒
    # 修改节气角度表（增加精度）
    SOLAR_TERM_ANGLES = {
        '立春': 315.0000,  # 原315改为精确值
        '雨水': 330.0000,
        # ...其他节气保持原值但增加小数位...
    }

    def __init__(self, year, month, day, hour,
                 minute=0, latitude=None, longitude=None,
                 use_ji_earth_kun=True, use_gui_separate=False,
                 strict_mode=False,use_threading=True,):
        # 1. 首先初始化基本属性
        self.latitude = latitude
        self.longitude = longitude
        self.strict_mode = strict_mode
        self._use_threading = use_threading
        self._solar_term_cache = {}

        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.hour = int(hour)
        self.minute = int(minute)
        self.latitude = float(latitude)
        self.longitude = float(longitude)

        # 计算真太阳时并赋值给self.date_obj
        self.date_obj = self.calculate_local_time()

        # 3. 初始化天文观测对象
        self._observer = ephem.Observer()
        if latitude and longitude:
            self._observer.lat = str(latitude)
            self._observer.lon = str(longitude)
        else:
            self._observer.lat = '39.9'  # 默认北京
            self._observer.lon = '116.4'
        self._observer.elevation = 0
        self._observer.pressure = 0

        self.SOLAR_TERM_TO_MONTH = {
            '立春': ('寅', 1), '雨水': ('寅', 1),
            '惊蛰': ('卯', 2), '春分': ('卯', 2),
            '清明': ('辰', 3), '谷雨': ('辰', 3),
            '立夏': ('巳', 4), '小满': ('巳', 4),
            '芒种': ('午', 5), '夏至': ('午', 5),
            '小暑': ('未', 6), '大暑': ('未', 6),
            '立秋': ('申', 7), '处暑': ('申', 7),
            '白露': ('酉', 8), '秋分': ('酉', 8),
            '寒露': ('戌', 9), '霜降': ('戌', 9),
            '立冬': ('亥', 10), '小雪': ('亥', 10),
            '大雪': ('子', 11), '冬至': ('子', 11),
            '小寒': ('丑', 12), '大寒': ('丑', 12)
        }

        # 4. 最后才调用节气计算
        self.get_precise_solar_term()  # 现在可以安全调用了


        # 初始化所有干支属性
        self.year_ganzhi = None
        self.month_ganzhi = None
        self.day_ganzhi = None
        # 添加 yin_yang 属性初始化
        self.yin_yang = None  # 初始化为None
        self.yin_yang=self.determine_yinyang_dun()

        # 新增：神煞五行属性映射
        self.shensha_wuxing_map = {
            '天乙贵人': '金',
            '文昌贵人': '木',
            '驿马': '火',
            '桃花': '水',
            '白虎': '金',
            '月德': '土',
            '天德': '火'
        }

        # 新增天乙贵人动态轨迹存储
        self.tianyi_trajectory = []
        # 值符转动方向（阳遁顺行1，阴遁逆行-1）
        self.zhifu_direction = 1 if self.yin_yang == "阳遁" else -1

        # 新增：神煞基础能量映射
        self.shensha_energy_map = {
            '天乙贵人': 0.7,
            '文昌贵人': 0.6,
            '驿马': 0.8,
            '桃花': 0.5,
            '白虎': 0.3,
            '月德': 0.65,
            '天德': 0.7
        }

        # 新增：八门五行属性映射
        self.door_wuxing_map = {
            '休门': '水',
            '生门': '土',
            '伤门': '木',
            '杜门': '木',
            '景门': '火',
            '死门': '土',
            '惊门': '金',
            '开门': '金'
        }

        # 宫位五行属性（坎1水，坤2土...离9火）
        self.palace_wuxing_map = {
            1: '水', 2: '土', 3: '木', 4: '木',
            6: '金', 7: '金', 8: '土', 9: '火'
        }


        # 新增：天干五行属性映射
        self.gan_wuxing_map = {
            '甲': '木', '乙': '木',
            '丙': '火', '丁': '火',
            '戊': '土', '己': '土',
            '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }
        # 新增：九星五行属性映射
        self.star_wuxing_map = {
            '天蓬': '水',
            '天芮': '土',
            '天冲': '木',
            '天辅': '木',
            '天禽': '土',
            '天心': '金',
            '天柱': '金',
            '天任': '土',
            '天英': '火'
        }

        # 在__init__中添加地支藏干映射
        self.BRANCH_HIDDEN_GAN = {
            '子': ['癸'],
            '丑': ['己', '癸', '辛'],
            '寅': ['甲', '丙', '戊'],
            '卯': ['乙'],
            '辰': ['戊', '乙', '癸'],
            '巳': ['丙', '戊', '庚'],
            '午': ['丁', '己'],
            '未': ['己', '丁', '乙'],
            '申': ['庚', '壬', '戊'],
            '酉': ['辛'],
            '戌': ['戊', '辛', '丁'],
            '亥': ['壬', '甲']
        }

        self.PALACE_OPPOSITES = {
            1: 9,  # 坎一宫↔离九宫
            2: 8,  # 坤二宫↔艮八宫
            3: 7,  # 震三宫↔兑七宫
            4: 6,  # 巽四宫↔乾六宫
            6: 4,  # 乾六宫↔巽四宫
            7: 3,  # 兑七宫↔震三宫
            8: 2,  # 艮八宫↔坤二宫
            9: 1  # 离九宫↔坎一宫
        }
        # 在__init__中增加
        self.STAR_FIXED_POSITIONS = {
            '天蓬': 1, '天芮': 2, '天冲': 3, '天辅': 4,
            '天禽': 5, '天心': 6, '天柱': 7, '天任': 8, '天英': 9
        }

        # 地支与宫位的专业映射（包含每个宫位对应的地支）
        self.PALACE_BRANCH_MAP = {
            1: ['子'],  # 坎一宫
            2: ['未', '申'],  # 坤二宫
            3: ['卯'],  # 震三宫
            4: ['辰', '巳'],  # 巽四宫
            6: ['戌', '亥'],  # 乾六宫
            7: ['酉'],  # 兑七宫
            8: ['丑', '寅'],  # 艮八宫
            9: ['午']  # 离九宫
        }


        # 神煞系统初始化
        self.shensha_calculator = None
        self.shensha_per_palace = {}
        # 添加strict_mode属性

        # 时辰地支索引计算
        self.hour_branch_index = self.calculate_hour_branch_index(hour)
        # 新增初始化




        # 宫位顺序（跳过中五宫）
        self.DOOR_PALACE_ORDER = [1, 8, 3, 4, 9, 2, 7, 6]  # 专业奇门宫位顺序

        # 宫位与方位映射
        self.PALACE_DIRECTIONS = {
            1: "坎宫（北）",
            2: "坤宫（西南）",
            3: "震宫（东）",
            4: "巽宫（东南）",
            5: "中宫",
            6: "乾宫（西北）",
            7: "兑宫（西）",
            8: "艮宫（东北）",
            9: "离宫（南）"
        }
        # 五行属性映射
        self.wuxing_map = {
            '坎': '水', '坤': '土', '震': '木', '巽': '木',
            '中': '土', '乾': '金', '兑': '金', '艮': '土', '离': '火',

            '休': '水', '死': '土', '伤': '木', '杜': '木',
            '中': '土', '开': '金', '惊': '金', '生': '土', '景': '火'
        }

        # 五行生克关系（我克为财，克我为迫）
        self.ke_relations = {
            '金': '木',  # 金克木
            '木': '土',  # 木克土
            '土': '水',  # 土克水
            '水': '火',  # 水克火
            '火': '金'  # 火克金
        }

        self.star_fu = False  # 星伏吟
        self.door_fu = False  # 门伏吟
        self.full_fu = False  # 全盘伏吟
        self.star_fan = False  # 星反吟
        self.door_fan = False  # 门反吟
        self.full_fan = False  # 全盘反吟
        self.use_gui_separate = use_gui_separate
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute



        # 计算真太阳时（带类型检查）
        self.local_time = self.calculate_local_time()
        if not isinstance(self.local_time, datetime.datetime):
            self.local_time = None



        self.use_ji_earth_kun = use_ji_earth_kun
        self.central_palace_host = None  # 中五宫寄宫目标(2或8)
        self.star_fu = False  # 星伏吟
        self.door_fu = False  # 门伏吟
        self.full_fu = False  # 全盘伏吟

        self.patterns = []  # 全局格局存储
        self.sgky = []  # 存储十干克应格局分析结果
        self.kongwang = []  # 空亡地支
        self.guxu = ""  # 孤虚方位

        # 初始化核心数据结构

        self.earthly_pan = {}
        self.main_pan = {
            'star_pan': [],
            'door_pan': [],
            'god_pan': [],
            'zhifu_star': '',
            'zhishi_door': ''
        }

        self.BRANCH_PALACE_MAP = {
            "子": 1, "午": 9, "卯": 3, "酉": 7,  # 四正位
            "丑": 8, "寅": 8,  # 艮宫
            "辰": 4, "巳": 4,  # 巽宫
            "未": 2, "申": 2,  # 坤宫
            "戌": 6, "亥": 6  # 乾宫
        }

        self.horse_star = None
        self.horse_star_palace = None

        self.ju = None




        # 执行核心计算
        try:
            self.calculate()
        except Exception as e:
            print(f"初始化计算失败: {str(e)}")
            raise

    @staticmethod
    def get_changsheng_state(day_gan, branch):
        """计算长生十二宫状态（基于日干与地支关系）"""
        # 长生十二宫顺序（阳干顺行，阴干逆行）
        changsheng_order = {
            '甲': ['亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌'],
            '乙': ['午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌', '酉', '申', '未'],
            '丙': ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'],
            '丁': ['酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌'],
            '戊': ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'],  # 同丙
            '己': ['酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥', '戌'],  # 同丁
            '庚': ['巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰'],
            '辛': ['子', '亥', '戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑'],
            '壬': ['申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰', '巳', '午', '未'],
            '癸': ['卯', '寅', '丑', '子', '亥', '戌', '酉', '申', '未', '午', '巳', '辰']
        }

        # 十二长生状态名称
        changsheng_names = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]

        # 查找地支在日干的十二长生顺序中的位置
        if day_gan in changsheng_order:
            order = changsheng_order[day_gan]
            if branch in order:
                idx = order.index(branch)
                return changsheng_names[idx]

        return ""  # 无对应状态

    def calculate_sizhu_with_jieqi(self):
        """
        考虑经度影响的八字计算

        参数:
            longitude: 东经为正数（如北京116.4），西经为负数
            默认120.0（北京时间基准经度)
        """
        solar_year=self.year
        solar_month=self.month
        solar_day=self.day
        hour=self.hour
        minute=self.minute
        longitude=self.longitude

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


    def get_tiangan_order(self):
        """获取十天干顺序（考虑阴阳遁）"""
        order = "甲乙丙丁戊己庚辛壬癸"
        return order if self.yin_yang == "阳遁" else order[::-1]

    def calculate_tianyi_movement(self):
        """计算天乙贵人（值符）的宫位移动轨迹"""
        # 1. 确定时辰天干（复用现有方法）
        hour_ganzhi = self.calculate_hour_ganzhi()
        hour_gan = hour_ganzhi[0]  # 时干

        # 2. 获取值符原始宫位（天盘值符星所在宫）
        zhifu_star = self.main_pan['zhifu_star']  # 如"天蓬"
        zhifu_palace = self.STAR_FIXED_POSITIONS[zhifu_star]  # 星原始宫位

        # 3. 计算移动步数（时干在十天干中的索引）
        tiangan_order = self.get_tiangan_order()
        steps = tiangan_order.index(hour_gan)  # 0-9

        # 4. 生成移动轨迹（洛书宫位顺序）
        luoshu_order = [4, 9, 2, 3, 5, 7, 8, 1, 6]  # 中宫不参与
        current_idx = luoshu_order.index(zhifu_palace)

        trajectory = []
        for i in range(1, steps + 1):
            next_idx = (current_idx + i * self.zhifu_direction) % 8
            trajectory.append(luoshu_order[next_idx])

        self.tianyi_trajectory = trajectory
        return trajectory

    def get_palace_energy(self, palace_num):
        """增强版宫位能量计算（含天乙贵人加成）"""
        base_energy = self._get_base_palace_energy(palace_num)  # 原有计算

        # 天乙贵人临宫能量增幅
        if palace_num in self.tianyi_trajectory:
            distance = self.tianyi_trajectory.index(palace_num) + 1
            # 距离越近能量越强（最近*1.5，最远*1.1）
            boost = 1.5 - (distance / len(self.tianyi_trajectory)) * 0.4
            base_energy *= boost

        return base_energy

    def calculate_bearing(self, target_lat, target_lon):
        """
        计算目标点相对于排盘点的方位角(0-360度)
        """
        if not self.latitude or not self.longitude:
            return None

        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(target_lat)
        lon2 = math.radians(target_lon)

        d_lon = lon2 - lon1
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)

        bearing = math.atan2(y, x)
        bearing_deg = math.degrees(bearing)
        return (bearing_deg + 360) % 360  # 转换为0-360度

    def get_detailed_direction(self, palace, bearing=None):
        """
        获取宫位的详细二十四山向
        :param palace: 宫位编号(1-9)
        :param bearing: 可选，精确方位角(0-360)
        :return: 详细方位描述
        """
        if palace == 5:  # 中五宫不分山向
            return "中宫(无山向)"

        mountains = self.MOUNTAINS_24.get(palace, [])

        # 如果有精确方位角，返回具体山向
        if bearing is not None:
            # 计算该宫位的起始角度 (宫位中心角度-15度)
            palace_center = (palace - 1) * 45  # 每宫45度
            start_angle = (palace_center - 15) % 360
            offset = (bearing - start_angle) % 360

            # 确定具体山向 (每15度一个山向)
            if offset < 15:
                return mountains[0]
            elif offset < 30:
                return mountains[1]
            else:
                return mountains[2]

        # 无精确方位时返回所有山向
        return "/".join(mountains)

    def get_wuxing_state(self, wuxing, month_zhi):
        """
        判断五行在当月支的旺衰状态
        返回：'旺'/'相'/'休'/'囚'/'死'
        """
        # 月支五行映射
        month_wuxing_map = {
            '寅': '木', '卯': '木', '辰': '土',
            '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土',
            '亥': '水', '子': '水', '丑': '土'
        }

        # 当前月支的五行
        current_wuxing = month_wuxing_map.get(month_zhi, '')
        if not current_wuxing:
            return '休'

        # 五行生克关系
        if wuxing == current_wuxing:
            return '旺'  # 同我者旺
        elif self.get_wuxing_relation(wuxing, current_wuxing) == '相生':
            return '相'  # 我生者相
        elif self.get_wuxing_relation(current_wuxing, wuxing) == '相生':
            return '休'  # 生我者休
        elif self.get_wuxing_relation(current_wuxing, wuxing) == '相克':
            return '囚'  # 克我者囚
        else:
            return '死'  # 我克者死

    def get_generating_wuxing(self, wuxing):
        """获取生该五行的五行"""
        generating_map = {
            '木': '水',
            '火': '木',
            '土': '火',
            '金': '土',
            '水': '金'
        }
        return generating_map.get(wuxing, '')

    # 动态计算
    def get_palace_by_branch(self, branch):
        """
        完整版地支-宫位映射（含藏干能量权重与阴阳遁调整）
        参数：
            branch: 地支（如'子','丑'）
        返回：
            宫位编号（1-9）
        """
        # 地支藏干权重表（本气60%+中气30%+余气10%）
        HIDDEN_GAN_WEIGHTS = {
            '子': [('癸', 1.0)],  # 纯癸水
            '丑': [('己', 0.7), ('癸', 0.2), ('辛', 0.1)],  # 本气己土70%,癸水20%,辛金10%
            '寅': [('甲', 0.7), ('丙', 0.2), ('戊', 0.1)],  # 本气甲木70%,丙火20%,戊土10%
            '卯': [('乙', 1.0)],  # 纯乙木
            '辰': [('戊', 0.7), ('乙', 0.2), ('癸', 0.1)],  # 本气戊土70%,乙木20%,癸水10%
            '巳': [('丙', 0.7), ('戊', 0.2), ('庚', 0.1)],  # 本气丙火70%,戊土20%,庚金10%
            '午': [('丁', 0.7), ('己', 0.3)],  # 丁火70%,己土30%（午火特殊，仅两藏干）
            '未': [('己', 0.7), ('丁', 0.2), ('乙', 0.1)],  # 本气己土70%,丁火20%,乙木10%
            '申': [('庚', 0.7), ('壬', 0.2), ('戊', 0.1)],  # 本气庚金70%,壬水20%,戊土10%
            '酉': [('辛', 1.0)],  # 纯辛金
            '戌': [('戊', 0.7), ('辛', 0.2), ('丁', 0.1)],  # 本气戊土70%,辛金20%,丁火10%
            '亥': [('壬', 0.7), ('甲', 0.3)]  # 壬水70%,甲木30%（亥水特殊，仅两藏干）
        }

        # 天干-宫位专业映射（含阴阳属性）
        GAN_PALACE_MAP = {
            # 阳干
            '甲': (3, '阳'),  # 震三宫（阳木）
            '丙': (9, '阳'),  # 离九宫（阳火）
            '戊': (2, '阳'),  # 坤二宫（阳土，特殊：戊土寄坤）
            '庚': (7, '阳'),  # 兑七宫（阳金）
            '壬': (1, '阳'),  # 坎一宫（阳水）
            # 阴干
            '乙': (3, '阴'),  # 震三宫（阴木）
            '丁': (9, '阴'),  # 离九宫（阴火）
            '己': (2, '阴'),  # 坤二宫（阴土）
            '辛': (7, '阴'),  # 兑七宫（阴金）
            '癸': (1, '阴')  # 坎一宫（阴水）
        }

        # 特殊天干寄宫规则（非标准情况）
        SPECIAL_GAN_RULES = {
            '戊': (8 if self.yin_yang == "阳遁" else 2),  # 阳遁戊寄艮，阴遁戊寄坤
            '己': (2 if self.yin_yang == "阳遁" else 8)  # 阳遁己寄坤，阴遁己寄艮
        }

        # 1. 获取地支藏干（按权重降序）
        hidden_gans = HIDDEN_GAN_WEIGHTS.get(branch, [])
        if not hidden_gans:
            return 1  # 默认坎宫

        # 2. 确定主导天干（权重最高者）
        main_gan = max(hidden_gans, key=lambda x: x[1])[0]

        # 3. 特殊天干处理（戊/己随遁甲变化）
        if main_gan in SPECIAL_GAN_RULES:
            return SPECIAL_GAN_RULES[main_gan]

        # 4. 标准天干映射
        palace, yinyang = GAN_PALACE_MAP.get(main_gan, (1, '阳'))

        # 5. 阴阳遁调整规则：
        #    - 阳遁时阳干能量增强，阴干减弱
        #    - 阴遁时阴干能量增强，阳干减弱
        if (self.yin_yang == "阳遁" and yinyang == '阴') or \
                (self.yin_yang == "阴遁" and yinyang == '阳'):
            # 能量减弱时转到对冲宫位
            opposite_palace = self.PALACE_OPPOSITES.get(palace, palace)

            # 土系特殊处理（坤艮互转）
            if main_gan in ('戊', '己'):
                return 8 if palace == 2 else 2
            return opposite_palace

        return palace

    def calculate_hour_branch_index(self, hour):
        """更安全的时辰地支索引计算"""
        if not 0 <= hour <= 23:
            raise ValueError("小时数必须在0-23之间")

        # 古代时辰划分（23-1为子时，1-3为丑时...）
        branch_idx = ((hour + 1) // 2) % 12
        return branch_idx

    def _validate_ganzhi(self, ganzhi):
        """专业优化版干支验证方法"""
        # 长度检查
        if len(ganzhi) != 2:
            return False

        # 使用预定义的完整六十甲子表（类常量）
        if not hasattr(QiMenCalculator, 'JIAZI_LIST'):
            QiMenCalculator.JIAZI_LIST = [
                "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
                "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
                "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
                "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
                "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
                "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"
            ]

        # 直接检查是否在六十甲子列表中（最可靠）
        return ganzhi in QiMenCalculator.JIAZI_LIST


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


    def calculate_local_time(self):
        """计算真太阳时（动态时区中央经度版）"""
        # 1. 输入时间视为 UTC+8（东八区）
        local_time = datetime.datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            tzinfo=pytz.timezone('Asia/Shanghai')
        )

        # 2. 计算经度差修正（东八区中央经度 120°E）
        central_meridian = 120.0
        longitude_diff = self.longitude - central_meridian
        time_diff = longitude_diff * 4  # 每度 4 分钟



        # 4. 计算真太阳时
        true_solar_time = local_time + timedelta(minutes=time_diff )

        return true_solar_time

    def get_comprehensive_wangshuai(self, palace_num, target_element):
        """
        综合旺衰判断（三维度加权评分）
        :param palace_num: 宫位(1-9)
        :param target_element: 需要判断旺衰的五行属性
        :return: (旺衰等级, 评分, 详细分析)
        """
        # 1. 获取宫位基本信息
        palace_name = self.PALACE_NAMES[palace_num - 1]
        palace_element = self.wuxing_map.get(palace_name[0], '')

        # 2. 三维度旺衰分析
        term_state = self.get_term_wangshuai(target_element)  # 节气旺衰
        palace_state = self.get_palace_relation(target_element, palace_element)  # 宫位生克
        shensha_state = self.get_shensha_effect(palace_num, target_element)  # 神煞影响

        # 3. 综合评分（权重：节气50% + 宫位30% + 神煞20%）
        score = (term_state['score'] * 0.5 +
                 palace_state['score'] * 0.3 +
                 shensha_state['score'] * 0.2)

        # 4. 确定旺衰等级
        if score >= 0.8:
            level = "帝旺"
        elif score >= 0.6:
            level = "相"
        elif score >= 0.4:
            level = "休"
        elif score >= 0.2:
            level = "囚"
        else:
            level = "死"

        # 5. 生成详细分析报告
        analysis = (
            f"【{target_element}在{self.get_precise_solar_term()}节气】{term_state['desc']}\n"
            f"【宫位关系】{palace_name}宫({palace_element}) → {target_element}: {palace_state['desc']}\n"
            f"【神煞影响】{shensha_state['desc']}"
        )

        return level, score, analysis

    def get_precise_solar_term(self):
        result = self.calculate_sizhu_with_jieqi()
        # 4. 返回当前最近的节气
        return result['当前节气']

    def _convert_term_name(self, english_name):
        """将 Skyfield 的英文节气名转为中文"""
        term_map = {
            'Spring begins': '立春',
            'Rain water': '雨水',
            'Awakening of insects': '惊蛰',
            'Vernal equinox': '春分',
            'Pure brightness': '清明',
            'Grain rain': '谷雨',
            'Summer begins': '立夏',
            'Grain full': '小满',
            'Grain in ear': '芒种',
            'Summer solstice': '夏至',
            'Slight heat': '小暑',
            'Great heat': '大暑',
            'Autumn begins': '立秋',
            'Limit of heat': '处暑',
            'White dew': '白露',
            'Autumnal equinox': '秋分',
            'Cold dew': '寒露',
            'Frost': '霜降',
            'Winter begins': '立冬',
            'Little snow': '小雪',
            'Heavy snow': '大雪',
            'Winter solstice': '冬至',
            'Little cold': '小寒',
            'Severe cold': '大寒'
        }
        return term_map.get(english_name, english_name)

    def get_days_into_term(self):
        """计算精确到分钟的节气进度"""
        term = self.get_precise_solar_term()
        term_time = self._solar_term_cache.get(term)

        if not term_time:
            return 0.0

        # 计算精确时间差（秒）
        delta_seconds = (self.date_obj - term_time).total_seconds()

        # 转换为天数（含小数）
        return delta_seconds / 86400.0

    def calculate_yuan(self, days_into_term):
        """专业三元划分（每元5天）"""
        # 精确到分钟的节气进度（0.0~15.0天）
        progress = days_into_term

        # 上元：0.0 ~ 4.999天
        if progress < 5.0:
            return 0  # 上元
        # 中元：5.0 ~ 9.999天
        elif progress < 10.0:
            return 1  # 中元
        # 下元：10.0 ~ 14.999天
        else:
            return 2  # 下元

    def get_term_wangshuai(self, wuxing):
        """
        节气旺衰（增强版：考虑节气交接能量渐变）
        :param wuxing: 五行属性
        :return: {'score': 0-1, 'desc': 描述}
        """
        # 当前节气
        term = self.get_precise_solar_term()

        # 节气五行映射（含能量强度）
        term_wuxing_map = {
            '立春': ('木', 1.0), '雨水': ('木', 0.9),
            '惊蛰': ('木', 0.8), '春分': ('木', 1.0),
            '清明': ('木', 0.7), '谷雨': ('木', 0.6),
            '立夏': ('火', 1.0), '小满': ('火', 0.9),
            '芒种': ('火', 0.8), '夏至': ('火', 1.0),
            '小暑': ('土', 0.7), '大暑': ('土', 0.6),
            '立秋': ('金', 1.0), '处暑': ('金', 0.9),
            '白露': ('金', 0.8), '秋分': ('金', 1.0),
            '寒露': ('金', 0.7), '霜降': ('金', 0.6),
            '立冬': ('水', 1.0), '小雪': ('水', 0.9),
            '大雪': ('水', 0.8), '冬至': ('水', 1.0),
            '小寒': ('土', 0.7), '大寒': ('土', 0.6)
        }

        # 获取当前节气五行和能量值
        term_wx, term_energy = term_wuxing_map.get(term, ('', 0))

        # 判断旺衰关系
        if wuxing == term_wx:
            return {'score': term_energy, 'desc': f"当令（能量{term_energy * 100}%）"}

        # 生我者相
        if self.get_generating_element(wuxing) == term_wx:
            return {'score': term_energy * 0.7, 'desc': f"得生（能量{term_energy * 70}%）"}

        # 我生者休
        if self.get_generated_element(wuxing) == term_wx:
            return {'score': term_energy * 0.4, 'desc': f"泄气（能量{term_energy * 40}%）"}

        # 克我者囚
        if self.get_ke_relation(term_wx) == wuxing:
            return {'score': term_energy * 0.3, 'desc': f"受克（能量{term_energy * 30}%）"}

        # 我克者死
        if self.get_ke_relation(wuxing) == term_wx:
            return {'score': term_energy * 0.2, 'desc': f"耗力（能量{term_energy * 20}%）"}

        return {'score': 0.5, 'desc': "平"}

    def get_palace_relation(self, target_element, palace_element):
        """
        宫位生克关系分析
        :param target_element: 目标五行
        :param palace_element: 宫位五行
        :return: {'score': 0-1, 'desc': 描述}
        """
        if not palace_element:
            return {'score': 0.5, 'desc': "宫位无五行属性"}

        # 宫位生目标（最佳）
        if self.get_generating_element(palace_element) == target_element:
            return {'score': 0.9, 'desc': f"宫位生{target_element}（大吉）"}

        # 目标生宫位（泄气）
        if self.get_generating_element(target_element) == palace_element:
            return {'score': 0.6, 'desc': f"{target_element}生宫位（泄气）"}

        # 宫位克目标（凶）
        if self.get_ke_relation(palace_element) == target_element:
            return {'score': 0.3, 'desc': f"宫位克{target_element}（受制）"}

        # 目标克宫位（小吉）
        if self.get_ke_relation(target_element) == palace_element:
            return {'score': 0.7, 'desc': f"{target_element}克宫位（得财）"}

        # 五行相同
        if target_element == palace_element:
            return {'score': 0.8, 'desc': "五行相同（旺相）"}

        return {'score': 0.5, 'desc': "无特殊关系"}

    def get_shensha_effect(self, palace_num, target_element):
        """
        神煞对五行的增强/削弱作用
        :param palace_num: 宫位(1-9)
        :param target_element: 目标五行
        :return: {'score': 0-1, 'desc': 描述}
        """
        shensha_list = self.get_shensha_for_palace(palace_num)
        if not shensha_list:
            return {'score': 0.5, 'desc': "无神煞影响"}

        boost_effects = []
        reduce_effects = []

        # 神煞能量映射
        shensha_energy_map = {
            '天乙贵人': 0.3, '文昌贵人': 0.2, '月德': 0.25,
            '天德': 0.25, '福星贵人': 0.2, '太极贵人': 0.15,
            '劫煞': -0.3, '灾煞': -0.4, '孤辰': -0.2,
            '寡宿': -0.2, '亡神': -0.35, '白虎': -0.5
        }

        # 五行相生神煞
        generate_map = {
            '金': ['天德', '月德', '金匮贵人'],
            '木': ['文昌贵人', '学堂贵人'],
            '水': ['天乙贵人', '福星贵人'],
            '火': ['太极贵人', '天厨贵人'],
            '土': ['华盖', '将星']
        }

        # 五行相克神煞
        ke_map = {
            '金': ['亡神', '白虎'],
            '木': ['劫煞', '灾煞'],
            '水': ['孤辰', '寡宿'],
            '火': ['卷舌煞', '披麻煞'],
            '土': ['五鬼', '勾绞煞']
        }

        total_score = 0.5  # 基准分

        for shensha in shensha_list:
            # 基本能量影响
            energy = shensha_energy_map.get(shensha, 0)
            total_score += energy

            # 五行相生增强
            if shensha in generate_map.get(target_element, []):
                total_score += 0.15
                boost_effects.append(f"{shensha}生{target_element}")

            # 五行相克削弱
            if shensha in ke_map.get(target_element, []):
                total_score -= 0.2
                reduce_effects.append(f"{shensha}克{target_element}")

        # 生成描述
        desc = []
        if boost_effects:
            desc.append("增益：" + "、".join(boost_effects))
        if reduce_effects:
            desc.append("削弱：" + "、".join(reduce_effects))

        return {
            'score': max(0, min(1, total_score)),  # 限制在0-1范围
            'desc': "；".join(desc) if desc else "中性影响"
        }

    # 辅助方法
    def get_generating_element(self, element):
        """获取生该五行的元素"""
        generating_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
        return generating_map.get(element, '')

    def get_generated_element(self, element):
        """获取该五行生的元素"""
        generated_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return generated_map.get(element, '')

    def get_ke_relation(self, element):
        """获取被该五行克的元素"""
        ke_map = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
        return ke_map.get(element, '')

    def get_shensha_for_palace(self, palace_num):
        """获取宫位神煞列表（简化版）"""
        # 实际项目中应从神煞系统获取
        return self.shensha_per_palace.get(palace_num, [])

    def analyze_central_palace_effect(self):
        """全面分析中五宫寄宫对各宫的影响（含天禽星能量传递）"""
        if not hasattr(self, 'central_palace_host') or not self.central_palace_host:
            return

        host_num = self.central_palace_host  # 寄宫宫位(2或8)
        host_name = self.PALACE_NAMES[host_num - 1]
        effects = []

        # 1. 天禽星与寄宫星的五行关系 ----------------------------------------
        celestial_star = self.main_pan['star_pan'][4]  # 中五宫天禽星
        host_star = self.main_pan['star_pan'][host_num - 1]  # 寄宫九星

        # 获取五行属性（天禽属土，寄宫星属性需映射）
        wuxing_map = {
            '天蓬': '水', '天芮': '土', '天冲': '木', '天辅': '木',
            '天禽': '土', '天心': '金', '天柱': '金', '天任': '土', '天英': '火'
        }
        star_effect = f"天禽星（土）寄{host_name}："

        # 天禽星与寄宫星的五行生克
        if host_star in wuxing_map:
            relation = self.get_wuxing_relation('土', wuxing_map[host_star])
            star_effect += f"与{host_star}（{wuxing_map[host_star]}）形成{relation} → "

            # 特殊星组合判断
            if host_star == '天芮':
                star_effect += "【土气过重】易引发疾病/拖延"
            elif host_star == '天英':
                star_effect += "【火生土】文书能量增强但易浮躁"
            elif relation == '相克':
                star_effect += "【能量冲突】需化解土气受阻"

        effects.append(star_effect)

        # 2. 天禽星对寄宫门的影响 ------------------------------------------
        host_door = self.main_pan['door_pan'][host_num - 1]
        if host_door:
            door_effect = f"{host_name}{host_door}受天禽星影响："
            door_wuxing = self.wuxing_map.get(host_door[0], '')

            # 门与天禽星的五行关系（天禽属土）
            if door_wuxing:
                door_relation = self.get_wuxing_relation('土', door_wuxing)
                door_effect += f"门（{door_wuxing}）被天禽土{door_relation} → "

                # 吉凶判断
                if host_door in ['生门', '开门'] and door_relation == '相生':
                    door_effect += "吉门得助（事业/财运提升）"
                elif host_door == '死门' and door_relation == '相生':
                    door_effect += "凶门能量增强（需化解病灾）"
                elif door_relation == '相克':
                    door_effect += "门受制（行动力下降）"

            effects.append(door_effect)

        # 3. 八神能量传导（值符/九天特殊作用）-----------------------------
        center_god = self.main_pan['god_pan'][4]  # 中五宫八神
        host_god = self.main_pan['god_pan'][host_num - 1]

        if center_god and host_god:
            god_effect = f"八神传导：{center_god}→{host_god} → "

            # 特殊组合
            if center_god == '值符' and host_god == '九天':
                god_effect += "【权威升级】贵人助力明显"
            elif center_god == '玄武' and host_god == '九地':
                god_effect += "【暗中谋划】适合潜伏行动"
            elif center_god == '腾蛇' and host_god == '太阴':
                god_effect += "【虚惊多变】注意欺骗信息"

            effects.append(god_effect)

        # 4. 三奇六仪激发效应 --------------------------------------------
        host_earthly = self.earthly_pan.get(host_num, '')
        if any(qi in host_earthly for qi in ['乙', '丙', '丁']):
            qi_effect = f"{host_name}三奇激发天禽星："

            if '乙' in host_earthly:
                qi_effect += "【木克土】贵人相助但压力大"
            elif '丙' in host_earthly:
                qi_effect += "【火生土】机遇爆发需防过激"
            elif '丁' in host_earthly:
                qi_effect += "【火生土】文书/桃花有利"

            effects.append(qi_effect)

        # 5. 中宫地盘干对寄宫的影响（戊/己特殊作用）---------------------
        center_earthly = self.earthly_pan.get(5, '')
        if '戊' in center_earthly or '己' in center_earthly:
            earth_effect = f"中宫地盘"

            if '戊' in center_earthly:
                earth_effect += "戊土增强天禽【财库】"
                if host_num == 2:  # 寄坤宫
                    earth_effect += "（地产/农业有利）"
            elif '己' in center_earthly:
                earth_effect += "己土引发天禽【淤滞】"
                if '天芮' in host_star:
                    earth_effect += "（慢性病风险）"

            effects.append(earth_effect)

        # 保存到格局分析（去重后按优先级排序）
        priority_order = ['相克', '值符', '九天', '三奇', '戊土', '己土']
        effects_sorted = sorted(
            list(set(effects)),  # 去重
            key=lambda x: next((i for i, kw in enumerate(priority_order) if kw in x), 999)
        )

        for effect in effects_sorted:
            if effect not in self.patterns:
                self.patterns.append(effect)

    def handle_chaoshen_jieqi(self, base_ju, term, days_into_term):
        """专业超神接气处理（拆补法规范）"""
        # 获取当前旬首
        hour_ganzhi = self.calculate_hour_ganzhi()
        xunshou = self.get_xunshou(hour_ganzhi)

        # 检查是否上元符头（甲子、甲午、己卯、己酉）
        shangyuan_futou = ['甲子', '甲午', '己卯', '己酉']

        if xunshou not in shangyuan_futou:
            return base_ju  # 非上元符头不处理

        # 计算符头超过节气的天数
        futou_days = self.get_futou_days(xunshou, term)

        # 专业规则：符头超过节气9天以上
        if futou_days > 9.0:
            # 获取当前节气对应的下元局数
            term_ju_map = self.get_term_ju_map()
            if term in term_ju_map:
                return term_ju_map[term][2]  # 使用下元局数

        return base_ju

    def find_futou_date(self, xunshou):
        """精确查找符头日期（天文级精度）"""
        # 1. 确定符头干支在60甲子中的位置
        jiazi = [...]  # 完整60甲子列表
        try:
            offset = jiazi.index(xunshou)
        except ValueError:
            return None

        # 2. 基于基准日计算（2000年1月1日为甲子日）
        base_date = datetime(2000, 1, 1, tzinfo=pytz.UTC)

        # 3. 计算目标日期（天文校准）
        target_days = offset * 6.0  # 60甲子循环（6个符头）

        # 4. 考虑月相影响（符头与新月关联）
        new_moon_correction = self.get_lunar_phase_correction(base_date)

        return base_date + timedelta(days=target_days + new_moon_correction)

    def get_lunar_phase_correction(self, base_date):
        """获取月相对符头的修正值"""
        # 使用ephem计算最近新月时间
        try:
            next_new_moon = ephem.next_new_moon(base_date)
            days_to_moon = (next_new_moon.datetime() - base_date).days
            return 0.5 * math.sin(2 * math.pi * days_to_moon / 29.53)
        except:
            return 0.0

    def get_futou_days(self, xunshou, current_term):
        """计算符头超过节气的天数"""
        # 1. 获取符头对应的日期
        futou_date = self.find_futou_date(xunshou)

        # 2. 获取当前节气时间
        term_time = self._solar_term_cache.get(current_term)

        if not futou_date or not term_time:
            return 0.0

        # 3. 计算时间差（天数）
        return (futou_date - term_time).total_seconds() / 86400.0

    def get_direction_luck(self, palace, bearing=None):
        """综合方位吉凶判断（整合神煞+门星）"""
        # 获取基础方位信息
        direction_info = self.get_detailed_direction(palace, bearing)

        # 门星组合吉凶
        star = self.main_pan['star_pan'][palace - 1]
        door = self.main_pan['door_pan'][palace - 1]
        luck = self._get_door_star_luck(door, star)

        # 神煞影响
        shensha = self.shensha_per_palace.get(palace, [])
        shensha_effect = sum(self.shensha_energy_map.get(s, 0) for s in shensha)

        # 综合评分（0-100）
        score = 50 + luck * 20 + shensha_effect * 30
        return {
            'direction': direction_info,
            'score': min(100, max(0, score)),
            'luck': '吉' if score > 60 else '凶' if score < 40 else '平'
        }

    def _get_door_star_luck(self, door, star):
        """八门九星组合吉凶（专业秘传规则）"""
        COMBINATIONS = {
            ('开门', '天心'): 1.0,  # 大吉
            ('死门', '天芮'): -0.8,  # 大凶
            # ...其他组合规则...
        }
        return COMBINATIONS.get((door, star), 0)

    def get_wuxing_relation(self, w1, w2, palace=None, term=None):
        """
        专业级五行关系判断（含能量强度计算）

        参数：
            w1: 主方五行
            w2: 客方五行
            palace: 所在宫位(1-9，可选)
            term: 节气名称(可选，自动获取当前节气)

        返回：
            (关系类型, 能量强度, 详细说明)
        """
        # 1. 完整五行生克关系表（含基础能量值）
        WUXING_RELATIONS = {
            # 相生关系（生方能量强度，被生方获得强度）
            ('木', '火'): ('相生', 0.7, "木生火，文明之象"),
            ('火', '土'): ('相生', 0.6, "火生土，燥土成器"),
            ('土', '金'): ('相生', 0.5, "土生金，矿藏出土"),
            ('金', '水'): ('相生', 0.8, "金生水，寒泉凝结"),
            ('水', '木'): ('相生', 0.9, "水生木，润泽成长"),

            # 相克关系（克方消耗强度，被克方受损强度）
            ('木', '土'): ('相克', 0.6, "木克土，根破坚壤"),
            ('土', '水'): ('相克', 0.5, "土克水，堤坝截流"),
            ('水', '火'): ('相克', 0.7, "水克火，激流灭火"),
            ('火', '金'): ('相克', 0.8, "火克金，熔炼成器"),
            ('金', '木'): ('相克', 0.6, "金克木，斧斤斫伐"),

            # 比和关系
            ('木', '木'): ('比和', 1.2, "双木成林，互助成长"),
            ('火', '火'): ('比和', 1.3, "烈焰叠加，过犹不及"),
            ('土', '土'): ('比和', 1.1, "厚土堆积，迟滞淤塞"),
            ('金', '金'): ('比和', 1.0, "双金争鸣，刚硬相击"),
            ('水', '水'): ('比和', 1.4, "众水汇流，泛滥成灾")
        }

        # 2. 获取基础关系
        relation_data = WUXING_RELATIONS.get((w1, w2))
        if not relation_data:
            return ('无关系', 0, "五行属性不匹配")

        relation_type, base_power, desc = relation_data

        # 3. 节气旺衰修正（自动获取当前节气）
        if term is None:
            term = self.get_precise_solar_term()

        # 节气五行能量表（季节修正系数）
        TERM_ENERGY = {
            '春分': ('木', 1.2), '清明': ('木', 1.1), '谷雨': ('木', 1.0),
            '立夏': ('火', 1.3), '小满': ('火', 1.2), '芒种': ('火', 1.1),
            '夏至': ('火', 1.4), '小暑': ('土', 1.1), '大暑': ('土', 1.0),
            '立秋': ('金', 1.3), '处暑': ('金', 1.2), '白露': ('金', 1.1),
            '秋分': ('金', 1.4), '寒露': ('金', 1.0), '霜降': ('金', 0.9),
            '立冬': ('水', 1.3), '小雪': ('水', 1.2), '大雪': ('水', 1.1),
            '冬至': ('水', 1.5), '小寒': ('土', 1.0), '大寒': ('土', 0.9)
        }

        term_element, term_factor = TERM_ENERGY.get(term, ('', 1.0))

        # 主方得令判断
        if w1 == term_element:
            base_power *= term_factor
            desc += f" | {w1}当令×{term_factor:.1f}"
        # 客方得令判断
        elif w2 == term_element:
            base_power /= term_factor
            desc += f" | {w2}当令÷{term_factor:.1f}"

        # 4. 宫位能量修正
        if palace is not None:
            palace_element = self.wuxing_map.get(self.PALACE_NAMES[palace - 1][0], '')

            # 宫位生主方
            if (palace_element, w1) in [('木', '火'), ('火', '土'), ('土', '金'), ('金', '水'), ('水', '木')]:
                base_power *= 1.2
                desc += f" | 宫位{palace_element}生{w1}+20%"

            # 宫位克主方
            elif (palace_element, w1) in [('木', '土'), ('土', '水'), ('水', '火'), ('火', '金'), ('金', '木')]:
                base_power *= 0.8
                desc += f" | 宫位{palace_element}克{w1}-20%"

            # 主方生宫位（泄气）
            elif (w1, palace_element) in [('木', '火'), ('火', '土'), ('土', '金'), ('金', '水'), ('水', '木')]:
                base_power *= 0.9
                desc += f" | {w1}生宫位{palace_element}-10%"

        # 5. 阴阳遁微调
        if self.yin_yang == "阴遁" and relation_type == "相克":
            base_power *= 0.95  # 阴遁时克制力稍减
            desc += " | 阴遁克力微调"

        return (relation_type, round(base_power, 2), desc)

    def arrange_celestial_gan(self):
        """排布天盘干（完全兼容现有结构）"""
        # 1. 初始化天盘干数组（长度9）
        celestial_gan = [''] * 9

        # 2. 获取值符星和时干宫位（复用现有数据）
        zhifu_star = self.main_pan['zhifu_star']
        hour_gan = self.calculate_hour_ganzhi()[0]
        target_palace = self.find_palace_by_gan(hour_gan)

        # 3. 星-宫映射表（保持现有STAR_FIXED_POSITIONS）
        star_origin = self.STAR_FIXED_POSITIONS

        # 4. 值符携干（核心逻辑）
        try:
            # 获取值符原始宫位地盘干
            origin_palace = star_origin[zhifu_star]
            zhifu_gan = self._extract_primary_gan(self.earthly_pan.get(origin_palace, ""))

            # 放置到新宫位（完全兼容索引0-8）
            celestial_gan[target_palace] = zhifu_gan
        except (KeyError, IndexError):
            pass

        # 5. 其他八星带干（保持原有转动方向）
        direction = 1 if self.yin_yang == "阳遁" else -1
        for star in self.STARS:
            if star == zhifu_star:
                continue

            try:
                # 获取星原始宫位地盘干
                origin_palace = star_origin[star]
                star_gan = self._extract_primary_gan(self.earthly_pan.get(origin_palace, ""))

                # 计算偏移量（复用现有逻辑）
                offset = (target_palace - star_origin[zhifu_star]) % 9
                new_position = (star_origin[star] + offset * direction) % 9

                # 放置天盘干（跳过中宫处理）
                if new_position != 4:  # 中宫索引为4
                    celestial_gan[new_position] = star_gan
            except KeyError:
                continue

        return celestial_gan

    def _extract_primary_gan(self, gan_str):
        """提取主天干（兼容寄宫格式）"""
        if not gan_str:
            return ""
        # 匹配第一个天干字符（兼容"戊(寄坤二宫)"格式）
        match = re.search(r'([甲乙丙丁戊己庚辛壬癸])', gan_str)
        return match.group(1) if match else ""

    def check_men_po(self):
        """判断八门迫制（门迫、门制），并考虑伏吟/反吟影响"""
        self.men_po = {}  # 结构: {宫位: {'door': 门, 'type': 类型, 'severity': 严重程度, 'desc': 描述}}

        for palace_num in range(1, 10):
            if palace_num == 5:  # 跳过中五宫
                continue

            door = self.main_pan['door_pan'][palace_num - 1]
            if not door:  # 无门则跳过
                continue

            men_wx = self.door_wuxing_map.get(door, '')
            palace_wx = self.palace_wuxing_map.get(palace_num, '')

            if not men_wx or not palace_wx:
                continue

            # 判断门迫（门克宫）
            if self.ke_relations.get(men_wx) == palace_wx:
                severity = self._get_men_po_severity(door, palace_num)
                if self.door_fu or self.star_fu:  # 伏吟加重门迫
                    severity = min(1.0, severity * 1.2)
                self.men_po[palace_num] = {
                    'door': door,
                    'type': '门迫',
                    'severity': severity,
                    'desc': f"{door}迫{self.PALACE_NAMES[palace_num - 1]}（{men_wx}克{palace_wx}）"
                }

            # 判断门制（宫克门）
            elif self.ke_relations.get(palace_wx) == men_wx:
                severity = 0.3  # 基础值
                if door in ['生门', '开门', '休门']:  # 吉门受克更严重
                    severity = 0.5
                self.men_po[palace_num] = {
                    'door': door,
                    'type': '门制',
                    'severity': severity,
                    'desc': f"{door}受{self.PALACE_NAMES[palace_num - 1]}克（{palace_wx}克{men_wx}）"
                }

    def check_dizhi_fuyin(self):
        """地支伏吟检查（安全版）"""
        if not hasattr(self, 'year_ganzhi'):
            self.year_ganzhi = self.calculate_year_ganzhi()

        # 确保所有干支已初始化
        required = ['year_ganzhi', 'month_ganzhi', 'day_ganzhi']
        for attr in required:
            if not hasattr(self, attr):
                getattr(self, f'calculate_{attr}')()

        # 实际检查逻辑
        year_zhi = self.year_ganzhi[1]
        month_zhi = self.month_ganzhi[1]
        day_zhi = self.day_ganzhi[1]

        self.dizhi_fuyin = (year_zhi == month_zhi == day_zhi)

    def _get_next_solar_term(self, current_term):
        """获取当前节气后的下一个节气"""
        solar_terms = [
            '冬至', '小寒', '大寒', '立春', '雨水', '惊蛰',
            '春分', '清明', '谷雨', '立夏', '小满', '芒种',
            '夏至', '小暑', '大暑', '立秋', '处暑', '白露',
            '秋分', '寒露', '霜降', '立冬', '小雪', '大雪'
        ]
        try:
            current_index = solar_terms.index(current_term)
            next_index = (current_index + 1) % len(solar_terms)
            return solar_terms[next_index]
        except ValueError:
            return '冬至'  # 默认返回冬至

    def _get_men_po_severity(self, door, palace_num):
        """门迫严重程度（0.1-1.0）"""
        severe_cases = {
            ('死门', 1): 1.0,  # 死门落坎宫（土克水，大凶）
            ('伤门', 2): 1.0,  # 伤门落坤宫（木克土，大凶）
            ('惊门', 9): 0.8,  # 惊门落离宫（金受火克，中凶）
            ('景门', 6): 0.7,  # 景门落乾宫（火克金，中凶）
            ('杜门', 8): 0.6,  # 杜门落艮宫（木克土，小凶）
            ('开门', 3): 0.5  # 开门落震宫（金克木，小凶）
        }
        return severe_cases.get((door, palace_num), 0.5)  # 默认0.5

    def calculate(self):
        """核心计算逻辑"""

        # 1. 先计算所有干支
        self.year_ganzhi = self.calculate_year_ganzhi()  # 必须先计算
        self.month_ganzhi = self.calculate_month_ganzhi()
        self.day_ganzhi = self.calculate_ganzhi(self.date_obj)


        # 1. 计算日干支
        self.day_ganzhi = self.calculate_ganzhi(self.date_obj)

        # 2. 确定阴阳遁（使用精确节气方法）
        self.solar_term = self.get_precise_solar_term()

        # 3. 确定局数（拆补法）
        self.ju = self.determine_ju()

        # 新增：超神接气修正
        adjusted_ju = self._check_chaoshen_jieqi()
        if adjusted_ju is not None:
            self.ju = adjusted_ju
            print(f"局数修正为：{self.ju}局（超神接气规则）")



        # 4. 排地盘
        self.earthly_pan = self.arrange_earthly_pan()

        # 5. 排天盘（包含九星、八门、八神）
        self.main_pan = self.arrange_main_pan()

        self.analyze_ten_gan_response()  # 确保在排盘完成后调用

        self.check_global_professional_patterns()

        # 新增迫制检查
        self.check_men_po()

        # 6. 计算方位信息
        if self.latitude and self.longitude:
            self.direction = self.calculate_direction()

        self.calculate_kongwang()  # 空亡计算
        self.check_hour_luck()  # 时辰吉凶
        self.check_dizhi_fuyin()  # 新增

        self.check_special_patterns()  # 伏吟反吟


        self.analyze_central_palace_effect()  # 中五宫

        # 计算马星
        self.horse_star, self.horse_star_palace = self.get_horse_star()

        self.check_angan_fuyin()  # 新增暗干fuyin
        self.calculate_shensha()
        self.calculate_tianyi_movement()  # 新增
        self.analyze_patterns()  # 重新分析格局

        # 计算长生十二宫状态（基于日干）
        self.changsheng_states = {}
        day_gan = self.day_ganzhi[0]  # 日干

        for palace in range(1, 10):
            branch = self.get_palace_dizhi(palace)  # 获取宫位地支
            self.changsheng_states[palace] = self.get_changsheng_state(day_gan, branch)



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

    def calculate_ganzhi(self, date):
        result = self.calculate_sizhu_with_jieqi()

        return result['四柱']['日柱']

    def calculate_shensha(self):
        """计算九宫神煞分布"""
        # 确保干支数据存在
        if not hasattr(self, 'year_ganzhi'):
            self.calculate_year_ganzhi()
        if not hasattr(self, 'month_ganzhi'):
            self.calculate_month_ganzhi()
        if not hasattr(self, 'day_ganzhi'):
            self.day_ganzhi = self.calculate_ganzhi(self.date_obj)
        hour_ganzhi = self.calculate_hour_ganzhi()

        # 初始化神煞计算器
        self.shensha_calculator = ShenShaCalculator(
            self.year_ganzhi,
            self.month_ganzhi,
            self.day_ganzhi,
            hour_ganzhi
        )

        # 计算每个宫位的神煞
        for palace in range(1, 10):
            dizhi = self.get_palace_dizhi(palace)
            self.shensha_per_palace[palace] = self.shensha_calculator.get_palace_shensha(dizhi)




    def _calculate_solar_azimuth(self):
        """天文级太阳方位角计算（取代简单时辰划分）"""
        observer = ephem.Observer()
        observer.lat = str(self.latitude)
        observer.lon = str(self.longitude)
        observer.date = self.date_obj

        sun = ephem.Sun(observer)
        return math.degrees(sun.az) % 360

    def calculate_direction(self):
        """增强版方位定位（整合二十四山+周天度数）"""
        if not self.latitude or not self.longitude:
            return self._fallback_direction()

        # 计算当前太阳方位角（替代简单时辰划分）
        azimuth = self._calculate_solar_azimuth()

        # 周天360度转换为二十四山（每15度一山）
        SHAN_POSITIONS = [
            (337.5, 352.5, "壬山"), (352.5, 7.5, "子山"), (7.5, 22.5, "癸山"),  # 坎宫
            (22.5, 37.5, "丑山"), (37.5, 52.5, "艮山"), (52.5, 67.5, "寅山"),  # 艮宫
            # ...完整二十四山数据...
        ]

        for start, end, name in SHAN_POSITIONS:
            if start <= azimuth < end:
                return f"{name}（{azimuth:.1f}°）"

        return "中宫（无山向）"



    def _check_chaoshen_jieqi(self):
        """检查是否需要因超神接气调整局数（不改变原determine_ju逻辑）"""
        # 1. 获取当前节气和下一个节气
        current_term = self.get_precise_solar_term()
        next_term = self._get_next_solar_term(current_term)

        # 2. 确保我们有节气时间数据
        if not hasattr(self, '_solar_term_cache'):
            return None

        # 3. 获取当前日干支（用于判断符头）
        day_ganzhi = self.day_ganzhi

        # 4. 定义符头（拆补法规则）
        fu_tou = ['甲子', '甲午', '己卯', '己酉']  # 上中元符头

        # 5. 判断是否需调整局数
        if day_ganzhi in fu_tou and current_term in self._solar_term_cache:
            days_to_term = (self._solar_term_cache[current_term] - self.date_obj).days
            if days_to_term > 0:
                # 超神：符头在节气前，使用下个节气的局数
                print(f"超神调整：符头 {day_ganzhi} 在 {current_term} 前，采用 {next_term} 局数")
                return self._get_ju_by_term(next_term)  # 获取下个节气的局数
            elif days_to_term == 0:
                # 正授：符头与节气同日，无需调整
                print(f"正授：符头 {day_ganzhi} 与节气 {current_term} 同日")
        return None  # 无需调整



    def _get_ju_by_term(self, term):
        """根据节气名称返回局数（复用原determine_ju的映射表）"""
        term_ju_map = {
            # 阳遁（冬至→夏至前）
            '冬至': (1, 7, 4), '小寒': (2, 8, 5), '大寒': (3, 9, 6),
            '立春': (8, 5, 2), '雨水': (9, 6, 3), '惊蛰': (1, 7, 4),
            '春分': (3, 9, 6), '清明': (4, 1, 7), '谷雨': (5, 2, 8),
            '立夏': (4, 1, 7), '小满': (5, 2, 8), '芒种': (6, 3, 9),
            # 阴遁（夏至→冬至前）
            '夏至': (9, 3, 6), '小暑': (8, 2, 5), '大暑': (7, 1, 4),
            '立秋': (2, 5, 8), '处暑': (1, 4, 7), '白露': (9, 3, 6),
            '秋分': (7, 1, 4), '寒露': (6, 9, 3), '霜降': (5, 8, 2),
            '立冬': (6, 9, 3), '小雪': (5, 8, 2), '大雪': (4, 7, 1)
        }
        # 默认返回当前局数（若节气不存在则不调整）
        return term_ju_map.get(term, (self.ju,))[0]

    def determine_ju(self):
        """
        根据四柱结果计算时家奇门局数（修正版，兼容拆补法）

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

        # 方法1：拆补法（按农历日直接分三元）
        if lunar_day <= 5:
            yuan = 0  # 上元
        elif lunar_day <= 10:
            yuan = 1  # 中元
        else:
            yuan = 2  # 下元

        # 方法2：符头法（日柱天干决定元，原逻辑）
        tiangan = rizhu[0]  # 日柱天干
        tiangan_yuan_mapping = {
            '甲': 0, '己': 0,  # 上元
            '乙': 1, '庚': 1, '丁': 1,  # 中元
            '丙': 2, '辛': 2, '戊': 2, '癸': 2  # 下元
        }
        yuan_futou = tiangan_yuan_mapping.get(tiangan, 2)  # 默认下元

        # 选择元（这里优先用拆补法，符头法备选）
        yuan = yuan  # 默认拆补法（如需符头法，改为 yuan = yuan_futou）

        # 获取局数
        ju = jieqi_ju_mapping[jieqi][yuan]

        # 记录元名称
        if yuan == 0:
            self.yuan_name = '上元'
        elif yuan == 1:
            self.yuan_name = '中元'
        else:
            self.yuan_name = '下元'
        self.yuan = yuan

        return ju

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

    def get_central_palace_host(self):
        """中宫寄宫规则优化（《御定奇门宝鉴》卷四 + 《遁甲演义》卷二）"""
        # 1. 获取精确节气和日干支
        term = self.get_precise_solar_term()
        day_gan = self.day_ganzhi[0]

        # 2. 四季寄宫基本规则（《御定奇门宝鉴》规范）
        season_rules = {
            # 春季（立春至立夏前）：寄艮八宫
            '立春': 8, '雨水': 8, '惊蛰': 8, '春分': 8, '清明': 8, '谷雨': 8,
            # 夏季（立夏至立秋前）：寄巽四宫（特殊规则）
            '立夏': 4, '小满': 4, '芒种': 4, '夏至': 4, '小暑': 4,
            # 秋季（立秋至立冬前）：寄坤二宫
            '立秋': 2, '处暑': 2, '白露': 2, '秋分': 2, '寒露': 2, '霜降': 2,
            # 冬季（立冬至立春前）：寄乾六宫（特殊规则）
            '立冬': 6, '小雪': 6, '大雪': 6, '冬至': 6, '小寒': 6, '大寒': 6
        }

        # 3. 日干特殊规则（《遁甲演义》卷二）
        gan_special_rules = {
            '戊': 2,  # 戊日必寄坤二宫
            '己': 8,  # 己日必寄艮八宫
            '壬': 1,  # 壬日寄坎一宫
            '癸': 9  # 癸日寄离九宫
        }
        # 4. 首选日干特殊规则
        if day_gan in gan_special_rules:
            return gan_special_rules[day_gan]
        # 5. 次选节气基本规则
        if term in season_rules:
            # 验证节气有效性（防止跨年节气错误）
            term_time = self._solar_term_cache.get(term)
            if term_time and abs((self.date_obj - term_time).days) <= 3:
                return season_rules[term]
        # 6. 阴阳遁保底规则（《奇门法窍》应急规则）
        return 2 if self.yin_yang == "阴遁" else 8


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

    def get_previous_term(self, current_term):
        """
        获取当前节气的前一个节气（严格匹配天文顺序）
        返回:
            str: 节气名称，如'立夏' → '谷雨'
            默认返回'冬至'如果输入无效
        """
        # --- 1. 定义节气顺序（与get_precise_solar_term保持一致）---
        SOLAR_TERM_ORDER = [
            '冬至', '小寒', '大寒', '立春', '雨水', '惊蛰',
            '春分', '清明', '谷雨', '立夏', '小满', '芒种',
            '夏至', '小暑', '大暑', '立秋', '处暑', '白露',
            '秋分', '寒露', '霜降', '立冬', '小雪', '大雪'
        ]

        # --- 2. 验证输入 ---
        if current_term not in SOLAR_TERM_ORDER:
            return '冬至'  # 无效输入默认值

        # --- 3. 动态计算前一个节气 ---
        try:
            # 3.1 优先从缓存中查找实际时间顺序
            if hasattr(self, '_solar_term_cache') and self._solar_term_cache:
                # 按时间排序所有已知节气
                sorted_terms = sorted(
                    self._solar_term_cache.items(),
                    key=lambda x: x[1]
                )
                # 找到当前节气的位置
                for i, (term, _) in enumerate(sorted_terms):
                    if term == current_term:
                        # 返回前一个节气（如果是第一个则取最后一个）
                        return sorted_terms[(i - 1) % len(sorted_terms)][0]

            # 3.2 缓存未命中时使用静态顺序
            idx = SOLAR_TERM_ORDER.index(current_term)
            return SOLAR_TERM_ORDER[(idx - 1) % len(SOLAR_TERM_ORDER)]

        except Exception as e:
            print(f"获取上一个节气失败: {str(e)}")
            return '冬至'  # 保底返回值



    def _get_approximate_solar_term(self, term_name):
        """天文近似公式计算节气（Jean Meeus简化版）"""
        year = self.date_obj.year
        term_formulas = {
            '立春': (2, (year % 100) * 0.2422 + 4.629 - (year % 100) // 4),
            '雨水': (2, (year % 100) * 0.2422 + 19.459 - (year % 100) // 4),
            '惊蛰': (3, (year % 100) * 0.2422 + 6.396 - (year % 100) // 4),
            '春分': (3, (year % 100) * 0.2422 + 21.415 - (year % 100) // 4),
            '清明': (4, (year % 100) * 0.2422 + 5.59 - (year % 100) // 4),
            '谷雨': (4, (year % 100) * 0.2422 + 20.888 - (year % 100) // 4),
            '立夏': (5, (year % 100) * 0.2422 + 6.318 - (year % 100) // 4),
            '小满': (5, (year % 100) * 0.2422 + 21.86 - (year % 100) // 4),
            '芒种': (6, (year % 100) * 0.2422 + 6.5 - (year % 100) // 4),
            '夏至': (6, (year % 100) * 0.2422 + 21.37 - (year % 100) // 4),
            '小暑': (7, (year % 100) * 0.2422 + 7.928 - (year % 100) // 4),
            '大暑': (7, (year % 100) * 0.2422 + 23.65 - (year % 100) // 4),
            '立秋': (8, (year % 100) * 0.2422 + 8.44 - (year % 100) // 4),
            '处暑': (8, (year % 100) * 0.2422 + 23.95 - (year % 100) // 4),
            '白露': (9, (year % 100) * 0.2422 + 8.44 - (year % 100) // 4),
            '秋分': (9, (year % 100) * 0.2422 + 23.82 - (year % 100) // 4),
            '寒露': (10, (year % 100) * 0.2422 + 9.098 - (year % 100) // 4),
            '霜降': (10, (year % 100) * 0.2422 + 24.218 - (year % 100) // 4),
            '立冬': (11, (year % 100) * 0.2422 + 8.218 - (year % 100) // 4),
            '小雪': (11, (year % 100) * 0.2422 + 23.08 - (year % 100) // 4),
            '大雪': (12, (year % 100) * 0.2422 + 7.9 - (year % 100) // 4),
            '冬至': (12, (year % 100) * 0.2422 + 22.6 - (year % 100) // 4),
            '小寒': (1, (year % 100) * 0.2422 + 6.11 - (year % 100) // 4),
            '大寒': (1, (year % 100) * 0.2422 + 20.84 - (year % 100) // 4),
        }

        if term_name not in term_formulas:
            return datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)

        month, day_float = term_formulas[term_name]
        day = int(day_float)
        hour = int((day_float - day) * 24)
        minute = int((((day_float - day) * 24) - hour) * 60)

        return datetime.datetime(year, month, day, hour, minute, tzinfo=pytz.UTC)



    def arrange_earthly_pan(self):
        """动态生成地盘（拆补法规则）"""
        ju = self.ju
        elements = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

        # 阳遁顺排，阴遁逆排
        order = list(range(9)) if self.yin_yang == "阳遁" else list(range(8, -1, -1))

        # 重新排序（洛书飞宫）
        start_idx = (ju - 1) % 9
        arranged = order[start_idx:] + order[:start_idx]

        # 中五宫处理 - 确保必有寄宫信息
        earthly_pan = {}
        for i in range(9):
            palace_num = i + 1
            if arranged[i] == 4:  # 中五宫
                # === 确保central_palace_host一定有值 ===
                if not hasattr(self, 'central_palace_host') or self.central_palace_host is None:
                    # 按节气确定寄宫
                    term = self.get_precise_solar_term()
                    yang_terms = ['冬至', '小寒', '大寒', '立春', '雨水', '惊蛰',
                                  '春分', '清明', '谷雨', '立夏', '小满', '芒种']

                    # 根据节气确定寄宫位置
                    if term in ['立春', '立夏']:
                        self.central_palace_host = 8  # 立春、立夏寄艮八宫
                    elif term in ['立秋', '立冬']:
                        self.central_palace_host = 2  # 立秋、立冬寄坤二宫
                    else:
                        # 其他节气按冬至到夏至前寄艮八，夏至到冬至前寄坤二
                        self.central_palace_host = 8 if term in yang_terms else 2

                # 添加寄宫信息到地盘表示
                # 确保central_palace_host是整数
                if isinstance(self.central_palace_host, int):
                    host_index = self.central_palace_host - 1
                    # 确保索引在有效范围内
                    if 0 <= host_index < len(self.PALACE_NAMES):
                        earthly_pan[palace_num] = elements[arranged[i]] + f"(寄{self.PALACE_NAMES[host_index]})"
                    else:
                        # 默认使用坤二宫
                        earthly_pan[palace_num] = elements[arranged[i]] + "(寄坤二宫)"
                else:
                    # 如果central_palace_host不是整数，使用默认值
                    earthly_pan[palace_num] = elements[arranged[i]] + "(寄坤二宫)"
            else:
                earthly_pan[palace_num] = elements[arranged[i]]

        return earthly_pan

    def handle_center_palace(self, palace):
        """处理中宫特殊规则"""
        if palace != 5:
            return palace

        # 中宫寄宫规则（根据节气变化）
        solar_term = self.get_precise_solar_term()

        # 冬至到夏至前：寄艮8宫
        if solar_term in ['冬至', '小寒', '大寒', '立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满']:
            return 8

        # 夏至到冬至前：寄坤2宫
        return 2

    def get_door_sequence(self, start_palace):
        """
        生成八门排布的专业宫位序列
        :param start_palace: 起始宫位(1-9)
        :return: 宫位序列列表（跳过中五宫）
        """
        if start_palace == 5:
            start_palace = 2  # 默认转坤宫

            # 宫位序列（排除中宫5）
        forward_order = [1, 8, 3, 4, 9, 2, 7, 6]  # 阳遁顺序
        reversed_order = [1, 6, 7, 2, 9, 4, 3, 8]  # 阴遁顺序

        # 找到起始宫位在标准序列中的位置
        try:
            start_idx = self.DOOR_PALACE_ORDER.index(start_palace)
        except ValueError:
            start_idx = 0  # 无效起始宫位时从坎一宫开始

        if self.yin_yang == "阳遁":
            # 阳遁：从起始位置顺序排布
            return self.DOOR_PALACE_ORDER[start_idx:] + self.DOOR_PALACE_ORDER[:start_idx]
        else:
            # 阴遁：从起始位置逆序排布
            # 1. 先反转整个序列
            reversed_order = self.DOOR_PALACE_ORDER[::-1]
            # 2. 找到起始宫位在反转序列中的位置
            rev_idx = reversed_order.index(start_palace)
            # 3. 从该位置开始顺序排列
            return reversed_order[rev_idx:] + reversed_order[:rev_idx]

    def get_wuxing_energy(self, gan):
        """计算天干五行在当令节气中的能量状态"""
        # 当前节气五行属性
        term_wuxing = {
            '春分': '木', '清明': '木', '谷雨': '木',
            '立夏': '火', '小满': '火', '芒种': '火',
            # ... [其他节气映射] ...
        }

        # 天干五行映射
        gan_wuxing = {
            '甲': '木', '乙': '木',
            '丙': '火', '丁': '火',
            '戊': '土', '己': '土',
            '庚': '金', '辛': '金',
            '壬': '水', '癸': '水'
        }

        current_term = self.get_precise_solar_term()
        term_wx = term_wuxing.get(current_term, '土')
        gan_wx = gan_wuxing.get(gan, '')

        if not gan_wx:
            return '平'

        # 五行旺相休囚死判断
        if gan_wx == term_wx:
            return '旺'
        if self.ke_relations.get(term_wx) == gan_wx:
            return '死'
        if self.ke_relations.get(gan_wx) == term_wx:
            return '休'
        return '相'



    def arrange_main_pan(self):
        """主盘（专业修正版）"""
        # 1. 获取时柱干支并确定旬首
        hour_ganzhi = self.calculate_hour_ganzhi()
        xunshou = self.get_xunshou(hour_ganzhi)

        # 2. 核心修正：取时支而非时干！
        hour_zhi = hour_ganzhi[1]  # 时支（非时干）
        start_palace = self.get_palace_by_branch(hour_zhi)  # 地支宫位

        # 3. 值使门确定（《御定奇门宝鉴》卷三规则）
        zhishi_door = self.get_zhishi_door()

        # 4. 专业宫位序列生成（洛书飞宫顺序）
        palace_sequence = self.generate_palace_sequence(start_palace)

        # 5. 八门动态排布（含中宫寄宫处理）
        door_pan = [None] * 9
        door_names = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
        door_start_idx = door_names.index(zhishi_door)

        valid_palace_count = 0  # 实际排布宫位计数（跳过中宫）
        for palace in palace_sequence:
            # 跳过中五宫（《奇门大成心法》规定）
            if palace == 5:
                continue

            # 门随宫转（《烟波钓叟歌》法则）
            door_idx = (door_start_idx + valid_palace_count) % 8
            door_pan[palace - 1] = door_names[door_idx]
            valid_palace_count += 1

        # 6. 值符宫位确定（《黄帝阴符经》规则）
        zhifu_star = self.STARS[(self.ju - 1) % 9]

        # 7. 八神排布（新增实现）
        god_pan = self.arrange_gods()

        # 8. 九星排布（保持原逻辑）
        star_pan = self.arrange_stars()

        # 保存结果
        self.main_pan = {
            'star_pan': star_pan,
            'door_pan': door_pan,
            'god_pan': god_pan,
            'zhifu_star': zhifu_star,
            'zhishi_door': zhishi_door
        }
        # 储存天盘干信息
        self.main_pan['celestial_gan'] = self.arrange_celestial_gan()

        return self.main_pan

    def arrange_gods(self):
        """专业八神排布（《奇门旨归》规范）"""
        # 八神顺序固定
        gods = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

        # 初始化空盘
        god_pan = [None] * 9

        # 1. 找到值符宫位（时干所在宫）
        hour_gan = self.calculate_hour_ganzhi()[0]
        zhifu_palace = self.find_palace_by_gan(hour_gan) + 1

        # 2. 确定转动方向（阳顺阴逆）
        direction = 1 if self.yin_yang == "阳遁" else -1

        # 3. 从值符宫开始排布
        current_palace = zhifu_palace
        for god in gods:
            # 跳过中五宫（《遁甲演义》规定）
            while current_palace == 5:
                current_palace = (current_palace + direction - 1) % 9 + 1

            # 放置八神
            god_pan[current_palace - 1] = god

            # 移动到下一个宫位
            current_palace = (current_palace + direction - 1) % 9 + 1

        return god_pan

    def arrange_stars(self):
        """九星排布（《御定奇门宝鉴》规范）"""
        # 1. 确定值符星（根据局数）
        zhifu_star = self.STARS[(self.ju - 1) % 9]

        # 2. 找到时干宫位
        hour_gan = self.calculate_hour_ganzhi()[0]
        hour_gan_palace = self.find_palace_by_gan(hour_gan)

        # 3. 确定值符星原始宫位
        star_fixed_positions = {
            '天蓬': 1, '天芮': 2, '天冲': 3, '天辅': 4,
            '天禽': 5, '天心': 6, '天柱': 7, '天任': 8, '天英': 9
        }
        zhifu_original_palace = star_fixed_positions[zhifu_star] - 1

        # 4. 计算偏移量
        offset = (hour_gan_palace - zhifu_original_palace) % 9

        # 5. 排布九星
        star_pan = [None] * 9
        direction = 1 if self.yin_yang == "阳遁" else -1

        for i, star in enumerate(self.STARS):
            new_position = (zhifu_original_palace + offset + i * direction) % 9
            star_pan[new_position] = star

        return star_pan

    def generate_palace_sequence(self, start_palace):
        """生成专业宫位序列（洛书飞宫顺序）"""
        # 标准洛书轨迹（《遁甲演义》规范）
        luoshu_path = [4, 9, 2, 7, 5, 3, 8, 1, 6] if self.yin_yang == "阳遁" else [6, 1, 8, 3, 5, 7, 2, 9, 4]

        # 找到起始位置
        try:
            start_idx = luoshu_path.index(start_palace)
        except ValueError:
            start_idx = 0

        # 生成循环序列
        return luoshu_path[start_idx:] + luoshu_path[:start_idx]



    def get_zhishi_door(self):
        """值使门精确确定（《遁甲符应经》卷三 + 《御定奇门宝鉴》卷五）"""
        """
            判断当前的值使门（基于值符星和局数）

            返回:
                值使门名称 (如 "休门") 或 None (如果无法确定)
            """
        ju = self.determine_ju()  # 获取当前局数 (1-9)
        dun = self.determine_yinyang_dun()  # 获取阴遁或阳遁
        zhi_fu_star = self.determine_zhi_fu_star()  # 获取值符星

        if ju is None or dun is None or zhi_fu_star is None:
            return None

        # 八门顺序（休、生、伤、杜、景、死、惊、开）
        men_order = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]

        # 阳遁：值符星初始宫位 = 局数
        # 阴遁：值符星初始宫位 = 10 - 局数
        initial_palace = ju if dun == "阳遁" else (10 - ju)

        # 值使门 = 初始宫位对应的门（循环映射）
        men_idx = (initial_palace - 1) % 8  # 0-7 对应八门
        return men_order[men_idx]

    def get_full_jiazi_cycle(self):
        """生成完整六十甲子循环（《遁甲符应经》顺序）"""
        tiangan = "甲乙丙丁戊己庚辛壬癸"
        dizhi = "子丑寅卯辰巳午未申酉戌亥"
        return [g + z for g in tiangan for z in dizhi][:60]

    def get_fallback_zhishi_door(self):
        """后备值使门规则（节气主导）"""
        term = self.get_precise_solar_term()
        season_door_map = {
            # 春季（立春→谷雨）：休门值使
            '立春': '休门', '雨水': '休门', '惊蛰': '休门',
            '春分': '休门', '清明': '休门', '谷雨': '休门',
            # 夏季（立夏→大暑）：景门值使
            '立夏': '景门', '小满': '景门', '芒种': '景门',
            '夏至': '景门', '小暑': '景门', '大暑': '景门',
            # 秋季（立秋→霜降）：死门值使
            '立秋': '死门', '处暑': '死门', '白露': '死门',
            '秋分': '死门', '寒露': '死门', '霜降': '死门',
            # 冬季（立冬→大寒）：生门值使
            '立冬': '生门', '小雪': '生门', '大雪': '生门',
            '冬至': '生门', '小寒': '生门', '大寒': '生门'
        }
        return season_door_map.get(term, "休门")

    def get_seasonal_zhishi_door(self):
        """阴阳遁+季节复合规则（《奇门旨归》后备）"""
        season = self.get_solar_season()

        if self.yin_yang == "阳遁":
            if season == "春": return "休门"
            if season == "夏": return "景门"
            if season == "秋": return "死门"
            if season == "冬": return "生门"
        else:  # 阴遁
            if season == "春": return "杜门"
            if season == "夏": return "惊门"
            if season == "秋": return "开门"
            if season == "冬": return "伤门"

        return "休门"  # 最终保底值

    def get_solar_season(self):
        """获取精确太阳季节（考虑节气交接）"""
        term = self.get_precise_solar_term()
        spring_terms = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨']
        summer_terms = ['立夏', '小满', '芒种', '夏至', '小暑', '大暑']
        autumn_terms = ['立秋', '处暑', '白露', '秋分', '寒露', '霜降']

        if term in spring_terms: return "春"
        if term in summer_terms: return "夏"
        if term in autumn_terms: return "秋"
        return "冬"  # 剩余节气默认为冬

    def is_tianyi_guiren(self, palace_num):
        """天乙贵人判断（日干+宫位地支）"""
        day_gan = self.day_ganzhi[0]
        dizhi = self.get_palace_dizhi(palace_num)

        guiren_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }
        return dizhi in guiren_map.get(day_gan, [])

    def get_palace_dizhi(self, palace_num):
        """获取宫位对应的地支（时家奇门固定映射）"""
        palace_to_dizhi = {
            1: '子', 2: '未', 3: '卯',
            4: '辰', 5: '', 6: '午',
            7: '酉', 8: '寅', 9: '申'
        }
        return palace_to_dizhi.get(palace_num, '')



    def add_special_zhonggong_patterns(self, host_palace, host_patterns):
        """添加中宫特有格局标识"""
        # 检查天禽星
        try:
            if self.main_pan['star_pan'][host_palace - 1] == "天禽":
                host_patterns.append("\033[36m★ 天禽星居中 → 百事皆宜，化解凶格\033[0m")
        except (IndexError, KeyError):
            pass

        # 检查戊土（中宫代表土）
        try:
            if '戊' in self.earthly_pan.get(host_palace, ""):
                host_patterns.append("\033[33m★ 戊土居中 → 稳固之象，宜守不宜攻\033[0m")
        except TypeError:
            pass

    def add_zhonggong_special_analysis(self, host_palace):
        """添加中宫特殊分析"""
        # 1. 中宫能量分析
        try:
            energy = self.calculate_zhonggong_energy(host_palace)
            print(f"\n★ 中宫能量评估: {energy}")
        except Exception:
            print("\n★ 中宫能量评估: 计算失败")

        # 2. 中宫影响领域
        try:
            effects = self.get_zhonggong_effects(host_palace)
            if effects:
                print("★ 中宫影响领域:")
                for effect in effects:
                    print(f"  - {effect}")
        except Exception:
            print("★ 中宫影响领域分析失败")

    def calculate_zhonggong_energy(self, host_palace):
        """计算中宫能量级别"""
        # 简化示例：实际应根据星、门、神组合计算
        elements = {
            '天禽': 3, '戊': 2, '己': 1,
            '死门': -2, '惊门': -1, '开门': 3
        }

        score = 0
        # 寄宫位置数据
        data = self.get_palace_data(host_palace)

        # 计算分值
        for key, value in elements.items():
            if key in data['star']:
                score += value
            if key in data['door']:
                score += value
            if key in data['earthly']:
                score += value

        # 评估级别
        if score >= 5:
            return "\033[1;32m★★★★★ 极强 (吉)\033[0m"
        elif score >= 3:
            return "\033[32m★★★★ 强 (吉)\033[0m"
        elif score >= 0:
            return "\033[33m★★★ 中等 (平)\033[0m"
        else:
            return "\033[31m★★ 弱 (凶)\033[0m"

    def get_zhonggong_effects(self, host_palace):
        """获取中宫影响领域"""
        effects = []
        host_name = self.PALACE_NAMES[host_palace - 1]

        # 根据寄宫位置确定影响领域
        domain_map = {
            1: "事业根基", 2: "家庭关系", 3: "人际关系",
            4: "学业发展", 5: "健康中心", 6: "财富积累",
            7: "子女运势", 8: "投资风险", 9: "名誉地位"
        }

        if host_palace in domain_map:
            effects.append(f"核心影响：{domain_map[host_palace]}")

        # 特殊门的影响
        if "开门" in self.main_pan['door_pan'][host_palace - 1]:
            effects.append("★ 开运之门 → 适合开启新项目")
        if "死门" in self.main_pan['door_pan'][host_palace - 1]:
            effects.append("▲ 死门当值 → 需化解阻滞")

        return effects

    def get_advanced_shensha(self, palace_num):
        """高阶神煞（需结合用神）"""
        advanced = []

        # 1. 暗干伏吟
        if self.has_anyang(palace_num):
            advanced.append('暗干伏吟')

        # 2. 八门迫制
        if self.is_menpo(palace_num):
            advanced.append('门迫')

        # 3. 星门反吟
        if self.is_fanyin(palace_num):
            advanced.append('反吟')

        return advanced

    def find_palace_by_gan(self, gan):
        """根据地盘天干定位宫位（洛书九宫顺序，0-8索引）
        修正说明：
        1. 己土默认寄坤二宫（索引1），可通过参数配置
        2. 甲木严格按隐干处理（跟随戊土）
        3. 癸水可配置是否与壬同宫
        """
        # 标准天干-宫位映射（索引对应洛书宫数-1）
        gan_palace_map = {
            '甲': 4,  # 甲木隐于戊土（中宫）
            '乙': 2,  # 震三宫
            '丙': 8,  # 离九宫
            '丁': 3,  # 巽四宫
            '戊': 4,  # 中五宫
            '庚': 5,  # 乾六宫
            '辛': 6,  # 兑七宫
            '壬': 0,  # 坎一宫
            '癸': 0 if not getattr(self, 'use_gui_separate', False) else 1  # 可配置
        }

        # 己土处理（优先判断）
        if gan == '己':
            return 1 if getattr(self, 'use_ji_earth_kun', True) else 4  # 默认寄坤二宫

        return gan_palace_map.get(gan, 4)  # 无效天干默认中宫


    def display(self):
        """显示完整的奇门遁甲排盘结果"""

        # 使用 main_pan 中的统一数据源

        try:

            print("\n=== 奇门遁甲排盘 ===")
            print(f"时间: {self.date_obj.strftime('%Y-%m-%d %H:%M')}")
            print(f"节气: {self.solar_term}")  # 添加节气打印
            # ===== 新增旬首打印 =====
            hour_ganzhi = self.calculate_hour_ganzhi()
            xunshou = self.get_xunshou(hour_ganzhi)
            print(f"旬首: {xunshou}")  # 添加在阴阳遁前面
            print(f"年干支: {self.year_ganzhi}")
            print(f"月干支: {self.month_ganzhi}")
            print(f"日干支: {self.day_ganzhi}")
            hour_ganzhi = self.calculate_hour_ganzhi()
            print(f"时干支: {hour_ganzhi}")


            print(f"阴阳遁: {self.yin_yang}")
            print(f"局数: {self.ju}局 {self.yuan_name}")
            print(f"值符星: {self.main_pan.get('zhifu_star', '')}")
            print(f"值使门: {self.main_pan.get('zhishi_door', '')}")

            # 5. 用神定位
            day_gan_palace = self.find_palace_by_gan(self.day_ganzhi[0]) + 1
            print(f"日干（求测人）落宫: {self.PALACE_NAMES[day_gan_palace - 1]}")
            hour_gan_palace = self.find_palace_by_gan(hour_ganzhi[0]) + 1
            print(f"时干（事体）落宫: {self.PALACE_NAMES[hour_gan_palace - 1]}")

            # === 新增空亡和孤虚方信息打印 ===
            if hasattr(self, 'kongwang') and self.kongwang:
                print(f"旬空（空亡）: {', '.join(self.kongwang)}")

                # 真空状态（能量完全消失）
                if self.true_kongwang:
                    print(f"真空（不可用）: \033[31m{', '.join(self.true_kongwang)}\033[0m")
                else:
                    print("真空：无")

                # 假空状态（能量可转宫）
                if self.false_kongwang:
                    print(f"假空（可转宫）: \033[33m{', '.join(self.false_kongwang)}\033[0m")
                else:
                    print("假空：无")

                print(f"孤虚方（空亡对冲方位）: \033[34m{self.guxu}\033[0m")
            else:
                print("旬空（空亡）: 无")

            # 马星信息
            # 在马星显示处增加精确方位
            if hasattr(self, 'horse_star') and hasattr(self, 'horse_star_palace'):
                palace = self.horse_star_palace
                direction = self.PALACE_DIRECTIONS.get(palace, "")

                # 获取精确山向 (示例：传入目标点坐标)
                target_lat, target_lon = 30.0, 120.0  # 实际使用时替换为真实坐标
                bearing = self.calculate_bearing(target_lat, target_lon)
                detailed_dir = self.get_detailed_direction(palace, bearing)

                print(
                    f"马星（驿马）: {self.horse_star}，落{self.horse_star_palace}宫（{direction}）- 精确方位: {detailed_dir}")

            else:
                print("马星计算未完成")

            print("\n★ 九宫格基础信息 ★")
            # 获取月支（用于状态计算）
            month_zhi = self.month_ganzhi[1] if hasattr(self, 'month_ganzhi') and len(self.month_ganzhi) > 1 else ''

            # 1. 定义简易评分规则（直接写在函数内）
            DOOR_SCORES = {
                '开门': 90, '休门': 85, '生门': 95,
                '伤门': 40, '杜门': 50, '景门': 70,
                '死门': 20, '惊门': 30
            }
            STAR_SCORES = {
                '天心': 90, '天任': 85, '天禽': 80,
                '天辅': 75, '天冲': 70, '天英': 65,
                '天芮': 40, '天蓬': 30, '天柱': 50
            }


            palace_scores = {}

            # 确保获取天盘干数据（使用正确的变量名）
            celestial_gans = self.main_pan.get('celestial_gan', [''] * 9)

            for palace in range(1, 10):
                # 宫名（保持不变）
                palace_name = self.PALACE_NAMES[palace - 1]

                # 获取原始数据（保持不变）
                star = self.main_pan['star_pan'][palace - 1] or ''
                earthly = self.earthly_pan.get(palace, '')
                door = self.main_pan['door_pan'][palace - 1] or ''
                god = self.main_pan['god_pan'][palace - 1] or ''

                # 新增：获取天盘干
                celestial_gan = celestial_gans[palace - 1] or ''


                # 状态计算（保持不变）
                gan = earthly.split('(')[0].strip()
                state = self.get_wuxing_state(self.gan_wuxing_map[gan], month_zhi) if gan in self.gan_wuxing_map else ''

                # 计算当前宫位得分（直接使用字典取值）
                door_score = DOOR_SCORES.get(door, 50)
                star_score = STAR_SCORES.get(star, 50)
                shensha_score = 10 * len(self.shensha_per_palace.get(palace, []))  # 每个神煞+10分

                total_score = int(0.4 * door_score + 0.3 * star_score + 0.3 * shensha_score)
                palace_scores[palace] = total_score

                # 神煞（保持不变）
                shensha_list = self.shensha_per_palace.get(palace, [])
                shensha_str = ','.join(shensha_list) if shensha_list else ''

                # 方位（保持不变）
                if palace == 5:
                    direction_str = "中宫(无山向)"
                else:
                    mountains = self.MOUNTAINS_24.get(palace, [])
                    direction_str = "/".join(mountains)

                # ==== 新增：获取长生状态 ====
                branch = self.get_palace_dizhi(palace)  # 获取宫位地支
                changsheng_state = self.get_changsheng_state(self.day_ganzhi[0], branch)  # 计算长生状态

                # 5宫特殊处理
                if palace == 5:
                    # 中宫显示格式：天盘干 | 地盘干
                    gan_display = f"天:{celestial_gan} | 地:（无地支）"
                    if earthly:  # 如果有地盘干信息
                        gan_display = f"天:{celestial_gan} | 地:{earthly}"

                    print(f"[{palace_name}]")
                    print(f"{gan_display} | 门:{door or '（随局）'} | 星:{star} | 神:{god or '（值符）'} | 状态:{state}")
                    print(f"神煞:{shensha_str or '（无）'} | 长生状态:（不适用）")

                else:
                    # 非中宫显示格式：天盘干/地盘干
                    gan_display = f"天:{celestial_gan} | 地:{earthly}"
                    if celestial_gan and earthly:
                        gan_display = f"天:{celestial_gan}|地:{earthly.split('(')[0]}"  # 去除寄宫注释

                    print(f"[{palace_name}]")
                    print(f"{gan_display} | 门:{door} | 星:{star} | 神:{god} | 状态:{state} ")
                    print(f"神煞:{shensha_str} | 长生状态:{changsheng_state}")


                    # === 新增内容开始 ===
                # 2.1 显示二十四山方位
                bearing = ((palace - 1) * 45) % 360  # 宫位中心角度简易计算
                print(f"🗺️ 方位：{self.get_detailed_direction(palace, bearing)}")

                # 2.2 显示五行能量状态
                palace_element = self.wuxing_map[self.PALACE_NAMES[palace - 1][0]]
                state = self.get_wuxing_state(palace_element, self.month_ganzhi)
                print(f"⚡ 能量：{palace_element}({state})", end=" ")

                # 2.3 显示神煞（最多3个）
                shensha = self.shensha_per_palace.get(palace, [])
                print(f"🧿 神煞：{','.join(shensha[:3])}" + ("..." if len(shensha) > 3 else ""))

                print(f"🔢 方位综合评分：{total_score}/100")
                print("")

            # ===== 新增：显示中五宫寄宫信息 =====
            show_zhonggong = False
            zhonggong_position = None

            # 1. 检查地盘中是否有中五宫标记
            for palace, value in self.earthly_pan.items():
                if "寄" in value or "中五" in value:
                    show_zhonggong = True
                    zhonggong_position = palace
                    break

            # 2. 如果未检测到但属性存在也显示
            if not show_zhonggong and hasattr(self, 'central_palace_host'):
                show_zhonggong = True
                zhonggong_position = 5  # 默认中宫位置

            # 3. 显示中五宫专项分析
            if show_zhonggong:
                print("\n【中五宫专项分析】")

                # 获取寄宫位置
                host_palace = getattr(self, 'central_palace_host', 2)  # 默认坤二宫

                # 显示基础信息
                # if zhonggong_position:
                    # print(f"★ 中五宫位置：{self.PALACE_NAMES[zhonggong_position - 1]}宫")
                print(f"★ 寄宫位置：{self.PALACE_NAMES[host_palace - 1]}宫")

                # 获取寄宫位置的格局信息
                host_patterns = []
                for pattern in getattr(self, 'patterns', []):
                    # 匹配格式："宫位名: 描述"
                    if pattern.startswith(self.PALACE_NAMES[host_palace - 1] + ":"):
                        host_patterns.append(pattern)

                # 添加中宫特有格局标识
                if hasattr(self, 'add_special_zhonggong_patterns'):
                    self.add_special_zhonggong_patterns(host_palace, host_patterns)

                # 显示格局结果
                if host_patterns:
                    print(f"★ 中宫寄宫格局 ({len(host_patterns)}项):")
                    for i, effect in enumerate(host_patterns, 1):
                        # 移除原始宫位名前缀，替换为中宫标识
                        cleaned = effect.replace(
                            f"{self.PALACE_NAMES[host_palace - 1]}:",
                            "中宫寄此 →"
                        )
                        print(f"{i}. {cleaned}")
                else:
                    print("※ 中宫寄宫位置无特殊格局")

                # 添加中宫专属分析
                if hasattr(self, 'add_zhonggong_special_analysis'):
                    self.add_zhonggong_special_analysis(host_palace)

            print("\n=== 十干克应单宫格局分析 ===")

            # 完整的宫位名称映射
            palace_names = {
                1: "坎一宫",2: "坤二宫",3: "震三宫",
                4: "巽四宫",5: "中五宫",6: "乾六宫",
                7: "兑七宫",8: "艮八宫",9: "离九宫"
            }

            # 吉凶符号映射
            luck_symbols = {
                "大吉": "(大吉)",  # 绿色圆
                "吉": "(吉)",  # 绿色方块
                "平": "(平)",  # 黄色方块
                "凶": "(凶)",  # 橙色方块
                "大凶": "(大凶)"  # 红色圆
            }

            for result in sorted(self.sgky, key=lambda x: x["宫位"]):
                palace_num = result["宫位"]
                palace_name = palace_names.get(palace_num, f"宫位{palace_num}")
                symbol = luck_symbols.get(result["吉凶"], "◻️")

                # 构建带完整宫位名称的输出行
                output = (
                    f"{symbol} {palace_name}: "
                    f"{result['天盘干']}+{result['地盘干']} → "
                    f"{result['格局名称']}"
                )

                print(output)
                print(f"   解释: {result['解释']}\n")

            # 全局格局分析
            print("\n★ 全局格局分析及其他 ★")
            if not self.patterns:
                print("  无显著特殊格局")
            else:
                # 按吉凶分组排序（大吉->吉->平->凶->大凶）
                level_order = {'大吉': 0, '吉': 1, '平': 2, '凶': 3, '大凶': 4}
                sorted_patterns = sorted(
                    [p for p in self.patterns if '（' in p and '）' in p],  # 过滤有效格局
                    key=lambda x: level_order.get(x.split('（')[1].split('）')[0].split('：')[0], 5)
                )

                for i, pattern in enumerate(sorted_patterns, 1):
                    # 颜色标记（ANSI颜色代码）
                    color_code = {
                        '大吉': '\033[1;32m',  # 亮绿
                        '吉': '\033[32m',  # 绿色
                        '平': '\033[37m',  # 白色
                        '凶': '\033[33m',  # 黄色
                        '大凶': '\033[1;31m'  # 亮红
                    }.get(pattern.split('（')[1].split('）')[0].split('：')[0], '\033[0m')

                    print(f"{i:2}. {color_code}{pattern}\033[0m")  # \033[0m 重置颜色



            # 伏吟信息显示

            if self.full_fu or self.star_fu or self.door_fu:
                print("\n伏吟信息：")
                if self.full_fu: print("- 全盘伏吟")
                if self.star_fu: print("- 九星伏吟")
                if self.door_fu: print("- 八门伏吟")

                # 添加伏吟深度分析
                if hasattr(self, 'patterns'):
                    fu_patterns = [p for p in self.patterns if "伏吟" in p]

                    if fu_patterns:
                        print("\n伏吟格局深度分析：")
                        for pattern in fu_patterns:
                            # 提取关键信息并格式化
                            if "【伏吟格局】" in pattern:
                                parts = pattern.split("：")
                                if len(parts) > 1:
                                    print(f"  * {parts[0]}")
                                    print(f"    {parts[1]}")
                                else:
                                    print(f"  * {pattern}")
                            else:
                                print(f"  * {pattern}")

                    # 如果没有专门的分析，显示基本解释
                    elif self.star_fu or self.door_fu:
                        print("\n基本解释：伏吟主静，事情进展缓慢或有重复")

            # 反吟信息显示
            if self.full_fan or self.star_fan or self.door_fan:
                print("\n反吟信息：")
                if self.full_fan: print("- 全盘反吟")
                if self.star_fan: print("- 九星反吟")
                if self.door_fan: print("- 八门反吟")

                # 值符星反吟状态
                if hasattr(self, 'star_fan') and self.star_fan is not None:
                    print(f"- 值符星反吟: {'是' if self.star_fan else '否'}")

                # 显示深度能量分析
                if hasattr(self, 'patterns'):
                    fan_patterns = [p for p in self.patterns if "反吟格局" in p]

                    if fan_patterns:
                        print("\n反吟格局深度分析：")
                        for pattern in fan_patterns:
                            # 提取关键信息并格式化
                            if "【反吟格局】" in pattern:
                                parts = pattern.split("：")
                                if len(parts) > 1:
                                    print(f"  * {parts[0]}")
                                    print(f"    {parts[1]}")
                                else:
                                    print(f"  * {pattern}")
                            else:
                                print(f"  * {pattern}")

                    # 如果没有专门的分析，显示基本解释
                    elif self.star_fan:
                        print("\n基本解释：星体反吟主事态反复，需注意计划变动")

            # 显示八门迫制情况
            if self.men_po:
                print("\n【八门迫制分析】")
                for palace, info in self.men_po.items():
                    print(
                        f"{self.PALACE_NAMES[palace - 1]}: {info['desc']}（{info['type']}，严重程度 {info['severity']}）")





            # ★★★ 新增：旺衰综合分析 ★★★
            print("\n★ 五行旺衰综合分析 ★")

            # 1. 分析九星旺衰
            print("\n【九星能量状态】")
            star_wangshuai = {}
            for palace in range(1, 10):
                star = self.main_pan['star_pan'][palace - 1]
                if star and star in self.star_wuxing_map:
                    element = self.star_wuxing_map[star]
                    level, score, analysis = self.get_comprehensive_wangshuai(palace, element)

                    # 获取宫位方向
                    direction = self.PALACE_DIRECTIONS.get(palace, "")

                    # 颜色编码
                    color_code = ""
                    if score >= 0.8:
                        color_code = "\033[1;32m"  # 亮绿色
                    elif score >= 0.6:
                        color_code = "\033[32m"  # 绿色
                    elif score >= 0.4:
                        color_code = "\033[33m"  # 黄色
                    else:
                        color_code = "\033[31m"  # 红色

                    print(f"{self.PALACE_NAMES[palace - 1]}（{direction}）: "
                          f"{color_code}{star}（{element}）→ {level}（{score:.2f}）\033[0m")
                    star_wangshuai[star] = level

            # 2. 新增：八门旺衰分析
            print("\n【八门能量状态】")
            door_wangshuai = {}
            for palace in range(1, 10):
                door = self.main_pan['door_pan'][palace - 1]
                if door:
                    # 获取八门五行属性
                    door_element = self.door_wuxing_map.get(door, '')



                    # 综合旺衰分析
                    level, score, analysis = self.get_comprehensive_wangshuai(palace, door_element)



                    # 获取宫位方向
                    direction = self.PALACE_DIRECTIONS.get(palace, "")
                    print(f"{self.PALACE_NAMES[palace - 1]}（{direction}）")
                    door_wangshuai[door] = level

            # 3. 新增：宫位自身旺衰
            print("\n【宫位五行状态】")
            palace_wangshuai = {}
            for palace in range(1, 10):
                palace_name = self.PALACE_NAMES[palace - 1]
                palace_element = self.wuxing_map.get(palace_name[0], '')
                if palace_element:
                    # 只分析宫位自身五行在节气中的状态
                    level, score, _ = self.get_comprehensive_wangshuai(palace, palace_element)

                    # 检查是否空亡宫位
                    kongwang = ""
                    dizhi = self.get_palace_dizhi(palace)
                    if hasattr(self, 'kongwang') and dizhi in self.kongwang:
                        kongwang = " \033[33m[空亡]\033[0m"

                    print(f"{palace_name}: {palace_element} → {level}（{score:.2f}){kongwang}")
                    palace_wangshuai[palace_name] = level

            # 4. 新增：三奇六仪旺衰
            print("\n【三奇六仪能量】")
            special_gan = {
                '乙': '木', '丙': '火', '丁': '火',  # 三奇
                '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'  # 六仪
            }
            for gan, element in special_gan.items():
                gan_palace = self.find_palace_by_gan(gan) + 1
                if gan_palace > 0:
                    level, score, _ = self.get_comprehensive_wangshuai(gan_palace, element)

                    # 标记三奇
                    prefix = "★" if gan in ['乙', '丙', '丁'] else "◎"
                    print(
                        f"{prefix} {gan}（{element}）在{self.PALACE_NAMES[gan_palace - 1]}宫: {level}（{score:.2f})")

            # 5. 新增：关键神煞旺衰
            print("\n【神煞能量状态】")
            key_shensha = ['天乙贵人', '文昌贵人', '驿马', '桃花', '白虎']
            shensha_energy = {}
            for palace in range(1, 10):
                shensha_list = self.get_shensha_for_palace(palace)
                for shensha in shensha_list:
                    if shensha in key_shensha:
                        # 神煞能量基础分
                        base_score = self.shensha_energy_map.get(shensha, 0.5)

                        # 神煞在宫位中的状态
                        palace_element = self.wuxing_map.get(self.PALACE_NAMES[palace - 1][0], '')
                        shensha_element = self.shensha_wuxing_map.get(shensha, '')

                        # 计算能量加成
                        if palace_element and shensha_element:
                            if self.get_generating_element(palace_element) == shensha_element:
                                base_score += 0.3  # 宫位生神煞
                            elif self.get_generating_element(shensha_element) == palace_element:
                                base_score -= 0.2  # 神煞生宫位（泄气）

                        # 确定旺衰等级
                        level = "旺" if base_score >= 0.6 else "平" if base_score >= 0.4 else "衰"

                        print(f"{shensha}在{self.PALACE_NAMES[palace - 1]}宫: {level}（{base_score:.2f})")
                        shensha_energy[shensha] = base_score

            # 6. 分析用神旺衰（日干和时干）
            print("\n【用神能量状态】")
            # 日干（求测人）
            day_gan = self.day_ganzhi[0]
            day_gan_palace = self.find_palace_by_gan(day_gan) + 1
            day_gan_element = self.gan_wuxing_map.get(day_gan, '')
            if day_gan_element:
                level, score, analysis = self.get_comprehensive_wangshuai(day_gan_palace, day_gan_element)
                print(f"日干（{day_gan}）在{self.PALACE_NAMES[day_gan_palace - 1]}宫: "
                      f"{level}（{score:.2f}）")

            # 时干（事体）
            hour_ganzhi = self.calculate_hour_ganzhi()
            hour_gan = hour_ganzhi[0]
            hour_gan_palace = self.find_palace_by_gan(hour_gan) + 1
            hour_gan_element = self.gan_wuxing_map.get(hour_gan, '')
            if hour_gan_element:
                level, score, analysis = self.get_comprehensive_wangshuai(hour_gan_palace, hour_gan_element)
                print(f"时干（{hour_gan}）在{self.PALACE_NAMES[hour_gan_palace - 1]}宫: "
                      f"{level}（{score:.2f}）")

            # 7. 显示最旺和最弱的星
            max_star = max(star_wangshuai, key=lambda k: star_wangshuai[k])
            min_star = min(star_wangshuai, key=lambda k: star_wangshuai[k])
            print(f"\n★ 能量最强: \033[1;32m{max_star}\033[0m，能量最弱: \033[31m{min_star}\033[0m")

            # 8. 显示详细分析报告（示例：天蓬星）
            sample_star = "天蓬"
            if sample_star in self.star_wuxing_map:
                element = self.star_wuxing_map[sample_star]
                # 找到天蓬星所在的宫位
                for palace in range(1, 10):
                    if self.main_pan['star_pan'][palace - 1] == sample_star:
                        level, score, analysis = self.get_comprehensive_wangshuai(palace, element)
                        print(f"\n【{sample_star}星详细分析】")
                        print(analysis)
                        break


            # 五行流通路径分析
            print("\n【五行流通路径分析】")
            for palace in range(1, 10):
                try:
                    flow = self.analyze_wuxing_flow(palace)
                    palace_name = self.PALACE_NAMES[palace - 1]
                    element = self.wuxing_map.get(palace_name[0], '')

                    # 生成文字版路径描述
                    generating_text = self._describe_flow(flow['generating_path'], "生")
                    controlling_text = self._describe_flow(flow['controlling_path'], "克")

                    print(f"""
            {palace_name}({element}) 能量:{self._energy_bar(flow['energy_score'])}
            生我路径: {generating_text if generating_text else "无生助路径"}
            克我路径: {controlling_text if controlling_text else "无克制路径"}
                        """)
                except Exception as e:
                    print(f"分析{palace_name}宫时出错: {str(e)}")


            """修正版天乙贵人信息输出"""
            # 定义完整的洛书宫位映射（包含中五宫处理）
            luoshu_map = {
                1: "坎一", 2: "坤二", 3: "震三", 4: "巽四",
                5: "中五(寄坤二)",  # 关键修复点
                6: "乾六", 7: "兑七", 8: "艮八", 9: "离九"
            }

            # 获取轨迹时处理中宫寄宫
            trajectory = []
            for palace in self.tianyi_trajectory:
                if palace == 5:
                    trajectory.append(2)  # 寄宫到坤二
                    # print("⚠️ 检测到中五宫，自动寄宫到坤二")
                else:
                    trajectory.append(palace)

            # 可视化输出
            print("\n贵人移动轨迹：")
            for i, palace in enumerate(trajectory, 1):
                arrow = "→" if i < len(trajectory) else ""
                print(f"{luoshu_map[palace]}宫{arrow}", end=" ")



        except Exception as e:
            print(f"显示错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def determine_zhi_fu_star(self):
        """
        根据当前局数和阴阳遁判断值符星

        返回:
            值符星名称 (如 "天蓬") 或 None (如果局数无效)
        """
        ju = self.determine_ju()  # 获取当前局数 (1-9)
        dun = self.determine_yinyang_dun()  # 获取阴遁或阳遁

        if ju is None or dun is None:
            return None

        # 阳遁的值符星顺序 (1-9局)
        yang_stars = [
            "天蓬", "天芮", "天冲", "天辅", "天禽",
            "天心", "天柱", "天任", "天英"
        ]

        # 阴遁的值符星顺序 (9-1局，反向)
        yin_stars = [
            "天英", "天任", "天柱", "天心", "天禽",
            "天辅", "天冲", "天芮", "天蓬"
        ]

        if dun == "阳遁":
            return yang_stars[ju - 1]  # 局数1对应索引0
        elif dun == "阴遁":
            return yin_stars[9 - ju]  # 阴遁反向取星
        else:
            return None

    def check_star_fanyin(self):
        """专业级九星反吟判断（修复所有语法错误）"""
        self.star_fan = False
        self.full_fan = False

        # 1. 获取值符星原始宫位（地盘位置）
        zhifu_earthly = None
        for star_name, palace in self.STAR_FIXED_POSITIONS.items():
            if self.main_pan['zhifu_star'] in star_name:
                zhifu_earthly = palace
                break

        if zhifu_earthly is None:
            return False

        # 2. 获取值符星当前落宫（天盘位置）
        zhifu_celestial = None
        for i, star in enumerate(self.main_pan['star_pan']):
            if star and self.main_pan['zhifu_star'] in star:
                zhifu_celestial = i + 1
                break

        if zhifu_celestial is None:
            return False

        # 3. 中五宫特殊处理
        if zhifu_earthly == 5:
            # 获取实际寄宫位置
            host_palace = self.central_palace_host or (2 if self.yin_yang == "阳遁" else 8)
            # 计算寄宫的对冲宫位
            opposite = self.PALACE_OPPOSITES.get(host_palace, host_palace)
            self.star_fan = (zhifu_celestial == opposite)
        else:
            # 常规宫位判断
            opposite = self.PALACE_OPPOSITES.get(zhifu_earthly)
            if opposite:
                self.star_fan = (zhifu_celestial == opposite)

        # 4. 全盘反吟判断（需80%以上星体反吟）
        fan_count = 0
        total_stars = 0

        # 遍历所有九星
        for star_name in self.STARS:
            # 获取地盘固定位置
            earthly_pos = self.STAR_FIXED_POSITIONS.get(star_name)
            if not earthly_pos:
                continue

            # 获取天盘实际位置
            celestial_pos = None
            for i, celestial_star in enumerate(self.main_pan['star_pan']):
                if celestial_star and star_name in celestial_star:
                    celestial_pos = i + 1
                    break

            if not celestial_pos:
                continue

            total_stars += 1

            # 检查是否反吟（特殊处理中五宫）
            if earthly_pos == 5:
                host = self.central_palace_host or (2 if self.yin_yang == "阳遁" else 8)
                opposite_pos = self.PALACE_OPPOSITES.get(host)
            else:
                opposite_pos = self.PALACE_OPPOSITES.get(earthly_pos)

            if opposite_pos and celestial_pos == opposite_pos:
                fan_count += 1

        # 计算反吟比例
        if total_stars > 0:
            fan_ratio = fan_count / total_stars
            self.full_fan = fan_ratio >= 0.8
        else:
            self.full_fan = False

        return self.star_fan

    def analyze_wuxing_flow(self, target_palace):
        """
        五行流通路径分析（修正版）
        :param target_palace: 起始宫位(1-9)
        :return: {
            'generating_path': [生我路径],
            'controlling_path': [克我路径],
            'energy_score': 能量强度(0-100)
        }
        """
        # 获取起始宫位五行属性
        palace_name = self.PALACE_NAMES[target_palace - 1]
        start_element = self.wuxing_map.get(palace_name[0], '')

        # 初始化路径容器
        flow_data = {
            'generating_path': self._trace_flow(target_palace, 'generating'),
            'controlling_path': self._trace_flow(target_palace, 'controlling'),
            'energy_score': self._calculate_energy_score(target_palace)
        }

        return flow_data

    def _trace_flow(self, start_palace, flow_type):
        """
        追踪五行流转路径（修正参数调用）
        """
        path = []
        current_palace = start_palace
        visited = set()

        while current_palace not in visited and len(path) < 8:
            visited.add(current_palace)
            path.append(current_palace)

            # 获取当前宫位五行
            current_name = self.PALACE_NAMES[current_palace - 1]
            current_element = self.wuxing_map.get(current_name[0], '')

            # 查找下一个宫位（修正参数调用）
            next_palace = None
            for palace in range(1, 10):
                if palace == current_palace:
                    continue

                target_name = self.PALACE_NAMES[palace - 1]
                target_element = self.wuxing_map.get(target_name[0], '')

                # 修正为正确的参数数量（3个参数）
                relation = self.get_wuxing_relation(current_element, target_element)

                if (flow_type == 'generating' and relation == '相生') or \
                        (flow_type == 'controlling' and relation == '相克'):
                    next_palace = palace
                    break

            if next_palace is None:
                break
            current_palace = next_palace

        return path

    def _calculate_energy_score(self, palace):
        """综合能量评分（结合节气旺衰和神煞）"""
        # 复用现有旺衰判断方法
        term_state = self.get_term_wangshuai(self.wuxing_map[self.PALACE_NAMES[palace - 1][0]])
        palace_state = self.get_palace_relation(self.wuxing_map[self.PALACE_NAMES[palace - 1][0]],
                                                self.wuxing_map[self.PALACE_NAMES[palace - 1][0]])

        # 能量计算公式（专业权重分配）
        score = term_state['score'] * 0.6 + palace_state['score'] * 0.4

        # 神煞加成（复用shensha系统）
        for shensha in self.shensha_per_palace.get(palace, []):
            score += self.shensha_energy_map.get(shensha, 0) * 0.1

        return min(100, max(0, int(score * 100)))

    def _detect_special_flow_patterns(self, flow_data):
        """检测特殊流通格局（直接写入patterns系统）"""
        # 1. 循环相生（如1→3→6→1）
        if len(flow_data['generating_path']) >= 3 and \
                flow_data['generating_path'][-1] in flow_data['generating_path'][:-1]:
            self.patterns.append("✅五行循环相生（能量倍增）")

        # 2. 断路相克（如4→9→克链中断）
        if len(flow_data['controlling_path']) <= 1:
            self.patterns.append("⚠️五行克链断裂（阻力显现）")

    def _describe_flow(self, path, flow_type):
        """生成文字版路径描述（安全版）"""
        if not path or len(path) < 2:
            return ""

        descriptions = []
        for i in range(len(path) - 1):
            try:
                from_p = path[i]
                to_p = path[i + 1]
                from_name = self.PALACE_NAMES[from_p - 1]
                to_name = self.PALACE_NAMES[to_p - 1]
                from_element = self.wuxing_map.get(from_name[0], '')
                to_element = self.wuxing_map.get(to_name[0], '')

                relation = "生" if flow_type == "生" else "克"
                descriptions.append(
                    f"{from_name}{relation}{to_name}({from_element}{relation}{to_element})"
                )
            except:
                continue

        return " → ".join(descriptions) if descriptions else "路径解析异常"

    def _energy_bar(self, score):
        """文字版能量条（容错处理）"""
        try:
            score = int(score)
            levels = {
                90: "★★★★★极强",
                70: "★★★★较强",
                50: "★★★中等",
                30: "★★较弱",
                0: "★极弱"
            }
            for threshold, label in levels.items():
                if score >= threshold:
                    return f"{label}({score}分)"
            return "能量值异常"
        except:
            return "能量评分无效"

    def _calculate_single_term(self, term_name):
        """计算特定节气的时间（返回带时区的datetime对象）"""
        try:
            # 1. 尝试天文精确计算
            observer = ephem.Observer()
            observer.lon = str(self.longitude) if self.longitude else '116.4'  # 北京经度
            observer.lat = str(self.latitude) if self.latitude else '39.9'  # 北京纬度
            observer.elevation = 0
            observer.pressure = 0

            # 计算节气对应的太阳黄经
            target_angle = self.SOLAR_TERM_ANGLES.get(term_name, 0)

            # 搜索范围（前后365天）
            start_date = self.date_obj - datetime.timedelta(days=365)
            end_date = self.date_obj + datetime.timedelta(days=365)

            # 精确计算节气时刻
            term_time = self._find_exact_solar_term(observer, ephem.Sun(), target_angle, start_date, end_date)

            # 2. 天文计算失败时的后备方案
            if not term_time:
                term_time = self._get_approximate_solar_term(term_name)
                print(f"使用近似公式计算节气: {term_name} = {term_time}")

            # 3. 确保时区信息正确 --------------------------------------
            # 3.1 如果已有时区，直接返回
            if term_time.tzinfo is not None:
                return term_time

            # 3.2 尝试确定本地时区
            if self.latitude and self.longitude:
                try:
                    tf = TimezoneFinder()
                    timezone_str = tf.timezone_at(lng=self.longitude, lat=self.latitude)
                    if timezone_str:
                        tz = pytz.timezone(timezone_str)
                        return tz.localize(term_time)
                except Exception as e:
                    print(f"时区查找失败: {str(e)}")

            # 3.3 默认使用UTC时区
            print(f"警告: {term_name}节气时间无时区信息，使用UTC")
            return term_time.replace(tzinfo=pytz.UTC)

        except Exception as e:
            print(f"节气计算失败: {term_name} - {str(e)}")
            # 后备方案：使用立春近似值并确保带时区
            try:
                # 创建默认时间（2月4日立春）
                default_time = datetime.datetime(self.year, 2, 4, 0, 0, 0)

                # 尝试本地化时间
                if self.latitude and self.longitude:
                    tf = TimezoneFinder()
                    timezone_str = tf.timezone_at(lng=self.longitude, lat=self.latitude)
                    if timezone_str:
                        tz = pytz.timezone(timezone_str)
                        return tz.localize(default_time)

                # 使用UTC作为最后手段
                return default_time.replace(tzinfo=pytz.UTC)
            except:
                # 终极后备方案
                return datetime.datetime(self.year, 2, 4, 0, 0, 0, tzinfo=pytz.UTC)

    def analyze_fanyin_effect(self):
        """反吟格局的深度能量分析（修复语法错误）"""
        if not self.star_fan:  # 确保仅在反吟时分析
            return

        # 获取值符星名称
        zhifu_star = self.main_pan.get('zhifu_star')
        if not zhifu_star:
            return

        # 1. 获取地盘原始位置 (from_palace)
        # from_palace = 值符星在地盘中的固定位置 (1-9)
        from_palace = None
        for star_name, palace in self.STAR_FIXED_POSITIONS.items():
            if zhifu_star in star_name:
                from_palace = palace
                break

        if from_palace is None:
            return

        # 2. 获取天盘落宫位置 (to_palace)
        to_palace = None
        for palace_index, star_name in enumerate(self.main_pan['star_pan']):
            if star_name and zhifu_star in star_name:
                to_palace = palace_index + 1
                break

        if to_palace is None:
            return

        # 3. 获取宫位五行属性
        palace_wuxing = {
            1: '水', 2: '土', 3: '木', 4: '木',
            5: '土', 6: '金', 7: '金', 8: '土', 9: '火'
        }
        from_wuxing = palace_wuxing.get(from_palace, '')
        to_wuxing = palace_wuxing.get(to_palace, '')

        if not from_wuxing or not to_wuxing:
            return

        # 4. 五行生克关系
        relation = self.get_wuxing_relation(from_wuxing, to_wuxing)

        # 5. 专业格局解读
        effects = {
            ('相克', '金', '木'): "金木相战，主变革破败，但蕴含新生之机",
            ('相克', '木', '土'): "木土相争，主资源争夺，事倍功半",
            ('相生', '火', '土'): "火土相生，虽动荡却可化危机为机遇",
            ('比和', '水', '水'): "水势倍增，动荡加剧，需以静制动",
            ('相生', '木', '火'): "木火通明，变中得利，宜主动出击",
            ('相克', '土', '水'): "土水相激，根基不稳，谨防财务损失"
        }

        # 获取具体解读
        effect_desc = effects.get(
            (relation, from_wuxing, to_wuxing),
            f"能量变化：{from_wuxing}{relation}{to_wuxing}，主变动反复"
        )

        # 6. 构建格局描述
        palace_names = ["坎一", "坤二", "震三", "巽四", "中五", "乾六", "兑七", "艮八", "离九"]
        pattern_desc = (
            f"【反吟格局】{zhifu_star}从{palace_names[from_palace - 1]}宫"
            f"→{palace_names[to_palace - 1]}宫：{effect_desc}"
        )

        # 添加到格局列表
        self.patterns.append(pattern_desc)

    def _is_yin_term(self, term_name, term_time):
        """精确到毫秒的阴阳遁判定"""
        yin_terms = ['夏至', '小暑', '大暑', '立秋', '处暑', '白露',
                     '秋分', '寒露', '霜降', '立冬', '小雪', '大雪']

        if term_name not in yin_terms:
            return False

        # 获取节气精确时间（带时区）
        term_time = self._solar_term_cache.get(term_name)
        if not term_time:
            return term_name in yin_terms  # 后备方案

        # 严格判断时间边界（含时区处理）
        time_diff = (self.date_obj - term_time).total_seconds()
        return time_diff >= -1e-6  # 处理浮点误差，包含临界点

    def check_dizhi_fuyin(self):
        """检查地支伏吟（四柱地支重复或与宫位地支相同）"""
        self.dizhi_fuyin = []

        # 确保年干支和月干支已计算
        if not hasattr(self, 'year_ganzhi'):
            self.calculate_year_ganzhi()
        if not hasattr(self, 'month_ganzhi'):
            self.calculate_month_ganzhi()

        # 获取四柱地支（年、月、日、时）
        hour_ganzhi = self.calculate_hour_ganzhi()
        sizhu_dizhi = [
            self.year_ganzhi[1],  # 年支
            self.month_ganzhi[1],  # 月支
            self.day_ganzhi[1],  # 日支
            hour_ganzhi[1]  # 时支
        ]

        # 检查宫位地支是否与四柱地支重复
        for palace in range(1, 10):
            dizhi = self.get_palace_dizhi(palace)
            if sizhu_dizhi.count(dizhi) >= 2:  # 地支重复
                self.dizhi_fuyin.append(palace)
                self.patterns.append(
                    f"{self.PALACE_NAMES[palace - 1]} 地支伏吟（{dizhi}重复）"
                )

    def check_angan_fuyin(self):
        """检查暗干伏吟（天盘干与地盘干相同）"""
        self.angan_fuyin = []
        # 确保已生成天盘干数据
        if 'celestial_gan' not in self.main_pan:
            return

        for palace in range(1, 10):
            # 获取天盘干（正确来源）
            tian_gan = self.main_pan['celestial_gan'][palace - 1]

            # 获取地盘干（需提取主天干）
            di_gan_str = self.earthly_pan.get(palace, "")
            di_gan = self._extract_primary_gan(di_gan_str)  # 提取主天干（忽略寄宫说明）

            # 判断伏吟
            if tian_gan and di_gan and tian_gan == di_gan:
                self.angan_fuyin.append(palace)
                self.patterns.append(
                    f"{self.PALACE_NAMES[palace - 1]} 暗干伏吟（{tian_gan}）"
                )

    def _extract_gan(self, text):
        """从字符串中提取天干（如'戊'或'天芮+癸'中提取'癸'）"""
        if not text:
            return None
        for c in text:
            if c in '甲乙丙丁戊己庚辛壬癸':
                return c
        return None

    def check_star_fuyin(self):
        """严谨的九星伏吟判断"""
        # 获取值符星原始宫位（局数对应宫位）
        zhifu_palace = (self.ju - 1) % 9

        # 检查所有天盘星是否与地盘星相同
        for i in range(9):
            # 跳过中五宫特殊处理
            if i == 4 and self.central_palace_host:
                continue

            celestial_star = self.main_pan['star_pan'][i]
            earthly_star = self.STARS[i]

            # 值符星必须落本宫或对冲宫
            if i == zhifu_palace and celestial_star != earthly_star:
                return False

            # 其他星必须落本宫
            if i != zhifu_palace and celestial_star != earthly_star:
                return False

        return True

    def get_wuxing_relation(self, w1, w2):
        """五行生克关系判断"""
        if w1 == w2:
            return "比和"

        # 相生关系：木→火→土→金→水→木
        if (w1 == '木' and w2 == '火') or \
                (w1 == '火' and w2 == '土') or \
                (w1 == '土' and w2 == '金') or \
                (w1 == '金' and w2 == '水') or \
                (w1 == '水' and w2 == '木'):
            return "相生"

        # 相克关系：木→土→水→火→金→木
        if (w1 == '木' and w2 == '土') or \
                (w1 == '土' and w2 == '水') or \
                (w1 == '水' and w2 == '火') or \
                (w1 == '火' and w2 == '金') or \
                (w1 == '金' and w2 == '木'):
            return "相克"

        return "无关系"

    def check_special_patterns(self):
        """完整修复：添加伏吟判断逻辑"""
        # 1. 先检查反吟（原有逻辑）
        self.check_star_fanyin()

        # 2. 新增伏吟判断逻辑
        self.check_fuyin()

    def check_fuyin(self):
        """专业伏吟判断（以值符星和值使门为主）"""
        self.star_fu = False
        self.door_fu = False
        self.full_fu = False

        # 1. 星伏吟：值符星落在地盘原始宫位
        zhifu_star = self.main_pan['zhifu_star']
        # 获取值符星原始宫位（固定位置）
        fixed_palace = self.STAR_FIXED_POSITIONS.get(zhifu_star, None)
        if fixed_palace is None:
            # 如果找不到，可能是天禽星寄宫，特殊处理
            if zhifu_star == '天禽':
                fixed_palace = 5  # 中五宫
            else:
                return

        # 查找值符星当前落宫
        current_palace = None
        for idx, star in enumerate(self.main_pan['star_pan']):
            if star == zhifu_star:
                current_palace = idx + 1
                break

        # 中五宫寄宫处理：如果原始宫位是5，则看寄宫位置
        if fixed_palace == 5:
            host_palace = self.central_palace_host or 2  # 默认寄坤2宫
            self.star_fu = (current_palace == host_palace)
        else:
            self.star_fu = (current_palace == fixed_palace)

        # 2. 门伏吟：值使门落在地盘原始宫位
        zhishi_door = self.main_pan['zhishi_door']
        door_fixed_map = {
            '休门': 1, '生门': 8, '伤门': 3, '杜门': 4,
            '景门': 9, '死门': 2, '惊门': 7, '开门': 6
        }
        fixed_door_palace = door_fixed_map.get(zhishi_door)
        if fixed_door_palace is None:
            return

        # 查找值使门当前落宫
        current_door_palace = None
        for idx, door in enumerate(self.main_pan['door_pan']):
            if door == zhishi_door:
                current_door_palace = idx + 1
                break

        self.door_fu = (current_door_palace == fixed_door_palace)

        # 3. 全盘伏吟：星伏吟且门伏吟
        self.full_fu = self.star_fu and self.door_fu

        # 添加格局信息
        if self.star_fu:
            self.patterns.append(f"★ 值符星（{zhifu_star}）伏吟 → 事有阻滞，宜守旧")
        if self.door_fu:
            self.patterns.append(f"★ 值使门（{zhishi_door}）伏吟 → 人事不动，需等待时机")
        if self.full_fu:
            self.patterns.append("★ 全盘伏吟 → 能量停滞，重大事项暂缓")

    def _get_star_wuxing(self, star):
        """九星五行映射"""
        wuxing_map = {
            '天蓬': '水', '天芮': '土', '天冲': '木',
            '天辅': '木', '天禽': '土', '天心': '金',
            '天柱': '金', '天任': '土', '天英': '火'
        }
        return wuxing_map.get(star, None)

    def _get_palace_wuxing(self, palace_num):
        """宫位五行映射（1坎水，2坤土...）"""
        palace_wuxing = ['水', '土', '木', '木', '土', '金', '金', '土', '火']
        return palace_wuxing[palace_num - 1]

    def calculate_kongwang(self):
        """计算旬空与孤虚（自动在calculate()中调用）"""
        hour_ganzhi = self.calculate_hour_ganzhi()
        xunshou = self.get_xunshou(hour_ganzhi)

        # 旬空地支（专业规则：旬首后两位地支为空亡）
        start_pos = self.EARTHLY_BRANCHES.index(xunshou[1])
        kongwang_dizhi = [
            self.EARTHLY_BRANCHES[(start_pos + i) % 12]
            for i in range(10, 12)  # 旬首后第10、11位
        ]

        # 清空之前的空亡记录
        self.kongwang = []
        self.true_kongwang = []  # 新增：真空列表
        self.false_kongwang = []  # 新增：假空列表

        # 获取月支
        if not hasattr(self, 'month_ganzhi'):
            self.calculate_month_ganzhi()
        month_zhi = self.month_ganzhi[1]

        # 地支五行映射
        dizhi_wuxing_map = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木',
            '辰': '土', '巳': '火', '午': '火', '未': '土',
            '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }

        # 判断每个空亡地支的状态
        for dz in kongwang_dizhi:
            wuxing = dizhi_wuxing_map.get(dz, '')
            if not wuxing:
                continue

            # 获取五行在当月的状态
            status = self.get_wuxing_state(wuxing, month_zhi)

            # 四季土旺特殊规则
            if month_zhi in ['辰', '戌', '丑', '未']:  # 土旺之月
                if wuxing == '土':
                    # 土旺之月土不为真空
                    self.false_kongwang.append(dz)
                elif status in ['死', '囚']:
                    # 其他五行在土旺月死囚为真空
                    self.true_kongwang.append(dz)
                else:
                    self.false_kongwang.append(dz)
            else:
                # 非土旺月，死囚为真空，其他为假空
                if status in ['死', '囚']:
                    self.true_kongwang.append(dz)
                else:
                    self.false_kongwang.append(dz)

        # 保留原始空亡列表
        self.kongwang = kongwang_dizhi

        # 孤虚方（空亡的对冲地支）
        self.guxu = self.EARTHLY_BRANCHES[(start_pos + 6) % 12]


    def get_palace_data(self, palace_num):
        """收集宫位完整数据（兼容原函数）"""
        idx = palace_num - 1

        # 获取宫位地支
        palace_dizhi = self.get_palace_dizhi(palace_num)

        # 初始化空亡状态（默认值）
        kongwang = False
        true_kongwang = False
        false_kongwang = False
        kongwang_desc = "不空"

        # 如果已计算空亡，则判断宫位状态
        if hasattr(self, 'kongwang') and hasattr(self, 'true_kongwang') and hasattr(self, 'false_kongwang'):
            kongwang = palace_dizhi in self.kongwang
            true_kongwang = palace_dizhi in self.true_kongwang
            false_kongwang = palace_dizhi in self.false_kongwang

            # 确定空亡状态描述
            if true_kongwang:
                kongwang_desc = "真空（能量全无）"
            elif false_kongwang:
                kongwang_desc = "假空（可转宫）"
            elif kongwang:
                kongwang_desc = "空亡（未分类）"

        # 返回完整宫位数据
        return {
            'palace': palace_num,
            'name': self.PALACE_NAMES[idx],
            'earthly': self.earthly_pan.get(palace_num, ""),
            'star': self.main_pan['star_pan'][idx] if idx < len(self.main_pan['star_pan']) else "",
            'door': self.main_pan['door_pan'][idx] if idx < len(self.main_pan['door_pan']) else "",
            'god': self.main_pan['god_pan'][idx] if idx < len(self.main_pan['god_pan']) else "",
            'dizhi': palace_dizhi,  # 保留原有dizhi字段

            # 新增空亡状态字段
            'kongwang': kongwang,  # 是否空亡
            'true_kongwang': true_kongwang,  # 是否真空
            'false_kongwang': false_kongwang,  # 是否假空
            'kongwang_desc': kongwang_desc  # 空亡状态描述
        }


    def add_pattern_match(self, data, key, pattern_db):
        """添加格局匹配结果（修复缺失方法问题）"""
        pattern_info = pattern_db[key]
        if len(pattern_info) == 4:
            name, level, desc, alias = pattern_info
            pattern_str = f"{data['name']}: 【{alias}】{name}（{level}）→ {desc}"
        else:
            # 兼容三元组格式
            name, level, desc = pattern_info
            pattern_str = f"{data['name']}: {name}（{level}）→ {desc}"

        # 根据吉凶级别设置颜色
        if '大吉' in level:
            color = '\033[1;32m'  # 亮绿色
        elif '吉' in level:
            color = '\033[32m'  # 绿色
        elif '大凶' in level:
            color = '\033[1;31m'  # 亮红色
        elif '凶' in level:
            color = '\033[31m'  # 红色
        else:
            color = '\033[33m'  # 黄色

        self.patterns.append(f"{color}{pattern_str}\033[0m")

    def check_global_professional_patterns(self):

        """检查全局专业格局（修复版）"""
        self._check_sqjs() # 检查三奇聚首
        self._check_twsz() # 检查天网
        self._check_wuxing_patterns()  #五行格局检查
        self._check_ganzhi_patterns()  #干支格局检查
        self._check_special_combinations()  #特殊组合格局
        self._check_shensha_patterns()  #神煞格局
        self._check_sanqi_deshi() # 三奇得使
        self._check_yunu_shoumen()  #玉女
        self._check_liuyi_jixing() # 六仪击刑
        self._check_sanqi_tomb_constrained() # 三奇入墓
        self._check_tianxian_shige()  # 添加天显时格检查
        self._check_sanqi_shengdian()  # 新增三奇升殿检查
        self._check_qiyou_luwei()  # 奇游禄位检查
        self._check_sanzha_wujia_patterns() #三假五诈
        self._check_sanqi_shouzhi() # 三奇受制
        self._check_feigan_fugan_patterns()  # 飞干伏干格局
        self._check_time_grid_pattern()  # 时格格局


    def _check_time_grid_pattern(self):
        """检查时格格局（庚+时干）（类内部方法）"""
        # 确保有时干数据
        if not hasattr(self, 'hour_ganzhi'):
            return

        hour_gan = self.hour_ganzhi[0]  # 获取时干

        # 获取天盘干和地盘干
        celestial_gan = self.main_pan.get('celestial_gan', [])
        earthly_gan_map = self.earthly_pan

        # 记录时干所在的宫位
        hour_gan_palace = None
        for palace in range(1, 10):
            # 跳过中五宫特殊处理
            if palace == 5:
                continue

            di_gan = earthly_gan_map.get(palace, "")

            # 提取地盘主天干（去除寄宫信息）
            if '(' in di_gan:
                di_gan = di_gan.split('(')[0]

            if di_gan == hour_gan:
                hour_gan_palace = palace
                break

        # 如果找到时干宫位，检查该宫位天盘是否为庚
        if hour_gan_palace:
            tian_gan = celestial_gan[hour_gan_palace - 1] if hour_gan_palace - 1 < len(celestial_gan) else None

            if tian_gan == '庚':
                direction = self.PALACE_DIRECTIONS.get(hour_gan_palace, "")
                self.patterns.append(
                    f"\033[31m全局: 【时格】{self.PALACE_NAMES[hour_gan_palace - 1]}{direction} "
                    f"（庚+{hour_gan}）→ 阻碍重重，诸事不宜\033[0m"
                )

    def _check_feigan_fugan_patterns(self):
        """检查飞干伏干格局（类内部方法）"""
        # 确保有日干数据
        if not hasattr(self, 'day_ganzhi'):
            return

        day_gan = self.day_ganzhi[0]  # 获取日干

        # 获取天盘干和地盘干
        celestial_gan = self.main_pan.get('celestial_gan', [])
        earthly_gan_map = self.earthly_pan

        # 五行相克关系
        ke_relations = {
            '甲': '戊', '乙': '己', '丙': '庚', '丁': '辛', '戊': '壬',
            '己': '癸', '庚': '甲', '辛': '乙', '壬': '丙', '癸': '丁'
        }

        for palace in range(1, 10):
            # 跳过中五宫特殊处理
            if palace == 5:
                continue

            # 获取当前宫位天地干
            tian_gan = celestial_gan[palace - 1] if palace - 1 < len(celestial_gan) else None
            di_gan = earthly_gan_map.get(palace, "")

            # 提取地盘主天干（去除寄宫信息）
            if '(' in di_gan:
                di_gan = di_gan.split('(')[0]

            if not tian_gan or not di_gan:
                continue

            # 1. 飞干格检测（天盘日干克地盘宫干）
            if tian_gan == day_gan and ke_relations.get(tian_gan) == di_gan:
                direction = self.PALACE_DIRECTIONS.get(palace, "")
                self.patterns.append(
                    f"\033[31m宫位: 【飞干格】{self.PALACE_NAMES[palace - 1]}{direction} "
                    f"（日干{day_gan}克{di_gan}）→ 主动出击反受其害\033[0m"
                )

            # 2. 伏干格检测（地盘日干被天盘宫干克）
            if di_gan == day_gan and ke_relations.get(tian_gan) == di_gan:
                direction = self.PALACE_DIRECTIONS.get(palace, "")
                self.patterns.append(
                    f"\033[31m宫位: 【伏干格】{self.PALACE_NAMES[palace - 1]}{direction} "
                    f"（{tian_gan}克日干{day_gan}）→ 暗中受害，被动受损\033[0m"
                )

    def _check_sanqi_shouzhi(self):
        """检查三奇受制格局（全局凶格）"""
        sanqi_patterns = []

        # 1. 获取三奇位置
        sanqi_positions = {}
        for palace in range(1, 10):
            # 检查天盘干
            celestial_gan = self.main_pan.get('celestial_gan', [])
            if palace - 1 < len(celestial_gan):
                gan = celestial_gan[palace - 1]
                if gan in ['乙', '丙', '丁']:
                    sanqi_positions.setdefault(gan, []).append(palace)

            # 检查地盘干
            earthly_gan = self.earthly_pan.get(palace, "")
            if '乙' in earthly_gan:
                sanqi_positions.setdefault('乙', []).append(palace)
            if '丙' in earthly_gan:
                sanqi_positions.setdefault('丙', []).append(palace)
            if '丁' in earthly_gan:
                sanqi_positions.setdefault('丁', []).append(palace)

        # 2. 检查每种三奇受制情况
        for qi, positions in sanqi_positions.items():
            for palace in positions:
                # 获取宫位信息
                palace_name = self.PALACE_NAMES[palace - 1]
                earthly_gan = self.earthly_pan.get(palace, "")
                star = self.main_pan['star_pan'][palace - 1]
                door = self.main_pan['door_pan'][palace - 1]
                god = self.main_pan['god_pan'][palace - 1] if palace - 1 < len(
                    self.main_pan['god_pan']) else ""

                # 乙奇受制检测
                if qi == '乙':
                    # 乙+庚/辛
                    if '庚' in earthly_gan or '辛' in earthly_gan:
                        sanqi_patterns.append(
                            f"\033[31m{qi}奇受制: 【乙遇庚辛】{palace_name}宫（金克木）→ 谋事受阻，贵人失力\033[0m")

                    # 乙落金宫（乾/兑）
                    if palace in [6, 7]:
                        sanqi_patterns.append(
                            f"\033[31m{qi}奇受制: 【乙入金宫】{palace_name}宫（金克木）→ 肝胆受损，决策失误\033[0m")

                    # 乙遇金神（白虎/天柱）
                    if god == '白虎' or star == '天柱':
                        sanqi_patterns.append(f"\033[31m{qi}奇受制: 【乙逢金神】{palace_name}宫 → 压力倍增，易遭打击\033[0m")

                # 丙/丁奇受制检测
                elif qi in ['丙', '丁']:
                    # 丙/丁+壬/癸
                    if '壬' in earthly_gan or '癸' in earthly_gan:
                        sanqi_patterns.append(
                            f"\033[31m{qi}奇受制: 【{qi}遇壬癸】{palace_name}宫（水克火）→ 文书不利，官非口舌\033[0m")

                    # 丙/丁落水宫（坎）
                    if palace == 1:
                        sanqi_patterns.append(f"\033[31m{qi}奇受制: 【{qi}入水宫】坎一宫（水克火）→ 心血不足，热情消退\033[0m")

                    # 丙/丁遇水神（玄武/天蓬）
                    if god == '玄武' or star == '天蓬':
                        sanqi_patterns.append(f"\033[31m{qi}奇受制: 【{qi}逢水神】{palace_name}宫 → 小人暗算，计划落空\033[0m")

                # 通用受制检测
                # 三奇入墓
                if (qi == '乙' and palace == 2) or (qi == '丙' and palace == 6) or (qi == '丁' and palace == 8):
                    sanqi_patterns.append(f"\033[31m{qi}奇受制: 【{qi}奇入墓】{palace_name}宫 → 才能埋没，机遇流失\033[0m")

                # 三奇逢空亡
                if palace in self.kongwang:
                    sanqi_patterns.append(f"\033[31m{qi}奇受制: 【{qi}奇落空】{palace_name}宫（空亡）→ 虚花不实，徒劳无功\033[0m")

                # 三奇被门迫
                if door and self.palace_wuxing_map.get(palace):
                    door_wx = self.door_wuxing_map.get(door, "")
                    palace_wx = self.palace_wuxing_map.get(palace, "")
                    qi_wx = '木' if qi == '乙' else '火'

                    # 门克宫（迫）且克三奇五行
                    if self.ke_relations.get(door_wx) == palace_wx and self.ke_relations.get(door_wx) == qi_wx:
                        sanqi_patterns.append(
                            f"\033[31m{qi}奇受制: 【{qi}奇门迫】{door}克{qi}于{palace_name}宫 → 内外交困，事倍功半\033[0m")

        # 添加到全局格局
        self.patterns.extend(sanqi_patterns)

    def _check_sanzha_wujia_patterns(self):
        """检查三诈五假格局（专业级实现）"""
        # 三诈格局检测（真诈、重诈、休诈）
        self._check_sanzha_patterns()

        # 五假格局检测（天假、地假、人假、神假、鬼假）
        self._check_wujia_patterns()

    def _check_sanzha_patterns(self):
        """三诈格局检测（真诈、重诈、休诈）"""
        sanzha_found = []

        for palace in range(1, 10):
            # 获取宫位要素
            door = self.main_pan['door_pan'][palace - 1]
            star = self.main_pan['star_pan'][palace - 1]
            god = self.main_pan['god_pan'][palace - 1]
            celestial_gan = self.main_pan['celestial_gan'][palace - 1]

            # 检查吉门（开、休、生）
            if door not in ["开门", "休门", "生门"]:
                continue

            # 检查三奇（乙、丙、丁）
            if celestial_gan not in ["乙", "丙", "丁"]:
                continue

            # 真诈：三吉门 + 三奇 + 太阴
            if god == "太阴":
                sanzha_found.append(f"真诈（{self.PALACE_NAMES[palace - 1]}）")

            # 重诈：三吉门 + 三奇 + 九地
            elif god == "九地":
                sanzha_found.append(f"重诈（{self.PALACE_NAMES[palace - 1]}）")

            # 休诈：三吉门 + 三奇 + 六合
            elif god == "六合":
                sanzha_found.append(f"休诈（{self.PALACE_NAMES[palace - 1]}）")

        if sanzha_found:
            self.patterns.append(f"\033[1;32m全局: 【三诈格局】{', '.join(sanzha_found)} → 宜用计谋，事半功倍\033[0m")

    def _check_wujia_patterns(self):
        """五假格局检测（天假、地假、人假、神假、鬼假）"""
        wujia_found = []

        for palace in range(1, 10):
            # 获取宫位要素
            door = self.main_pan['door_pan'][palace - 1]
            star = self.main_pan['star_pan'][palace - 1]
            god = self.main_pan['god_pan'][palace - 1]
            celestial_gan = self.main_pan['celestial_gan'][palace - 1]
            earthly_gan = self.earthly_pan.get(palace, "")

            # 天假：景门 + 三奇 + 九天（宜上书献策）
            if (door == "景门" and celestial_gan in ["乙", "丙", "丁"] and god == "九天"):
                wujia_found.append(f"天假（{self.PALACE_NAMES[palace - 1]}）")

            # 地假：杜门 + 丁己癸 + 太阴/六合（宜潜行隐匿）
            elif (door == "杜门" and celestial_gan in ["丁", "己", "癸"] and god in ["太阴", "六合"]):
                wujia_found.append(f"地假（{self.PALACE_NAMES[palace - 1]}）")

            # 人假：惊门 + 壬 + 九天（宜捕捉逃犯）
            elif (door == "惊门" and "壬" in celestial_gan and god == "九天"):
                wujia_found.append(f"人假（{self.PALACE_NAMES[palace - 1]}）")

            # 神假：伤门 + 丁己癸 + 九地（宜埋藏祭祀）
            elif (door == "伤门" and celestial_gan in ["丁", "己", "癸"] and god == "九地"):
                wujia_found.append(f"神假（{self.PALACE_NAMES[palace - 1]}）")

            # 鬼假：死门 + 丁己癸 + 九地（宜超度亡灵）
            elif (door == "死门" and celestial_gan in ["丁", "己", "癸"] and god == "九地"):
                wujia_found.append(f"鬼假（{self.PALACE_NAMES[palace - 1]}）")

        if wujia_found:
            self.patterns.append(f"\033[33m全局: 【五假格局】{', '.join(wujia_found)} → 借势而为，灵活运用\033[0m")

    def _check_qiyou_luwei(self):
        """检查奇游禄位格局（三奇在禄位宫）"""
        lu_positions = {
            '乙': 3,  # 乙禄在卯（震三宫）
            '丙': 4,  # 丙禄在巳（巽四宫）
            '丁': 9  # 丁禄在午（离九宫）
        }

        found_patterns = []

        # 检查每个宫位
        for palace in range(1, 10):
            palace_name = self.PALACE_NAMES[palace - 1]

            # 获取天盘干和地盘干
            tian_gan = self.main_pan['celestial_gan'][palace - 1] if palace - 1 < len(
                self.main_pan['celestial_gan']) else ''
            di_gan = self.earthly_pan.get(palace, '')

            # 检查乙丙丁是否在禄位
            for qi, lu_palace in lu_positions.items():
                # 正禄检测（精确位置）
                if palace == lu_palace:
                    if qi in tian_gan or qi in di_gan:
                        found_patterns.append(
                            f"\033[1;32m【{qi}奇正禄】{qi}在{lu_palace}{palace_name}（大吉）→ 得禄位加持，贵人显达\033[0m")

                # 游禄检测（相邻宫位）
                elif abs(palace - lu_palace) == 1:
                    if qi in tian_gan or qi in di_gan:
                        direction = "顺" if palace > lu_palace else "逆"
                        found_patterns.append(
                            f"\033[32m【{qi}奇游禄】{qi}近{lu_palace}{palace_name}（{direction}行，中吉）→ 流动财源，需主动求取\033[0m")

        # 添加到全局格局
        if found_patterns:
            self.patterns.extend(found_patterns)

    def _check_sanqi_shengdian(self):
        """检查三奇升殿格局（乙丙丁三奇落本位宫）"""
        sanqi_patterns = []

        # 1. 乙奇升殿（震三宫）
        if self.main_pan['star_pan'][2] in ['天辅', '天冲']:  # 震三宫索引2
            # 检查乙奇在天盘或地盘
            if '乙' in self.earthly_pan.get(3, "") or \
                    (len(self.main_pan.get('celestial_gan', [])) > 2 and \
                     self.main_pan['celestial_gan'][2] == '乙'):
                sanqi_patterns.append("\033[1;32m全局: 【乙奇升殿】震宫（大吉）→ 贵人扶持，谋事顺遂\033[0m")

        # 2. 丙奇升殿（离九宫）
        if self.main_pan['star_pan'][8] == '天英':  # 离九宫索引8
            if '丙' in self.earthly_pan.get(9, "") or \
                    (len(self.main_pan.get('celestial_gan', [])) > 8 and \
                     self.main_pan['celestial_gan'][8] == '丙'):
                sanqi_patterns.append("\033[1;32m全局: 【丙奇升殿】离宫（大吉）→ 光明普照，化解阴晦\033[0m")

        # 3. 丁奇升殿（兑七宫）
        if self.main_pan['star_pan'][6] in ['天柱', '天心']:  # 兑七宫索引6
            if '丁' in self.earthly_pan.get(7, "") or \
                    (len(self.main_pan.get('celestial_gan', [])) > 6 and \
                     self.main_pan['celestial_gan'][6] == '丁'):
                sanqi_patterns.append("\033[1;32m全局: 【丁奇升殿】兑宫（大吉）→ 玉女守门，文书大利\033[0m")

        # 添加特殊能量加成
        if len(sanqi_patterns) >= 2:
            sanqi_patterns.append("\033[1;36m★ 三奇聚顶 → 天地人三才贯通，万事大吉\033[0m")

        self.patterns.extend(sanqi_patterns)

    def get_zhifu_position(self):
        """获取值符所在宫位（1-9）"""
        gods = self.main_pan.get('god_pan', [])
        for i, god in enumerate(gods):
            if god == '值符':
                return i + 1
        return 0  # 未找到

    def _check_tianxian_shige(self):
        """检查天显时格（甲己日+甲子时/甲戌时）"""
        # 1. 确保日干支和时干支已计算
        if not hasattr(self, 'day_ganzhi'):
            self.day_ganzhi = self.calculate_ganzhi(self.date_obj)
        if not hasattr(self, 'hour_ganzhi'):
            self.hour_ganzhi = self.calculate_hour_ganzhi()

        day_gan = self.day_ganzhi[0]  # 日干
        hour_ganzhi = self.hour_ganzhi  # 时干支

        # 2. 严格标准：甲己日 + 甲子时
        if day_gan in ['甲', '己'] and hour_ganzhi == '甲子':
            self.patterns.append("\033[1;36m全局: 【天显时格】甲己日甲子时（大吉）→ 百事皆宜，逢凶化吉\033[0m")
            return

        # 3. 扩展标准：甲己日 + 甲戌时（《遁甲演义》标准）
        if day_gan in ['甲', '己'] and hour_ganzhi == '甲戌':
            self.patterns.append("\033[1;36m全局: 【天显时格】甲己日甲戌时（吉）→ 诸事可行，利化解危机\033[0m")
            return

        # 4. 其他六甲时判断（《御定奇门宝鉴》补充）
        liujia_shis = ['甲子', '甲戌', '甲申', '甲午', '甲辰', '甲寅']
        if hour_ganzhi in liujia_shis:
            # 获取当前节气
            term = self.get_precise_solar_term()

            # 冬夏至特殊节气判断
            if term in ['冬至', '夏至']:
                self.patterns.append(f"\033[36m全局: 【天显变格】{hour_ganzhi}时+{term} → 大事可成\033[0m")

            # 值符临宫判断
            zhifu_position = self.get_zhifu_position()
            if zhifu_position in [1, 6, 8]:  # 坎、乾、艮宫
                self.patterns.append(
                    f"\033[36m全局: 【天显辅格】{hour_ganzhi}时+值符临{self.PALACE_NAMES[zhifu_position - 1]} → 得贵人助\033[0m")

    def _check_twsz(self):
        # 3. 天网四张（检查天盘干中的癸水）
        celestial_gan = self.main_pan.get('celestial_gan', [])

        gui_count = sum(1 for gan in celestial_gan if gan == '癸')

        # 增强判断：癸+癸在坤宫（2宫）才是真天网
        if gui_count >= 2:
            msg = "\033[31m全局: 【天网恢恢】天网四张（凶）→ 诸事不利，动则见咎\033[0m"
            # 检查是否在坤宫
            if 1 <= self.zhishi_palace <= 9 and celestial_gan[
                self.zhishi_palace - 1] == '癸' and self.zhishi_palace == 2:
                msg = "\033[1;31m全局: 【真天网四张】（大凶）→ 牢狱灾祸，万事宜止\033[0m"
            self.patterns.append(msg)

    def _check_sqjs(self):
        # 确保获取天盘干数据
        celestial_gan = self.main_pan.get('celestial_gan', [])
        # 1. 三奇聚首（严格判断）
        sanqi_positions = []
        for palace in range(1, 10):
            gan = celestial_gan[palace - 1] if len(celestial_gan) > palace - 1 else None
            if gan == '乙': sanqi_positions.append((palace, '乙'))
            if gan == '丙': sanqi_positions.append((palace, '丙'))
            if gan == '丁': sanqi_positions.append((palace, '丁'))

        # 必须满足三个条件才是真三奇聚首
        if len(sanqi_positions) >= 3:
            # 条件1：三奇在不同宫位
            palaces = {pos[0] for pos in sanqi_positions}
            # 条件2：不构成伏吟（星伏吟时三奇聚首无效）
            # 条件3：至少两奇不在四墓位（辰戌丑未）
            if (len(palaces) >= 3 and
                    not self.star_fu and
                    sum(1 for p, _ in sanqi_positions if p not in [2, 4, 6, 8]) >= 2):
                self.patterns.append("\033[1;32m全局: 三奇聚首（大吉）→ 万事顺遂，贵人相助\033[0m")
            else:
                pass

    def _check_liuyi_jixing(self):
        """检查六仪击刑格局（类内部方法）"""
        # 六仪击刑映射表：{天干: (凶宫, 刑害关系)}
        jixing_map = {
            '戊': (3, "子刑卯"),
            '己': (2, "戌刑未"),
            '庚': (8, "申刑寅"),
            '辛': (9, "午自刑"),
            '壬': (4, "辰自刑"),
            '癸': (4, "寅刑巳")  # 癸在巽四宫有两个击刑位置
        }

        jixing_found = []
        for palace in range(1, 10):
            # 获取天盘干
            try:
                celestial_gan = self.main_pan['celestial_gan'][palace - 1]
            except (IndexError, KeyError):
                continue

            # 检查是否形成击刑
            if celestial_gan in jixing_map:
                target_palace, relation = jixing_map[celestial_gan]
                if palace == target_palace:
                    # 特殊处理癸在巽四宫
                    if celestial_gan == '癸':
                        dizhi = self.get_palace_dizhi(palace)
                        if dizhi == '巳':  # 寅刑巳
                            jixing_found.append(f"癸在巽四宫(巳) → {relation}")
                    else:
                        palace_name = self.PALACE_NAMES[palace - 1]
                        jixing_found.append(f"{celestial_gan}在{palace_name} → {relation}")

        # 添加到全局格局
        if jixing_found:
            patterns_str = "，".join(jixing_found)
            self.patterns.append(
                f"\033[31m全局: 【六仪击刑】{patterns_str}（凶）→ 易有伤灾诉讼，行动受阻\033[0m"
            )

    def get_palace_branches(self, palace_num):
        """获取宫位对应的地支列表"""
        return self.PALACE_BRANCH_MAP.get(palace_num, [])
    def _check_sanqi_tomb_constrained(self):
        """专业级三奇入墓/受制格局检测"""
        # 三奇定义：乙(木)、丙(火)、丁(火)
        sanqi = {'乙': '木', '丙': '火', '丁': '火'}

        # 三奇入墓规则（宫位+地支）
        tomb_rules = {
            '乙': (2, ['未']),  # 乙奇入未墓（坤宫）
            '丙': (6, ['戌']),  # 丙奇入戌墓（乾宫）
            '丁': (8, ['丑'])  # 丁奇入丑墓（艮宫）
        }

        # 三奇受制规则（被克宫位）
        constrained_rules = {
            '乙': [6, 7],  # 乙木受制于乾(金)、兑(金)宫
            '丙': [1],  # 丙火受制于坎(水)宫
            '丁': [1]  # 丁火受制于坎(水)宫
        }

        # 1. 遍历所有宫位检测三奇
        for palace in range(1, 10):
            # 获取天盘干（三奇主要看天盘）
            celestial_gan = self.main_pan.get('celestial_gan', [])
            if len(celestial_gan) >= palace:
                gan = celestial_gan[palace - 1]
            else:
                continue

            # 检查是否三奇
            if gan not in sanqi:
                continue

            # 2. 检查入墓格局
            tomb_palace, tomb_branches = tomb_rules.get(gan, (None, []))
            palace_branches = self.get_palace_branches(palace)

            if palace == tomb_palace and any(branch in tomb_branches for branch in palace_branches):
                self.patterns.append(
                    f"\033[31m宫位{self.PALACE_NAMES[palace - 1]}: 【{gan}奇入墓】"
                    f"{gan}落{self.PALACE_NAMES[palace - 1]}({''.join(palace_branches)}) "
                    "→ 能量受阻，吉事成凶\033[0m"
                )

            # 3. 检查受制格局
            if palace in constrained_rules.get(gan, []):
                # 获取克制关系
                wx_gan = sanqi[gan]
                wx_palace = self.palace_wuxing_map.get(palace, '')
                relation = self.get_wuxing_relation(wx_palace, wx_gan)

                self.patterns.append(
                    f"\033[31m宫位{self.PALACE_NAMES[palace - 1]}: 【{gan}奇受制】"
                    f"{gan}{wx_gan}被{self.PALACE_NAMES[palace - 1]}{wx_palace}{relation} "
                    "→ 贵人无力，谋事难成\033[0m"
                )

        # 4. 全局三奇状态评估
        sanqi_status = {qi: False for qi in sanqi}
        for qi in sanqi:
            for palace in range(1, 10):
                celestial_gan = self.main_pan.get('celestial_gan', [])
                if len(celestial_gan) >= palace and celestial_gan[palace - 1] == qi:
                    sanqi_status[qi] = True
                    break

        # 如果有三奇全部入墓/受制
        if all(sanqi_status.values()) and any("奇入墓" in p or "奇受制" in p for p in self.patterns):
            self.patterns.append(
                "\033[31m全局: 【三奇皆困】乙、丙、丁三奇均入墓或受制 "
                "→ 大凶之兆，诸事不宜\033[0m"
            )

    def _check_yunu_shoumen(self):
        """检查玉女守门格局（值使门+丁奇在时支宫位）"""
        try:
            # 1. 获取时支对应的宫位
            hour_zhi = self.calculate_hour_ganzhi()[1]  # 时支
            zhi_palace = self.get_palace_by_branch(hour_zhi)

            # 2. 获取该宫位的值使门和丁奇信息
            palace_door = self.main_pan['door_pan'][zhi_palace - 1]
            palace_star = self.main_pan['star_pan'][zhi_palace - 1]
            palace_earthly = self.earthly_pan.get(zhi_palace, "")
            palace_celestial_gan = self.main_pan.get('celestial_gan', [""] * 9)[zhi_palace - 1]

            # 3. 检查值使门是否在此宫位
            if palace_door != self.main_pan['zhishi_door']:
                return  # 值使门不在此宫

            # 4. 检查丁奇存在形式
            ding_present = ""
            if palace_celestial_gan == '丁':  # 天盘丁（最佳）
                ding_present = "天盘丁"
                level = "\033[1;32m大吉"  # 绿色
            elif '丁' in palace_earthly:  # 地盘丁
                ding_present = "地盘丁"
                level = "\033[32m中吉"  # 浅绿
            elif self._check_hidden_ding(zhi_palace):  # 暗干丁
                ding_present = "暗干丁"
                level = "\033[33m半吉"  # 黄色

            if ding_present:
                # 5. 生成格局描述
                palace_name = self.PALACE_NAMES[zhi_palace - 1]
                desc = (
                    f"全局: 【玉女守门】{level} → "
                    f"值使门({self.main_pan['zhishi_door']})+{ding_present}落{hour_zhi}时支{palace_name}\n"
                    "         ✓ 宜：机密事务、女性相关、文书合同、喜庆之事\033[0m"
                )
                self.patterns.append(desc)

        except (IndexError, KeyError, TypeError) as e:
            if self.strict_mode:
                print(f"玉女守门检测异常: {str(e)}")

    def _check_hidden_ding(self, palace_num):
        """检查暗干丁奇（专业方法）"""
        # 暗干排法：时干+值使门宫位地盘干
        hour_gan = self.calculate_hour_ganzhi()[0]
        earthly_gan = self.earthly_pan.get(palace_num, "")[0]  # 取主干

        # 时干加地盘干的组合
        hidden_gan = {
            '甲': {'戊', '己'}, '乙': {'庚', '辛'}, '丙': {'壬', '癸'},
            '丁': {'戊', '己'}, '戊': {'庚', '辛'}, '己': {'壬', '癸'},
            '庚': {'戊', '己'}, '辛': {'庚', '辛'}, '壬': {'壬', '癸'}, '癸': {'戊', '己'}
        }

        # 检查是否含丁
        return '丁' in hidden_gan.get(hour_gan, set())

    def _check_sanqi_deshi(self):
        """专业三奇得使检测（全局格局）"""
        # 获取时柱旬首
        hour_ganzhi = self.calculate_hour_ganzhi()
        xunshou = self.get_xunshou(hour_ganzhi)

        # 三奇得使映射表
        sanqi_map = {
            '乙': {'甲戌': '己', '甲午': '辛'},
            '丙': {'甲子': '戊', '甲申': '庚'},
            '丁': {'甲辰': '壬', '甲寅': '癸'}
        }

        # 遍历所有宫位检测三奇
        for palace in range(1, 10):
            if palace == 5:  # 跳过中宫
                continue

            # 获取天盘干（三奇）
            tian_gan = self.main_pan['celestial_gan'][palace - 1]

            # 获取地盘干（六甲对应）
            di_gan = self._extract_primary_gan(self.earthly_pan.get(palace, ""))

            # 检测三奇得使
            if tian_gan in sanqi_map:
                required_gan = sanqi_map[tian_gan].get(xunshou)
                if di_gan == required_gan:
                    # 获取宫位方向
                    direction = self.PALACE_DIRECTIONS[palace].split("（")[1].replace("）", "")

                    # 格局描述
                    pattern_name = {
                        '乙': "乙奇得使",
                        '丙': "丙奇得使",
                        '丁': "丁奇得使"
                    }[tian_gan]

                    # 直接添加到全局格局列表
                    self.patterns.append(
                        f"\033[1;32m全局: 【{pattern_name}】{tian_gan}+{di_gan} "
                        f"于{self.PALACE_NAMES[palace - 1]}{direction}（大吉）→ "
                        "贵人相助，万事亨通\033[0m"
                    )

    def _check_wuxing_patterns(self):
        """检查五行全局格局（类内部方法）"""
        wuxing_map = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}

        # 统计地盘五行分布
        for palace in range(1, 10):
            if palace == 5:  # 中五宫特殊处理
                continue

            # 宫位五行
            palace_wx = self.palace_wuxing_map.get(palace, '')
            if palace_wx:
                wuxing_map[palace_wx] += 1

            # 门五行
            door = self.main_pan['door_pan'][palace - 1]
            if door:
                door_wx = self.door_wuxing_map.get(door, '')
                if door_wx:
                    wuxing_map[door_wx] += 1

            # 星五行
            star = self.main_pan['star_pan'][palace - 1]
            if star:
                star_wx = self.star_wuxing_map.get(star, '')
                if star_wx:
                    wuxing_map[star_wx] += 1

        # 检查缺失的五行
        missing_wx = [wx for wx, count in wuxing_map.items() if count == 0]
        if missing_wx:
            self.patterns.append(f"\033[33m全局: 【五行缺{'、'.join(missing_wx)}】→ 能量失衡，需补强相关领域\033[0m")

        # 检查过旺的五行
        dominant_wx = [wx for wx, count in wuxing_map.items() if count >= 4]
        if dominant_wx:
            self.patterns.append(f"\033[31m全局: 【五行过旺】{'、'.join(dominant_wx)}过盛 → 需泄化平衡\033[0m")

    def _check_ganzhi_patterns(self):
        """检查干支全局格局（类内部方法）"""
        # 五不遇时（时干克日干）
        if hasattr(self, 'day_ganzhi') and hasattr(self, 'hour_ganzhi'):
            day_gan = self.day_ganzhi[0]
            hour_gan = self.hour_ganzhi[0]

            # 五行相克关系
            ke_map = {
                '甲': '戊', '乙': '己', '丙': '庚', '丁': '辛', '戊': '壬',
                '己': '癸', '庚': '甲', '辛': '乙', '壬': '丙', '癸': '丁'
            }

            if ke_map.get(hour_gan) == day_gan:
                self.patterns.append("\033[31m全局: 【五不遇时】时干克日干（凶）→ 行事多阻，宜谨慎\033[0m")

        # 三刑格局（寅巳申、丑戌未、子卯）
        dizhi_list = [self.get_palace_dizhi(p) for p in range(1, 10) if p != 5]
        sanxing_sets = [{'寅', '巳', '申'}, {'丑', '戌', '未'}, {'子', '卯'}]

        for sanxing in sanxing_sets:
            if sanxing.issubset(set(dizhi_list)):
                self.patterns.append(f"\033[31m全局: 【三刑】{''.join(sanxing)}相刑（凶）→ 易生纠纷官非\033[0m")

    def _check_special_combinations(self):
        """检查特殊组合格局（类内部方法）"""
        celestial_gan = self.main_pan.get('celestial_gan', [])

        # 青龙返首（戊+丙）
        has_dragon = False
        for i, gan in enumerate(celestial_gan):
            palace = i + 1
            if gan == '戊' and '丙' in self.earthly_pan.get(palace, ""):
                has_dragon = True
        if has_dragon:
            self.patterns.append("\033[1;32m全局: 【青龙返首】戊+丙（大吉）→ 万事亨通，逢凶化吉\033[0m")

        # 朱雀投江（丁+癸）
        has_phoenix = False
        for i, gan in enumerate(celestial_gan):
            palace = i + 1
            if gan == '丁' and '癸' in self.earthly_pan.get(palace, ""):
                has_phoenix = True
        if has_phoenix:
            self.patterns.append("\033[31m全局: 【朱雀投江】丁+癸（凶）→ 文书口舌，音信沉溺\033[0m")

        # 蛇夭矫（癸+丁）
        has_snake = False
        for i, gan in enumerate(celestial_gan):
            palace = i + 1
            if gan == '癸' and '丁' in self.earthly_pan.get(palace, ""):
                has_snake = True
        if has_snake:
            self.patterns.append("\033[31m全局: 【腾蛇夭矫】癸+丁（凶）→ 虚惊不宁，文书官司\033[0m")

    def _check_shensha_patterns(self):
        """检查全局神煞格局（类内部方法）"""
        # 贵人格局（天乙贵人+值符）
        has_tianyi = False
        has_zhifu = False

        for palace in range(1, 10):
            shensha_list = self.shensha_per_palace.get(palace, [])
            if '天乙贵人' in shensha_list:
                has_tianyi = True

            # 检查八神盘中的值符
            gods = self.main_pan.get('god_pan', [])
            if palace <= len(gods) and gods[palace - 1] == '值符':
                has_zhifu = True

        if has_tianyi and has_zhifu:
            self.patterns.append("\033[1;32m全局: 【贵人拱照】天乙贵人+值符（大吉）→ 得贵人助力，诸事顺遂\033[0m")

        # 凶煞汇聚（白虎+腾蛇+玄武）
        evil_count = 0
        for palace in range(1, 10):
            shensha_list = self.shensha_per_palace.get(palace, [])
            gods = self.main_pan.get('god_pan', [])

            if palace <= len(gods):
                god = gods[palace - 1]
                if '白虎' in shensha_list or god == '白虎':
                    evil_count += 1
                if god == '腾蛇':
                    evil_count += 1
                if god == '玄武':
                    evil_count += 1

        if evil_count >= 3:
            self.patterns.append("\033[31m全局: 【凶煞汇聚】白虎+腾蛇+玄武（大凶）→ 多灾多难，需化解\033[0m")


    def calculate_angan(self):
        """计算暗干（隐干）分布"""
        # 1. 获取时干
        hour_ganzhi = self.calculate_hour_ganzhi()
        hour_gan = hour_ganzhi[0]

        # 2. 暗干排布规则：时干加在地盘时干所在宫位
        angan_pan = {}  # {宫位: 暗干}

        # 3. 找到地盘时干所在宫位
        for palace, earthly in self.earthly_pan.items():
            if hour_gan in earthly:
                # 4. 从该宫位开始，按阳顺阴逆排布天干
                tiangan_order = "甲乙丙丁戊己庚辛壬癸"
                start_idx = tiangan_order.index(hour_gan)

                # 确定排布方向
                step = 1 if self.yin_yang == "阳遁" else -1

                # 排布顺序（跳过中五宫）
                palace_order = [1, 8, 3, 4, 9, 2, 7, 6]

                # 找到起始宫位在顺序中的位置
                try:
                    start_pos = palace_order.index(palace)
                except ValueError:
                    # 中五宫情况
                    if palace == 5:
                        start_pos = palace_order.index(self.central_palace_host)
                    else:
                        start_pos = 0

                # 排布暗干
                for i in range(8):
                    current_palace = palace_order[(start_pos + i * step) % 8]
                    gan_idx = (start_idx + i) % 10
                    angan_pan[current_palace] = tiangan_order[gan_idx]

        return angan_pan

    def check_hour_luck(self):
        """时辰吉凶判断（专业版）"""
        hour_ganzhi = self.calculate_hour_ganzhi()
        tiangan, dizhi = hour_ganzhi[0], hour_ganzhi[1]

        # 五不遇时（时干克日干）
        day_gan = self.day_ganzhi[0]
        clash_map = {
            '甲': '庚', '乙': '辛', '丙': '壬',
            '丁': '癸', '戊': '甲', '己': '乙',
            '庚': '丙', '辛': '丁', '壬': '戊', '癸': '己'
        }
        if clash_map.get(day_gan) == tiangan:
            self.patterns.append("五不遇时（大凶）")

        # 天乙贵人（时辰地支对应）
        noble_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }
        if dizhi in noble_map.get(tiangan, []):
            self.patterns.append("天乙贵人（吉）")



    def analyze_patterns(self):
        """分析吉凶格局"""

        # 叠加伏吟/反吟的吉凶权重
            # 检查是否有"吉"的格局描述
        if self.star_fan and any('吉' in p for p in self.patterns):  # 修复这里
            self.patterns.append("星反吟但有吉格，凶中有救")

        # 检查是否有"凶"的格局描述
        if self.star_fan and any('凶' in p for p in self.patterns):  # 修复这里
            self.patterns.append("星反吟加凶格，雪上加霜")

    def analyze_ten_gan_response(self):
        """分析十干克应格局并存储到self.sgky"""
        # 十干克应格局定义表（先实现10组）
        gan_patterns = {
            # 三奇特殊格局
            ("丙", "戊"): {"name": "飞鸟跌穴", "luck": "大吉", "desc": "百事可为，事半功倍"},
            ("丁", "癸"): {"name": "朱雀投江", "luck": "凶", "desc": "文书官司，音信沉溺"},
            ("乙", "庚"): {"name": "日奇被刑", "luck": "凶", "desc": "夫妻矛盾，合作破裂"},

            # 六仪特殊格局
            ("戊", "丙"): {"name": "青龙返首", "luck": "大吉", "desc": "柳暗花明，转危为安"},
            ("庚", "戊"): {"name": "天乙伏宫", "luck": "凶", "desc": "破财伤身，换地方可解"},
            ("壬", "戊"): {"name": "小蛇化龙", "luck": "吉", "desc": "平民发迹，寒门将贵"},
            ("辛", "戊"): {"name": "困龙被伤", "luck": "凶", "desc": "官司破财，屈抑难伸"},

            # 伏吟/反吟格
            ("戊", "戊"): {"name": "伏吟", "luck": "平", "desc": "静守为佳，动则招咎"},
            ("癸", "癸"): {"name": "天网四张", "luck": "凶", "desc": "病讼缠身，出行有殃"},

            # 特殊组合
            ("庚", "庚"): {"name": "战格", "luck": "凶", "desc": "官灾横祸，兄弟失和"},

            # 三奇组合扩展
            ("乙", "丙"): {"name": "奇仪顺遂", "luck": "吉", "desc": "贵人相助，谋事可成"},
            ("乙", "丁"): {"name": "奇仪相佐", "luck": "吉", "desc": "文书吉利，百事可为"},
            ("丙", "乙"): {"name": "日月并行", "luck": "吉", "desc": "公谋私利皆吉"},
            ("丙", "丁"): {"name": "星随月转", "luck": "吉", "desc": "贵人提拔，升迁有利"},
            ("丁", "乙"): {"name": "玉女奇生", "luck": "吉", "desc": "贵人恩宠，机缘巧合"},
            ("丁", "丙"): {"name": "星随月转", "luck": "吉", "desc": "贵人相助，乐极生悲"},

            # 六仪组合扩展
            ("戊", "丁"): {"name": "青龙耀明", "luck": "吉", "desc": "求名求利，洞房花烛"},
            ("己", "戊"): {"name": "犬遇青龙", "luck": "吉", "desc": "贵人提携，常人吉利"},
            ("庚", "丙"): {"name": "太白入荧", "luck": "凶", "desc": "贼必来，主破财"},
            ("庚", "丁"): {"name": "亭亭之格", "luck": "平", "desc": "因私暱起官司，门吉有救"},
            ("辛", "丙"): {"name": "干合悖师", "luck": "凶", "desc": "门吉则事吉，门凶则事凶"},
            ("壬", "丙"): {"name": "水蛇入火", "luck": "凶", "desc": "官灾刑禁，祸不单行"},
            ("癸", "戊"): {"name": "天乙会合", "luck": "吉", "desc": "婚姻财喜，吉人赞助"},

            # 特殊凶格
            ("乙", "辛"): {"name": "青龙逃走", "luck": "凶", "desc": "人亡财破，奴仆拐带"},
            ("辛", "乙"): {"name": "白虎猖狂", "luck": "大凶", "desc": "家破人亡，远行多灾"},
            ("丁", "己"): {"name": "火入勾陈", "luck": "凶", "desc": "奸私仇冤，事因女人"},
            ("己", "丁"): {"name": "朱雀入墓", "luck": "凶", "desc": "文书口舌，音信沉溺"},
            ("癸", "丁"): {"name": "腾蛇夭矫", "luck": "凶", "desc": "文书官司，难逃火焚"},
            ("壬", "辛"): {"name": "腾蛇相缠", "luck": "凶", "desc": "纵得吉门，亦不能安"},

            # 三奇与六仪深度组合
            ("乙", "戊"): {"name": "利阴害阳", "luck": "凶", "desc": "门凶事更凶，宜守旧"},
            ("乙", "己"): {"name": "日奇入墓", "luck": "凶", "desc": "被土暗昧，门凶事必凶"},
            ("乙", "壬"): {"name": "日奇入地", "luck": "凶", "desc": "尊卑悖乱，官讼是非"},
            ("丙", "己"): {"name": "火悖入刑", "luck": "凶", "desc": "囚人刑杖，文书不行"},
            ("丙", "庚"): {"name": "荧入太白", "luck": "凶", "desc": "门户破败，盗贼耗失"},
            ("丙", "辛"): {"name": "月奇相合", "luck": "吉", "desc": "谋事能成，病人不凶"},
            ("丁", "戊"): {"name": "青龙转光", "luck": "吉", "desc": "官人升迁，常人威昌"},
            ("丁", "庚"): {"name": "玉女刑杀", "luck": "凶", "desc": "文书阻隔，行人必归"},
            ("丁", "辛"): {"name": "朱雀入狱", "luck": "凶", "desc": "罪人释囚，官人失位"},

            # 六仪特殊互动
            ("戊", "己"): {"name": "贵人入狱", "luck": "凶", "desc": "公私皆不利"},
            ("戊", "庚"): {"name": "值符飞宫", "luck": "凶", "desc": "吉事不吉，凶事更凶"},
            ("戊", "辛"): {"name": "青龙折足", "luck": "凶", "desc": "吉门有生助尚可谋为"},
            ("己", "丙"): {"name": "火孛地户", "luck": "凶", "desc": "男人冤冤相害"},
            ("己", "己"): {"name": "地户逢鬼", "luck": "凶", "desc": "病者必死，百事不遂"},
            ("己", "庚"): {"name": "利格反名", "luck": "凶", "desc": "词讼先动者不利"},
            ("庚", "己"): {"name": "官符刑格", "luck": "凶", "desc": "官司被重刑"},
            ("庚", "辛"): {"name": "白虎干格", "luck": "凶", "desc": "远行不利，车折马死"},
            ("庚", "壬"): {"name": "金化水流", "luck": "凶", "desc": "远行迷路，男女音信茫然"},

            # 壬癸水系列
            ("壬", "己"): {"name": "凶蛇入狱", "luck": "凶", "desc": "大祸将至，顺守可吉"},
            ("壬", "庚"): {"name": "太白擒蛇", "luck": "平", "desc": "刑狱公平，立判邪正"},
            ("壬", "壬"): {"name": "蛇入地网", "luck": "凶", "desc": "外人缠绕，内事索索"},
            ("壬", "癸"): {"name": "阴阳重地", "luck": "凶", "desc": "主有家丑外扬之事"},
            ("癸", "乙"): {"name": "华盖逢星", "luck": "平", "desc": "贵人禄位，常人平安"},
            ("癸", "丙"): {"name": "华盖孛师", "luck": "凶", "desc": "贵贱逢之皆不利"},
            ("癸", "己"): {"name": "华盖地户", "luck": "凶", "desc": "音信阻隔，男女占之皆凶"},
            ("癸", "庚"): {"name": "太白入网", "luck": "凶", "desc": "争讼力平，自罹罪责"},
            ("癸", "辛"): {"name": "网盖天牢", "luck": "凶", "desc": "占病占讼大凶"},

            # 特殊伏吟组合
            ("乙", "乙"): {"name": "日奇伏吟", "luck": "平", "desc": "不宜谒贵求名，只宜安分"},
            ("丙", "丙"): {"name": "月奇悖师", "luck": "凶", "desc": "文书逼迫，破耗遗失"},
            ("丁", "丁"): {"name": "奇入太阴", "luck": "吉", "desc": "文书即至，喜事遂心"},
        }

        self.sgky = []  # 重置结果



        # 遍历9个宫位
        for palace in range(1, 10):
            # 获取天盘干和地盘干

            c_gan = self.main_pan['celestial_gan'][palace - 1]
            e_gan = self._extract_primary_gan(self.earthly_pan.get(palace, ""))

            # 查找匹配格局

            pattern = gan_patterns.get((c_gan, e_gan))

            # 构建结果字典
            result = {
                "宫位": palace,
                "天盘干": c_gan,
                "地盘干": e_gan,
                "格局名称": "普通组合",
                "吉凶": "平",
                "解释": "无明显特殊格局"
            }

            # 若找到预定义格局则更新
            if pattern:
                result.update({
                    "格局名称": pattern['name'],
                    "吉凶": pattern['luck'],
                    "解释": pattern['desc']
                })
            self.sgky.append(result)



# 专业排盘验证
qimen_pro = QiMenCalculator(
    year=year,
    month=month,
    day=day,
    hour=hour,
    latitude=lat,
    longitude=lon,
    strict_mode=False  # 设置为False避免严格模式报错
)


# print('系统角色扮演：')
# print(role)

qimen_pro.display()

print("")
print("用户问题：")
print(user_question)

print('系统回答要求：')
print(response)

