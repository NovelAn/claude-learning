#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的内容分析脚本
专门用于对已抓取的文章进行智能文本分析
不调用极致了API，只使用OpenAI进行内容分析
"""

import sys
import json
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from content_analyzer import ContentAnalyzer
from config import DEEPSEEK_CONFIG, OPENAI_CONFIG, DATA_CONFIG
import glob


def analyze_article_file(article_file: str) -> dict:
    """
    分析单个文章JSON文件

    Args:
        article_file: 文章JSON文件路径

    Returns:
        dict: 包含原始数据和内容分析的结果
    """
    print(f"\n{'='*80}")
    print(f"📄 分析文件: {Path(article_file).name}")
    print('='*80)

    # 读取文章数据
    with open(article_file, 'r', encoding='utf-8') as f:
        article_data = json.load(f)

    print(f"📝 标题: {article_data.get('title', 'N/A')[:60]}...")
    print(f"🏢 账号: {article_data.get('account_name', 'N/A')}")

    # 创建内容分析器（优先使用DeepSeek）
    llm_config = None
    if DEEPSEEK_CONFIG.get('api_key'):
        llm_config = DEEPSEEK_CONFIG
        llm_provider = 'DeepSeek'
    elif OPENAI_CONFIG.get('api_key'):
        llm_config = OPENAI_CONFIG
        llm_provider = 'OpenAI'

    analyzer = ContentAnalyzer(
        api_key=llm_config.get('api_key') if llm_config else None,
        base_url=llm_config.get('base_url') if llm_config else None,
        model=llm_config.get('model') if llm_config else None
    )

    # 执行内容分析
    analysis_result = analyzer.analyze_article(article_data)

    # 合并数据
    result = {
        'article_data': article_data,
        'content_analysis': analysis_result
    }

    return result


def analyze_batch(article_dir: str = None, pattern: str = '*.json') -> list:
    """
    批量分析文章

    Args:
        article_dir: 文章目录路径，默认使用DATA_CONFIG配置
        pattern: 文件匹配模式

    Returns:
        list: 分析结果列表
    """
    if article_dir is None:
        article_dir = DATA_CONFIG['articles_dir']

    article_files = glob.glob(str(Path(article_dir) / pattern))

    if not article_files:
        print(f"❌ 未找到文章文件: {article_dir}/{pattern}")
        return []

    print(f"\n🔍 找到 {len(article_files)} 篇文章待分析")
    print("="*80)

    results = []
    for i, article_file in enumerate(article_files, 1):
        print(f"\n[{i}/{len(article_files)}] 处理中...")
        try:
            result = analyze_article_file(article_file)
            results.append(result)
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            continue

    return results


def save_analysis_results(results: list, output_file: str = None):
    """
    保存分析结果

    Args:
        results: 分析结果列表
        output_file: 输出文件路径
    """
    if output_file is None:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(DATA_CONFIG.get('reports_dir', 'reports'))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f'content-analysis-{timestamp}.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析结果已保存到: {output_file}")


def print_summary(results: list):
    """
    打印分析摘要

    Args:
        results: 分析结果列表
    """
    print("\n" + "="*80)
    print("📊 内容分析摘要")
    print("="*80)

    total_articles = len(results)
    total_insights = sum(len(r.get('content_analysis', {}).get('key_insights', []))
                         for r in results)
    total_data_points = sum(len(r.get('content_analysis', {}).get('data_points', []))
                            for r in results)
    total_entities = sum(len(r.get('content_analysis', {}).get('entities', []))
                        for r in results)

    print(f"✅ 成功分析: {total_articles} 篇文章")
    print(f"💡 提取观点: {total_insights} 条")
    print(f"📊 标注数据: {total_data_points} 个")
    print(f"🏢 识别实体: {total_entities} 个")

    print("\n📋 文章列表:")
    for i, result in enumerate(results, 1):
        article = result.get('article_data', {})
        analysis = result.get('content_analysis', {})
        print(f"\n{i}. {article.get('title', 'N/A')[:50]}...")
        print(f"   摘要长度: {len(analysis.get('summary', ''))} 字符")
        print(f"   核心观点: {len(analysis.get('key_insights', []))} 条")
        print(f"   关键数据: {len(analysis.get('data_points', []))} 个")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         🎯 微信公众号文章智能内容分析工具                      ║
║         (独立版 - 仅内容分析，不调用数据API)                   ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 检查API密钥
    has_llm_api = bool(DEEPSEEK_CONFIG.get('api_key') or OPENAI_CONFIG.get('api_key'))
    if not has_llm_api:
        print("⚠️  警告: 未配置LLM API密钥")
        print("   内容分析功能需要DeepSeek API（推荐）或OpenAI API")
        print("   请在.env文件中配置: DEEPSEEK_API_KEY=your-key-here\n")
        print("   你仍然可以运行，但会使用降级方案（基础规则提取）\n")

    print("请选择操作:")
    print("1. 分析单篇文章")
    print("2. 批量分析所有文章")
    print("3. 分析最新的一篇文章")
    print("4. 退出")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == '1':
        # 分析单篇文章
        file_path = input("请输入文章JSON文件路径: ").strip()
        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            return

        result = analyze_article_file(file_path)
        save_analysis_results([result])

        # 打印详细报告
        analyzer = ContentAnalyzer()
        print("\n" + analyzer.format_analysis_report(result['content_analysis']))

    elif choice == '2':
        # 批量分析
        print("\n开始批量分析所有文章...")
        results = analyze_batch()
        if results:
            save_analysis_results(results)
            print_summary(results)

    elif choice == '3':
        # 分析最新文章
        article_dir = DATA_CONFIG['articles_dir']
        article_files = glob.glob(str(Path(article_dir) / '*.json'))

        if not article_files:
            print(f"❌ 未找到文章文件: {article_dir}")
            return

        # 按修改时间排序，取最新的
        latest_file = max(article_files, key=lambda f: Path(f).stat().st_mtime)
        print(f"\n🔍 找到最新文章: {Path(latest_file).name}")

        result = analyze_article_file(latest_file)
        save_analysis_results([result])

        # 打印详细报告
        analyzer = ContentAnalyzer()
        print("\n" + analyzer.format_analysis_report(result['content_analysis']))

    elif choice == '4':
        print("👋 再见!")
        return

    else:
        print("❌ 无效的选项")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
