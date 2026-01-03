#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章分析报告生成器
生成美观的网页版交互分析报告
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import jinja2

class WeChatReportGenerator:
    """微信公众号数据分析报告生成器"""

    def __init__(self, template_dir: Optional[str] = None):
        """初始化报告生成器"""
        # 使用配置文件中的路径
        self.reports_dir = DATA_CONFIG['reports_dir']
        os.makedirs(self.reports_dir, exist_ok=True)

        # 设置Jinja2模板环境
        template_dir = template_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
        os.makedirs(template_dir, exist_ok=True)
        self.template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    def generate_weekly_report(self, articles_data: List[Dict], output_file: Optional[str] = None) -> str:
        """
        生成周报

        Args:
            articles_data: 包含所有文章数据的列表
            output_file: 输出文件名（可选）

        Returns:
            生成的HTML报告文件路径
        """
        if not articles_data:
            print("⚠️  没有文章数据可用于生成报告")
            return ""

        print("🎯 正在生成公众号热点分析周报...")

        # 分析数据
        analysis = self._analyze_batch_data(articles_data)

        # 渲染模板
        template = self.template_env.get_template('report.html')
        html_content = template.render(
            report_title="微信公众号热点分析周报",
            report_date=datetime.now().strftime("%Y年%m月%d日"),
            **analysis
        )

        # 保存HTML报告
        if not output_file:
            output_file = f"weekly-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        output_path = os.path.join(self.reports_dir, output_file)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"🎉 周报已生成: {output_path}")
        return output_path

    def _analyze_batch_data(self, articles_data: List[Dict]) -> Dict:
        """分析批量文章数据"""
        # 基础统计
        total_articles = len(articles_data)

        # 只处理有互动数据的文章
        articles_with_data = [a for a in articles_data if a.get('interaction_data')]

        if not articles_with_data:
            return self._create_empty_report()

        # 计算总指标
        total_reads = int(sum(a['interaction_data'].get('read_count', 0) for a in articles_with_data) / 10000)  # 转换为万
        total_likes = sum(a['interaction_data'].get('like_count', 0) for a in articles_with_data)
        total_shares = sum(a['interaction_data'].get('share_count', 0) for a in articles_with_data)
        total_comments = sum(a['interaction_data'].get('comment_count', 0) for a in articles_with_data)
        total_collects = sum(a['interaction_data'].get('collect_count', 0) for a in articles_with_data)  # 添加收藏总数

        # 计算平均数据
        avg_like_rate = (total_likes / (total_reads * 10000) * 100) if total_reads > 0 else 0
        avg_share_rate = (total_shares / (total_reads * 10000) * 100) if total_reads > 0 else 0
        avg_comment_rate = (total_comments / (total_reads * 10000) * 100) if total_reads > 0 else 0
        avg_collect_rate = (total_collects / (total_reads * 10000) * 100) if total_reads > 0 else 0  # 添加平均收藏率
        top_hot_index = max(a.get('hot_index', 0) for a in articles_with_data)

        # 热门文章排序
        sorted_articles = sorted(articles_with_data, key=lambda x: x.get('hot_index', 0), reverse=True)[:10]

        # 关键词热度分析
        all_topics = []
        for article in articles_with_data:
            topics = article.get('content_analysis', {}).get('key_topics', [])
            for topic in topics[:5]:  # 每篇文章取前5个主题
                all_topics.append({
                    'name': topic.get('term', ''),
                    'score': topic.get('weight', 0),
                    'article': article['title']
                })

        # 聚合主题得分
        topic_scores = {}
        for topic in all_topics:
            if topic['name'] and len(topic['name']) >= 2:
                topic_scores[topic['name']] = topic_scores.get(topic['name'], 0) + topic['score']

        top_topics = sorted(
            [{'name': name, 'score': round(score, 2)} for name, score in topic_scores.items()],
            key=lambda x: x['score'],
            reverse=True
        )[:20]

        return {
            'total_articles': total_articles,
            'articles_with_data': len(articles_with_data),
            'total_reads': f"{total_reads}",
            'total_likes': f"{total_likes}",
            'avg_like_rate': f"{avg_like_rate:.2f}%",
            'avg_share_rate': f"{avg_share_rate:.2f}%",
            'avg_comment_rate': f"{avg_comment_rate:.2f}%",
            'top_hot_index': int(top_hot_index),
            'hot_articles': [
                {
                    'title': a['title'],
                    'account_name': a['account_name'],
                    'read_count': f"{int(a['interaction_data'].get('read_count', 0) / 10000 * 10000):,}",
                    'like_count': f"{a['interaction_data'].get('like_count', 0)}",
                    'comment_count': f"{a['interaction_data'].get('comment_count', 0)}",
                    'collect_count': f"{a['interaction_data'].get('collect_count', 0)}",  # 添加收藏数
                    'hot_index': int(a.get('hot_index', 0))
                }
                for a in sorted_articles
            ],
            'top_topics': top_topics[:15],
            'content_analysis': self._generate_content_analysis(articles_with_data),
            'interaction_analysis': self._generate_interaction_analysis(articles_with_data),
            'insights': self._generate_insights(articles_with_data, {
                'total_reads': total_reads,
                'total_likes': total_likes,
                'avg_like_rate': avg_like_rate
            }),
            'generated_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'api_credits_used': len(articles_with_data)
        }

    def _create_empty_report(self) -> Dict:
        """创建空报告"""
        return {
            'total_articles': 0,
            'total_reads': "0",
            'total_likes': "0",
            'avg_like_rate': "0.00%",
            'top_hot_index': 0,
            'hot_articles': [],
            'top_topics': [],
            'content_analysis': '暂无内容可分析',
            'interaction_analysis': '暂无互动数据',
            'insights': ['请提供有效的文章数据后重新生成报告'],
            'generated_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'api_credits_used': 0
        }

    def _generate_content_analysis(self, articles: List[Dict]) -> str:
        """生成内容分析部分"""
        metrics = []

        # 内容长度分析
        lengths = [len(a.get('content_text', '')) for a in articles]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            if avg_length > 3000:
                metrics.append("文章普遍较长，内容深度较高")
            elif avg_length > 1500:
                metrics.append("文章长度适中，平衡了信息密度和可读性")
            else:
                metrics.append("文章内容相对简洁，注重快速传达要点")

        # 情绪分析
        tones = [a.get('tone_analysis', 'neutral') for a in articles]
        positive_pct = (tones.count('positive') / len(tones)) * 100
        negative_pct = (tones.count('negative') / len(tones)) * 100

        if positive_pct > 60:
            metrics.append(f"整体情绪积极正面（{positive_pct:.0f}%的文章表现乐观态度）")
        elif negative_pct > 60:
            metrics.append(f"整体情绪偏谨慎，{negative_pct:.0f}%的文章呈现负面倾向")
        else:
            metrics.append("内容情绪中性，以客观报道和分析为主")

        return "\n".join(f"• {metric}" for metric in metrics)

    def _generate_interaction_analysis(self, articles: List[Dict]) -> str:
        """生成互动分析"""
        metrics = []

        # 互动数据聚合
        total_reads = sum(a['interaction_data'].get('read_count', 0) for a in articles)
        total_likes = sum(a['interaction_data'].get('like_count', 0) for a in articles)
        total_comments = sum(a['interaction_data'].get('comment_count', 0) for a in articles)

        avg_like_rate = (total_likes / max(total_reads, 1) * 100)
        avg_comment_rate = (total_comments / max(total_reads, 1) * 100)

        # 基准对比
        if avg_like_rate >= 3:
            metrics.append(f"点赞率 {avg_like_rate:.2f}% 高于行业平均水平（2-3%）")
        elif avg_like_rate >= 2:
            metrics.append(f"点赞率 {avg_like_rate:.2f}% 处于行业平均水平")
        else:
            metrics.append(f"点赞率 {avg_like_rate:.2f}% 低于行业平均，需优化内容吸引力")

        # 深度参与分析
        if avg_comment_rate >= 0.8:
            metrics.append("读者评论参与度高，内容能够引发深度思考和讨论")
        elif avg_comment_rate >= 0.5:
            metrics.append("评论参与度良好，有一定话题讨论基础")
        else:
            metrics.append("评论参与度偏低，建议增加互动引导元素")

        # 不同类型文章表现
        high_engagement = [a for a in articles if a.get('hot_index', 0) >= 70]
        if len(high_engagement) > len(articles) / 3:
            metrics.append(f"有 {len(high_engagement)} 篇文章获得高互动，选题策略成功")

        return "\n".join(f"• {metric}" for metric in metrics)

    def _generate_insights(self, articles: List[Dict], metrics: Dict) -> List[str]:
        """生成洞察建议"""
        insights = []

        # 阅读量洞察
        read_millions = metrics['total_reads']
        if read_millions >= 100:
            insights.append(f"总阅读量突破{read_millions:.0f}万，达到爆款量级，建议趁热打铁持续推出相关内容")
        elif read_millions >= 50:
            insights.append(f"累计阅读量达到{read_millions:.0f}万，在该垂直领域表现亮眼，可考虑扩大选题范围")

        # 互动表现
        like_rate = metrics['avg_like_rate']
        if like_rate >= 5:
            insights.append("点赞率表现优异，内容质量得到了读者的高度认可，建议总结成功要素持续复用")
        elif like_rate >= 3:
            insights.append("互动表现良好，已形成稳定的读者参与基础，可考虑引导更多分享和讨论")
        else:
            insights.append("互动参与有待提升，建议在文章结尾增加引导点赞或评论的行动号召")

        # 热门话题洞察
        top_topics = list(set([topic.get('term', '') for a in articles
                              for topic in a.get('content_analysis', {}).get('key_topics', [])[:3]]))
        if len(top_topics) >= 5:
            insights.append(f"本周热门讨论话题包括：{', '.join(top_topics[:3])}，这些主题获得了较高关注")

        # 成功文章分析
        best_article = max(articles, key=lambda x: x.get('hot_index', 0))
        best_score = best_article.get('hot_index', 0)
        if best_score >= 90:
            insights.append(f"「{best_article['title'][:30]}...」热度指数高达{best_score}，可深度分析其成功要素用于后续选题")

        # 账号表现
        accounts = list(set(a['account_name'] for a in articles if a['account_name'] != '未知公众号'))
        if len(accounts) >= 3:
            insights.append(f"本周分析了{len(accounts)}个不同账号的内容，多元化视角帮助发现更多热门选题机会")

        return insights[:6]  # 最多6条洞察

if __name__ == '__main__':
    generator = WeChatReportGenerator()

    # 演示用的示例数据
    demo_data = {
        'title': '突发 | Ferragamo与中国长期伙伴股东协议到期不续',
        'account_name': '时尚商业Daily',
        'author': 'Drizzie',
        'publish_time': '2025-12-30',
        'content_text': '这是示例文章内容，包含了详细的分析...',
        'hot_index': 85,
        'tone_analysis': 'negative',
        'key_topics': [{'term': '奢侈品', 'weight': 0.8}, {'term': '股东协议', 'weight': 0.7}],
        'interaction_data': {
            'read_count': 50212,
            'like_count': 1094,
            'like_rate': 0.0218,
            'comment_count': 293
        }
    }

    print("📋 生成示例报告...")
    report_path = generator.generate_weekly_report([demo_data])
    print(f"✅ 报告已生成: {report_path}")