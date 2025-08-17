import requests
import json
import os
import time
import ssl
import urllib3
import logging
from urllib3 import PoolManager
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from A_qimen.core.A2qm_base import QiMenCalculator
from A_qimen.core.A3qm_changsheng import ChangShengCalculator
from A_qimen.core.A4qm_shensha import ShenShaCalculator
from A_qimen.core.A5qm_direction import DirectionCalculator
from datetime import datetime, timedelta
from lunar_python import Solar, Lunar

# 设置简洁的日志记录 - 只记录错误到文件
logging.basicConfig(
    level=logging.ERROR,  # 只记录错误级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/error.log", encoding='utf-8'),
    ]
)
logger = logging.getLogger("DeepSeekConnection")

# 禁用不安全的HTTPS请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 1. 修复SSL验证错误
class CustomHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        # 直接创建SSL上下文，避免使用create_default_context
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')

        # 必须按此顺序设置
        ctx.verify_mode = ssl.CERT_NONE  # 禁用证书验证
        ctx.check_hostname = False  # 禁用主机名验证

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )


# 2. 奇门排盘函数
def generate_qimen_pan(year, month, day, hour, minute, lat, lon):
    qimen = QiMenCalculator(year=year, month=month, day=day,
                            hour=hour, minute=minute,
                            latitude=lat, longitude=lon)
    base_result = qimen.calculate_base()

    changsheng_calc = ChangShengCalculator(base_result)
    base_result['年干_月干_日干_时干_长生状态'] = changsheng_calc.calculate()

    shensha_calc = ShenShaCalculator(base_result)
    shensha_calc.calculate_all_shensha()

    direction_calculator = DirectionCalculator(base_result)
    return direction_calculator.enhance_pan_info()


# 干支映射工具函数
def get_ganzhi(year, month, day, hour, minute):
    """获取指定时间的干支"""
    # 这里简化实现，实际应用中应使用完整的干支计算库
    gan_list = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    zhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 简化的年干支计算
    year_last_digit = int(str(year)[-1])
    gan_index = (year_last_digit - 4) % 10
    year_gan = gan_list[gan_index]
    year_zhi = zhi_list[(year - 4) % 12]

    # 简化的日干支计算
    day_gan = gan_list[(day + gan_index) % 10]
    day_zhi = zhi_list[(day + 9) % 12]

    # 时干支计算
    hour_zhi_index = hour // 2 % 12
    if hour_zhi_index == 0:
        hour_zhi_index = 12
    hour_zhi = zhi_list[hour_zhi_index - 1]

    # 时干计算
    gan_index_map = {gan: i for i, gan in enumerate(gan_list)}
    hour_gan_index = (gan_index_map[day_gan] * 2 + hour_zhi_index - 1) % 10
    hour_gan = gan_list[hour_gan_index]

    return {
        '年': f"{year_gan}{year_zhi}",
        '月': "",  # 简化处理
        '日': f"{day_gan}{day_zhi}",
        '时': f"{hour_gan}{hour_zhi}"
    }


# 六甲遁干映射
def map_jia_to_dungan(ganzhi):
    """处理甲日甲时的六甲遁干映射"""
    dungan_map = {
        '甲子': '戊', '甲戌': '己', '甲申': '庚',
        '甲午': '辛', '甲辰': '壬', '甲寅': '癸'
    }

    # 处理日干
    if ganzhi['日'][0] == '甲':
        mapped_gan = dungan_map.get(ganzhi['日'], '')
        if mapped_gan:
            ganzhi['日'] = mapped_gan + ganzhi['日'][1]

    # 处理时干
    if ganzhi['时'][0] == '甲':
        mapped_gan = dungan_map.get(ganzhi['时'], '')
        if mapped_gan:
            ganzhi['时'] = mapped_gan + ganzhi['时'][1]

    return ganzhi


# 3. DeepSeek API交互函数（使用统一对话日志）
class DeepSeekAnalyzer:
    def __init__(self, pan_data, role_content, response_requirements):
        self.pan_data = pan_data
        self.conversation_history = []
        self.api_endpoints = ["https://api.deepseek.com/v1/chat/completions"]
        self.url = self.api_endpoints[0]
        self.role_content = role_content
        self.response_requirements = response_requirements
        self.log_file = "conversation_log.txt"  # 固定日志文件名

        # 创建会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = CustomHttpAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

        # 设置User-Agent
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })

        # 获取代理设置
        self.proxy_config = self._get_proxy_config()

        # 初始化系统提示
        self._initialize_system_prompt()

        # 获取并验证API密钥
        self.api_key = self._get_api_key()
        self._validate_api_key()

        # 初始化日志文件
        self._init_log_file()

    def _init_log_file(self):
        """初始化日志文件，添加分隔符"""
        # 如果文件不存在则创建
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("奇门遁甲分析系统 - 对话记录\n")
                f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
        else:
            # 添加新会话分隔符
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("\n\n" + "=" * 80 + "\n")
                f.write(f"新会话开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

    def _validate_api_key(self):
        """静默验证API密钥有效性"""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        test_payload = {"model": "deepseek-reasoner", "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5}

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=test_payload,
                timeout=15,
                verify=False,
                proxies=self.proxy_config
            )

            if response.status_code == 401:
                print("\n❌ API密钥无效或已过期")
                print("请访问 https://platform.deepseek.com/api-keys 获取有效密钥")
                print("程序将在5秒后退出...")
                time.sleep(5)
                exit(1)
        except:
            pass

    def _get_proxy_config(self):
        """获取代理设置"""
        try:
            http_proxy = os.getenv("HTTP_PROXY")
            https_proxy = os.getenv("HTTPS_PROXY")
            if http_proxy or https_proxy:
                return {"http": http_proxy, "https": https_proxy or http_proxy}

            if os.path.exists('proxy_config.json'):
                with open('proxy_config.json', 'r') as f:
                    config = json.load(f)
                    return config
        except:
            return None

    def _get_api_key(self):
        """获取API密钥"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key and api_key.startswith("sk-") and len(api_key) > 20:
            return api_key

        if os.path.exists('api_key.txt'):
            try:
                with open('api_key.txt', 'r') as f:
                    api_key = f.read().strip()
                    if api_key.startswith("sk-") and len(api_key) > 20:
                        return api_key
            except:
                pass

        print("\n⚠️ 需要DeepSeek API密钥")
        print("请访问 https://platform.deepseek.com/api-keys 获取密钥")

        while True:
            api_key = input("请输入您的API密钥: ").strip()
            if api_key.startswith("sk-") and len(api_key) > 20:
                try:
                    with open('api_key.txt', 'w') as f:
                        f.write(api_key)
                    return api_key
                except:
                    return api_key
            else:
                print("密钥格式不正确，应以'sk-'开头且长度至少20字符")

    def _initialize_system_prompt(self):
        """初始化系统提示词"""
        pan_text = "\n".join([f"{k}: {v}" for k, v in self.pan_data.items()])
        system_prompt = f"{self.role_content}\n\n### 当前奇门遁甲排盘信息 ###\n{pan_text}\n\n{self.response_requirements}"
        self.conversation_history.append({"role": "system", "content": system_prompt})

        # 记录排盘信息到日志
        self._save_to_log("奇门排盘信息:\n")
        for key, value in self.pan_data.items():
            self._save_to_log(f"{key}: {value}\n")
        self._save_to_log("\n")

    def add_user_message(self, message):
        """添加用户消息并记录到日志"""
        self.conversation_history.append({"role": "user", "content": message})
        self._save_to_log(f"[用户] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{message}\n\n")

    def get_ai_response(self):
        """获取完整AI响应并记录到日志"""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-reasoner",
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 4096,  # 确保完整输出
            "stream": False
        }

        try:
            # 发送请求
            response = self.session.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=(15, 120),
                verify=False,
                proxies=self.proxy_config
            )

            # 处理响应
            if response.status_code != 200:
                error_msg = self._handle_error(response)
                self._save_to_log(f"[系统错误] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{error_msg}\n\n")
                return error_msg

            response_data = response.json()
            ai_message = response_data["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": ai_message})

            # 记录AI响应到日志
            self._save_to_log(f"[AI] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{ai_message}\n\n")
            return ai_message

        except requests.exceptions.Timeout:
            error_msg = "❌ 请求超时：请稍后重试"
            self._save_to_log(f"[系统错误] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{error_msg}\n\n")
            return error_msg
        except requests.exceptions.RequestException:
            error_msg = "❌ 网络错误：请检查网络连接"
            self._save_to_log(f"[系统错误] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{error_msg}\n\n")
            return error_msg
        except Exception:
            error_msg = "❌ 处理响应时出错"
            self._save_to_log(f"[系统错误] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{error_msg}\n\n")
            return error_msg

    def _save_to_log(self, content):
        """将内容追加到日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"❌ 保存日志失败: {str(e)}")

    def _handle_error(self, response):
        """简洁错误处理"""
        if response.status_code == 401:
            return "❌ 认证失败：API密钥无效"
        elif response.status_code == 429:
            return "❌ 请求过多：请稍后再试"
        else:
            return f"❌ API错误 ({response.status_code})"

    def get_network_status(self):
        """简洁网络状态"""
        try:
            requests.get("https://www.baidu.com", timeout=5, verify=False)
            return "网络连接正常"
        except:
            return "网络连接异常"


# === 修正的四柱计算函数 ===
def calculate_sizhu(year, month, day, hour, minute, lon):
    """
    使用lunar_python库计算四柱（考虑真太阳时校正和日柱23:00切换）
    """
    # 计算经度时差（分钟）
    time_diff_minutes = (lon - 120.0) * 4
    total_minutes = hour * 60 + minute + time_diff_minutes

    # 创建基准日期时间
    base_dt = datetime(year, month, day)
    adjusted_dt = base_dt + timedelta(minutes=total_minutes)

    # 处理日柱切换点（23:00）
    if adjusted_dt.hour >= 23:
        # 23:00后属于下一天的日柱
        adjusted_dt = adjusted_dt - timedelta(hours=23) + timedelta(days=1)

    # 提取调整后的日期时间
    solar_year = adjusted_dt.year
    solar_month = adjusted_dt.month
    solar_day = adjusted_dt.day
    solar_hour = adjusted_dt.hour
    solar_minute = adjusted_dt.minute

    # 创建Solar对象
    try:
        solar = Solar.fromYmdHms(solar_year, solar_month, solar_day,
                                 solar_hour, solar_minute, 0)
        lunar = solar.getLunar()

        return {
            '年柱': lunar.getYearInGanZhi(),
            '月柱': lunar.getMonthInGanZhi(),
            '日柱': lunar.getDayInGanZhi(),
            '时柱': lunar.getTimeInGanZhi()
        }
    except Exception as e:
        print(f"计算四柱时出错: {e}")
        return {
            '年柱': "未知",
            '月柱': "未知",
            '日柱': "未知",
            '时柱': "未知"
        }


# 主函数 - 时间输入选择式界面
def main():
    print("\n=== 奇门遁甲分析系统 ===")
    print(f"所有对话将记录到: conversation_log.txt")

    # 读取配置文件
    try:
        with open('role_content.txt', 'r', encoding='utf-8') as f:
            role_content = f.read()
    except:
        role_content = "你是一位精通奇门遁甲的宗师，回答不要提及由deepseek或ai生成，你是一位宗师"

    try:
        with open('response_requirements.txt', 'r', encoding='utf-8') as f:

            response_requirements = f.read()
    except:
        response_requirements = "请根据奇门遁甲排盘信息进行详细分析"

    # 用户输入
    core_question = input("\n请提出您的问题：").strip()
    background_info = input("\n背景信息补充（可选）：").strip()
    user_question = f"问题：{core_question}"
    if background_info:
        user_question += f"\n背景：{background_info}"

    # 时间输入选择界面
    print("\n请选择时间输入方式：")
    print("1. 使用当前时间（自动获取当前北京时间）")
    print("2. 手动输入时间")
    choice = input("请输入选择 (1/2): ").strip()

    # 默认坐标（重庆）
    default_lat, default_lon = 29.83, 106.40

    if choice == "1":
        # 使用当前时间
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        hour, minute = now.hour, now.minute

        print(f"\n已使用当前时间: {year}年{month}月{day}日 {hour}时{minute}分")
        print(f"使用默认坐标: 纬度 {default_lat}, 经度 {default_lon}")

        lat, lon = default_lat, default_lon

        # 使用统一算法计算四柱
        sizhu = calculate_sizhu(year, month, day, hour, minute, lon)

        print("\n干支信息:")
        print(f"年干支: {sizhu['年柱']}")
        print(f"月干支: {sizhu['月柱']}")
        print(f"日干支: {sizhu['日柱']}")
        print(f"时干支: {sizhu['时柱']}")

    elif choice == "2":
        # 手动输入时间
        print("\n请提供事件发生的时间（北京时间）:")

        # 日期输入
        while True:
            date_input = input("日期 (格式: 年 月 日, 如 2025 7 12): ").split()
            if len(date_input) == 3:
                try:
                    year, month, day = map(int, date_input)
                    break
                except:
                    print("日期格式错误，请重新输入")
            else:
                print("日期格式错误，请按格式输入")

        # 时间输入
        while True:
            time_input = input("时间 (格式: 时 分, 如 10 53): ").split()
            if len(time_input) == 2:
                try:
                    hour, minute = map(int, time_input)
                    break
                except:
                    print("时间格式错误，请重新输入")
            else:
                print("时间格式错误，请按格式输入")

        # 坐标输入
        while True:
            coord_input = input("坐标 (格式: 纬度 经度, 如 29.83 106.40): ").split()
            if len(coord_input) == 0:
                # 如果用户直接回车，使用默认坐标
                lat, lon = default_lat, default_lon
                print(f"使用默认坐标: 纬度 {lat}, 经度 {lon}")
                break
            elif len(coord_input) == 2:
                try:
                    lat, lon = map(float, coord_input)
                    break
                except:
                    print("坐标格式错误，请重新输入")
            else:
                print("坐标格式错误，请按格式输入")

        # 使用统一算法计算四柱
        sizhu = calculate_sizhu(year, month, day, hour, minute, lon)

        print("\n干支信息:")
        print(f"年干支: {sizhu['年柱']}")
        print(f"月干支: {sizhu['月柱']}")
        print(f"日干支: {sizhu['日柱']}")
        print(f"时干支: {sizhu['时柱']}")

    else:
        print("无效选择，将使用当前时间")
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        hour, minute = now.hour, now.minute
        lat, lon = default_lat, default_lon
        print(f"\n已使用当前时间: {year}年{month}月{day}日 {hour}时{minute}分")
        print(f"使用默认坐标: 纬度 {lat}, 经度 {lon}")

        # 使用统一算法计算四柱
        sizhu = calculate_sizhu(year, month, day, hour, minute, lon)

        print("\n干支信息:")
        print(f"年干支: {sizhu['年柱']}")
        print(f"月干支: {sizhu['月柱']}")
        print(f"日干支: {sizhu['日柱']}")
        print(f"时干支: {sizhu['时柱']}")

    # 生成排盘
    print("\n正在生成奇门排盘...")
    pan_data = generate_qimen_pan(year, month, day, hour, minute, lat, lon)
    print("排盘完成！")

    # 初始化分析器
    analyzer = DeepSeekAnalyzer(pan_data, role_content, response_requirements)
    print(analyzer.get_network_status())

    # 分析问题
    analyzer.add_user_message(user_question)
    print("\n正在分析中，请稍候...")

    response = analyzer.get_ai_response()
    print("\n=== 奇门分析结果 ===")
    print(response)

    # 多轮对话
    print("\n继续提问（输入'exit'退出）：")
    while True:
        user_input = input("\n您：").strip()
        if user_input.lower() in ['exit', '退出']:
            print("对话结束")
            # 在日志中记录结束信息
            analyzer._save_to_log(f"会话结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            break

        if user_input:
            analyzer.add_user_message(user_input)
            print("分析中...")
            response = analyzer.get_ai_response()
            print("\n分析结果：")
            print(response)
            print("\n继续提问或输入'exit'退出...")


if __name__ == "__main__":
    main()
