class DirectionCalculator:
    """奇门遁甲方位增强计算器（含24山向）"""

    # 九宫方位映射（洛书九宫）
    PALACE_DIRECTIONS = {
        1: "北", 2: "西南", 3: "东", 4: "东南",
        5: "中", 6: "西北", 7: "西", 8: "东北", 9: "南"
    }

    # 24山向定义（360度划分）
    MOUNTAIN_DIRECTIONS = {
        # 角度范围: (山向名称, 八卦方位, 地支)
        (0, 15): ("壬", "坎", None),
        (15, 30): ("子", "坎", "子"),
        (30, 45): ("癸", "坎", None),
        (45, 60): ("丑", "艮", "丑"),
        (60, 75): ("艮", "艮", None),
        (75, 90): ("寅", "艮", "寅"),
        (90, 105): ("甲", "震", None),
        (105, 120): ("卯", "震", "卯"),
        (120, 135): ("乙", "震", None),
        (135, 150): ("辰", "巽", "辰"),
        (150, 165): ("巽", "巽", None),
        (165, 180): ("巳", "巽", "巳"),
        (180, 195): ("丙", "离", None),
        (195, 210): ("午", "离", "午"),
        (210, 225): ("丁", "离", None),
        (225, 240): ("未", "坤", "未"),
        (240, 255): ("坤", "坤", None),
        (255, 270): ("申", "坤", "申"),
        (270, 285): ("庚", "兑", None),
        (285, 300): ("酉", "兑", "酉"),
        (300, 315): ("辛", "兑", None),
        (315, 330): ("戌", "乾", "戌"),
        (330, 345): ("乾", "乾", None),
        (345, 360): ("亥", "乾", "亥")
    }

    # 八卦方位映射
    BAGUA_DIRECTIONS = {
        "坎": "北", "艮": "东北", "震": "东", "巽": "东南",
        "离": "南", "坤": "西南", "兑": "西", "乾": "西北"
    }

    def __init__(self, base_result):
        """
        初始化方位计算器
        :param base_result: 奇门遁甲基础排盘结果
        """
        self.base_result = base_result

    def get_palace_direction(self, palace):
        """
        获取宫位的基本方位
        :param palace: 宫位编号(1-9)
        :return: 方位字符串
        """
        return self.PALACE_DIRECTIONS.get(palace, "未知方位")

    def calculate_24_mountains(self, angle=None):
        """
        计算24山向方位
        :param angle: 可选的角度值(0-360度)，不提供则返回所有宫位信息
        :return: 24山向信息
        """
        if angle is not None:
            # 计算单个角度的24山向
            return self._get_mountain_by_angle(angle)
        else:
            # 为所有宫位计算方位信息
            return self._get_all_palace_directions()

    def _get_mountain_by_angle(self, angle):
        """根据角度获取24山向信息"""
        # 确保角度在0-360范围内
        normalized_angle = angle % 360

        # 查找对应的山向
        for (start, end), (name, bagua, dz) in self.MOUNTAIN_DIRECTIONS.items():
            if start <= normalized_angle < end:
                return {
                    "角度": angle,
                    "山向": name,
                    "八卦": bagua,
                    "地支": dz,
                    "方位": self.BAGUA_DIRECTIONS.get(bagua, "未知")
                }

        # 默认返回（理论上不会执行到这里）
        return {"角度": angle, "山向": "未知", "八卦": "未知", "地支": None, "方位": "未知"}

    def _get_all_palace_directions(self):
        """获取所有宫位的详细方位信息"""
        palace_info = {}

        for palace in range(1, 10):
            # 基本方位
            basic_dir = self.get_palace_direction(palace)

            # 计算24山向（每个宫位45度范围）
            start_angle = (palace - 1) * 40  # 宫位起始角度
            center_angle = (palace - 1) * 40 + 20  # 宫位中心角度

            # 获取宫位中心的24山向
            mountain_info = self._get_mountain_by_angle(center_angle)

            # 获取宫位对应的三个山向
            mountain_range = self._get_mountains_for_palace(palace)

            palace_info[palace] = {
                "宫位": palace,
                "基本方位": basic_dir,
                "中心方位": mountain_info,
                "山向范围": mountain_range,
                "八卦": self._get_bagua_for_palace(palace),
                "地支": self._get_dizhi_for_palace(palace)
            }

        return palace_info

    def _get_mountains_for_palace(self, palace):
        """获取宫位对应的三个山向"""
        # 宫位与24山向的映射关系
        palace_mountains = {
            1: ["壬", "子", "癸"],  # 坎宫（北）
            2: ["未", "坤", "申"],  # 坤宫（西南）
            3: ["甲", "卯", "乙"],  # 震宫（东）
            4: ["辰", "巽", "巳"],  # 巽宫（东南）
            5: ["无"],  # 中宫（特殊处理）
            6: ["戌", "乾", "亥"],  # 乾宫（西北）
            7: ["庚", "酉", "辛"],  # 兑宫（西）
            8: ["丑", "艮", "寅"],  # 艮宫（东北）
            9: ["丙", "午", "丁"]  # 离宫（南）
        }
        return palace_mountains.get(palace, [])

    def _get_bagua_for_palace(self, palace):
        """获取宫位对应的八卦"""
        palace_bagua = {
            1: "坎", 2: "坤", 3: "震", 4: "巽",
            5: "中", 6: "乾", 7: "兑", 8: "艮", 9: "离"
        }
        return palace_bagua.get(palace, "未知")

    def _get_dizhi_for_palace(self, palace):
        """获取宫位对应的地支"""
        palace_dizhi = {
            1: "子", 2: ["未", "申"], 3: "卯", 4: ["辰", "巳"],
            5: "无", 6: ["戌", "亥"], 7: "酉", 8: ["丑", "寅"], 9: "午"
        }
        return palace_dizhi.get(palace, "未知")

    def enhance_pan_info(self):
        """增强排盘信息，添加方位数据"""
        # 获取所有宫位的方位信息
        direction_info = self._get_all_palace_directions()

        # 添加到基础结果中
        self.base_result['24山向方位信息'] = direction_info

        # 为每个宫位的排盘信息添加方位数据
        for palace, info in self.base_result.get('宫位布局', {}).items():
            if palace in direction_info:
                info['方位'] = direction_info[palace]

        return self.base_result
