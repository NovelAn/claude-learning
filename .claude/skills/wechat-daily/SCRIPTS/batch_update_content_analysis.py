#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新文章内容分析
遍历 articles 文件夹下的所有文章，使用新的 ContentAnalyzer 进行分析
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

from content_analyzer import ContentAnalyzer
from config import DEEPSEEK_CONFIG


def load_article_files(articles_dir):
    """加载所有文章JSON文件"""
    articles_dir = Path(articles_dir)
    article_files = list(articles_dir.glob('article-*.json'))
    return sorted(article_files)


def update_article_analysis(article_file, analyzer):
    """
    更新单篇文章的内容分析

    Args:
        article_file: 文章JSON文件路径
        analyzer: ContentAnalyzer实例

    Returns:
        dict: 更新后的文章数据
    """
    print(f"\n{'='*80}")
    print(f"📄 处理文件: {article_file.name}")
    print('='*80)

    # 读取文章数据
    with open(article_file, 'r', encoding='utf-8') as f:
        article_data = json.load(f)

    print(f"📝 标题: {article_data.get('title', 'N/A')[:60]}...")
    print(f"🏢 账号: {article_data.get('account_name', 'N/A')}")

    # 检查是否有 content_text
    content_text = article_data.get('content_text', '')
    if not content_text:
        print("   ⚠️  文章没有 content_text，跳过")
        return None

    print(f"   📄 内容长度: {len(content_text)} 字符")

    # 删除旧的字段
    removed_fields = []
    if 'key_topics' in article_data:
        del article_data['key_topics']
        removed_fields.append('key_topics')

    if 'content_analysis' in article_data:
        old_analysis = article_data['content_analysis']
        # 删除旧的分析字段，但保留其他重要字段
        del article_data['content_analysis']
        removed_fields.append('content_analysis')

    if removed_fields:
        print(f"   🗑️  删除旧字段: {', '.join(removed_fields)}")

    # 执行新的内容分析
    print(f"\n🔍 执行智能内容分析...")
    try:
        new_analysis = analyzer.analyze_article(article_data)

        # 添加新的分析结果
        article_data['content_analysis'] = new_analysis
        article_data['analysis_type'] = f'ai_powered_{new_analysis.get("model_used", "deepseek")}'
        article_data['analysis_updated_at'] = datetime.now().isoformat()

        # 显示分析结果摘要
        print(f"\n✅ 分析完成:")
        print(f"   📝 摘要长度: {len(new_analysis.get('summary', ''))} 字符")
        print(f"   💡 核心观点: {len(new_analysis.get('key_insights', []))} 条")
        print(f"   📊 关键数据: {len(new_analysis.get('data_points', []))} 个")
        print(f"   🏢 识别实体: {len(new_analysis.get('entities', []))} 个")
        print(f"   ✅ 行动建议: {len(new_analysis.get('recommendations', []))} 条")

        return article_data

    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_updated_article(article_data, output_file):
    """保存更新后的文章数据"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)
    print(f"   💾 已保存: {output_file}")


def batch_update_articles(articles_dir, backup=True):
    """
    批量更新所有文章的内容分析

    Args:
        articles_dir: 文章目录路径
        backup: 是否创建备份
    """
    articles_dir = Path(articles_dir)

    if not articles_dir.exists():
        print(f"❌ 目录不存在: {articles_dir}")
        return

    # 加载所有文章文件
    article_files = load_article_files(articles_dir)

    if not article_files:
        print(f"❌ 未找到文章文件: {articles_dir}/article-*.json")
        return

    print(f"\n🔍 找到 {len(article_files)} 篇文章")

    # 创建备份目录
    if backup:
        backup_dir = articles_dir.parent / 'articles_backup' / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 备份目录: {backup_dir}")

    # 创建内容分析器
    print(f"\n🔧 初始化 ContentAnalyzer...")
    analyzer = ContentAnalyzer(
        api_key=DEEPSEEK_CONFIG.get('api_key'),
        base_url=DEEPSEEK_CONFIG.get('base_url'),
        model=DEEPSEEK_CONFIG.get('model')
    )

    # 统计信息
    stats = {
        'total': len(article_files),
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    # 处理每篇文章
    for i, article_file in enumerate(article_files, 1):
        print(f"\n[{i}/{stats['total']}] 处理中...")

        try:
            # 备份原文件
            if backup:
                import shutil
                backup_file = backup_dir / article_file.name
                shutil.copy2(article_file, backup_file)
                print(f"   📦 已备份到: {backup_file.name}")

            # 更新文章分析
            updated_data = update_article_analysis(article_file, analyzer)

            if updated_data:
                # 保存更新后的数据
                save_updated_article(updated_data, article_file)
                stats['success'] += 1
            else:
                stats['skipped'] += 1

        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            stats['failed'] += 1
            continue

    # 打印统计信息
    print("\n" + "="*80)
    print("📊 批量更新完成统计")
    print("="*80)
    print(f"总文章数: {stats['total']}")
    print(f"✅ 成功更新: {stats['success']}")
    print(f"⏭️  跳过: {stats['skipped']}")
    print(f"❌ 失败: {stats['failed']}")

    if backup:
        print(f"\n📦 备份位置: {backup_dir}")

    print("\n✨ 批量更新完成!")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         🔄 批量更新文章内容分析                              ║
║         使用新的 DeepSeek ContentAnalyzer                    ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 确认API配置
    if not DEEPSEEK_CONFIG.get('api_key'):
        print("⚠️  未配置DeepSeek API密钥")
        print("   将使用降级方案（基础规则分析）")
        response = input("\n是否继续？(y/n): ").strip().lower()
        if response != 'y':
            print("👋 操作取消")
            return
    else:
        print("✅ DeepSeek API已配置")
        cost_estimate = DEEPSEEK_CONFIG.get('max_tokens', 2000) * 0.000001  # 粗略估算
        print(f"   预估成本: 约 ¥{cost_estimate:.4f}/篇")

    # 设置文章目录
    from config import DATA_CONFIG
    articles_dir = DATA_CONFIG['articles_dir']

    print(f"\n📂 文章目录: {articles_dir}")

    # 确认操作
    print("\n⚠️  此操作将:")
    print("   1. 遍历所有文章文件")
    print("   2. 删除旧的 key_topics 和 content_analysis 字段")
    print("   3. 使用新的 ContentAnalyzer 生成内容分析")
    print("   4. 自动备份原文件")

    response = input("\n是否继续？(y/n): ").strip().lower()
    if response != 'y':
        print("👋 操作取消")
        return

    # 执行批量更新
    batch_update_articles(articles_dir, backup=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
