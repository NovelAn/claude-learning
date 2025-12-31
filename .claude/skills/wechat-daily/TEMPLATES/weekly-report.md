# 微信公众号热点周报

**报告周期**: {{ year }}年第{{ week_num }}周
**生成时间**: {{ generation_time }}

---

## 📊 本周概况

- **文章总数**: {{ total_articles }} 篇
- **公众号数量**: {{ total_accounts }} 个
- **内容总字数**: {{ total_chars }} 字
- **平均字数**: {{ avg_chars }} 字

---

## 🔥 热点话题排行

{% for topic in topics %}
{{ loop.index }}. **{{ topic.name }}** - 相关文章 {{ topic.article_count }} 篇

   代表文章：
   {% for article in topic.sample_articles %}
   - {{ article.title }}
   {% endfor %}

{% endfor %}

---

## 🔑 核心关键词

| 排名 | 关键词 | 权重 |
|------|--------|------|
{% for kw in keywords %}
| {{ loop.index }} | {{ kw.word }} | {{ kw.score }} |
{% endfor %}

---

## 📱 公众号分析

### 最活跃公众号

{% for account in top_accounts %}
{{ loop.index }}. **{{ account.account }}** - {{ account.count }} 篇文章
{% endfor %}

---

## 📝 文章列表

| # | 标题 | 公众号 | 发布时间 | 字数 |
|---|------|--------|----------|------|
{% for article in articles %}
| {{ loop.index }} | {{ article.title }} | {{ article.account }} | {{ article.publish_time }} | {{ article.content_length }} |
{% endfor %}

---

## 💡 关键洞察

{% for insight in insights %}
- {{ insight }}
{% endfor %}

---

*本报告由 /wechat-daily Skill 自动生成*
*数据来源: 微信公众号文章*
