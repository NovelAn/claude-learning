# 📝 智能内容分析 - 快速开始指南

## 功能概述

智能内容分析模块使用 **DeepSeek API** 对微信公众号文章进行深度文本分析，提取关键信息并生成结构化报告。

## 为什么选择 DeepSeek？

- ✅ **中文优化**：在中文文本分析上表现优于OpenAI
- ✅ **性价比高**：约 ¥1/百万tokens（OpenAI约$15/百万tokens）
- ✅ **兼容性强**：完全兼容OpenAI SDK，无需学习新接口
- ✅ **本地服务**：国内访问稳定，响应快速

## 核心功能

### 1. 文章摘要生成 ✍️
- 自动生成300字以内的精炼摘要
- 突出核心信息和价值点
- 语言简洁专业

### 2. 核心观点提炼 💡
- 提取3-5个最重要的观点或论点
- 按重要性排序
- 每个观点一句话概括

### 3. 关键数据标注 📊
- 识别财务数据（营收/利润/市值）
- 标注百分比和增长率
- 提取时间相关数据
- 提供上下文信息

### 4. 品牌实体识别 🏢
- 识别品牌名称（Gucci/Prada等）
- 识别公司实体（LVMH等）
- 识别关键人物
- 自动分类标注

### 5. 行动建议提炼 ✅
- 提炼可操作的建议
- 提供行业启示
- 3-5条具体建议

## 使用方式

### 方式一：独立内容分析（推荐）

如果只需要对已抓取的文章进行内容分析：

```bash
cd /Users/novel/Documents/trae_projects/claude-learning/.claude/skills/wechat-daily/SCRIPTS
python analyze_content.py
```

选择操作：
- **1**: 分析单篇文章（需要提供JSON文件路径）
- **2**: 批量分析所有文章
- **3**: 分析最新的一篇文章

### 方式二：集成到数据抓取流程

使用 `main.py` 或 `article_fetcher.py` 时，会自动进行内容分析：

```bash
python main.py
# 选择 1. 分析单篇文章
```

## 配置说明

### DeepSeek API配置（推荐）

在 `.env` 文件中添加DeepSeek API密钥：

```bash
# 在 .claude/skills/wechat-daily/.env 文件中添加
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**获取DeepSeek API密钥：**

1. 访问 [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. 注册并登录账号
3. 进入"API Keys"页面
4. 点击"创建API密钥"
5. 复制密钥到 `.env` 文件

**费用估算：**
- 约 ¥0.001-0.005/篇文章
- 使用 deepseek-chat 模型（性价比极高）
- 具体取决于文章长度

**OpenAI API（可选）：**

如果更喜欢使用OpenAI，也可以配置：

```bash
# 在 .env 文件中添加
OPENAI_API_KEY=your_openai_api_key_here
```

系统会优先使用DeepSeek API，如果未配置则使用OpenAI。

## 输出示例

### 分析报告格式

```json
{
  "content_analysis": {
    "summary": "文章核心摘要...",
    "key_insights": [
      "核心观点1",
      "核心观点2",
      "核心观点3"
    ],
    "data_points": [
      {
        "value": "2.3",
        "unit": "亿欧元",
        "category": "财务数据",
        "context": "..."
      }
    ],
    "entities": [
      {
        "name": "Ferragamo",
        "type": "品牌",
        "description": "检测到Ferragamo相关内容"
      }
    ],
    "recommendations": [
      "建议1",
      "建议2"
    ]
  }
}
```

### 控制台输出

```
🔍 开始智能内容分析...
   标题: 突发 | Ferragamo与中国长期伙伴股东协议到期不续
   内容长度: 1234 字符

📝 1/5 生成文章摘要...
💡 2/5 提取核心观点...
📊 3/5 标注关键数据...
🏢 4/5 识别品牌/公司/人物...
✅ 5/5 提炼行动建议...

✅ 内容分析完成!
   ✅ 智能分析完成: 4个观点, 6个数据点
```

## 技术架构

### 模块结构

```
content_analyzer.py       # 核心分析类
├── _generate_summary()          # 摘要生成
├── _extract_key_insights()      # 观点提取
├── _extract_data_points()       # 数据标注
├── _extract_entities()          # 实体识别
└── _extract_recommendations()   # 建议提炼

analyze_content.py        # 独立分析脚本
├── analyze_article_file()       # 单篇分析
├── analyze_batch()              # 批量分析
└── save_analysis_results()      # 保存结果
```

### 降级方案

当OpenAI API不可用时：
- ✅ 使用首尾段生成简单摘要
- ✅ 规则匹配提取数字数据
- ✅ 使用预定义品牌库识别实体
- ✅ 编号列表解析提取观点

## 常见问题

### Q: 必须配置OpenAI API吗？
A: 不是必须的。系统有完整的降级方案，即使不配置也能进行基础分析。

### Q: 内容分析和数据抓取的关系？
A: 完全独立。可以单独运行内容分析，不调用极致了API。

### Q: 分析结果保存在哪里？
A:
- 单篇文章分析：与原始文章数据保存在同一个JSON文件
- 批量分析：保存为独立的 `content-analysis-TIMESTAMP.json` 文件

### Q: 支持哪些文章类型？
A: 适用于所有微信公众号文章，特别适合：
- 奢侈品/时尚行业
- 商业财经类内容
- 市场分析报告

## 下一步

内容分析完成后，可以：
1. 使用 `report_generator.py` 生成可视化报告
2. 批量分析多篇文章进行趋势分析
3. 导出数据用于进一步研究

---

*版本: 3.3.0*
*更新时间: 2025-01-04*
*使用DeepSeek API进行智能内容分析*
