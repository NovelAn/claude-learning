
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章智能内容分析模块
使用OpenAI API进行深度内容分析
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class ContentAnalyzer:
    """智能内容分析器 - 使用OpenAI API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化内容分析器

        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量读取
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY', '')
        self.model = "gpt-4o-mini"  # 使用性价比高的模型
        self.max_tokens = 2000
        self.temperature = 0.3  # 降低随机性，提高稳定性

        if not self.api_key:
            print("⚠️  未配置OpenAI API密钥")
            print("   请设置环境变量: export OPENAI_API_KEY='your-key-here'")
            print("   或在代码中提供api_key参数")

    def _call_openai_api(self, prompt: str, system_prompt: str = None) -> str:
        """
        调用OpenAI API

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）

        Returns:
            str: API返回的文本
        """
        if not self.api_key:
            return json.dumps({
                'error': 'API_KEY_MISSING',
                'message': '未配置OpenAI API密钥'
            }, ensure_ascii=False)

        try:
            import openai

            # 设置API密钥
            openai.api_key = self.api_key

            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 调用API
            response = openai.OpenAI().chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except ImportError:
            return json.dumps({
                'error': 'PACKAGE_NOT_INSTALLED',
                'message': '请先安装openai包: pip install openai'
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                'error': 'API_CALL_FAILED',
                'message': str(e)
            }, ensure_ascii=False)

    def analyze_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        对文章进行完整的内容分析

        Args:
            article_data: 文章数据字典，包含title, content_text等字段

        Returns:
            Dict: 分析结果，包含summary, key_insights, data_points等
        """
        title = article_data.get('title', '')
        content = article_data.get('content_text', '')
        author = article_data.get('author', '')
        account = article_data.get('account_name', '')

        # 限制内容长度，避免超过API限制
        max_content_length = 12000  # 约3000个汉字
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n[内容过长，已截断]"

        analysis_result = {
            'analyzer_version': '1.0.0',
            'analysis_time': datetime.now().isoformat(),
            'model_used': self.model,
            'summary': '',
            'key_insights': [],
            'data_points': [],
            'entities': [],
            'recommendations': [],
            'raw_api_response': ''
        }

        print("🔍 开始智能内容分析...")
        print(f"   标题: {title[:50]}...")
        print(f"   内容长度: {len(content)} 字符")

        # 1. 生成文章摘要
        print("\n📝 1/5 生成文章摘要...")
        summary = self._generate_summary(title, content, author, account)
        analysis_result['summary'] = summary

        # 2. 提取核心观点
        print("💡 2/5 提取核心观点...")
        insights = self._extract_key_insights(title, content)
        analysis_result['key_insights'] = insights

        # 3. 标注关键数据
        print("📊 3/5 标注关键数据...")
        data_points = self._extract_data_points(content)
        analysis_result['data_points'] = data_points

        # 4. 识别实体
        print("🏢 4/5 识别品牌/公司/人物...")
        entities = self._extract_entities(title, content)
        analysis_result['entities'] = entities

        # 5. 提炼行动建议
        print("✅ 5/5 提炼行动建议...")
        recommendations = self._extract_recommendations(title, content)
        analysis_result['recommendations'] = recommendations

        print("\n✅ 内容分析完成!")

        return analysis_result

    def _generate_summary(self, title: str, content: str, author: str, account: str) -> str:
        """
        生成文章摘要（300字以内）

        Args:
            title: 文章标题
            content: 文章内容
            author: 作者
            account: 账号名称

        Returns:
            str: 摘要文本
        """
        system_prompt = """你是一位专业的内容分析师，擅长总结微信公众号文章。
你的任务是生成简明扼要的文章摘要，突出核心信息和价值点。"""

        prompt = f"""请为以下文章生成一个简明扼要的摘要（300字以内）：

标题：{title}
账号：{account}
作者：{author}

文章内容：
{content}

摘要要求：
1. 概括文章核心主题和主要内容
2. 突出最重要的信息或观点
3. 语言简洁明了，控制在300字以内
4. 使用专业但易懂的表达

请直接输出摘要内容，不要包含任何前缀或说明："""

        response = self._call_openai_api(prompt, system_prompt)

        # 清理响应
        if response.startswith('{') and '"error"' in response:
            print(f"   ⚠️  摘要生成失败: {response}")
            return self._generate_fallback_summary(content)

        return response.strip()

    def _generate_fallback_summary(self, content: str) -> str:
        """降级方案：基于首尾段生成简单摘要"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 2:
            first_part = paragraphs[0][:200]
            last_part = paragraphs[-1][:100]
            return f"{first_part}...\n\n文章结尾：{last_part}"
        else:
            return content[:300] + "..."

    def _extract_key_insights(self, title: str, content: str) -> List[str]:
        """
        提取3-5个核心观点

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            List[str]: 核心观点列表
        """
        system_prompt = """你是一位专业的内容分析师，擅长提炼文章核心观点。
你需要从文章中提取3-5个最重要的观点或论点。"""

        prompt = f"""请从以下文章中提取3-5个核心观点或论点：

标题：{title}

文章内容：
{content}

要求：
1. 提取文章最重要的3-5个观点
2. 每个观点用一句话概括，简洁明了
3. 按重要性排序
4. 以JSON数组格式返回，例如：["观点1", "观点2", "观点3"]

请直接返回JSON数组："""

        response = self._call_openai_api(prompt, system_prompt)

        # 尝试解析JSON
        try:
            # 清理可能的markdown代码块标记
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1]
            if response.endswith('```'):
                response = response.rsplit('\n', 1)[0]
            response = response.strip()
            if response.startswith('json'):
                response = response[4:].strip()

            insights = json.loads(response)
            if isinstance(insights, list):
                return insights[:5]  # 最多返回5个
            else:
                return []
        except:
            # JSON解析失败，尝试提取编号列表
            return self._parse_numbered_list(response)

    def _parse_numbered_list(self, text: str) -> List[str]:
        """从文本中解析编号列表"""
        insights = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            # 匹配 "1." 或 "1、" 或 "1 )" 等格式
            match = re.match(r'^[\d]+\s*[.、)]\s*(.+)', line)
            if match:
                insights.append(match.group(1).strip())
            elif len(insights) > 0 and len(insights) < 5:
                # 继续行作为上一个观点的补充
                if line and not line.startswith('##'):
                    insights[-1] += ' ' + line

        return insights[:5]

    def _extract_data_points(self, content: str) -> List[Dict[str, Any]]:
        """
        提取文章中的关键数据和统计信息

        Args:
            content: 文章内容

        Returns:
            List[Dict]: 数据点列表，每个包含value, context, category
        """
        # 首先使用规则匹配提取数字
        data_points = []

        # 匹配模式：数字 + 单位/说明
        patterns = [
            r'([\d,]+\.?\d*)\s*([万亿千百]?\s*[元美金%个百分点倍])',  # 财务数据
            r'([\d,]+)\s*([人个次篇篇条评论])',  # 数量统计
            r'([\d,]+)\s*([年月日季度])',  # 时间数据
            r'增长\s*([\d,]+\.?\d*)\s*%?',  # 增长率
            r'下降\s*([\d,]+\.?\d*)\s*%?',  # 下降率
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                value = match.group(1)
                context = self._get_context(content, match.start(), 50)

                data_points.append({
                    'value': value,
                    'unit': match.group(2) if len(match.groups()) > 1 else '',
                    'context': context,
                    'category': self._categorize_data_point(context)
                })

        # 去重，限制数量
        unique_points = []
        seen_values = set()
        for point in data_points[:15]:  # 最多15个
            value_key = point['value'] + point['unit']
            if value_key not in seen_values:
                unique_points.append(point)
                seen_values.add(value_key)

        return unique_points

    def _get_context(self, text: str, position: int, window: int = 50) -> str:
        """获取数据点的上下文"""
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end].strip()

    def _categorize_data_point(self, context: str) -> str:
        """根据上下文对数据点分类"""
        if any(word in context for word in ['元', '营收', '利润', '销售额', '市值']):
            return '财务数据'
        elif any(word in context for word in ['%', '增长', '下降', '率']):
            return '百分比/比率'
        elif any(word in context for word in ['年', '季度', '月']):
            return '时间数据'
        else:
            return '其他数据'

    def _extract_entities(self, title: str, content: str) -> List[Dict[str, str]]:
        """
        识别文章中的品牌、公司、人物等实体

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            List[Dict]: 实体列表，每个包含name, type, description
        """
        system_prompt = """你是一位专业的实体识别专家，擅长识别文章中的品牌、公司、人物等实体。"""

        prompt = f"""请从以下文章中识别重要的品牌、公司、人物实体：

标题：{title}

文章内容：
{content}

要求：
1. 识别文章中提到的品牌、公司、人物
2. 返回JSON数组格式，每个实体包含name（名称）、type（类型：品牌/公司/人物）、description（简要描述）
3. 最多返回10个最重要的实体
4. 示例格式：[{{"name": "LVMH", "type": "公司", "description": "全球最大的奢侈品集团"}}]

请直接返回JSON数组："""

        response = self._call_openai_api(prompt, system_prompt)

        # 解析JSON响应
        try:
            # 清理markdown标记
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1]
            if response.endswith('```'):
                response = response.rsplit('\n', 1)[0]
            response = response.strip()
            if response.startswith('json'):
                response = response[4:].strip()

            entities = json.loads(response)
            if isinstance(entities, list):
                return entities[:10]
            else:
                return []
        except:
            # 降级：使用关键词匹配
            return self._extract_entities_fallback(title, content)

    def _extract_entities_fallback(self, title: str, content: str) -> List[Dict[str, str]]:
        """降级方案：使用已知实体库匹配"""
        entities = []
        text = title + ' ' + content

        # 已知品牌/公司库（奢侈品/时尚行业）
        known_brands = {
            'LVMH': '公司',
            'Gucci': '品牌',
            'Prada': '品牌',
            'Ferragamo': '品牌',
            'Cartier': '品牌',
            'Hermès': '品牌',
            'Chanel': '品牌',
            'Dior': '品牌',
            'Louis Vuitton': '品牌',
            'Burberry': '品牌',
            'Tiffany': '品牌',
            'Coach': '品牌',
            'Nike': '品牌',
            'Adidas': '品牌',
            'Lululemon': '品牌',
            'Abercrombie': '品牌',
        }

        for brand, brand_type in known_brands.items():
            if brand in text:
                entities.append({
                    'name': brand,
                    'type': brand_type,
                    'description': f'检测到{brand}相关内容'
                })

        return entities[:10]

    def _extract_recommendations(self, title: str, content: str) -> List[str]:
        """
        提炼文章中的行动建议或启示

        Args:
            title: 文章标题
            content: 文章内容

        Returns:
            List[str]: 行动建议列表
        """
        system_prompt = """你是一位专业的商业分析师，擅长从文章中提炼可操作的建议和启示。"""

        prompt = f"""请从以下文章中提炼可操作的行动建议或行业启示：

标题：{title}

文章内容：
{content}

要求：
1. 提炼3-5条可操作的建议或启示
2. 建议应该具体、实用，能够指导实际工作
3. 以JSON数组格式返回，例如：["建议1", "建议2", "建议3"]
4. 如果文章没有明确的建议，请提炼出对行业的启示或观察

请直接返回JSON数组："""

        response = self._call_openai_api(prompt, system_prompt)

        # 解析JSON
        try:
            # 清理markdown标记
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1]
            if response.endswith('```'):
                response = response.rsplit('\n', 1)[0]
            response = response.strip()
            if response.startswith('json'):
                response = response[4:].strip()

            recommendations = json.loads(response)
            if isinstance(recommendations, list):
                return recommendations[:5]
            else:
                return []
        except:
            # JSON解析失败，尝试提取编号列表
            return self._parse_numbered_list(response)[:5]

    def format_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """
        格式化分析结果为可读报告

        Args:
            analysis: 分析结果字典

        Returns:
            str: 格式化报告
        """
        report = []
        report.append("=" * 80)
        report.append("📊 智能内容分析报告")
        report.append("=" * 80)

        # 摘要
        if analysis.get('summary'):
            report.append("\n📝 文章摘要：")
            report.append("-" * 80)
            report.append(analysis['summary'])

        # 核心观点
        if analysis.get('key_insights'):
            report.append("\n💡 核心观点：")
            report.append("-" * 80)
            for i, insight in enumerate(analysis['key_insights'], 1):
                report.append(f"{i}. {insight}")

        # 关键数据
        if analysis.get('data_points'):
            report.append("\n📊 关键数据：")
            report.append("-" * 80)
            for i, point in enumerate(analysis['data_points'][:10], 1):
                report.append(f"{i}. {point['value']} {point['unit']} ({point['category']})")
                report.append(f"   上下文: {point['context'][:60]}...")

        # 实体识别
        if analysis.get('entities'):
            report.append("\n🏢 识别实体：")
            report.append("-" * 80)
            for entity in analysis['entities']:
                report.append(f"• {entity['name']} ({entity['type']})")
                if entity.get('description'):
                    report.append(f"  {entity['description']}")

        # 行动建议
        if analysis.get('recommendations'):
            report.append("\n✅ 行动建议：")
            report.append("-" * 80)
            for i, rec in enumerate(analysis['recommendations'], 1):
                report.append(f"{i}. {rec}")

        report.append("\n" + "=" * 80)
        report.append(f"分析时间: {analysis.get('analysis_time', 'N/A')}")
        report.append(f"使用模型: {analysis.get('model_used', 'N/A')}")

        return '\n'.join(report)


# 测试代码
if __name__ == '__main__':
    # 测试内容分析器
    analyzer = ContentAnalyzer()

    # 模拟文章数据
    test_article = {
        'title': '突发 | Ferragamo与中国长期伙伴股东协议到期不续',
        'author': 'Drizzie',
        'account_name': '时尚商业Daily',
        'content_text': '''
        意大利奢侈品牌 Salvatore Ferragamo（菲拉格慕）宣布与中国长期合作伙伴的股东协议已到期，将不再续签。
        这一决定标志着该品牌在中国市场战略的重大调整。

        据了解，Ferragamo与该合作伙伴的合作超过10年，期间共同开拓了中国市场。
        分析认为，此次调整可能与品牌全球战略转型有关。

        数据显示，Ferragamo 2023年在中国市场的销售额达到2.3亿欧元，占全球销售额的15%。
        然而，近年来中国奢侈品市场增速放缓，2023年增长率仅为12%，低于前年的28%。

        业内人士指出，Ferragamo正在重新评估其在中国市场的分销策略，可能转向直营模式。
        这一趋势在奢侈品行业并不鲜见，Gucci、Prada等品牌都在加强直营渠道建设。
        '''
    }

    print("🧪 测试智能内容分析功能...\n")

    # 执行分析
    result = analyzer.analyze_article(test_article)

    # 打印报告
    print("\n" + analyzer.format_analysis_report(result))

    # 保存结果
    output_file = 'test_content_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析结果已保存到: {output_file}")
