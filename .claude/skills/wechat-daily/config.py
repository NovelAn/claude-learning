# -*- coding: utf-8 -*-
"""
WeChat Daily Skill Configuration
配置极致了API密钥和其他参数
跨平台支持：Mac、Windows、Linux
"""

import os
from pathlib import Path

def load_api_key():
    """
    加载极致了API密钥 - 优先使用项目 .env 文件

    优先级（从高到低）:
    1. .env 配置文件（项目根目录）
    2. 环境变量 JIZHILA_API_KEY（可选）
    3. 默认空值

    Returns:
        str: API密钥字符串，如果未配置则返回空字符串
    """
    return load_env_key('JIZHILA_API_KEY', '极致了')


def load_deepseek_api_key():
    """
    加载DeepSeek API密钥 - 优先使用项目 .env 文件

    优先级（从高到低）:
    1. .env 配置文件（项目根目录）
    2. 环境变量 DEEPSEEK_API_KEY（可选）
    3. 默认空值

    Returns:
        str: API密钥字符串，如果未配置则返回空字符串
    """
    return load_env_key('DEEPSEEK_API_KEY', 'DeepSeek')


def load_env_key(key_name: str, service_name: str = '') -> str:
    """
    通用的环境变量加载函数 - 优先从 .env 文件读取

    Args:
        key_name: 环境变量名称（如 JIZHILA_API_KEY）
        service_name: 服务名称（用于提示信息，如"极致了"）

    Returns:
        str: API密钥字符串
    """
    # 方法1: 优先从 .env 文件加载
    skill_dir = Path(__file__).parent
    env_file = skill_dir / '.env'

    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    # 解析 KEY=VALUE 格式
                    if '=' in line and key_name in line:
                        value = line.split('=', 1)[1].strip()
                        value = value.strip('"').strip("'")
                        # 跳过占位符
                        if value and value != f'your_{key_name.lower()}_here':
                            if value != f'your_{key_name.lower()}_key_here':
                                print(f"✅ 从 .env 文件加载{service_name}API密钥")
                                return value
        except Exception as e:
            print(f"⚠️  读取 .env 文件失败: {e}")

    # 方法2: 检查环境变量（可选，备选方案）
    api_key = os.environ.get(key_name, '')
    if api_key and api_key != f'your_{key_name.lower()}_here':
        if api_key != f'your_{key_name.lower()}_key_here':
            print(f"✅ 从环境变量加载{service_name}API密钥")
            return api_key

    # 未找到配置
    if service_name:
        print(f"⚠️  未找到{service_name}API密钥配置")
        print(f"   请在 .env 文件中配置: {key_name}=your_key_here")

    return ''

# 极致了数据API配置
JIZHILA_API = {
    'key': load_api_key(),  # 自动跨平台加载
    'url': 'https://www.dajiala.com/fbmain/monitor/v3/read_zan_pro',  # Pro版本API
    'price_per_query': 0.04,  # 元/次
    'free_quota': 10,  # 免费测试额度
    'description': '极致了数据微信公众号文章互动数据接口Pro版'
}

# 数据存储配置 - 使用绝对路径，确保一致性
import os
# 获取项目根目录（claude-learning）
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../'))

DATA_CONFIG = {
    'base_dir': os.path.join(PROJECT_ROOT, 'projects/wechat-daily-data'),
    'articles_dir': os.path.join(PROJECT_ROOT, 'projects/wechat-daily-data/articles'),
    'reports_dir': os.path.join(PROJECT_ROOT, 'projects/wechat-daily-data/reports'),
    'templates_dir': os.path.join(PROJECT_ROOT, 'projects/wechat-daily-data/templates'),
    'config_file': os.path.join(PROJECT_ROOT, 'projects/wechat-daily-data/config.json')
}

# 分析算法配置
ANALYSIS_CONFIG = {
    'min_content_length': 100,  # 最小分析内容长度
    'key_topics_limit': 20,     # 关键词提取数量限制
    'hot_index_weights': {      # 热度指数计算权重
        'read_count': 50,       # 阅读量权重 50%
        'like_rate': 30,        # 点赞率权重 30%
        'content_value': 15,    # 内容价值权重 15%
        'freshness': 5          # 时效性权重 5%
    }
}

# 报告生成配置
REPORT_CONFIG = {
    'web_template': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号热点分析 - {title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            background: #f8f9fa;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 20px;
            border-left: 4px solid #007bff;
        }}
        .article-item {{
            border-left: 3px solid #28a745;
            padding-left: 15px;
            margin: 15px 0;
        }}
        .topic-badge {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin: 2px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 微信公众号热点分析</h1>
        <p>Generated on {timestamp}</p>
    </div>

    <div class="card">
        <h2>📊 总体概况</h2>
        {overview}
    </div>

    <div class="card">
        <h2>🔥 热门文章排行</h2>
        {hot_articles}
    </div>

    <div class="card">
        <h2>📈 关键词热度</h2>
        {keywords}
    </div>

    <div class="card">
        <h2>💡 市场洞察</h2>
        {insights}
    </div>
</body>
</html>'''
}

# DeepSeek API配置（用于智能内容分析）
DEEPSEEK_CONFIG = {
    'api_key': load_deepseek_api_key(),  # 自动从.env或环境变量加载
    'base_url': 'https://api.deepseek.com',  # DeepSeek API地址
    'model': 'deepseek-chat',  # 使用DeepSeek-V3模型
    'temperature': 0.3,  # 降低随机性，提高稳定性
    'max_tokens': 2000,  # 最大token数
    'description': 'DeepSeek API用于文章摘要生成和智能内容分析，在中文文本分析上表现优秀'
}

# 保留OpenAI配置（兼容旧版本）
OPENAI_CONFIG = {
    'api_key': os.environ.get('OPENAI_API_KEY', ''),
    'base_url': 'https://api.openai.com/v1',
    'model': 'gpt-4o-mini',
    'temperature': 0.3,
    'max_tokens': 2000,
    'description': 'OpenAI API（可选）- 如果想使用OpenAI代替DeepSeek'
}

# 错误配置和提示
ERROR_MESSAGES = {
    'no_api_key': '''
⚠️  未配置API密钥

请先配置极致了API密钥，步骤如下：
1. 访问: https://www.dajiala.com/main/interface
2. 注册账号并申请API密钥
3. 设置环境变量: export JIZHILA_API_KEY="your_api_key_here"
4. 或直接编辑本文件，将key替换为真实值

费用: 0.04元/次查询，新用户有免费额度
''',
    'api_error': '''
❌ API调用失败

可能原因：
- API密钥无效或额度用完
- 请求频率过高（建议间隔>1秒）
- 文章URL格式错误（需完整微信公众号文章链接）

解决方案：
1. 检查API密钥是否正确
2. 充值或等待额度刷新
3. 重新尝试或更换文章链接
''',
    'insufficient_balance': '''
余额不足提醒

当前API余额不足，无法获取更多数据。
建议：
1. 登录 https://www.dajiala.com 充值
2. 使用模拟数据作为演示
3. 联系客服了解套餐方案
'''
}