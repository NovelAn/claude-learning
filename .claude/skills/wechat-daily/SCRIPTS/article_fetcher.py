#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章抓取器
结合极致了API获取完整的文章内容和互动数据
"""

import json
import os
import time
import random
from datetime import datetime
from typing import Dict, Optional, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import re
from config import JIZHILA_API, DATA_CONFIG, ERROR_MESSAGES

class WeChatArticleFetcher:
    """微信公众号文章综合抓取器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化抓取器"""
        self.api_key = api_key or JIZHILA_API['key']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # 使用配置文件中的路径
        self.articles_dir = DATA_CONFIG['articles_dir']
        self.reports_dir = DATA_CONFIG['reports_dir']

        # 确保目录存在
        os.makedirs(self.articles_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def fetch_article(self, url: str) -> Optional[Dict]:
        """
        抓取单篇微信文章的完整数据

        Args:
            url: 微信公众号文章URL

        Returns:
            包含文章内容和互动数据的字典
        """
        print(f"📇 正在抓取文章: {url}")

        try:
            # 1. 获取文章内容
            article_data = self._get_article_content(url)
            if not article_data:
                print("❌ 文章内容抓取失败")
                return None

            # 2. 获取互动数据（依赖API）
            if self.api_key:
                print("📊 正在通过极致了API获取互动数据...")
                interaction_data = self._get_interaction_data(url)
                if interaction_data:
                    article_data['interaction_data'] = interaction_data

                    # 3. 计算热度指数
                    article_data['hot_index'] = self._calculate_hot_index(article_data, interaction_data)
                    article_data['interaction_status'] = 'success'
                    print(f"✅ 互动数据获取成功")
                    print(f"   📖 阅读数: {interaction_data['read_count']:,}")
                    print(f"   👍 点赞数: {interaction_data['like_count']:,}")
                    print(f"   📈 热度指数: {article_data['hot_index']}/100")
                else:
                    print("⚠️  互动数据获取失败，使用模拟数据")
                    article_data['interaction_status'] = 'failed'
                    article_data['hot_index'] = self._calculate_hot_index_without_interaction(article_data)
            else:
                print("⚠️  未配置API密钥，将使用模拟互动数据")
                article_data['interaction_status'] = 'mock'
                mock_data = self._generate_mock_interaction_data(article_data)
                article_data['interaction_data'] = mock_data
                article_data['hot_index'] = self._calculate_hot_index(article_data, mock_data)

            # 4. 保存数据
            article_data['fetched_at'] = datetime.now().isoformat()
            self._save_article_data(article_data)

            return article_data

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return None

    def _get_article_content(self, url: str) -> Optional[Dict]:
        """获取文章内容"""
        try:
            # 添加随机延迟避免IP被封
            time.sleep(random.uniform(0.5, 1.5))

            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取各项内容
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            content = self._extract_content(soup)
            publish_time = self._extract_publish_time(soup)
            account_name = self._extract_account_name(soup)

            article_data = {
                'url': url,
                'title': title,
                'author': author,
                'content': content,
                'content_text': BeautifulSoup(content, 'html.parser').get_text(strip=True),
                'account_name': account_name,
                'publish_time': publish_time,
                'snapshot_time': datetime.now().isoformat()
            }

            # 初步分析
            article_data.update(self._analyze_content(article_data['content_text']))

            print(f"✅ 文章内容抓取完成")
            print(f"   📝 标题: {title[:50]}...")
            print(f"   👤 作者: {author}")
            print(f"   🏢 账号: {account_name}")
            print(f"   📏 内容长度: {len(article_data['content_text'])} 字符")

            return article_data

        except Exception as e:
            print(f"❌ 内容抓取失败: {e}")
            return None

    def _get_interaction_data(self, url: str) -> Optional[Dict]:
        """通过极致了API获取互动数据"""
        if not self.api_key:
            print("❌ 未配置API密钥")
            return None

        try:
            # API调用
            params = {
                'key': self.api_key,
                'url': url
            }

            response = requests.get(
                JIZHILA_API['url'],
                params=params,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # 极致了API成功判断：code == 1 或 code == 0 都表示成功
            if result.get('code') in [0, 1]:
                data = result.get('data', {})

                # 标准数据结构
                interaction_data = {
                    'read_count': data.get('read', 0),
                    'like_count': data.get('zan', 0),
                    'share_count': data.get('share_num', 0),
                    'collect_count': data.get('collect_num', 0),
                    'comment_count': data.get('comment_count', 0),
                    'data_source': 'jizhila_api',
                    'api_response': data,
                    'confidence': 'high',
                    'notes': '来自极致了数据API'
                }

                # 计算互动率
                if interaction_data['read_count'] > 0:
                    interaction_data['like_rate'] = interaction_data['like_count'] / interaction_data['read_count']
                    interaction_data['share_rate'] = interaction_data['share_count'] / interaction_data['read_count']
                    interaction_data['collect_rate'] = interaction_data['collect_count'] / interaction_data['read_count']
                    interaction_data['comment_rate'] = interaction_data['comment_count'] / interaction_data['read_count']

                return interaction_data

            else:
                print(f"API返回错误: {result.get('msg', '未知错误')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None

    def _generate_mock_interaction_data(self, article_data: Dict) -> Dict:
        """生成模拟互动数据"""
        # 基于文章特征生成合理的模拟数据
        content_length = len(article_data.get('content_text', ''))
        title = article_data.get('title', '')

        # 安全处理发布时间
        publish_time_str = article_data.get('publish_time', '')
        try:
            if publish_time_str:
                published_ago = (datetime.now() - datetime.fromisoformat(publish_time_str)).days
            else:
                published_ago = 0  # 默认为今天发布
        except:
            published_ago = 0  # 解析失败，默认为今天发布

        # 基础阅读数（考虑内容长度和时效性）
        base_read = max(5000, min(content_length * 10, 80000))
        if published_ago > 7:
            base_read *= 0.8  # 超过一周的文章，阅读量做乘法减少

        # 领域调整
        topic_boost = 1.0
        if any(word in title for word in ['时尚', '奢品', '奢侈品', 'Ferragamo', 'LVMH']):
            topic_boost = 1.8
        elif any(word in title for word in ['商业', '财报', '收购']):
            topic_boost = 1.4
        elif any(word in title for word in ['美妆', '美容']):
            topic_boost = 1.6

        read_count = int(base_read * topic_boost)

        # 互动数据
        like_count = int(read_count * random.uniform(0.015, 0.035))  # 1.5%-3.5%点赞率
        share_count = int(read_count * random.uniform(0.003, 0.008))  # 0.3%-0.8%分享率
        collect_count = int(read_count * random.uniform(0.003, 0.008))  # 0.3%-0.8%收藏率
        comment_count = int(read_count * random.uniform(0.005, 0.012))  # 0.5%-1.2%评论率

        return {
            'read_count': read_count,
            'like_count': like_count,
            'share_count': share_count,
            'comment_count': comment_count,
            'collect_count': collect_count,
            'data_source': 'simulation',
            'confidence': 'low',
            'notes': '基于文章特征生成的模拟数据'
        }

    def _calculate_hot_index(self, article_data: Dict, interaction_data: Dict) -> int:
        """计算文章热度指数 (0-100)"""
        score = 0

        # 1. 阅读量权重 (50分)
        read_count = interaction_data.get('read_count', 0)
        if read_count >= 100000: score += 50
        elif read_count >= 50000: score += 40
        elif read_count >= 20000: score += 30
        elif read_count >= 10000: score += 20
        elif read_count >= 5000: score += 10
        else: score += 0

        # 2. 互动率权重 (30分)
        read_count = max(read_count, 1)  # 避免除零
        like_rate = interaction_data.get('like_count', 0) / read_count
        share_rate = interaction_data.get('share_count', 0) / read_count

        if like_rate >= 0.05: score += 20  # 5%+点赞率
        elif like_rate >= 0.03: score += 15
        elif like_rate >= 0.02: score += 10
        else: score += 5

        if share_rate >= 0.01: score += 10  # 1%+分享率
        elif share_rate >= 0.005: score += 7
        elif share_rate >= 0.003: score += 5
        else: score += 0

        # 3. 内容价值权重 (15分)
        title_score = 0
        title = article_data.get('title', '')
        for keyword in ['时尚', '奢侈品', '财报', '收购', 'CEO', '数据']:
            if keyword in title:
                title_score += 2
        score += min(title_score, 15)

        # 4. 时效性权重 (5分)
        publish_time = datetime.fromisoformat(article_data.get('publish_time', datetime.now().isoformat()))
        days_old = (datetime.now() - publish_time).days
        if days_old <= 1: score += 5
        elif days_old <= 3: score += 3
        elif days_old <= 7: score += 1

        return min(score, 100)

    def _calculate_hot_index_without_interaction(self, article_data: Dict) -> int:
        """无互动数据时的热度估算"""
        score = 30  # 基础分

        # 基于内容分析
        topics = article_data.get('content_analysis', {}).get('key_topics', [])
        if len(topics) > 5: score += 10
        if article_data.get('tone_analysis') == 'positive': score += 10

        # 内容长度
        content_length = len(article_data.get('content_text', ''))
        if content_length > 2000: score += 15
        elif content_length > 1000: score += 10
        else: score += 5

        return min(score, 100)

    def _save_article_data(self, article_data: Dict):
        """保存文章数据"""
        # 生成文件名
        from urllib.parse import urlparse
        import hashlib

        url_hash = hashlib.md5(article_data['url'].encode()).hexdigest()[:10]
        filename = f"article-{url_hash}-{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.articles_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)

        print(f"💾 数据已保存: {filepath}")

    def fetch_multiple(self, urls: List[str]) -> List[Dict]:
        """批量抓取文章"""
        results = []
        print(f"\n📚 开始批量抓取 {len(urls)} 篇文章...")

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 正在处理...")
            result = self.fetch_article(url)
            if result:
                results.append(result)

            # 间隔处理，避免封号
            if i < len(urls):
                time.sleep(random.uniform(2, 4))

        print(f"\n✅ 批量抓取完成: {len(results)}/{len(urls)} 篇文章")
        return results

    # 辅助提取方法
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        selectors = ['h1', '.rich_media_title', 'title']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()[:200]
        return '无标题'

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者"""
        selectors = ['#js_name', '.rich_media_meta_text', '.profile_nickname']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()[:50]
        return '未知作者'

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取内容"""
        selectors = ['#js_content', '.rich_media_content']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return str(elem)
        return ''

    def _extract_publish_time(self, soup: BeautifulSoup) -> str:
        """提取发布时间"""
        selectors = ['#publish_time', '.rich_media_meta_date', '#post-date']
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return datetime.now().isoformat()

    def _extract_account_name(self, soup: BeautifulSoup) -> str:
        """提取公众号名称"""
        # 微信文章页面结构
        account_elem = soup.select_one('.rich_media_meta_list a') or soup.select_one('#js_name')
        if account_elem:
            return account_elem.get_text().strip()[:100]
        return '未知公众号'

    def _analyze_content(self, content_text: str) -> Dict:
        """分析内容"""
        analysis = {
            'content_analysis': {
                'char_count': len(content_text),
                'word_count': len(content_text.split()),
                'paragraph_count': content_text.count('\n\n') + 1
            },
            'key_topics': [],
            'tone_analysis': 'neutral'
        }

        # 简单的关键词提取
        words = re.findall(r'[\u4e00-\u9fa5]{2,6}', content_text)
        word_freq = {}
        for word in words:
            if len(word) >= 2:
                word_freq[word] = word_freq.get(word, 0) + 1

        # 按频率排序，取前15个
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        analysis['key_topics'] = [{'term': w[0], 'weight': w[1]/max(word_freq.values()) if word_freq else 0}
                                  for w in top_words]

        # 情感分析（简化版）
        positive_words = ['好消息', '增长', '成功', '盈利', '提升', '创新', '突破']
        negative_words = ['下滑', '亏损', '困境', '危机', '衰退', '失败', '问题']

        pos_count = sum(content_text.count(word) for word in positive_words)
        neg_count = sum(content_text.count(word) for word in negative_words)

        if pos_count > neg_count * 1.5:
            analysis['tone_analysis'] = 'positive'
        elif neg_count > pos_count * 1.5:
            analysis['tone_analysis'] = 'negative'
        else:
            analysis['tone_analysis'] = 'neutral'

        return analysis


if __name__ == '__main__':
    # 测试示例
    fetcher = WeChatArticleFetcher()

    # 测试文章
    test_urls = [
        "https://mp.weixin.qq.com/s/nNhtCWVzgkv6vbPyR-JOVQ",    # Ferragamo文章
        "https://mp.weixin.qq.com/s/Ggf3HzkOp8AjCHp-kgo1dw"     # Lululemon文章
    ]

    print("🚀 开始测试/wechat-daily文章抓取功能...")
    print("如果未配置API密钥，将使用模拟数据演示...\n")

    results = fetcher.fetch_multiple(test_urls)

    if results:
        print("\n" + "="*60)
        print("📊 抓取汇总报告")
        print("="*60)

        total_reads = sum(r.get('interaction_data', {}).get('read_count', 0) for r in results)
        total_likes = sum(r.get('interaction_data', {}).get('like_count', 0) for r in results)

        print(f"成功抓取: {len(results)} 篇文章")
        print(f"总阅读量: {total_reads:,}")
        print(f"总点赞数: {total_likes:,}")

        print("\n📋 文章详情:")
        for i, article in enumerate(results, 1):
            interaction = article.get('interaction_data', {})
            print(f"\n{i}. {article['title'][:60]}...")
            print(f"   🏢 账号: {article['account_name']}")
            print(f"   📊 热度: {article['hot_index']}/100")
            print(f"   📖 阅读: {interaction.get('read_count', 0):,}")
            print(f"   👍 点赞: {interaction.get('like_count', 0):,}")
            print(f"   💎 关键主题: {len(article['key_topics'])} 个")

    print(f"\n✨ 抓取完成，详细报告已保存到: {fetcher.reports_dir}")