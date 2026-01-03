#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Data Synchronization Module
/expression>将互动数据获取功能集成到/wechat-daily Skill工作流中
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 导入互动数据获取模块
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fetch_interaction_data import WeChatInteractionFetcher as Fetcher

class WeChatDataSync:
    """整合数据获取、分析和报告生成的完整工作流"""

    def __init__(self, config_path: str = "config.json"):
        """
        初始化数据同步器

        Args:
            config_path: 配置文件路径，包含API密钥等信息
        """
        self.config = self._load_config(config_path)
        self.interaction_fetcher = Fetcher(
            self.config.get('interaction_api_key')
        )

        # 基础路径设置
        self.data_dir = "data"
        self.articles_dir = os.path.join(self.data_dir, "articles")
        self.reports_dir = os.path.join(self.data_dir, "reports")

        # 确保目录存在
        for dir_path in [self.articles_dir, self.reports_dir]:
            os.makedirs(dir_path, exist_ok=True)

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"配置文件 {config_path} 不存在，使用默认配置")
                return {}
        except Exception as e:
            print(f"加载配置文件失败：{e}")
            return {}

    def sync_article_with_interaction(self, article_file: str) -> Optional[Dict]:
        """
        为已有文章添加互动数据

        Args:
            article_file: 文章JSON文件路径

        Returns:
            更新后的文章数据
        """
        try:
            # 读取文章基础数据
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)

            print(f"正在同步文章互动数据: {article_data.get('title', '未知标题')}")

            # 获取互动数据
            interaction_data = self.interaction_fetcher.get_interaction_data(
                article_data['url']
            )

            if interaction_data:
                # 合并数据
                article_data['interaction_metrics'] = interaction_data

                # 获取额外的质量分析
                quality_analysis = self.interaction_fetcher.analyze_interaction_quality(
                    interaction_data
                )
                article_data['interaction_metrics']['quality_analysis'] = quality_analysis

                # 计算热度指数
                hot_index = self._calculate_hot_index(interaction_data, article_data)
                article_data['hot_index'] = hot_index

                # 更新同步时间
                article_data['interaction_synced_at'] = datetime.now().isoformat()

                # 保存更新后的数据
                self._save_updated_article(article_file, article_data)

                print(f"✅ 数据同步完成")
                print(f"   阅读数: {interaction_data['read_count']:,}")
                print(f"   点赞数: {interaction_data['like_count']:,}")
                print(f"   热度指数: {hot_index}/100")

                return article_data
            else:
                print("⚠️  未能获取互动数据")
                return None

        except Exception as e:
            print(f"同步失败：{e}")
            return None

    def _calculate_hot_index(self, interaction_data: Dict, article_data: Dict) -> int:
        """
        计算文章热度指数

        Args:
            interaction_data: 互动数据
            article_data: 文章内容数据

        Returns:
            热度指数（0-100）
        """
        score = 0

        # 1. 阅读数权重（50分）
        read_count = interaction_data.get('read_count', 0)
        if read_count >= 100000:
            score += 50
        elif read_count >= 50000:
            score += 40
        elif read_count >= 10000:
            score += 30
        elif read_count >= 5000:
            score += 20
        elif read_count >= 1000:
            score += 10

        # 2. 互动率权重（30分）
        like_count = interaction_data.get('like_count', 0)
        if read_count > 0:
            like_rate = like_count / read_count * 100

            if like_rate >= 5:
                score += 30
            elif like_rate >= 3:
                score += 25
            elif like_rate >= 2:
                score += 20
            elif like_rate >= 1:
                score += 15
            else:
                score += 10

        # 3. 内容价值权重（15分）
        content_length = len(article_data.get('content_text', ''))
        key_topics = len(article_data.get('content_analysis', {}).get('key_topics', []))

        if content_length >= 2000:
            score += 5
        if key_topics >= 10:
            score += 5
        if article_data.get('account_name') in ['时尚商业Daily', 'HYPEBEAST']:
            score += 5  # 权威性账号加分

        # 4. 时效性权重（5分）
        publish_time = article_data.get('publish_time')
        if publish_time:
            days_old = (datetime.now() - datetime.fromisoformat(publish_time)).days
            if days_old <= 1:
                score += 5
            elif days_old <= 3:
                score += 3
            elif days_old <= 7:
                score += 1

        return min(score, 100)

    def _save_updated_article(self, article_path: str, data: Dict):
        """保存更新后的文章数据"""
        # 在原文件名基础上添加更新时间戳
        base_name = os.path.basename(article_path)
        name_parts = base_name.split('.')
        updated_name = f"{name_parts[0]}-with-interaction.{name_parts[1]}"

        save_path = os.path.join(os.path.dirname(article_path), updated_name)

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def sync_all_articles(self) -> List[Dict]:
        """批量同步所有已有文章"""
        print("🔄 开始批量同步文章互动数据...")

        # 查找所有文章文件
        article_files = []
        for file in os.listdir(self.articles_dir):
            if file.startswith('article-') and file.endswith('.json') and 'with-interaction' not in file:
                article_files.append(os.path.join(self.articles_dir, file))

        if not article_files:
            print("⚠️  未找到需要同步的文章")
            return []

        print(f"📋 发现 {len(article_files)} 篇文章需要同步")

        results = []
        for idx, article_file in enumerate(article_files, 1):
            print(f"\n[{idx}/{len(article_files)}] ", end='')
            result = self.sync_article_with_interaction(article_file)
            if result:
                results.append(result)

        # 生成汇总报告
        self._generate_sync_summary(results)

        return results

    def _generate_sync_summary(self, results: List[Dict]):
        """生成同步汇总报告"""
        if not results:
            print("未成功同步任何文章数据")
            return

        total_reads = sum(r['interaction_metrics']['read_count'] for r in results)
        total_likes = sum(r['interaction_metrics']['like_count'] for r in results)
        avg_hot_index = sum(r['hot_index'] for r in results) / len(results)

        report = {
            'synced_at': datetime.now().isoformat(),
            'total_articles': len(results),
            'total_read_count': total_reads,
            'total_like_count': total_likes,
            'average_hot_index': round(avg_hot_index, 1),
            'top_articles': sorted(results, key=lambda x: x['hot_index'], reverse=True)[:3],
            'articles_data': results
        }

        # 保存报告
        report_file = f"sync-summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        report_path = os.path.join(self.reports_dir, report_file)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n\n🎯 数据同步汇总")
        print("="*60)
        print(f"成功同步: {len(results)} 篇文章")
        print(f"总阅读量: {total_reads:,}")
        print(f"总点赞数: {total_likes:,}")
        print(f"平均热度: {avg_hot_index:.1f}/100")
        print(f"报告保存: {report_path}")
        print("="*60)

    def get_hot_articles(self, top_n: int = 5) -> List[Dict]:
        """获取热度最高的文章"""
        interaction_files = [
            f for f in os.listdir(self.articles_dir)
            if f.endswith('with-interaction.json')
        ]

        articles = []
        for file in interaction_files:
            with open(os.path.join(self.articles_dir, file), 'r') as f:
                data = json.load(f)
                articles.append(data)

        return sorted(articles, key=lambda x: x.get('hot_index', 0), reverse=True)[:top_n]

    def generate_weekly_report_data(self) -> Dict:
        """生成周报数据"""
        interaction_files = [
            f for f in os.listdir(self.articles_dir)
            if f.endswith('with-interaction.json')
        ]

        if not interaction_files:
            return {}

        articles = []
        total_metrics = {
            'read_count': 0,
            'like_count': 0,
            'share_count': 0,
            'comment_count': 0
        }

        for file in interaction_files:
            with open(os.path.join(self.articles_dir, file), 'r') as f:
                data = json.load(f)
                articles.append(data)

                # 汇总指标
                metrics = data.get('interaction_metrics', {})
                total_metrics['read_count'] += metrics.get('read_count', 0)
                total_metrics['like_count'] += metrics.get('like_count', 0)
                total_metrics['share_count'] += metrics.get('share_count', 0)
                total_metrics['comment_count'] += metrics.get('comment_count', 0)

        # 计算热度排行
        hot_articles = sorted(articles, key=lambda x: x.get('hot_index', 0), reverse=True)[:10]

        # 获取内容分析汇总
        all_topics = []
        for article in articles:
            topics = article.get('content_analysis', {}).get('key_topics', [])
            all_topics.extend([(t['term'], t.get('weight', 0)) for t in topics])

        # 聚合主题热度
        topic_counter = {}
        for term, weight in all_topics:
            topic_counter[term] = topic_counter.get(term, 0) + weight

        top_topics = sorted(topic_counter.items(), key=lambda x: x[1], reverse=True)[:15]

        return {
            'report_type': 'weekly_interaction',
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'total_metrics': total_metrics,
            'hot_articles': hot_articles,
            'top_topics': [{'topic': t[0], 'score': round(t[1], 2)} for t in top_topics],
            'interaction_quality': self._calculate_overall_interaction_quality(articles),
            'market_insights': self._generate_market_insights(articles, total_metrics)
        }

    def _calculate_overall_interaction_quality(self, articles: List[Dict]) -> Dict:
        """计算整体互动质量"""
        total_score = sum(r.get('interaction_metrics', {}).get('quality_analysis', {}).get('interaction_score', 0)
                         for r in articles)
        avg_score = total_score / len(articles) if articles else 0
        total_reads = sum(r.get('interaction_metrics', {}).get('read_count', 0) for r in articles)
        total_likes = sum(r.get('interaction_metrics', {}).get('like_count', 0) for r in articles)

        like_rate = (total_likes / total_reads * 100) if total_reads > 0 else 0

        return {
            'average_interaction_score': round(avg_score, 1),
            'overall_like_rate': f'{like_rate:.2f}%',
            'total_readers': total_reads,
            'engagement_level': 'High' if avg_score >= 60 else 'Medium' if avg_score >= 40 else 'Low'
        }

    def _generate_market_insights(self, articles: List[Dict], metrics: Dict) -> List[str]:
        """生成市场洞察"""
        insights = []

        total_reads = metrics['read_count']
        read_millions = total_reads / 10000

        # 阅读量洞察
        if read_millions >= 100:
            insights.append(f"总阅读量超过{read_millions:.0f}万，显示奢侈品领域内容关注度极高")
        elif read_millions >= 50:
            insights.append(f"总阅读量达到{read_millions:.0f}万，在该垂直领域表现优秀")
        elif read_millions >= 10:
            insights.append(f"总阅读量{read_millions:.0f}万，保持稳定的读者关注")

        # 互动质量洞察
        like_rate = metrics['like_count'] / total_reads * 100 if total_reads > 0 else 0
        if like_rate >= 3:
            insights.append(f"平均点赞率{like_rate:.1f}%，读者参与度高于行业平均水平")
        elif like_rate >= 2:
            insights.append(f"平均点赞率{like_rate:.1f}%，读者参与度适中")
        else:
            insights.append("互动率有待提升，建议优化内容形式和呈现方式")

        # 账号权威度分析
        accounts = list(set(r.get('account_name', '') for r in articles))
        if len(accounts) >= 3:
            insights.append(f"本周分析了{len(accounts)}个不同账号的内容，展现多元化视角")

        # 热门主题洞察
        topics = {}
        for article in articles:
            article_topics = article.get('content_analysis', {}).get('key_topics', [])
            for topic in article_topics[:5]:  # 只取前5个主题
                term = topic.get('term', '')
                if len(term) >= 2:  # 过滤太短的主题词
                    topics[term] = topics.get(term, 0) + topic.get('weight', 0)

        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_topics:
            topic_names = [t[0] for t in top_topics]
            insights.append(f"本周热门讨论话题包括：{', '.join(topic_names[:3])}")

        return insights


# 使用示例
def main():
    """演示完整的数据同步流程"""

    print("🔄 开始微信公众号数据同步流程...")

    # 1. 初始化同步器
    syncer = WeChatDataSync()

    # 2. 同步已有文章数据（添加互动指标）
    synced_articles = syncer.sync_all_articles()

    # 3. 生成周报数据
    if synced_articles:
        print("\n📊 正在生成周报数据...")
        weekly_data = syncer.generate_weekly_report_data()

        # 显示本周热点
        print("\n🔥 本周热点文章：")
        for i, article in enumerate(weekly_data['hot_articles'][:5], 1):
            metrics = article['interaction_metrics']
            print(f"  {i}. {article['title'][:50]}...")
            print(f"     阅读量: {metrics['read_count']:,} | 热度指数: {article['hot_index']}")

        # 显示热门话题
        print(f"\n📈 本周热门话题（共{len(weekly_data['top_topics'])}个）：")
        for topic in weekly_data['top_topics'][:10]:
            print(f"   - {topic['topic']} (热度: {topic['score']})")

        # 保存报告
        report_file = "weekly-interaction-report.json"
        report_path = os.path.join(syncer.reports_dir, report_file)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(weekly_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 周报数据已保存到：{report_path}")
        print(f"📊 本周总阅读量：{weekly_data['total_metrics']['read_count']:,}")
        print(f"👥 参与账号数： {weekly_data['total_articles']}")

    else:
        print("未发现可同步的文章数据")

    print("\n✅ 数据同步流程完成！")

if __name__ == "__main__":
    main()