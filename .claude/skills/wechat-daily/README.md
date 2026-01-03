# /wechat-daily Skill 配置说明

## 🔑 API密钥配置（跨平台）

### 快速配置（3步）

1. **编辑 `.env` 文件**
   ```bash
   cd .claude/skills/wechat-daily
   nano .env  # Mac/Linux
   notepad .env  # Windows
   ```

2. **填入你的API密钥**
   ```env
   JIZHILA_API_KEY=your_actual_api_key_here
   ```

3. **保存即可使用** ✅

---

## 📁 配置文件位置

```
.claude/skills/wechat-daily/
├── .env                 ← 你的API密钥（已配置）
├── .env.example         ← 配置模板
├── .gitignore           ← 忽略敏感文件
└── config.py            ← 自动加载.env
```

---

## 🎯 工作原理

程序启动时自动查找 `.env` 文件（无需手动配置环境变量）：

**优先级**：
1. ✅ `.env` 文件（推荐）
2. ✅ 环境变量 `JIZHILA_API_KEY`（可选）

---

## 🧪 验证配置

运行诊断脚本：
```bash
python3 .claude/skills/wechat-daily/SCRIPTS/check_env.py
```

---

## 📖 获取API密钥

1. 访问 [极致了数据](https://www.dajiala.com/main/interface)
2. 注册账号（新用户有免费额度）
3. 获取API密钥
4. 填入 `.env` 文件

---

## 🌐 跨平台支持

- ✅ **macOS**: 直接使用 `.env` 文件
- ✅ **Windows**: 直接使用 `.env` 文件
- ✅ **Linux**: 直接使用 `.env` 文件

**无需配置系统环境变量！**

---

## 🔒 安全提示

- ✅ `.env` 已加入 `.gitignore`，不会提交到 Git
- ✅ 不要分享你的 `.env` 文件
- ✅ 定期更换API密钥

---

**最后更新**: 2026-01-04
