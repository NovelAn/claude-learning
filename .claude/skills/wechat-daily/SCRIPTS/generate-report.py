#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Article Report Generator
Generates markdown reports from analyzed WeChat article data.
"""

import json
import os
import sys
from datetime import datetime
from jinja2 import Template


class ReportGenerator:
    """Generates markdown reports from analysis data."""

    def __init__(self, output_dir="data/reports", template_dir=None):
        """Initialize the report generator.

        Args:
            output_dir: Directory to save generated reports
            template_dir: Directory containing report templates (optional)
        """
        self.output_dir = output_dir
        self.template_dir = template_dir

    def load_analysis(self, analysis_file):
        """Load analysis results from JSON file.

        Args:
            analysis_file: Path to analysis JSON file

        Returns:
            dict: Analysis data
        """
        with open(analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_markdown(self, analysis):
        """Generate markdown report from analysis data.

        Args:
            analysis: Analysis results dictionary

        Returns:
            str: Markdown report content
        """
        # Get week number from analysis date
        analyzed_date = datetime.fromisoformat(analysis['analyzed_at'])
        week_num = analyzed_date.isocalendar()[1]
        year = analyzed_date.year

        # Build markdown report
        report_lines = []

        # Title
        report_lines.append(f"# 微信公众号热点周报\n")
        report_lines.append(f"**报告周期**: {year}年第{week_num}周\n")
        report_lines.append(f"**生成时间**: {analyzed_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")

        # Overview
        report_lines.append("## 📊 本周概况\n")
        stats = analysis['statistics']
        report_lines.append(f"- **文章总数**: {analysis['total_articles']} 篇\n")
        report_lines.append(f"- **公众号数量**: {stats['total_accounts']} 个\n")
        report_lines.append(f"- **内容总字数**: {analysis['total_content_chars']:,} 字\n")
        report_lines.append(f"- **平均字数**: {stats['avg_content_length']:,} 字\n")
        report_lines.append("\n")

        # Hot topics
        report_lines.append("## 🔥 热点话题排行\n")
        if analysis['topics']:
            for i, topic in enumerate(analysis['topics'][:10], 1):
                report_lines.append(f"{i}. **{topic['name']}** - 相关文章 {topic['article_count']} 篇\n\n")
                if topic.get('sample_articles'):
                    report_lines.append("   代表文章：\n")
                    for article in topic['sample_articles'][:3]:
                        report_lines.append(f"   - {article['title']}\n")
                    report_lines.append("\n")
        else:
            report_lines.append("暂无热点话题数据\n")
        report_lines.append("\n")

        # Keywords
        report_lines.append("## 🔑 核心关键词\n")
        if analysis['keywords']:
            report_lines.append("| 排名 | 关键词 | 权重 |\n")
            report_lines.append("|------|--------|------|\n")
            for i, kw in enumerate(analysis['keywords'][:20], 1):
                report_lines.append(f"| {i} | {kw['word']} | {kw['score']:.2f} |\n")
        report_lines.append("\n")

        # Account analysis
        report_lines.append("## 📱 公众号分析\n")
        top_accounts = stats.get('top_accounts', [])
        if top_accounts:
            report_lines.append("### 最活跃公众号\n\n")
            for i, account in enumerate(top_accounts[:10], 1):
                report_lines.append(f"{i}. **{account['account']}** - {account['count']} 篇文章\n")
        report_lines.append("\n")

        # Article list
        report_lines.append("## 📝 文章列表\n")
        report_lines.append("| # | 标题 | 公众号 | 发布时间 | 字数 |\n")
        report_lines.append("|---|------|--------|----------|------|\n")
        for i, article in enumerate(analysis['articles_summary'], 1):
            title = article['title'][:50] + '...' if len(article['title']) > 50 else article['title']
            report_lines.append(
                f"| {i} | {title} | {article['account']} | "
                f"{article['publish_time']} | {article['content_length']:,} |\n"
            )
        report_lines.append("\n")

        # Insights
        report_lines.append("## 💡 关键洞察\n")
        if analysis.get('insights'):
            for insight in analysis['insights']:
                report_lines.append(f"- {insight}\n")
        else:
            report_lines.append("暂无洞察数据\n")
        report_lines.append("\n")

        # Footer
        report_lines.append("---\n")
        report_lines.append(f"\n*本报告由 /wechat-daily Skill 自动生成*\n")
        report_lines.append(f"*数据来源: 微信公众号文章*\n")

        return ''.join(report_lines)

    def save_report(self, markdown_content, filename=None):
        """Save markdown report to file.

        Args:
            markdown_content: Markdown report content
            filename: Optional filename (auto-generated if not provided)

        Returns:
            str: Path to saved file
        """
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y-W%U')
            filename = f"weekly-report-{timestamp}.md"

        filepath = os.path.join(self.output_dir, filename)

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return filepath

    def generate_from_analysis(self, analysis_file, output_filename=None):
        """Generate report from analysis file.

        Args:
            analysis_file: Path to analysis JSON file
            output_filename: Optional output filename

        Returns:
            str: Path to generated report file
        """
        # Load analysis
        print("Loading analysis data...")
        analysis = self.load_analysis(analysis_file)

        # Generate markdown
        print("Generating markdown report...")
        markdown = self.generate_markdown(analysis)

        # Save report
        filepath = self.save_report(markdown, output_filename)
        print(f"[OK] Report saved to: {filepath}")

        return filepath


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate-report.py <analysis_file> [output_filename]")
        print("\nExample:")
        print("  python generate-report.py data/analysis-2025-W01.json")
        print("  python generate-report.py data/analysis-2025-W01.json my-report.md")
        sys.exit(1)

    analysis_file = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None

    # Check if analysis file exists
    if not os.path.exists(analysis_file):
        print(f"Error: Analysis file not found: {analysis_file}")
        sys.exit(1)

    # Generate report
    generator = ReportGenerator()
    filepath = generator.generate_from_analysis(analysis_file, output_filename)

    print(f"\n{'='*60}")
    print("Report Generation Complete!")
    print(f"{'='*60}")
    print(f"Output: {filepath}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
