# GrillRadar 快速开始指南

> 5 分钟内完成配置并运行！

## 🚀 三种配置方式

### 方式 1: 一键配置向导 ⭐推荐

**最简单的方式，适合所有用户：**

```bash
# Python 版本（跨平台，功能最全）
python setup_config.py

# Bash 版本（Linux/macOS）
./setup_config.sh
```

**向导会帮你：**
- ✅ 选择 LLM 提供商（Anthropic/OpenAI）
- ✅ 配置 API 密钥
- ✅ 选择模型和参数
- ✅ 自动生成 .env 文件
- ✅ 验证配置正确性
- ✅ 提供下一步指引

### 方式 2: 复制模板配置

**适合熟悉环境变量的用户：**

```bash
# 1. 复制模板
cp .env.example .env

# 2. 编辑配置
nano .env  # 或使用你喜欢的编辑器

# 3. 修改这一行（必需）
ANTHROPIC_API_KEY=your_api_key_here
```

### 方式 3: 使用环境变量

**适合生产环境和 Docker 部署：**

```bash
# 设置环境变量
export ANTHROPIC_API_KEY=your_api_key_here
export DEFAULT_LLM_PROVIDER=anthropic
export DEFAULT_MODEL=claude-sonnet-4

# 直接启动
python -m uvicorn app.main:app
```

---

## 📋 配置清单

### 必需配置

**至少配置一个 LLM 提供商：**

```bash
# Option A: Anthropic Claude (推荐)
ANTHROPIC_API_KEY=sk-ant-xxx

# Option B: OpenAI GPT
OPENAI_API_KEY=sk-xxx
```

### 推荐配置

```bash
# LLM 提供商
DEFAULT_LLM_PROVIDER=anthropic  # 或 openai

# 模型选择
DEFAULT_MODEL=claude-sonnet-4   # 或 gpt-4o

# 参数调优（可选）
LLM_TEMPERATURE=0.7            # 0.0-1.0
LLM_MAX_TOKENS=16000           # 8000-32000
LLM_TIMEOUT=120                # 秒
```

---

## 🎯 获取 API 密钥

### Anthropic Claude

1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 导航到 "API Keys"
4. 点击 "Create Key"
5. 复制密钥到配置文件

**国内用户：** 可使用 BigModel 等第三方服务
- 注册：https://open.bigmodel.cn/
- 配置方式见 [CONFIGURATION.md](../CONFIGURATION.md)

### OpenAI GPT

1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 导航到 https://platform.openai.com/api-keys
4. 点击 "Create new secret key"
5. 复制密钥到配置文件（只显示一次）

---

## ✅ 验证配置

### 方法 1: 使用测试工具

```bash
python setup_config.py --test
```

### 方法 2: 启动应用

```bash
python -m uvicorn app.main:app --reload

# 看到这条消息表示成功:
# ✅ Application configuration validated successfully
```

### 方法 3: API 端点测试

```bash
# 启动应用后
curl http://localhost:8000/api/config/status
```

---

## 🏃 启动应用

### 开发环境

```bash
# 标准启动（自动重载）
python -m uvicorn app.main:app --reload

# 指定端口
python -m uvicorn app.main:app --port 8080 --reload

# 调试模式
DEBUG=True python -m uvicorn app.main:app --log-level debug --reload
```

### 生产环境

```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker 部署

```bash
# 使用环境变量
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=xxx \
  -e DEFAULT_LLM_PROVIDER=anthropic \
  grillradar:latest

# 使用 .env 文件
docker run -p 8000:8000 --env-file .env grillradar:latest
```

---

## 📖 访问应用

启动成功后，访问：

- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health
- **配置状态**: http://localhost:8000/api/config/status

---

## 🆚 配置方式对比

| 方式 | 难度 | 时间 | 适用场景 |
|------|------|------|----------|
| **配置向导** | ⭐ | 5 分钟 | 新手、首次配置 |
| **复制模板** | ⭐⭐ | 2 分钟 | 熟悉配置文件 |
| **环境变量** | ⭐⭐⭐ | 1 分钟 | 生产部署、CI/CD |

---

## ❓ 常见问题速查

### Q: 我应该选择哪个 LLM？

**A:** Anthropic Claude (推荐)
- 更强的推理能力
- 更长的上下文（200K vs 128K）
- 更好的中文支持

### Q: 配置在哪里？

**A:** 按优先级：
1. 环境变量 (最高)
2. .env 文件
3. 默认值 (最低)

### Q: 配置修改后不生效？

**A:** 重启应用：
```bash
# Ctrl+C 停止应用
# 重新启动
python -m uvicorn app.main:app --reload
```

### Q: 如何切换模型？

**A:** 修改 .env 文件：
```bash
# 从 Sonnet 切换到 Opus
DEFAULT_MODEL=claude-opus-4

# 从 Claude 切换到 GPT
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
```

---

## 🔧 故障排除

### 问题：配置验证失败

```bash
# 1. 测试配置
python setup_config.py --test

# 2. 检查配置文件
cat .env | grep -E "(API_KEY|PROVIDER|MODEL)"

# 3. 查看详细日志
python -m uvicorn app.main:app --log-level debug
```

### 问题：API 密钥无效

```bash
# 1. 检查密钥格式
# Anthropic: sk-ant-xxx
# OpenAI: sk-xxx

# 2. 检查密钥有效性
# 登录对应平台验证

# 3. 重新配置
python setup_config.py
```

### 问题：模块未找到

```bash
# 安装依赖
pip install -r requirements.txt

# 或
pip install anthropic openai pydantic-settings
```

---

## 📚 深入学习

- **完整配置指南**: [CONFIGURATION.md](../CONFIGURATION.md)
- **API 文档**: http://localhost:8000/docs
- **项目 README**: [README.md](../README.md)
- **示例代码**: [examples/](../examples/)

---

## 🎉 下一步

配置完成后，你可以：

1. **生成第一份面试报告**
   ```bash
   # 使用 API
   curl -X POST http://localhost:8000/api/generate-report \
     -H "Content-Type: application/json" \
     -d @examples/sample_request.json
   ```

2. **探索 API 功能**
   - 访问 http://localhost:8000/docs
   - 查看所有可用端点

3. **自定义配置**
   - 调整 Temperature 参数
   - 修改领域配置（domains.yaml）
   - 调整模式配置（modes.yaml）

4. **查看示例**
   ```bash
   ls examples/
   # sample_request.json - API 请求示例
   # sample_report.md - 生成报告示例
   ```

---

**祝使用愉快！** 🚀

有问题？查看 [配置文档](../CONFIGURATION.md) 或提交 Issue
