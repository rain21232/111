class ShenShaCalculator:
    """专业神煞计算系统（时家奇门专用）"""

    def __init__(self, year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi):
        # 基础参数
        self.year_gan = year_ganzhi[0]  # 年干
        self.year_zhi = year_ganzhi[1]  # 年支
        self.month_zhi = month_ganzhi[1]  # 月支
        self.day_gan = day_ganzhi[0]  # 日干
        self.day_zhi = day_ganzhi[1]  # 日支
        self.hour_zhi = hour_ganzhi[1]  # 时支
        self.day_ganzhi = day_ganzhi  # 完整的日干支



    def get_all_shensha(self):
        """返回所有神煞的计算方法"""
        return {
            "天乙贵人": self.tianyi_guiren(),
            "文昌贵人": self.wenchang_guiren(),
            "桃花": self.taohua(),
            "劫煞": self.jiesha(),
            "灾煞": self.zaisha(),
            "孤辰": self.guchen(),
            "寡宿": self.guasu(),
            "华盖": self.huagai(),
            "天德": self.tiande(),
            "月德": self.yuede(),
            "将星": self.jiangxing(),
            "天医": self.tianyi(),
            "金舆": self.jinyu(),
            "红鸾": self.hongluan(),
            "阴煞": self.yinsha(),
            "丧门": self.sangmen(),
            "吊客": self.diaoke(),
            "白虎": self.baihu(),

            # ====== 新增专业神煞 ======
            "天喜": self.tianxi(),
            "天德合": self.tiandehe(),
            "月德合": self.yuedehe(),
            "截空": self.jiekong(),
            "咸池": self.xianchi(),
            "月空": self.yuekong(),
            "伏吟": self.fuyin(),
            "反吟": self.fanyin(),
            "驿马": self.yima(),
            "天禄": self.tianlu(),
            "五鬼": self.wugui(),
            "勃兰": self.bolan(),
            # ====== 新增10个神煞 ======
            "将军": self.jiangjun(),
            "咸池(日支)": self.xianchi(),
            "天喜(日支)": self.tianxi(),
            "月破": self.yuepo(),
            "天乙": self.tianyi(),
            "太阴": self.taiyin(),
            "流煞": self.liusha(),
            "天官": self.tianguan(),
            "生耗": self.shenghao(),
            "亡神": self.wangshen(),

            # 新增神煞
            "天官贵人": self.tianguan_guiren(),
            "太极贵人": self.taiji_guiren(),
            "福星贵人": self.fuxing_guiren(),
            "天厨贵人": self.tianchu_guiren(),
            "学堂贵人": self.xuetang_guiren(),
            "金匮贵人": self.jinkui_guiren(),
            "血刃煞": self.xueren_sha(),
            "卷舌煞": self.juanshe_sha(),
            "披麻煞": self.pima_sha(),
            "流霞煞": self.liuxia_sha(),

            # ====== 新增神煞 ======
            "国印贵人": self.guoyin_guiren(),
            "学堂": self.xuetang(),
            "词馆": self.ciguan(),
            "羊刃": self.yangren(),
            "飞刃": self.feiren(),
            "勾绞煞": self.gouliao(),
            "孤鸾煞": self.guluansha(),
            "十二月将": self.shieryue(),
            "天禄修正": self.tianlu(),  # 修正版天禄
            "十恶大败": self.shie_dabai(),

            # ====== 新增神煞 ======
            "月德贵": self.yuede_gui(),
            "将星贵": self.jiangxing_gui(),
            "文昌贵": self.wenchang_gui(),
            "红鸾煞": self.hongluan_sha(),
            "天喜煞": self.tianxi_sha(),
        }

    def get_palace_shensha(self, palace_dizhi):
        """获取指定宫位的神煞列表"""
        shensha_list = []
        all_shensha = self.get_all_shensha()

        for name, value in all_shensha.items():
            if isinstance(value, list):
                if palace_dizhi in value:
                    shensha_list.append(name)
            elif palace_dizhi == value:
                shensha_list.append(name)

        return shensha_list

    def yuede_gui(self):
        """月德贵（月支）"""
        yuede_gui_map = {
            '寅': '丙', '卯': '甲', '辰': '壬',
            '巳': '庚', '午': '丙', '未': '甲',
            '申': '壬', '酉': '庚', '戌': '丙',
            '亥': '甲', '子': '壬', '丑': '庚'
        }
        return yuede_gui_map.get(self.month_zhi, '')

    def jiangxing_gui(self):
        """将星贵（日支）"""
        jiangxing_map = {
            '申': '子', '子': '子', '辰': '子',
            '寅': '午', '午': '午', '戌': '午',
            '巳': '酉', '酉': '酉', '丑': '酉',
            '亥': '卯', '卯': '卯', '未': '卯'
        }
        return jiangxing_map.get(self.day_zhi, '')

    def wenchang_gui(self):
        """文昌贵（日干）"""
        wenchang_map = {
            '甲': '巳', '乙': '午', '丙': '申',
            '丁': '酉', '戊': '申', '己': '酉',
            '庚': '亥', '辛': '子', '壬': '寅', '癸': '卯'
        }
        return wenchang_map.get(self.day_gan, '')

    def hongluan_sha(self):
        """红鸾煞（年支）"""
        hongluan_map = {
            '子': '卯', '丑': '寅', '寅': '丑',
            '卯': '子', '辰': '亥', '巳': '戌',
            '午': '酉', '未': '申', '申': '未',
            '酉': '午', '戌': '巳', '亥': '辰'
        }
        return hongluan_map.get(self.year_zhi, '')

    def tianxi_sha(self):
        """天喜煞（年支）"""
        tianxi_map = {
            '子': '酉', '丑': '申', '寅': '未',
            '卯': '午', '辰': '巳', '巳': '辰',
            '午': '卯', '未': '寅', '申': '丑',
            '酉': '子', '戌': '亥', '亥': '戌'
        }
        return tianxi_map.get(self.year_zhi, '')

    # 新增神煞计算方法
    def guoyin_guiren(self):
        """国印贵人（日干）"""
        guoyin_map = {
            '甲': '戌', '乙': '亥', '丙': '丑',
            '丁': '寅', '戊': '丑', '己': '寅',
            '庚': '辰', '辛': '巳', '壬': '未', '癸': '申'
        }
        return guoyin_map.get(self.day_gan, '')

    def xuetang(self):
        """学堂（日干）"""
        xuetang_map = {
            '甲': '亥', '乙': '午', '丙': '寅',
            '丁': '酉', '戊': '寅', '己': '酉',
            '庚': '巳', '辛': '子', '壬': '申', '癸': '卯'
        }
        return xuetang_map.get(self.day_gan, '')

    def ciguan(self):
        """词馆（日干）"""
        ciguan_map = {
            '甲': '寅', '乙': '卯', '丙': '巳',
            '丁': '午', '戊': '巳', '己': '午',
            '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'
        }
        return ciguan_map.get(self.day_gan, '')

    def yangren(self):
        """羊刃（日干）"""
        yangren_map = {
            '甲': '卯', '乙': '寅', '丙': '午',
            '丁': '巳', '戊': '午', '己': '巳',
            '庚': '酉', '辛': '申', '壬': '子', '癸': '亥'
        }
        return yangren_map.get(self.day_gan, '')

    def feiren(self):
        """飞刃（日干）"""
        # 飞刃是羊刃的对冲支
        yangren = self.yangren()
        if not yangren:
            return ''

        # 地支对冲关系
        chong_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        return chong_map.get(yangren, '')

    def gouliao(self):
        """勾绞煞（日支）"""
        gouliao_map = {
            '子': ['酉', '卯'], '丑': ['戌', '辰'],
            '寅': ['亥', '巳'], '卯': ['子', '午'],
            '辰': ['丑', '未'], '巳': ['寅', '申'],
            '午': ['卯', '酉'], '未': ['辰', '戌'],
            '申': ['巳', '亥'], '酉': ['午', '子'],
            '戌': ['未', '丑'], '亥': ['申', '寅']
        }
        return gouliao_map.get(self.day_zhi, [])

    def guluansha(self):
        """孤鸾煞（日柱）"""
        # 使用新添加的 day_ganzhi 属性
        guluan_days = ['乙巳', '丁巳', '辛亥', '戊申', '壬寅', '戊午', '壬子', '丙午']
        return self.day_ganzhi in guluan_days

    def shieryue(self):
        """十二月将（月支）"""
        yuejiang_map = {
            '寅': '功曹', '卯': '太冲', '辰': '天罡',
            '巳': '太乙', '午': '胜光', '未': '小吉',
            '申': '传送', '酉': '从魁', '戌': '河魁',
            '亥': '登明', '子': '神后', '丑': '大吉'
        }
        return yuejiang_map.get(self.month_zhi, '')

    def tianlu(self):
        """天禄（日干）修正版"""
        tianlu_map = {
            '甲': '寅', '乙': '卯', '丙': '巳',
            '丁': '午', '戊': '巳', '己': '午',
            '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'
        }
        return tianlu_map.get(self.day_gan, '')

    def shie_dabai(self):
        """十恶大败（日柱）"""
        dabai_days = [
            '甲辰', '乙巳', '丙申', '丁亥', '戊戌',
            '己丑', '庚辰', '辛巳', '壬申', '癸亥'
        ]
        return self.day_ganzhi in dabai_days

    # 核心神煞计算方法
    def tianyi_guiren(self):
        """天乙贵人（日干）"""
        guiren_map = {
            '甲': ['丑', '未'], '乙': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '戊': ['丑', '未'], '己': ['子', '申'],
            '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }
        return guiren_map.get(self.day_gan, [])

    def wenchang_guiren(self):
        """文昌贵人（日干）"""
        wenchang_map = {
            '甲': '巳', '乙': '午', '丙': '申',
            '丁': '酉', '戊': '申', '己': '酉',
            '庚': '亥', '辛': '子', '壬': '寅', '癸': '卯'
        }
        return wenchang_map.get(self.day_gan, '')

    def taohua(self):
        """桃花（年支）"""
        taohua_map = {
            '申': '酉', '子': '酉', '辰': '酉',
            '寅': '卯', '午': '卯', '戌': '卯',
            '巳': '午', '酉': '午', '丑': '午',
            '亥': '子', '卯': '子', '未': '子'
        }
        return taohua_map.get(self.year_zhi, '')

    def jiesha(self):
        """劫煞（年支）"""
        jiesha_map = {
            '申': '巳', '子': '巳', '辰': '巳',
            '寅': '亥', '午': '亥', '戌': '亥',
            '巳': '寅', '酉': '寅', '丑': '寅',
            '亥': '申', '卯': '申', '未': '申'
        }
        return jiesha_map.get(self.year_zhi, '')

    def zaisha(self):
        """灾煞（年支）"""
        zaisha_map = {
            '申': '午', '子': '午', '辰': '午',
            '寅': '子', '午': '子', '戌': '子',
            '巳': '卯', '酉': '卯', '丑': '卯',
            '亥': '酉', '卯': '酉', '未': '酉'
        }
        return zaisha_map.get(self.year_zhi, '')

    def guchen(self):
        """孤辰（年支）"""
        guchen_map = {
            '亥': '寅', '子': '寅', '丑': '寅',
            '寅': '巳', '卯': '巳', '辰': '巳',
            '巳': '申', '午': '申', '未': '申',
            '申': '亥', '酉': '亥', '戌': '亥'
        }
        return guchen_map.get(self.year_zhi, '')

    def guasu(self):
        """寡宿（年支）"""
        guasu_map = {
            '亥': '戌', '子': '戌', '丑': '戌',
            '寅': '丑', '卯': '丑', '辰': '丑',
            '巳': '辰', '午': '辰', '未': '辰',
            '申': '未', '酉': '未', '戌': '未'
        }
        return guasu_map.get(self.year_zhi, '')

    def huagai(self):
        """华盖（年支）"""
        huagai_map = {
            '申': '辰', '子': '辰', '辰': '辰',
            '寅': '戌', '午': '戌', '戌': '戌',
            '巳': '丑', '酉': '丑', '丑': '丑',
            '亥': '未', '卯': '未', '未': '未'
        }
        return huagai_map.get(self.year_zhi, '')

    def tiande(self):
        """天德（月支）"""
        tiande_map = {
            '寅': '丁', '卯': '申', '辰': '壬',
            '巳': '辛', '午': '亥', '未': '甲',
            '申': '癸', '酉': '寅', '戌': '丙',
            '亥': '乙', '子': '巳', '丑': '庚'
        }
        return tiande_map.get(self.month_zhi, '')

    def yuede(self):
        """月德（月支）"""
        yuede_map = {
            '寅': '丙', '卯': '甲', '辰': '壬',
            '巳': '庚', '午': '丙', '未': '甲',
            '申': '壬', '酉': '庚', '戌': '丙',
            '亥': '甲', '子': '壬', '丑': '庚'
        }
        return yuede_map.get(self.month_zhi, '')

    def jiangxing(self):
        """将星（年支）"""
        jiangxing_map = {
            '申': '子', '子': '子', '辰': '子',
            '寅': '午', '午': '午', '戌': '午',
            '巳': '酉', '酉': '酉', '丑': '酉',
            '亥': '卯', '卯': '卯', '未': '卯'
        }
        return jiangxing_map.get(self.year_zhi, '')

    def tianyi(self):
        """天医（月支）"""
        tianyi_map = {
            '寅': '丑', '卯': '寅', '辰': '卯',
            '巳': '辰', '午': '巳', '未': '午',
            '申': '未', '酉': '申', '戌': '酉',
            '亥': '戌', '子': '亥', '丑': '子'
        }
        return tianyi_map.get(self.month_zhi, '')

    def jinyu(self):
        """金舆（日干）"""
        jinyu_map = {
            '甲': '辰', '乙': '巳', '丙': '未',
            '丁': '申', '戊': '未', '己': '申',
            '庚': '戌', '辛': '亥', '壬': '丑', '癸': '寅'
        }
        return jinyu_map.get(self.day_gan, '')

    def hongluan(self):
        """红鸾（年支）"""
        hongluan_map = {
            '子': '卯', '丑': '寅', '寅': '丑',
            '卯': '子', '辰': '亥', '巳': '戌',
            '午': '酉', '未': '申', '申': '未',
            '酉': '午', '戌': '巳', '亥': '辰'
        }
        return hongluan_map.get(self.year_zhi, '')

    def yinsha(self):
        """阴煞（年支）"""
        yinsha_map = {
            '子': '寅', '丑': '寅', '寅': '子',
            '卯': '子', '辰': '戌', '巳': '戌',
            '午': '申', '未': '申', '申': '午',
            '酉': '午', '戌': '辰', '亥': '辰'
        }
        return yinsha_map.get(self.year_zhi, '')

    def sangmen(self):
        """丧门（年支）"""
        sangmen_map = {
            '子': '寅', '丑': '卯', '寅': '辰',
            '卯': '巳', '辰': '午', '巳': '未',
            '午': '申', '未': '酉', '申': '戌',
            '酉': '亥', '戌': '子', '亥': '丑'
        }
        return sangmen_map.get(self.year_zhi, '')

    def diaoke(self):
        """吊客（年支）"""
        diaoke_map = {
            '子': '戌', '丑': '亥', '寅': '子',
            '卯': '丑', '辰': '寅', '巳': '卯',
            '午': '辰', '未': '巳', '申': '午',
            '酉': '未', '戌': '申', '亥': '酉'
        }
        return diaoke_map.get(self.year_zhi, '')

    def baihu(self):
        """白虎（年支）"""
        baihu_map = {
            '申': '午', '子': '午', '辰': '午',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '戌', '酉': '戌', '丑': '戌',
            '亥': '子', '卯': '子', '未': '子'
        }

    # ====== 新增专业神煞 ======
    def tianxi(self):
        """天喜（年支）"""
        tianxi_map = {
            '子': '酉', '丑': '申', '寅': '未',
            '卯': '午', '辰': '巳', '巳': '辰',
            '午': '卯', '未': '寅', '申': '丑',
            '酉': '子', '戌': '亥', '亥': '戌'
        }
        return tianxi_map.get(self.year_zhi, '')

    def tiandehe(self):
        """天德合（月支）"""
        tiandehe_map = {
            '寅': '壬', '卯': '巳', '辰': '丁',
            '巳': '丙', '午': '寅', '未': '己',
            '申': '戊', '酉': '亥', '戌': '辛',
            '亥': '庚', '子': '申', '丑': '乙'
        }
        return tiandehe_map.get(self.month_zhi, '')

    def yuedehe(self):
        """月德合（月支）"""
        yuedehe_map = {
            '寅': '辛', '卯': '己', '辰': '丁',
            '巳': '乙', '午': '辛', '未': '己',
            '申': '丁', '酉': '乙', '戌': '辛',
            '亥': '己', '子': '丁', '丑': '乙'
        }
        return yuedehe_map.get(self.month_zhi, '')

    def jiekong(self):
        """截空（日干）"""
        jiekong_map = {
            '甲': '申酉', '乙': '午未', '丙': '辰巳',
            '丁': '寅卯', '戊': '子丑', '己': '戌亥',
            '庚': '申酉', '辛': '午未', '壬': '辰巳',
            '癸': '寅卯'
        }
        return jiekong_map.get(self.day_gan, '')

    def xianchi(self):
        """咸池（年支）"""
        xianchi_map = {
            '申': '酉', '子': '酉', '辰': '酉',
            '寅': '卯', '午': '卯', '戌': '卯',
            '巳': '午', '酉': '午', '丑': '午',
            '亥': '子', '卯': '子', '未': '子'
        }
        return xianchi_map.get(self.year_zhi, '')

    def yuekong(self):
        """月空（月支）"""
        yuekong_map = {
            '寅': '壬', '卯': '庚', '辰': '丙',
            '巳': '甲', '午': '壬', '未': '庚',
            '申': '丙', '酉': '甲', '戌': '壬',
            '亥': '庚', '子': '丙', '丑': '甲'
        }
        return yuekong_map.get(self.month_zhi, '')

    def fuyin(self):
        """伏吟（日干）"""
        fuyin_map = {
            '甲': '寅', '乙': '卯', '丙': '巳',
            '丁': '午', '戊': '辰戌', '己': '丑未',
            '庚': '申', '辛': '酉', '壬': '亥',
            '癸': '子'
        }
        return fuyin_map.get(self.day_gan, '')

    def fanyin(self):
        """反吟（日干）"""
        fanyin_map = {
            '甲': '申', '乙': '酉', '丙': '亥',
            '丁': '子', '戊': '寅', '己': '卯',
            '庚': '巳', '辛': '午', '壬': '辰戌',
            '癸': '丑未'
        }
        return fanyin_map.get(self.day_gan, '')

    def yima(self):
        """驿马（日支）"""
        yima_map = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        return yima_map.get(self.day_zhi, '')

    def tianlu(self):
        """天禄（日干）"""
        tianlu_map = {
            '甲': '寅', '乙': '卯', '丙': '巳',
            '丁': '午', '戊': '巳', '己': '午',
            '庚': '申', '辛': '酉', '壬': '亥',
            '癸': '子'
        }
        return tianlu_map.get(self.day_gan, '')

    def wugui(self):
        """五鬼（年支）"""
        wugui_map = {
            '子': '辰', '丑': '卯', '寅': '寅',
            '卯': '丑', '辰': '子', '巳': '亥',
            '午': '戌', '未': '酉', '申': '申',
            '酉': '未', '戌': '午', '亥': '巳'
        }
        return wugui_map.get(self.year_zhi, '')

    def bolan(self):
        """勃兰（日干）"""
        bolan_map = {
            '甲': '卯', '乙': '辰', '丙': '未',
            '丁': '申', '戊': '未', '己': '申',
            '庚': '戌', '辛': '亥', '壬': '丑',
            '癸': '寅'
        }
        return bolan_map.get(self.day_gan, '')

    # ====== 新增10个专业神煞 ======
    def jiangjun(self):
        """将军（年支）"""
        jiangjun_map = {
            '子': '酉', '丑': '子', '寅': '卯',
            '卯': '午', '辰': '酉', '巳': '子',
            '午': '卯', '未': '午', '申': '酉',
            '酉': '子', '戌': '卯', '亥': '午'
        }
        return jiangjun_map.get(self.year_zhi, '')



    def yuepo(self):
        """月破（月支）"""
        yuepo_map = {
            '寅': '申', '卯': '酉', '辰': '戌',
            '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰',
            '亥': '巳', '子': '午', '丑': '未'
        }
        return yuepo_map.get(self.month_zhi, '')

    def tianyi(self):
        """天乙（日干）"""
        tianyi_map = {
            '甲': '未', '乙': '申', '丙': '酉',
            '丁': '亥', '戊': '丑', '己': '子',
            '庚': '丑', '辛': '寅', '壬': '卯',
            '癸': '巳'
        }
        return tianyi_map.get(self.day_gan, '')

    def taiyin(self):
        """太阴（日干）"""
        taiyin_map = {
            '甲': '子', '乙': '丑', '丙': '寅',
            '丁': '卯', '戊': '辰', '己': '巳',
            '庚': '午', '辛': '未', '壬': '申',
            '癸': '酉'
        }
        return taiyin_map.get(self.day_gan, '')

    def liusha(self):
        """流煞（年支）"""
        liusha_map = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '巳': '亥', '酉': '亥', '丑': '亥',
            '亥': '巳', '卯': '巳', '未': '巳'
        }
        return liusha_map.get(self.year_zhi, '')

    def tianguan(self):
        """天官（月支）"""
        tianguan_map = {
            '寅': '未', '卯': '申', '辰': '酉',
            '巳': '戌', '午': '亥', '未': '子',
            '申': '丑', '酉': '寅', '戌': '卯',
            '亥': '辰', '子': '巳', '丑': '午'
        }
        return tianguan_map.get(self.month_zhi, '')

    def shenghao(self):
        """生耗（日干）"""
        shenghao_map = {
            '甲': '卯', '乙': '辰', '丙': '午',
            '丁': '未', '戊': '午', '己': '未',
            '庚': '酉', '辛': '戌', '壬': '子',
            '癸': '丑'
        }
        return shenghao_map.get(self.day_gan, '')

    def wangshen(self):
        """亡神（年支）"""
        wangshen_map = {
            '申': '巳', '子': '亥', '辰': '申',
            '寅': '巳', '午': '寅', '戌': '亥',
            '巳': '申', '酉': '亥', '丑': '寅',
            '亥': '申', '卯': '寅', '未': '巳'
        }
        return wangshen_map.get(self.year_zhi, '')

    def tianguan_guiren(self):
        """天官贵人（日干）"""
        tianguan_map = {
            '甲': '未', '乙': '辰', '丙': '巳',
            '丁': '酉', '戊': '卯', '己': '申',
            '庚': '亥', '辛': '子', '壬': '寅', '癸': '午'
        }
        return tianguan_map.get(self.day_gan, '')

    def taiji_guiren(self):
        """太极贵人（日干）"""
        taiji_map = {
            '甲': '子午', '乙': '子午', '丙': '卯酉',
            '丁': '卯酉', '戊': '辰戌', '己': '丑未',
            '庚': '寅亥', '辛': '寅亥', '壬': '巳申', '癸': '巳申'
        }
        return taiji_map.get(self.day_gan, '').split()

    def fuxing_guiren(self):
        """福星贵人（日干）"""
        fuxing_map = {
            '甲': '寅', '乙': '丑', '丙': '子',
            '丁': '酉', '戊': '申', '己': '未',
            '庚': '午', '辛': '巳', '壬': '辰', '癸': '卯'
        }
        return fuxing_map.get(self.day_gan, '')

    def tianchu_guiren(self):
        """天厨贵人（日干）"""
        tianchu_map = {
            '甲': '巳', '乙': '午', '丙': '子',
            '丁': '巳', '戊': '申', '己': '酉',
            '庚': '亥', '辛': '子', '壬': '寅', '癸': '卯'
        }
        return tianchu_map.get(self.day_gan, '')

    def xuetang_guiren(self):
        """学堂贵人（日干）"""
        xuetang_map = {
            '甲': '亥', '乙': '午', '丙': '寅',
            '丁': '酉', '戊': '寅', '己': '酉',
            '庚': '巳', '辛': '子', '壬': '申', '癸': '卯'
        }
        return xuetang_map.get(self.day_gan, '')

    def jinkui_guiren(self):
        """金匮贵人（日干）"""
        jinkui_map = {
            '甲': '辰', '乙': '寅', '丙': '午',
            '丁': '卯', '戊': '子', '己': '申',
            '庚': '戌', '辛': '酉', '壬': '丑', '癸': '巳'
        }
        return jinkui_map.get(self.day_gan, '')

    def xueren_sha(self):
        """血刃煞（日支）"""
        xueren_map = {
            '子': '戌', '丑': '酉', '寅': '未',
            '卯': '午', '辰': '巳', '巳': '辰',
            '午': '丑', '未': '寅', '申': '子',
            '酉': '亥', '戌': '申', '亥': '未'
        }
        return xueren_map.get(self.day_zhi, '')

    def juanshe_sha(self):
        """卷舌煞（日支）"""
        juanshe_map = {
            '子': '酉', '丑': '戌', '寅': '亥',
            '卯': '子', '辰': '丑', '巳': '寅',
            '午': '卯', '未': '辰', '申': '巳',
            '酉': '午', '戌': '未', '亥': '申'
        }
        return juanshe_map.get(self.day_zhi, '')

    def pima_sha(self):
        """披麻煞（日支）"""
        pima_map = {
            '子': '酉', '丑': '戌', '寅': '亥',
            '卯': '子', '辰': '丑', '巳': '寅',
            '午': '卯', '未': '辰', '申': '巳',
            '酉': '午', '戌': '未', '亥': '申'
        }
        return pima_map.get(self.day_zhi, '')

    def liuxia_sha(self):
        """流霞煞（日干）"""
        liuxia_map = {
            '甲': '酉', '乙': '戌', '丙': '未',
            '丁': '申', '戊': '巳', '己': '午',
            '庚': '辰', '辛': '卯', '壬': '亥', '癸': '寅'
        }
        return liuxia_map.get(self.day_gan, '')