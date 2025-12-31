---
name: wechat-daily
description: Analyze WeChat public account articles and generate weekly hot topic reports. Supports fetching articles from URLs, extracting keywords, analyzing trends, and generating markdown reports with insights.
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# WeChat Daily - 微信公众号热点分析 Skill

## Overview

The `/wechat-daily` skill helps you analyze WeChat public account articles and generate comprehensive weekly hot topic reports. It can fetch article content, extract keywords, identify trending topics, and generate structured markdown reports.

## When to Use This Skill

Use this skill when you need to:
- Analyze WeChat public account articles for specific topics (e.g., "时尚奢品圈", "AI发展")
- Monitor articles from specific accounts (e.g., "时尚商业Daily", "HYPEBEAST")
- Generate weekly reports with hot topic rankings and insights
- Extract and organize article metadata and content
- Track trending topics over time

## Examples

### Example 1: Analyze Articles by Topic
<example>
**Context**: User wants to analyze recent articles about "时尚奢品圈" (fashion luxury)

**User**: "/wechat-daily 主题:时尚奢品圈"

**Assistant**:
"I'll help you analyze WeChat articles about 时尚奢品圈. Please provide the article URLs you'd like me to analyze.

After fetching the articles, I'll:
1. Extract content and metadata
2. Identify trending keywords and topics
3. Generate a weekly hot topic report

Please share the WeChat article URLs (one per line or comma-separated)."
</example>

### Example 2: Analyze Articles by Account
<example>
**Context**: User wants to analyze articles from specific fashion accounts

**User**: "/wechat-daily 账号:时尚商业Daily,HYPEBEAST"

**Assistant**:
"I'll analyze articles from 时尚商业Daily and HYPEBEAST. Please provide the article URLs from these accounts.

Once I have the URLs, I'll:
1. Fetch all articles
2. Analyze content and extract key topics
3. Compare performance across accounts
4. Generate a comprehensive report

Share the article URLs to get started."
</example>

### Example 3: Analyze Specific Article URLs
<example>
**Context**: User has a list of WeChat article URLs to analyze

**User**: "Analyze these WeChat articles:
https://mp.weixin.qq.com/s/xxxxx
https://mp.weixin.qq.com/s/yyyyy
https://mp.weixin.qq.com/s/zzzzz"

**Assistant**:
"Perfect! I'll analyze these 3 WeChat articles. Let me fetch the content and generate a report.

**Analysis Process**:
1. ✅ Fetching articles...
2. ✅ Extracting content and metadata...
3. ✅ Analyzing keywords and topics...
4. ✅ Generating report...

**Report Generated**: `data/reports/weekly-report-2025-W01.md`

**Key Insights**:
- Top topics: 奢侈品, 可持续发展, 数字化转型
- Total articles: 3
- Average engagement: High

Report saved successfully!"
</example>

### Example 4: Generate Weekly Summary
<example>
**Context**: User wants a summary of articles analyzed this week

**User**: "/wechat-daily summary"

**Assistant**:
"Here's your weekly summary:

## 📊 Weekly Report - Week 2025-W01

**Articles Analyzed**: 15
**Top Topics**: 时尚奢品圈, AI发展
**Key Insights**:
- Luxury brands focusing on sustainability
- AI technology adoption accelerating

Full report available at: `data/reports/weekly-report-2025-W01.md`"
</example>

---

## Workflow

### Step 1: Input Collection
1. Parse user input to identify:
   - Input type: Topic keywords OR Account names OR Direct URLs
   - Topic or account names (if provided)
   - Article URLs

2. Validate input:
   - If URLs provided: Verify they are valid WeChat article URLs
   - If topic/account provided: Request article URLs from user

### Step 2: Data Fetching
1. Use `fetch-articles.py` to fetch article content
   - Script location: `.claude/skills/wechat-daily/SCRIPTS/fetch-articles.py`
   - Input: List of WeChat article URLs
   - Output: JSON files in `data/articles/`

2. Extract for each article:
   - Title
   - Content (markdown format)
   - Author
   - Account name
   - Publish time
   - Read count (if available)
   - Like count (if available)
   - Images

### Step 3: Data Analysis
1. Use `analyze-data.py` to process fetched articles
   - Script location: `.claude/skills/wechat-daily/SCRIPTS/analyze-data.py`
   - Input: Article JSON files from `data/articles/`
   - Output: Analysis JSON file

2. Perform analysis:
   - **Keyword Extraction**: Use jieba for Chinese word segmentation
   - **Topic Identification**: TF-IDF ranking
   - **Statistics**: Article count, average engagement, publication patterns

### Step 4: Report Generation
1. Use `generate-report.py` to create markdown report
   - Script location: `.claude/skills/wechat-daily/SCRIPTS/generate-report.py`
   - Input: Analysis JSON + Report template
   - Output: Markdown report in `data/reports/`

2. Report structure:
   ```markdown
   # 微信公众号热点周报

   ## 📊 本周概况
   - 文章总数: XX
   - 分析时间: YYYY-MM-DD

   ## 🔥 热点话题排行
   1. [话题] - 相关文章 XX 篇
      - 关键词: ...
      - 代表文章: ...

   ## 📈 文章数据分析
   - 总阅读量: ...
   - 平均点赞: ...
   - 发布时间分布: ...

   ## ⭐ 优质内容推荐
   Top 5 高质量文章列表

   ## 📝 所有文章列表
   Complete article listing
   ```

### Step 5: Output and Storage
1. Save generated report to `data/reports/`
2. Display summary to user
3. Provide file location for reference

---

## Project Context

This skill is part of the **Claude Code Mastery - Module 2.2: Custom Skills Creation** learning path.

**Learning Goals**:
- Understanding Skill structure and YAML configuration
- Implementing data processing workflows
- Integrating Python scripts with Skills
- Building practical content analysis tools

**Current Phase**: MVP (Minimum Viable Product)
- Manual URL input
- Local data storage
- Basic keyword extraction and reporting
- Future phases will add MCP integration, advanced analytics, and automation

---

## Error Handling

### Common Issues and Solutions

**Issue**: Invalid WeChat article URL
```
Error: The URL provided is not a valid WeChat article URL.
Solution: Ensure the URL starts with https://mp.weixin.qq.com/s/
```

**Issue**: Article fetch failed
```
Error: Unable to fetch article content. The article may be deleted or access-restricted.
Solution:
1. Verify the article is publicly accessible
2. Check if the URL is complete and correct
3. Try opening the URL in a browser first
```

**Issue**: No keywords extracted
```
Warning: No significant keywords found in the articles.
Solution:
1. Ensure articles have sufficient text content
2. Check if articles are in Chinese (for jieba segmentation)
3. Try with more articles for better analysis
```

**Issue**: Python dependencies missing
```
Error: ModuleNotFoundError: No module named 'jieba'
Solution: Install required dependencies:
pip install requests beautifulsoup4 markdownify jieba scikit-learn pandas numpy jinja2
```

---

## File Structure

```
.claude/skills/wechat-daily/
├── SKILL.md                    # This file - Main skill definition
├── SCRIPTS/
│   ├── fetch-articles.py       # Fetch article content from URLs
│   ├── analyze-data.py         # Analyze articles and extract topics
│   └── generate-report.py      # Generate markdown reports
├── TEMPLATES/
│   └── weekly-report.md        # Report template
└── RESOURCES/
    └── README.md               # Detailed documentation

data/
├── articles/                   # Fetched articles (JSON)
└── reports/                    # Generated reports (Markdown)
```

---

## Usage Tips

1. **Batch Processing**: You can provide multiple URLs at once for batch analysis
2. **Regular Analysis**: Use this skill weekly to track trending topics over time
3. **Custom Topics**: Specify any topic or account name to focus your analysis
4. **Report Storage**: All reports are saved locally in `data/reports/` for future reference

---

## Future Enhancements (Planned for Later Phases)

- [ ] Phase 2: Feishu Bitable integration for cloud storage
- [ ] Phase 2: MCP server integration for automated data fetching
- [ ] Phase 3: Advanced analytics with trend prediction
- [ ] Phase 3: Content quality scoring
- [ ] Phase 4: Automated weekly scheduling
- [ ] Phase 5: Third-party WeChat API integration

---

## Getting Started

To use this skill:

1. **Install Python dependencies**:
   ```bash
   pip install requests beautifulsoup4 markdownify jieba scikit-learn pandas numpy jinja2
   ```

2. **Prepare article URLs**:
   - Collect WeChat article URLs you want to analyze
   - Ensure URLs are publicly accessible

3. **Invoke the skill**:
   - Use `/wechat-daily` followed by your topic or account names
   - Or simply provide article URLs directly

4. **Review the report**:
   - Check `data/reports/` for the generated markdown report
   - Review insights and topic rankings

---

## Support

For issues or questions:
- Check the detailed documentation in `RESOURCES/README.md`
- Review error messages in the console
- Ensure all Python dependencies are installed
- Verify article URLs are accessible

---

**Skill Version**: 1.0.0 (Phase 1 MVP)
**Last Updated**: 2025-12-31
**Learning Path**: Module 2.2 - Custom Skills Creation
