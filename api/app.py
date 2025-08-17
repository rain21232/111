import os
import json
import logging
import requests
import ssl
import urllib3
from urllib3 import PoolManager
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from lunar_python import Solar, Lunar
import sys

# ========== 路径配置 ==========
# 获取当前文件所在目录的绝对路径（app.py 所在目录）
current_dir = os.path.dirname(os.path.abspath(__file__))

# 计算项目根目录（A_qimen/）
project_root = os.path.join(current_dir, '..')

# 配置文件的完整路径（指向 core/ 目录）
role_content_path = os.path.join(project_root, 'core', 'role_content.txt')
response_requirements_path = os.path.join(project_root, 'core', 'response_requirements.txt')
api_key_path = os.path.join(project_root, 'core', 'api_key.txt')

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "logs", "api.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QimenAPI")

# 记录路径信息
logger.info(f"当前文件目录: {current_dir}")
logger.info(f"项目根目录: {project_root}")
logger.info(f"角色内容文件路径: {role_content_path}")
logger.info(f"响应要求文件路径: {response_requirements_path}")
logger.info(f"API密钥文件路径: {api_key_path}")

# 禁用不安全的HTTPS请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 修复SSL验证错误
class CustomHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.verify_mode = ssl.CERT_NONE
        ctx.check_hostname = False
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )


# 奇门排盘函数
def generate_qimen_pan(year, month, day, hour, minute, lat, lon):
    # 确保可以导入 core 模块
    core_dir = os.path.join(project_root, 'core')
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)

    try:
        from A2qm_base import QiMenCalculator
        from A3qm_changsheng import ChangShengCalculator
        from A4qm_shensha import ShenShaCalculator
        from A5qm_direction import DirectionCalculator

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

    except ImportError as e:
        logger.error(f"导入排盘模块失败: {str(e)}")
        return {"error": f"排盘模块加载失败: {str(e)}"}


# 四柱计算函数
def calculate_sizhu(year, month, day, hour, minute, lon):
    time_diff_minutes = (lon - 120.0) * 4
    total_minutes = hour * 60 + minute + time_diff_minutes
    base_dt = datetime(year, month, day)
    adjusted_dt = base_dt + timedelta(minutes=total_minutes)

    if adjusted_dt.hour >= 23:
        adjusted_dt = adjusted_dt - timedelta(hours=23) + timedelta(days=1)

    solar_year = adjusted_dt.year
    solar_month = adjusted_dt.month
    solar_day = adjusted_dt.day
    solar_hour = adjusted_dt.hour
    solar_minute = adjusted_dt.minute

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
        logger.error(f"计算四柱时出错: {e}")
        return {
            '年柱': "未知",
            '月柱': "未知",
            '日柱': "未知",
            '时柱': "未知"
        }


# DeepSeek API交互类
class DeepSeekAnalyzer:
    def __init__(self, pan_data):
        self.pan_data = pan_data
        self.conversation_history = []
        self.api_endpoints = ["https://api.deepseek.com/v1/chat/completions"]
        self.url = self.api_endpoints[0]

        # 读取配置文件
        try:
            if os.path.exists(role_content_path):
                with open(role_content_path, 'r', encoding='utf-8') as f:
                    self.role_content = f.read()
                logger.info(f"成功读取角色内容文件: {role_content_path}")
            else:
                raise FileNotFoundError(f"角色内容文件不存在: {role_content_path}")
        except Exception as e:
            logger.error(f"读取角色内容失败: {str(e)}")
            self.role_content = "你是一位精通奇门遁甲的宗师，回答不要提及由deepseek或ai生成，你是一位宗师"

        try:
            if os.path.exists(response_requirements_path):
                with open(response_requirements_path, 'r', encoding='utf-8') as f:
                    self.response_requirements = f.read()
                logger.info(f"成功读取响应要求文件: {response_requirements_path}")
            else:
                raise FileNotFoundError(f"响应要求文件不存在: {response_requirements_path}")
        except Exception as e:
            logger.error(f"读取响应要求失败: {str(e)}")
            self.response_requirements = "请根据奇门遁甲排盘信息进行详细分析"

        # 获取API密钥
        self.api_key = self._get_api_key()

        # 初始化系统提示
        self._initialize_system_prompt()

    def _get_api_key(self):
        """获取API密钥"""
        # 首先尝试环境变量
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key and api_key.startswith("sk-") and len(api_key) > 20:
            logger.info("从环境变量获取API密钥")
            return api_key

        # 然后尝试从文件读取
        if os.path.exists(api_key_path):
            try:
                with open(api_key_path, 'r') as f:
                    api_key = f.read().strip()
                    if api_key.startswith("sk-") and len(api_key) > 20:
                        logger.info(f"从文件获取API密钥: {api_key_path}")
                        return api_key
                    else:
                        logger.error("API密钥格式不正确")
            except Exception as e:
                logger.error(f"读取API密钥文件失败: {str(e)}")
        else:
            logger.error(f"API密钥文件不存在: {api_key_path}")

        logger.error("DeepSeek API密钥未找到或格式不正确")
        return None

    def _initialize_system_prompt(self):
        """初始化系统提示词"""
        pan_text = "\n".join([f"{k}: {v}" for k, v in self.pan_data.items()])
        system_prompt = f"{self.role_content}\n\n### 当前奇门遁甲排盘信息 ###\n{pan_text}\n\n{self.response_requirements}"
        self.conversation_history.append({"role": "system", "content": system_prompt})

        logger.info("系统提示初始化完成")

    def get_prediction(self, user_question):
        """获取预测结果"""
        if not self.api_key:
            logger.error("API密钥未配置，无法获取预测结果")
            return "预测失败: API密钥未配置"

        # 添加用户问题
        self.conversation_history.append({"role": "user", "content": user_question})
        logger.info(f"添加用户问题: {user_question[:50]}...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-reasoner",
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }

        try:
            # 发送请求
            logger.info(f"发送请求到DeepSeek API: {self.url}")
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=120,  # 增加超时时间
                verify=False
            )

            # 处理响应
            if response.status_code != 200:
                error_msg = f"DeepSeek API错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"预测失败: API错误 ({response.status_code})"

            response_data = response.json()
            ai_message = response_data["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": ai_message})

            logger.info(f"成功获取预测结果，长度: {len(ai_message)}字符")
            return ai_message

        except Exception as e:
            error_msg = f"获取预测结果时出错: {str(e)}"
            logger.error(error_msg)
            return f"预测失败: {str(e)}"


# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求


@app.route('/predict', methods=['POST'])
def predict():
    """API预测端点"""
    # 1. 获取请求数据
    data = request.get_json()

    if not data or 'question' not in data:
        error_msg = "缺少问题参数"
        logger.warning(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'code': 400
        }), 400

    question = data['question'].strip()
    background_info = data.get('background_info', '').strip()

    # 组合完整问题
    user_question = f"问题：{question}"
    if background_info:
        user_question += f"\n背景：{background_info}"

    logger.info(f"接收预测请求: {user_question[:100]}...")

    # 2. 参数验证
    if len(question) < 3:
        error_msg = "问题太短，请至少输入3个字符"
        logger.warning(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'code': 400
        }), 400

    if len(question) > 500:
        error_msg = "问题过长，请限制在500字符内"
        logger.warning(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'code': 400
        }), 400

    # 3. 处理时间选择
    time_choice = data.get('time_choice', '1')  # 默认使用当前时间
    time_data = data.get('time_data', {})

    # 默认坐标（重庆）
    default_lat, default_lon = 29.83, 106.40

    try:
        if time_choice == "1":
            # 使用当前时间
            now = datetime.now()
            year, month, day = now.year, now.month, now.day
            hour, minute = now.hour, now.minute
            lat, lon = default_lat, default_lon

            logger.info(f"使用当前时间: {year}-{month}-{day} {hour}:{minute}")

        elif time_choice == "2":
            # 手动输入时间
            year = time_data.get('year')
            month = time_data.get('month')
            day = time_data.get('day')
            hour = time_data.get('hour')
            minute = time_data.get('minute')
            lat = time_data.get('lat', default_lat)
            lon = time_data.get('lon', default_lon)

            if None in [year, month, day, hour, minute]:
                error_msg = "时间参数不完整"
                logger.warning(error_msg)
                return jsonify({
                    'status': 'error',
                    'message': error_msg,
                    'code': 400
                }), 400

            logger.info(f"使用手动输入时间: {year}-{month}-{day} {hour}:{minute} 坐标: {lat},{lon}")

        else:
            error_msg = "无效的时间选择"
            logger.warning(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'code': 400
            }), 400

        # 计算四柱
        sizhu = calculate_sizhu(year, month, day, hour, minute, lon)
        logger.info(f"四柱计算完成: {sizhu}")

        # 生成排盘
        pan_data = generate_qimen_pan(year, month, day, hour, minute, lat, lon)
        logger.info("奇门排盘生成完成")

        # 添加四柱信息到排盘数据
        pan_data['年柱'] = sizhu['年柱']
        pan_data['月柱'] = sizhu['月柱']
        pan_data['日柱'] = sizhu['日柱']
        pan_data['时柱'] = sizhu['时柱']

        # 初始化分析器
        analyzer = DeepSeekAnalyzer(pan_data)

        # 获取预测结果
        result = analyzer.get_prediction(user_question)
        logger.info(f"预测结果长度: {len(result)}字符")

        return jsonify({
            'status': 'success',
            'question': question,
            'answer': result
        })

    except Exception as e:
        error_msg = f"预测处理失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'code': 500
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    # 检查配置文件是否存在
    files_exist = {
        'role_content.txt': os.path.exists(role_content_path),
        'response_requirements.txt': os.path.exists(response_requirements_path),
        'api_key.txt': os.path.exists(api_key_path)
    }

    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'qimen-prediction-api',
        'files_exist': files_exist
    })


if __name__ == '__main__':
    # 确保日志目录存在
    logs_dir = os.path.join(current_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    logger.info(f"日志目录: {logs_dir}")

    # 检查配置文件是否存在
    for path, exists in {
        'role_content.txt': role_content_path,
        'response_requirements.txt': response_requirements_path,
        'api_key.txt': api_key_path
    }.items():
        if os.path.exists(path):
            logger.info(f"文件存在: {path}")
        else:
            logger.warning(f"文件不存在: {path}")

    # 启动服务
    host = '0.0.0.0'
    port = 5000
    logger.info(f"🚀 启动奇门遁甲API服务: http://{host}:{port}")
    app.run(host=host, port=port)
