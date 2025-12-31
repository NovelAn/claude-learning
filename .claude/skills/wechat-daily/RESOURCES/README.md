# /wechat-daily Skill - 完整使用指南

## 目录

1. [简介](#简介)
2. [系统要求](#系统要求)
3. [安装步骤](#安装步骤)
4. [快速开始](#快速开始)
5. [详细使用说明](#详细使用说明)
6. [脚本详解](#脚本详解)
7. [常见问题](#常见问题)
8. [输出示例](#输出示例)
9. [后续开发计划](#后续开发计划)

---

## 简介

`/wechat-daily` 是一个用于分析微信公众号文章并生成热点报告的 Claude Code 自定义 Skill。

### 核心功能

- ✅ **文章抓取**: 从微信公众号文章 URL 抓取内容和元数据
- ✅ **关键词提取**: 使用 jieba 进行中文分词和关键词提取
- ✅ **话题识别**: 识别热点话题和相关文章
- ✅ **数据统计**: 分析文章字数、发布时间、公众号分布等
- ✅ **报告生成**: 自动生成 Markdown 格式的分析报告

### 适用场景

- 监控特定领域（如时尚、AI、科技）的公众号文章
- 分析特定公众号的内容表现
- 追踪热点话题和趋势
- 定期生成行业分析报告

---

## 系统要求

### Python 环境

- Python 3.7 或更高版本
- pip 包管理器

### 依赖库

```bash
requests          # HTTP 请求
beautifulsoup4    # HTML 解析
markdownify       # HTML 转 Markdown
jieba             # 中文分词
scikit-learn      # 机器学习（可选）
pandas            # 数据分析（可选）
numpy             # 数值计算（可选）
jinja2            # 模板引擎
```

---

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install requests beautifulsoup4 markdownify jieba jinja2
```

**可选依赖**（用于高级分析）：

```bash
pip install scikit-learn pandas numpy
```

### 2. 验证安装

```bash
python --version
python -c "import jieba; print('jieba installed successfully')"
```

### 3. 准备工作目录

确保以下目录结构存在：

```
data/
├── articles/    # 存储抓取的文章（JSON格式）
└── reports/     # 存储生成的报告（Markdown格式）
```

Skill 会自动创建这些目录。

---

## 快速开始

### 步骤 1: 准备微信公众号文章 URL

示例 URL：
```
https://mp.weixin.qq.com/s/xxxxxxxxxxxxxx
https://mp.weixin.qq.com/s/yyyyyyyyyyyyyy
```

### 步骤 2: 使用 Skill

在 Claude Code 中输入：

```
/wechat-daily
```

然后提供文章 URL。

### 步骤 3: 查看报告

报告将保存在 `data/reports/weekly-report-YYYY-WNN.md`

---

## 详细使用说明

### 使用方式一：直接提供文章 URL

```
请分析这些微信文章：

https://mp.weixin.qq.com/s/xxxxx
https://mp.weixin.qq.com/s/yyyyy
https://mp.weixin.qq.com/s/zzzzz
```

### 使用方式二：指定主题

```
/wechat-daily 主题:时尚奢品圈
```

然后提供相关文章 URL。

### 使用方式三：指定公众号

```
/wechat-daily 账号:时尚商业Daily,HYPEBEAST
```

然后提供这些账号的文章 URL。

---

## 脚本详解

### 1. fetch-articles.py - 文章抓取脚本

**功能**：
- 从微信公众号 URL 抓取文章内容
- 提取标题、作者、发布时间、正文等
- 保存为 JSON 格式

**使用方法**：

```bash
# 单个 URL
python fetch-articles.py https://mp.weixin.qq.com/s/xxxxx

# 多个 URL
python fetch-articles.py https://mp.weixin.qq.com/s/xxxxx https://mp.weixin.qq.com/s/yyyyy

# 从文件读取 URL
cat urls.txt | python fetch-articles.py -
```

**输出示例**：

```json
{
  "url": "https://mp.weixin.qq.com/s/xxxxx",
  "title": "文章标题",
  "content": "<div>...</div>",
  "content_text": "纯文本内容",
  "author": "作者名",
  "account_name": "公众号名称",
  "publish_time": 1234567890,
  "publish_time_str": "2025-12-31 10:00:00",
  "read_count": null,
  "like_count": null,
  "images": ["url1", "url2"],
  "fetched_at": "2025-12-31T15:00:00"
}
```

---

### 2. analyze-data.py - 数据分析脚本

**功能**：
- 加载已抓取的文章
- 使用 jieba 提取关键词
- 识别热点话题
- 统计分析数据

**使用方法**：

```bash
# 分析默认目录的文章
python analyze-data.py

# 指定文章目录
python analyze-data.py /path/to/articles
```

**输出文件**：

`data/analysis-YYYY-WUN.json`

**输出结构**：

```json
{
  "analyzed_at": "2025-12-31T15:00:00",
  "total_articles": 10,
  "total_content_chars": 50000,
  "keywords": [
    {"word": "奢侈品", "score": 0.85},
    {"word": "可持续发展", "score": 0.72}
  ],
  "topics": [
    {
      "name": "奢侈品",
      "article_count": 5,
      "sample_articles": [...]
    }
  ],
  "statistics": {...},
  "insights": [...]
}
```

---

### 3. generate-report.py - 报告生成脚本

**功能**：
- 读取分析结果
- 生成 Markdown 格式报告
- 包含图表、表格和洞察

**使用方法**：

```bash
# 使用最新分析结果
python generate-report.py data/analysis-2025-W01.json

# 指定输出文件名
python generate-report.py data/analysis-2025-W01.json my-report.md
```

**报告结构**：

```markdown
# 微信公众号热点周报

## 📊 本周概况
## 🔥 热点话题排行
## 🔑 核心关键词
## 📱 公众号分析
## 📝 文章列表
## 💡 关键洞察
```

---

## 常见问题

### Q1: 如何获取微信公众号文章 URL？

**A**: 有以下几种方式：

1. **从微信公众号直接获取**
   - 打开文章
   - 点击右上角"..."
   - 选择"复制链接"

2. **从微信搜狗搜索获取**
   - 访问 https://weixin.sogou.com/
   - 搜索公众号或文章
   - 复制文章链接

3. **从浏览器地址栏复制**
   - 打开文章链接
   - 直接复制浏览器地址栏的 URL

### Q2: 为什么文章抓取失败？

**可能原因**：

1. **URL 不正确**
   - 确保 URL 以 `https://mp.weixin.qq.com/s/` 开头

2. **文章已删除或设为私密**
   - 在浏览器中尝试打开 URL 验证

3. **网络问题**
   - 检查网络连接
   - 某些地区可能需要代理

4. **反爬虫限制**
   - 频繁请求可能被限制
   - 建议添加延迟

### Q3: 关键词提取不准确怎么办？

**解决方案**：

1. **添加自定义词典**
   ```python
   import jieba
   jieba.load_userdict('custom_dict.txt')
   ```

2. **调整关键词数量**
   - 修改 `analyze-data.py` 中的 `top_k` 参数

3. **过滤停用词**
   - 在 `_load_stopwords()` 方法中添加更多停用词

### Q4: 如何分析历史文章？

**方法**：

1. 批量抓取历史文章 URL
2. 将所有 URL 保存到文件
3. 使用 `fetch-articles.py` 批量抓取
4. 运行 `analyze-data.py` 分析
5. 生成报告

### Q5: 能否自动化执行？

**Phase 1 (MVP)**：手动执行
**Phase 2+**：将支持 cron 定时任务

---

## 输出示例

### 生成的报告示例

```markdown
# 微信公众号热点周报

**报告周期**: 2025年第1周
**生成时间**: 2025-12-31 15:00:00

---

## 📊 本周概况

- **文章总数**: 15 篇
- **公众号数量**: 5 个
- **内容总字数**: 75,000 字
- **平均字数**: 5,000 字

---

## 🔥 热点话题排行

1. **奢侈品** - 相关文章 8 篇

   代表文章：
   - 2024奢侈品行业报告
   - 可持续发展：奢侈品的未来
   - 数字化转型案例

2. **AI技术** - 相关文章 5 篇

   代表文章：
   - AI在时尚零售的应用
   - 虚拟试穿技术发展
   - 智能客服系统

---

## 💡 关键洞察

- 最热门话题是「奢侈品」，共 8 篇相关文章
- 本次分析涵盖 5 个公众号
- 文章内容较为详实，平均字数超过2000
- 核心关键词为「奢侈品」
```

---

## 后续开发计划

### Phase 2: MCP 集成（第2周）

- [ ] 集成 Feishu Bitable MCP
- [ ] 云端数据存储
- [ ] 多人协作分析

### Phase 3: 高级分析（第3-4周）

- [ ] 趋势预测算法
- [ ] 内容质量评分
- [ ] 情感分析
- [ ] 数据可视化图表

### Phase 4: 自动化（第5周）

- [ ] 定时任务
- [ ] 自动监控
- [ ] 错误恢复

### Phase 5: 生产级系统（第6周+）

- [ ] 第三方 API 集成
- [ ] Web Dashboard
- [ ] 性能优化
- [ ] 完整文档

---

## 技术支持

### 获取帮助

1. 查看 `SKILL.md` 了解 Skill 详细说明
2. 检查错误消息和建议
3. 验证所有依赖已安装

### 反馈和贡献

这是学习项目的一部分，欢迎：
- 报告 Bug
- 提出改进建议
- 分享使用经验

---

## 许可证

本项目用于学习目的，遵循 MIT 许可证。

---

**文档版本**: 1.0.0
**最后更新**: 2025-12-31
**Skill Phase**: Phase 1 (MVP)
