#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/wechat-daily Skill 主入口
用于微信公众号文章抓取、分析和报告生成的完整工作流
依赖：极致了数据API获取互动数据（需要提供API密钥）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from article_fetcher import WeChatArticleFetcher
from report_generator import WeChatReportGenerator
from config import ERROR_MESSAGES, DATA_CONFIG

def main():
    """主程序入口"""

    print("🎯 欢迎使用 /wechat-daily Skill")
    print("="*60)
    print("微信公众号热点分析与报告生成工具")
    print("="*60 + "\n")

    # 1. 加载配置
    api_key = load_api_key()
    if not api_key:
        print(ERROR_MESSAGES['no_api_key'])
        return

    # 2. 交互模式 - 让用户选择操作
    while True:
        print("\n请选择一个操作：")
        print("1. 🔍 抓取并分析单篇文章")
        print("2. 📚 批量处理文章列表")
        print("3. 📊 生成周报分析报告")
        print("4. 🔧 修改配置/API密钥")
        print("5. ❌ 退出")

        choice = input("\n请输入选项（1-5）: ").strip()

        if choice == '1':
            handle_single_article(api_key)
        elif choice == '2':
            handle_batch_articles(api_key)
        elif choice == '3':
            generate_report()
        elif choice == '4':
            api_key = update_api_key()
        elif choice == '5':
            print("\n感谢您的使用！欢迎再次体验 /wechat-daily ✨")
            break
        else:
            print("❌ 请输入有效的选项！")

def load_api_key() -> str:
    """加载API密钥"""
    # 优先从环境变量读取
    import os
    api_key = os.environ.get('JIZHILA_API_KEY', '')

    if api_key:
        print("✅ 已检测到环境变量中的API密钥")
        return api_key

    # 从配置文件读取备用方案
    try:
        import json
        config_path = DATA_CONFIG['external_reports_dir'].replace('/external-reports', '') + '/config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                api_key = config.get('jizhila_api_key', '')
                if api_key:
                    print("✅ 已从配置文件读取API密钥")
                    return api_key
    except:
        pass

    print("⚠️  未找到API密钥，正在使用模拟模式")
    return ''

def handle_single_article(api_key: str):
    """处理单个文章分析"""
    print("\n" + "="*50)
    print("🔍 单篇文章抓取分析")
    print("="*50)

    url = input("请输入微信公众号文章URL: ").strip()

    if not url.startswith('https://mp.weixin.qq.com/'):
        print("❌ 请输入有效的微信公众号文章链接")
        return

    print(f"\n开始抓取: {url}")

    # 创建抓取器
    fetcher = WeChatArticleFetcher(api_key)

    try:
        article = fetcher.fetch_article(url)

        if article:
            print(f"\n🎉抓取成功!")
            print(f"📄标题: {article['title']}")
            print(f"🏢账号: {article['account_name']}")
            print(f"📊热度指数: {article['hot_index']}/100")

            # 显示关键数据
            interaction = article.get('interaction_data', {})
            print(f"\n💫 互动数据:")
            print(f"  📖 阅读量: {interaction.get('read_count', 'N/A'):,}")
            print(f"  👍 点赞数: {interaction.get('like_count', 'N/A'):,}")
            print(f"  📊点赞率: {(interaction.get('like_count', 0) / interaction.get('read_count', 1) * 100):.2f}%" if interaction else "N/A")

            # 生成单篇文章报告
            generator = WeChatReportGenerator()
            report_path = generator.generate_article_report(article)
            print(f"\n📑单篇文章报告已生成: {report_path}")
        else:
            print("\n❌ 抓取失败，请检查URL是否正确")

    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

def handle_batch_articles(api_key: str):
    """批量处理文章"""
    print("\n" + "="*50)
    print("📚 批量文章处理")
    print("="*50)

    print("\n请提供微信公众号文章URL列表（每行一个或逗号分隔）：")
    print("示例: https://mp.weixin.qq.com/s/xxxxx")

    urls_input = input("\n输入文章URL: ").strip()

    # 解析URL
    import re
    urls = re.findall(r'https://mp\.weixin\.qq\.com/s/\w+', urls_input)

    if not urls:
        print("❌ 未检测到有效的微信公众号文章URL")
        return

    print(f"\n检测到 {len(urls)} 个文章链接，开始批量处理...")

    fetcher = WeChatArticleFetcher(api_key)

    try:
        results = fetcher.fetch_multiple(urls)

        if results:
            print(f"\n✅ 批量处理完成：{len(results)}/{len(urls)} 成功")

            # 生成汇总报告
            generator = WeChatReportGenerator()
            report_path = generator.generate_weekly_report(results)

            print(f"\n📝周报已生成: {report_path}")

            # 显示汇总信息
            total_reads = sum(r.get('interaction_data', {}).get('read_count', 0) for r in results)
            print(f"\n📈 数据汇总:")
            print(f"    总阅读量: {total_reads:,}")
            print(f"    平均热度: {sum(r.get('hot_index', 0) for r in results) / len(results):.1f}/100")
            print(f"    热门主题: {len(list(set([t['term'] for r in results for t in r.get('key_topics', [])])))} 个")
        else:
            print("\n❌ 批量处理失败")
    except Exception as e:
        print(f"\n❌ 批量处理出错: {e}")

def generate_report():
    """生成报告"""
    import json
    import os

    articles_dir = DATA_CONFIG['articles_dir']

    print("\n" + "="*50)
    print("📊 生成数据分析报告")
    print("="*50)

    # 查找所有文章文件
    if not os.path.exists(articles_dir):
        print(f"❌ 未找到文章数据目录: {articles_dir}")
        return

    article_files = [f for f in os.listdir(articles_dir)
                    if f.endswith('.json') and 'article' in f]

    if not article_files:
        print("😴 未发现已抓取的文章数据，请先抓取一些文章")
        return

    print(f"共有 {len(article_files)} 篇文章可生成报告")

    articles = []
    for file in article_files:
        file_path = os.path.join(articles_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                article = json.load(f)
                articles.append(article)
        except:
            print(f"⚠️  加载文件失败: {file}")

    if not articles:
        print("❌ 没有有效的文章数据")
        return

    print(f"\n正在分析 {len(articles)} 篇文章...")
    generator = WeChatReportGenerator()
    report_path = generator.generate_weekly_report(articles)

    if report_path:
        print(f"\n🎉 周报已生成! ⚡️")
        print(f"📖 总阅读量统计: {sum(a.get('interaction_data', {}).get('read_count', 0) for a in articles):,}")
        print(f"📄 报告文件: {report_path}")
        print("\n💡用浏览器打开报告文件，查看可视化分析结果")
    else:
        print("❌报告生成失败")

def update_api_key():
    """更新API密钥"""
    print("\n" + "="*50)
    print("🔧 更新API密钥")
    print("="*50)
    print("\n您可以输入两种方式:")
    print("1. 直接输入完整的API密钥")
    print("2. 输入 'env' 使用环境变量模式")
    print("3. 回车取消修改")

    new_key = input("\nNew API Key: ").strip()

    if not new_key:
        return ''

    if new_key == 'env':
        print("\n✅ 已切换到环境变量模式")
        print("请运行: export JIZHILA_API_KEY='你的真实密钥'")
        return ''

    # 保存到配置文件
    import json
    config_path = DATA_CONFIG['external_reports_dir'].replace('/external-reports', '') + '/config.json'

    try:
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

        config['jizhila_api_key'] = new_key

        # 注意：密钥将保存在本地，注意文件安全
        import getpass
        confirm = input(f"\n⚠️ 密钥将保存到 {config_path}，确认保存吗?(y/N): ")
        if confirm.lower() == 'y':
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ API密钥更新成功")
            return new_key
        else:
            print("已取消保存")
            return ''
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return ''

if __name__ == '__main__':
    main()