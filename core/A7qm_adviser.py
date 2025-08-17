import configparser
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv


class MysticAdviser:
    def __init__(self, config_path='A6qm_config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        # 从环境变量或配置文件获取API密钥
        load_dotenv()
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or self.config['DeepSeek']['api_key']

        # 咨询师人设
        self.persona = {
            'name': self.config['Persona']['name'],
            'title': self.config['Persona']['title'],
            'style': self.config['Persona']['style'],
            'language': self.config['Persona']['language'],
            'specialty': self.config['Persona']['specialty'].split(',')
        }

    def _build_system_prompt(self):
        """构建系统角色设定"""
        return (
            f"你是一位资深的奇门遁甲占卜师{self.persona['name']}，"
            f"头衔是{self.persona['title']}，"
            f"擅长{self.persona['style']}。请用{self.persona['language']}回答，"
            "回答风格为：专业分析和积极建议，回答内容接地气，不故作玄虚，真实可靠的占卜大师。"
        )

    def ask_oracle(self, user_query, method="auto"):
        """
        核心占卜方法
        :param user_query: 用户问题
        :param method: 占卜方法 (精通奇门遁甲，八字也很厉害)
        :return: 准确的占卜结果，和有效的建议
        """
        # 确定占卜方法
        if method == "auto":
            method = self._determine_method(user_query)

        # 构建专属提示词
        prompt = self._build_divination_prompt(user_query, method)

        # 调用API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.config['DeepSeek']['default_model'],
            "messages": messages,
            "temperature": float(self.config['DeepSeek']['temperature']),
            "max_tokens": int(self.config['DeepSeek']['max_tokens'])
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']

            # 保存咨询记录
            if self.config['Consultation'].getboolean('save_history'):
                self._save_consultation(user_query, method, result)

            return result
        except Exception as e:
            return f"天机暂不可泄露，请稍后再试或 联系作者：铉錚本人咨询（错误: {str(e)}）"

    def _determine_method(self, query):
        """根据问题自动选择占卜方法"""
        method_keywords = {
            "奇门遁甲": ["感情发展",'未来桃花' "人生选择", "六亲关系", "未来短期运势","寻物","选岗","占卜考试成绩","公务员选岗","当下身体健康","疾病占卜","人际关系",'当下状态','投资抉择'],
            "八字": [ "年份运势", "大运运势", "子女性别","财富格局","职业规划","地理发展方向",'投资','事业前景','怀才不遇'],

        }

        for method, keywords in method_keywords.items():
            if any(keyword in query for keyword in keywords):
                return method

        # 默认方法
        return "奇门遁甲"

    def _build_divination_prompt(self, query, method):
        """构建占卜专用提示词"""
        method_prompts = {
            "奇门遁甲": f"使用奇门遁甲为以下问题提供深度解读：'{query}'。请分析奇门盘，天盘干与地盘干的组合关系，长生状态，九星、八门。八神落宫旺衰情况及吉凶情况，及在各个宫位的意义，分析年月日时柱的生克关系，宫门相生相克的关系，六亲关系，使用各种奇门主流技法，等等，给出详细的占卜结果并给出具体有效的建议。",
            "八字": f"根据传统八字命理、盲派八字、精通《穷通宝鉴》《子平真诠》《渊海子平》《千里命稿》《神峰通考》《天滴髓》里的八字知识并且还能结合现代理论）分析以下问题：'{query}'。排盘并解读命主的事业、财运、感情和健康运势，给出未来3个月的建议。",

        return method_prompts.get(method, method_prompts["奇门"])

    def _save_consultation(self, query, method, result):
        """保存咨询记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record = {
            "timestamp": timestamp,
            "query": query,
            "method": method,
            "result": result
        }

        # 确保目录存在
        history_path = self.config['Consultation']['history_path']
        os.makedirs(history_path, exist_ok=True)

        # 保存为JSON文件
        filename = f"{history_path}consultation_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

    def generate_report(self, client_info):
        """生成客户综合报告"""
        prompt = (
            f"根据以下客户信息生成一份综合玄学报告：\n{client_info}\n\n"
            "报告需包含：\n1. 奇门遁甲有问必答，包含当前状态、财运、学业运、情感状况，身体健康情况，近期注意事项\n2. 八字命理简析"
            "请用专业且温暖的语言呈现，最后询问客户是否需要具体行动建议，若需要则提出能够落实的建议。"
        )
        return self.ask_oracle(prompt, method="综合")