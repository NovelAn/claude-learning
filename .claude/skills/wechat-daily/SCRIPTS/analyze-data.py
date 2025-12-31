#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Article Analyzer
Analyzes fetched WeChat articles and extracts keywords, topics, and insights.
"""

import json
import os
import sys
from datetime import datetime
from collections import Counter
import re

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("Warning: jieba not installed. Install with: pip install jieba")


class ArticleAnalyzer:
    """Analyzes WeChat articles and extracts insights."""

    def __init__(self, articles_dir="data/articles", output_dir="data"):
        """Initialize the analyzer.

        Args:
            articles_dir: Directory containing fetched article JSON files
            output_dir: Directory to save analysis results
        """
        self.articles_dir = articles_dir
        self.output_dir = output_dir

        # Initialize jieba if available
        if JIEBA_AVAILABLE:
            # Add custom stopwords
            self.stopwords = self._load_stopwords()
        else:
            self.stopwords = set()

    def _load_stopwords(self):
        """Load Chinese stopwords."""
        # Common Chinese stopwords
        stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '有',
            '与', '及', '其', '中', '为', '或', '但是', '因为', '所以', '如果',
            '虽然', '然后', '不过', '而且', '虽然', '这个', '那个', '什么',
            '怎么', '如何', '为什么', '哪', '些', '吗', '啊', '吧', '呢', '嘛'
        ])
        return stopwords

    def load_articles(self):
        """Load all article JSON files from directory.

        Returns:
            list: List of article dictionaries
        """
        articles = []

        if not os.path.exists(self.articles_dir):
            print(f"Error: Articles directory not found: {self.articles_dir}")
            return articles

        for filename in os.listdir(self.articles_dir):
            if filename.startswith('article-') and filename.endswith('.json'):
                filepath = os.path.join(self.articles_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        article = json.load(f)
                        articles.append(article)
                except Exception as e:
                    print(f"Warning: Error loading {filename}: {e}")

        return articles

    def extract_keywords(self, text, top_k=20):
        """Extract keywords from text using jieba.

        Args:
            text: Input text
            top_k: Number of top keywords to return

        Returns:
            list: List of (keyword, score) tuples
        """
        if not JIEBA_AVAILABLE:
            # Fallback: simple word frequency
            words = re.findall(r'[\u4e00-\u9fff]+', text)
            word_freq = Counter(words)
            # Remove stopwords
            for word in self.stopwords:
                word_freq.pop(word, None)
            # Remove single characters
            word_freq = {k: v for k, v in word_freq.items() if len(k) > 1}
            return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Use jieba TF-IDF
        keywords = jieba.analyse.extract_tags(
            text,
            topK=top_k,
            withWeight=True,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vd', 'vn', 'a', 'ad', 'an')
        )

        # Filter out stopwords
        keywords = [(kw, score) for kw, score in keywords if kw not in self.stopwords]

        return keywords

    def analyze_articles(self, articles):
        """Analyze multiple articles and extract insights.

        Args:
            articles: List of article dictionaries

        Returns:
            dict: Analysis results
        """
        print(f"\nAnalyzing {len(articles)} articles...\n")

        # Combine all text for keyword analysis
        all_text = ' '.join([a.get('content_text', '') for a in articles])
        total_chars = len(all_text)

        print(f"Total content length: {total_chars} characters")

        # Extract keywords
        print("Extracting keywords...")
        keywords = self.extract_keywords(all_text, top_k=50)
        top_keywords = keywords[:20]

        print(f"  [OK] Extracted {len(top_keywords)} top keywords")

        # Identify topics (clusters of related keywords)
        print("Identifying topics...")
        topics = self._identify_topics(keywords, articles)
        print(f"  [OK] Identified {len(topics)} topics")

        # Calculate statistics
        print("Calculating statistics...")
        stats = self._calculate_statistics(articles)
        print(f"  [OK] Total articles: {stats['total_articles']}")
        print(f"  [OK] Total accounts: {stats['total_accounts']}")

        # Analyze publication patterns
        print("Analyzing publication patterns...")
        pub_patterns = self._analyze_publication_patterns(articles)

        # Generate insights
        insights = self._generate_insights(articles, keywords, topics, stats)

        analysis = {
            'analyzed_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'total_content_chars': total_chars,
            'keywords': [
                {'word': word, 'score': float(score)}
                for word, score in top_keywords
            ],
            'topics': topics,
            'statistics': stats,
            'publication_patterns': pub_patterns,
            'insights': insights,
            'articles_summary': [
                {
                    'id': a.get('url', '')[-12:],
                    'title': a.get('title', ''),
                    'account': a.get('account_name', ''),
                    'publish_time': a.get('publish_time_str', ''),
                    'content_length': len(a.get('content_text', ''))
                }
                for a in articles
            ]
        }

        return analysis

    def _identify_topics(self, keywords, articles):
        """Identify topics from keywords and articles.

        Args:
            keywords: List of (keyword, score) tuples
            articles: List of article dictionaries

        Returns:
            list: List of topic dictionaries
        """
        # Group top keywords into topics
        # Simple approach: Use top keywords as topic seeds
        top_keywords = [kw for kw, score in keywords[:15]]

        topics = []
        for keyword in top_keywords[:10]:  # Top 10 become topics
            # Find articles containing this keyword
            related_articles = []
            for article in articles:
                title = article.get('title', '')
                content = article.get('content_text', '')
                if keyword in title or keyword in content:
                    related_articles.append({
                        'title': article.get('title', ''),
                        'account': article.get('account_name', '')
                    })

            if related_articles:
                topics.append({
                    'name': keyword,
                    'article_count': len(related_articles),
                    'sample_articles': related_articles[:3]  # Top 3 articles
                })

        # Sort by article count
        topics.sort(key=lambda x: x['article_count'], reverse=True)

        return topics

    def _calculate_statistics(self, articles):
        """Calculate statistics about articles.

        Args:
            articles: List of article dictionaries

        Returns:
            dict: Statistics
        """
        total_articles = len(articles)
        accounts = Counter(a.get('account_name', 'Unknown') for a in articles)

        # Content length stats
        content_lengths = [len(a.get('content_text', '')) for a in articles]
        avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0

        # Publish time stats (if available)
        publish_times = [a.get('publish_time') for a in articles if a.get('publish_time')]
        time_range = {}
        if publish_times:
            time_range = {
                'earliest': min(publish_times),
                'latest': max(publish_times)
            }

        return {
            'total_articles': total_articles,
            'total_accounts': len(accounts),
            'top_accounts': [
                {'account': account, 'count': count}
                for account, count in accounts.most_common(10)
            ],
            'avg_content_length': int(avg_content_length),
            'min_content_length': min(content_lengths) if content_lengths else 0,
            'max_content_length': max(content_lengths) if content_lengths else 0,
            'time_range': time_range
        }

    def _analyze_publication_patterns(self, articles):
        """Analyze publication time patterns.

        Args:
            articles: List of article dictionaries

        Returns:
            dict: Publication patterns
        """
        # Count articles by account
        account_counts = Counter(a.get('account_name', 'Unknown') for a in articles)

        # Most productive accounts
        top_accounts = [
            {'account': account, 'count': count}
            for account, count in account_counts.most_common(5)
        ]

        return {
            'top_accounts_by_volume': top_accounts,
            'total_accounts': len(account_counts)
        }

    def _generate_insights(self, articles, keywords, topics, stats):
        """Generate textual insights from analysis.

        Args:
            articles: List of article dictionaries
            keywords: List of (keyword, score) tuples
            topics: List of topic dictionaries
            stats: Statistics dictionary

        Returns:
            list: List of insight strings
        """
        insights = []

        # Top topics insight
        if topics:
            top_topic = topics[0]
            insights.append(
                f"最热门话题是「{top_topic['name']}」，共 {top_topic['article_count']} 篇相关文章"
            )

        # Account diversity insight
        if stats['total_accounts'] > 1:
            insights.append(
                f"本次分析涵盖 {stats['total_accounts']} 个公众号"
            )

        # Content volume insight
        avg_length = stats['avg_content_length']
        if avg_length > 0:
            if avg_length > 2000:
                insights.append("文章内容较为详实，平均字数超过2000")
            elif avg_length > 1000:
                insights.append("文章内容适中，平均字数约1000-2000")
            else:
                insights.append("文章较为简洁，平均字数少于1000")

        # Keyword diversity insight
        if keywords:
            top_keyword = keywords[0][0]
            insights.append(f"核心关键词为「{top_keyword}」")

        return insights

    def save_analysis(self, analysis):
        """Save analysis results to JSON file.

        Args:
            analysis: Analysis results dictionary

        Returns:
            str: Path to saved file
        """
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-W%U')
        filename = f"analysis-{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] Analysis saved to: {filepath}")
        return filepath


def main():
    """Main entry point."""
    articles_dir = sys.argv[1] if len(sys.argv) > 1 else "data/articles"

    # Initialize analyzer
    analyzer = ArticleAnalyzer(articles_dir=articles_dir)

    # Load articles
    print("Loading articles...")
    articles = analyzer.load_articles()

    if not articles:
        print("Error: No articles found to analyze.")
        sys.exit(1)

    # Analyze
    analysis = analyzer.analyze_articles(articles)

    # Save results
    filepath = analyzer.save_analysis(analysis)

    # Print summary
    print(f"\n{'='*60}")
    print("Analysis Summary")
    print(f"{'='*60}")
    print(f"Articles analyzed: {analysis['total_articles']}")
    print(f"Total characters: {analysis['total_content_chars']}")
    print(f"Topics identified: {len(analysis['topics'])}")
    print(f"\nTop Keywords:")
    for kw in analysis['keywords'][:10]:
        print(f"  - {kw['word']}: {kw['score']:.2f}")
    print(f"\nTop Topics:")
    for topic in analysis['topics'][:5]:
        print(f"  - {topic['name']}: {topic['article_count']} articles")
    print(f"\nInsights:")
    for insight in analysis['insights']:
        print(f"  - {insight}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
