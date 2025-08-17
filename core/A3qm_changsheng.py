class ChangShengCalculator:
    """干支长生状态计算器（遵循《御定奇门宝鉴》理论）"""

    def __init__(self, base_result):
        self.base_result = base_result

        # 识别寄宫关系（中五宫寄在其他宫位）
        self.ji_palace = self._detect_ji_palace()
        print(f"识别到寄宫关系：中五宫寄在{self.ji_palace}宫")

        # 宫位地支映射（主气地支） - 考虑寄宫
        self.palace_branches = self._get_palace_branches_with_ji()

        # 天干五行阴阳属性
        self.gan_properties = {
            '甲': ('木', '阳'), '乙': ('木', '阴'),
            '丙': ('火', '阳'), '丁': ('火', '阴'),
            '戊': ('土', '阳'), '己': ('土', '阴'),
            '庚': ('金', '阳'), '辛': ('金', '阴'),
            '壬': ('水', '阳'), '癸': ('水', '阴')
        }

        # 修正：五行长生起始位（根据图片）
        self.changsheng_start = {
            '甲': '亥', '乙': '午',  # 木
            '丙': '寅', '丁': '酉',  # 火
            '戊': '寅', '己': '酉',  # 土
            '庚': '巳', '辛': '子',  # 金
            '壬': '申', '癸': '卯'  # 水
        }

        # 长生十二神序列
        self.stages = ["长生", "沐浴", "冠带", "临官", "帝旺",
                       "衰", "病", "死", "墓", "绝", "胎", "养"]

        # 地支顺序（固定）
        self.branches_order = ["子", "丑", "寅", "卯", "辰", "巳",
                               "午", "未", "申", "酉", "戌", "亥"]

    def _detect_ji_palace(self):
        """检测中五宫寄在哪个宫位"""
        # 1. 优先检查天盘寄宫信息
        tian_pan = self.base_result.get('天盘', {})
        for palace, gan in tian_pan.items():
            if isinstance(gan, str) and '/' in gan and palace != 5:
                return palace

        # 2. 检查地盘寄宫信息
        di_pan = self.base_result.get('地盘带寄宫', {})
        if di_pan.get(2) and isinstance(di_pan[2], list) and len(di_pan[2]) > 1:
            return 2

        # 默认寄坤二宫
        return 2

    def _get_palace_branches_with_ji(self):
        """获取考虑寄宫关系的宫位地支映射"""
        # 基本宫位地支
        branches = {
            1: "子",  # 坎宫
            2: "申",  # 坤宫（主气申）
            3: "卯",  # 震宫
            4: "巳",  # 巽宫（主气巳）
            5: "申",  # 中宫寄坤（同坤宫）-> 实际使用寄宫地支
            6: "亥",  # 乾宫（主气亥）
            7: "酉",  # 兑宫
            8: "寅",  # 艮宫（主气寅）
            9: "午"  # 离宫
            }

        # 更新中五宫的实际地支（使用寄宫地支）
        if self.ji_palace in branches:
            branches[5] = branches[self.ji_palace]
        else:
            branches[5] = "申"  # 默认坤宫地支

        return branches

    def _get_actual_gans(self, palace, gan_type):
        """获取实际的天干列表（处理寄宫关系）"""
        if gan_type == '天盘':
            gan_data = self.base_result.get('天盘', {})
        else:  # 地盘
            gan_data = self.base_result.get('地盘带寄宫', {})

        # 获取原始数据
        raw_gan = gan_data.get(palace, "无")
        gans = []

        # 处理字符串格式的寄宫数据（如"辛/戊"）
        if isinstance(raw_gan, str) and '/' in raw_gan:
            gans = raw_gan.split('/')
        # 处理列表格式的寄宫数据
        elif isinstance(raw_gan, list):
            gans = raw_gan
        # 处理普通单一值
        else:
            gans = [raw_gan]

        # 处理中五宫的寄宫情况
        if palace == 5:
            # 中五宫的天干实际存储在寄宫位置
            ji_data = gan_data.get(self.ji_palace, "无")
            ji_gans = []

            if isinstance(ji_data, str) and '/' in ji_data:
                ji_gans = ji_data.split('/')
            elif isinstance(ji_data, list):
                ji_gans = ji_data
            else:
                ji_gans = [ji_data]

            # 只取寄宫部分（通常是第二部分）
            if len(ji_gans) > 1:
                gans = [ji_gans[1]]  # 寄宫干
            elif ji_gans:
                gans = [ji_gans[0]]
        # 处理寄宫目标宫位（如坤二宫或7宫）
        elif palace == self.ji_palace:
            # 保留所有天干（本宫干和寄宫干）
            pass

        return gans

    def _calculate_changsheng(self, gan, yinyang_dun):
        """计算指定天干的长生状态（内部方法）"""
        # 获取天干属性
        if gan not in self.gan_properties:
            return {}

        # 确定起始长生位（根据图片修正）
        start_branch = self.changsheng_start[gan]

        # 构建长生序列（阳顺阴逆）
        start_idx = self.branches_order.index(start_branch)
        if self.gan_properties[gan][1] == '阳':  # 阳干
            # 阳干顺行
            rotated = self.branches_order[start_idx:] + self.branches_order[:start_idx]
        else:  # 阴干
            # 阴干逆行（根据图片修正）
            reversed_order = self.branches_order[::-1]
            reverse_start_idx = reversed_order.index(start_branch)
            rotated = reversed_order[reverse_start_idx:] + reversed_order[:reverse_start_idx]

        # 计算各宫位状态
        changsheng_results = {}
        for palace, branch in self.palace_branches.items():
            try:
                stage_idx = rotated.index(branch)
                changsheng_results[palace] = self.stages[stage_idx]
            except ValueError:
                changsheng_results[palace] = "未知"

        return changsheng_results

    def _find_gan_palace(self, gan):
        """查找天干在天盘中的宫位（考虑寄宫）"""
        for palace in range(1, 10):
            actual_gans = self._get_actual_gans(palace, '天盘')
            if gan in actual_gans:
                return palace
        return None

    def calculate_ri_gan(self):
        """计算日干长生状态"""
        ri_gan = self.base_result['四柱']['日柱'][0]  # 日干
        yinyang_dun = self.base_result['阴阳遁']

        # 计算各宫状态
        changsheng_results = self._calculate_changsheng(ri_gan, yinyang_dun)

        # 查找日干所在宫位
        ri_gan_palace = self._find_gan_palace(ri_gan)

        return {
            '日干': ri_gan,
            '五行': self.gan_properties[ri_gan][0],
            '阴阳': self.gan_properties[ri_gan][1],
            '长生位': self.changsheng_start[ri_gan],
            '各宫状态': changsheng_results,
            '宫位': ri_gan_palace,
            '状态': changsheng_results.get(ri_gan_palace, "未知") if ri_gan_palace else "未知"
        }

    def calculate_shi_gan(self):
        """计算时干长生状态"""
        shi_gan = self.base_result['四柱']['时柱'][0]  # 时干
        yinyang_dun = self.base_result['阴阳遁']

        # 计算各宫状态
        changsheng_results = self._calculate_changsheng(shi_gan, yinyang_dun)

        # 查找时干所在宫位
        shi_gan_palace = self._find_gan_palace(shi_gan)

        return {
            '时干': shi_gan,
            '五行': self.gan_properties[shi_gan][0],
            '阴阳': self.gan_properties[shi_gan][1],
            '长生位': self.changsheng_start[shi_gan],
            '各宫状态': changsheng_results,
            '宫位': shi_gan_palace,
            '状态': changsheng_results.get(shi_gan_palace, "未知") if shi_gan_palace else "未知"
        }

    def calculate_yue_gan(self):
        """计算月干长生状态"""
        yue_gan = self.base_result['四柱']['月柱'][0]  # 月干
        yinyang_dun = self.base_result['阴阳遁']

        # 计算各宫状态
        changsheng_results = self._calculate_changsheng(yue_gan, yinyang_dun)

        # 查找月干所在宫位
        yue_gan_palace = self._find_gan_palace(yue_gan)

        return {
            '天干': yue_gan,
            '五行': self.gan_properties[yue_gan][0],
            '阴阳': self.gan_properties[yue_gan][1],
            '长生位': self.changsheng_start[yue_gan],
            '各宫状态': changsheng_results,
            '宫位': yue_gan_palace,
            '状态': changsheng_results.get(yue_gan_palace, "未知") if yue_gan_palace else "未知"
        }

    def calculate_nian_gan(self):
        """计算年干长生状态"""
        nian_gan = self.base_result['四柱']['年柱'][0]  # 年干
        yinyang_dun = self.base_result['阴阳遁']

        # 计算各宫状态
        changsheng_results = self._calculate_changsheng(nian_gan, yinyang_dun)

        # 查找年干所在宫位
        nian_gan_palace = self._find_gan_palace(nian_gan)

        return {
            '天干': nian_gan,
            '五行': self.gan_properties[nian_gan][0],
            '阴阳': self.gan_properties[nian_gan][1],
            '长生位': self.changsheng_start[nian_gan],
            '各宫状态': changsheng_results,
            '宫位': nian_gan_palace,
            '状态': changsheng_results.get(nian_gan_palace, "未知") if nian_gan_palace else "未知"
        }

    def generate_analysis(self, changsheng_result):
        """生成长生状态综合分析报告（遵循《奇门法窍》）"""
        # 获取各干状态
        nian = changsheng_result['年干']['状态']
        yue = changsheng_result['月干']['状态']
        ri = changsheng_result['日干']['状态']
        shi = changsheng_result['时干']['状态']

        # 吉凶判断规则
        favorable = ["长生", "冠带", "临官", "帝旺"]
        neutral = ["养", "胎", "沐浴"]
        unfavorable = ["衰", "病", "死", "墓", "绝"]

        # 核心判断：日干为体，时干为用
        analysis = "【长生状态分析】\n"
        analysis += f"日干（体）状态: {ri}\n"
        analysis += f"时干（用）状态: {shi}\n"

        # 日时关系判断
        if ri in favorable and shi in favorable:
            analysis += "→ 体用皆旺，大吉之象（主事体顺利，发展迅速）\n"
        elif ri in favorable and shi in unfavorable:
            analysis += "→ 体旺用衰，先吉后凶（主开始顺利但后续乏力）\n"
        elif ri in unfavorable and shi in favorable:
            analysis += "→ 体衰用旺，先凶后吉（主开始困难但结果向好）\n"
        elif ri in unfavorable and shi in unfavorable:
            analysis += "→ 体用皆衰，事多阻碍（主全程困难，需谨慎行事）\n"
        else:
            analysis += "→ 体用状态复杂，需结合其他因素判断\n"

        # 年月影响分析
        analysis += f"\n年干（根基）状态: {nian}"
        if nian in favorable:
            analysis += " → 根基稳固，长期有利"
        elif nian in unfavorable:
            analysis += " → 根基不稳，长期不利"
        analysis += f"\n月干（时运）状态: {yue}"
        if yue in favorable:
            analysis += " → 时运助力，近期有利"
        elif yue in unfavorable:
            analysis += " → 时运不济，近期不利"

        # 特殊状态提醒
        if ri == "死" or shi == "死":
            analysis += "\n\n⚠️ 注意：有'死'状态出现，主事体停滞或终结"
        if ri == "墓" or shi == "墓":
            analysis += "\n\n⚠️ 注意：有'墓'状态出现，主事体受困或隐藏"
        if ri == "绝" or shi == "绝":
            analysis += "\n\n⚠️ 注意：有'绝'状态出现，主事体断绝或极端变化"

        # 综合建议
        analysis += "\n\n【综合分析建议】"
        if ri in favorable and shi in favorable:
            analysis += "\n- 天时地利人和俱备，宜积极进取"
        elif ri in unfavorable and shi in unfavorable:
            analysis += "\n- 内外交困，宜保守防御或另寻时机"
        else:
            analysis += "\n- 吉凶参半，需审时度势，灵活应对"

        return analysis

    def _calculate_changsheng_for_gan_at_branch(self, gan, branch, yinyang_dun):
        """计算指定天干在指定地支上的长生状态（修正版）"""
        if gan not in self.gan_properties or gan == "无":
            return "无"

        # 确定起始长生位（根据图片修正）
        start_branch = self.changsheng_start[gan]

        # 构建长生序列（阳顺阴逆）
        start_idx = self.branches_order.index(start_branch)
        if self.gan_properties[gan][1] == '阳':  # 阳干
            # 阳干顺行
            rotated = self.branches_order[start_idx:] + self.branches_order[:start_idx]
        else:  # 阴干
            # 阴干逆行（根据图片修正）
            reversed_order = self.branches_order[::-1]
            reverse_start_idx = reversed_order.index(start_branch)
            rotated = reversed_order[reverse_start_idx:] + reversed_order[:reverse_start_idx]

        try:
            stage_idx = rotated.index(branch)
            return self.stages[stage_idx]
        except:
            return "未知"

    def calculate(self):
        """计算四柱天干长生状态并生成分析报告"""
        changsheng_result = {
            '年干': self.calculate_nian_gan(),
            '月干': self.calculate_yue_gan(),
            '日干': self.calculate_ri_gan(),
            '时干': self.calculate_shi_gan()
        }

        # 生成分析报告
        analysis_report = self.generate_analysis(changsheng_result)

        # 将分析报告加入结果
        changsheng_result['分析报告'] = analysis_report

        #############################
        # 打印天盘地盘长生状态（修正版） #
        #############################
        print("\n=== 天盘干与地盘干长生状态（考虑寄宫） ===")
        yinyang_dun = self.base_result['阴阳遁']

        # 遍历1-9宫
        palaces = sorted(self.palace_branches.keys())
        for palace in palaces:
            branch = self.palace_branches[palace]

            # 获取实际天干列表（考虑寄宫）
            tian_gans = self._get_actual_gans(palace, '天盘')
            di_gans = self._get_actual_gans(palace, '地盘')

            # 计算并格式化天盘干状态
            tian_parts = []
            for gan in tian_gans:
                if gan != "无":
                    stage = self._calculate_changsheng_for_gan_at_branch(gan, branch, yinyang_dun)
                    tian_parts.append(f"{gan}({stage})")
            tian_str = "/".join(tian_parts) if tian_parts else "无"

            # 计算并格式化地盘干状态
            di_parts = []
            for gan in di_gans:
                if gan != "无":
                    stage = self._calculate_changsheng_for_gan_at_branch(gan, branch, yinyang_dun)
                    di_parts.append(f"{gan}({stage})")
            di_str = "/".join(di_parts) if di_parts else "无"

            # 特殊标记寄宫关系
            ji_note = ""
            if palace == 5:
                ji_note = f"（寄{self.ji_palace}宫）"
            elif palace == self.ji_palace:
                ji_note = f"（含寄宫）"

            # 打印当前宫位信息
            print(f"宫位{palace}{ji_note}（{branch}）: "
                  f"天盘干={tian_str} "
                  f"地盘干={di_str}")

        return changsheng_result
