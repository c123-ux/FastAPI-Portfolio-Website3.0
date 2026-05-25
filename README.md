# FastAPI 个人作品集网站 v3.0

这是一个使用 **FastAPI + SQLAlchemy + JWT** 构建的全栈个人作品集网站，采用生产级模块化架构。项目经过全面重构升级至 v3.0，引入了 6 层架构设计、安全加固、速率限制、审计日志等企业级特性。

---

##  v3.0 新增功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 🏗️ **6 层模块化架构** | ✅ 已完成 | models/schemas/routers/services/middleware/utils |
|  **JWT 双 Token 认证** | ✅ 已完成 | Access Token (15min) + Refresh Token (7天) |
| ️ **CORS 白名单模式** | ✅ 已完成 | 生产环境禁用 `*`，仅允许指定域名 |
| ⚡ **速率限制中间件** | ✅ 已完成 | 登录 5次/分、留言 10次/分、验证码 20次/分 |
|  **密码强度校验** | ✅ 已完成 | ≥8位 + 大写字母 + 数字 + 特殊字符 |
| 📝 **审计日志系统** | ✅ 已完成 | 所有管理员操作可追溯 |
| ✅ **XSS 防护** | ✅ 已完成 | HTML 转义，防止脚本注入 |
| 🗄️ **SQLAlchemy 异步 ORM** | ✅ 已完成 | 支持 SQLite/PostgreSQL |
|  **Pydantic V2 数据验证** | ✅ 已完成 | 类型安全、自动文档生成 |
| 🧪 **自动化测试覆盖** | ✅ 已完成 | pytest + TestClient |
| 🚢 **Docker Compose 多环境** | ✅ 已完成 | 开发环境 + 生产环境配置 |
| 🌙 **暗黑模式** | ✅ 已完成 | 前端和管理后台都支持 |
| 📥 **CSV 数据导出** | ✅ 已完成 | Bearer Token 认证下载 |
|  **访客统计面板** | ✅ 已完成 | 实时追踪访客、浏览量、留言统计 |

---

## 📁 项目结构（v3.0）

```
FastAPI-Portfolio-Website3.0/
├── backend/                          # v3.0 模块化后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 应用入口
│   │   ├── config.py                 # pydantic-settings 配置
│   │   ├── database.py               # SQLAlchemy 异步引擎
│   │   ├── dependencies.py           # 依赖注入
│   │   ├── middleware/               # 中间件层
│   │   │   ├── __init__.py
│   │   │   └── rate_limit.py         # 速率限制中间件
│   │   ├── models/                   # ORM 模型层
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── contact.py            # 留言模型
│   │   │   └── audit.py              # 审计日志模型
│   │   ├── schemas/                  # Pydantic 模型层
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # 认证相关模型
│   │   │   ├── contact.py            # 留言相关模型
│   │   │   └── common.py             # 通用响应模型
│   │   ├── routers/                  # 路由层
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # 认证路由
│   │   │   ├── contacts.py           # 留言路由
│   │   │   ├── admin.py              # 管理员路由
│   │   │   ├── admin_frontend.py     # 管理后台页面
│   │   │   ── stats.py              # 统计路由
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # 认证服务
│   │   │   ├── contact_service.py    # 留言服务
│   │   │   ├── captcha_service.py    # 验证码服务
│   │   │   ├── email_service.py      # 邮件服务
│   │   │   └── audit_service.py      # 审计服务
│   │   └── utils/                    # 工具层
│   │       ├── __init__.py
│   │       ├── jwt.py                # JWT 工具（python-jose）
│   │       ├── security.py           # 密码加密（bcrypt）
│   │       └── validators.py         # 数据验证
│   ├── tests/                        # 测试目录
│   │   ├── __init__.py
│   │   ├── conftest.py               # pytest 配置
│   │   ├── test_auth.py              # 认证测试
│   │   ├── test_contacts.py          # 留言测试
│   │   └── test_security.py          # 安全测试
│   ├── alembic/                      # 数据库迁移
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial_migration.py
│   ├── alembic.ini                   # Alembic 配置
│   ├── requirements.txt              # 生产依赖
│   ├── requirements-dev.txt          # 开发依赖
│   └── Dockerfile                    # 后端 Docker 镜像
├── index.html                        # 前端主页面
├── style.css                         # 前端样式
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git 忽略规则
├── README.md                         # 项目说明（本文件）
├── DEPLOYMENT.md                     # 部署指南
├── TEST_REPORT.md                    # 测试报告
├── railway.yaml                      # Railway 部署配置
├── docker-compose.yml                # Docker 开发环境
└── docker-compose.prod.yml           # Docker 生产环境
```

---

## 🚀 完整运行教程（小白友好）

### 第一步：确认 Python 环境

打开 PowerShell，检查 Python 版本（需要 3.8+）：

```powershell
python --version
```

如果显示类似 `Python 3.11.x` 就可以继续。

---

### 第二步：进入项目目录并激活虚拟环境

```powershell
cd D:\PythonProject1-v3
```

激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

> **注意**：如果提示权限错误，需要先执行一次：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

### 第三步：安装后端依赖

```powershell
cd backend
pip install -r requirements.txt
```

等待安装完成（首次可能需要几分钟）。

---

### 第四步：启动后端服务

```powershell
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)"
```

**启动成功的标志**：看到以下日志
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

> **注意**：PowerShell 不支持 `&&` 命令分隔符，必须使用上述方式。

---

### 第五步：验证后端是否正常

打开浏览器访问：http://127.0.0.1:8000/api/v1/health

应该看到：
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "database": "connected"
}
```

---

### 第六步：打开前端页面

**方法 1：PyCharm 右键打开（推荐）**
- 在 PyCharm 中右键 `index.html` → Open in Browser

**方法 2：直接双击打开**
- 直接双击 `index.html` 文件

**方法 3：使用 HTTP 服务器（最佳实践）**
```powershell
python -m http.server 8080
```
然后访问：http://localhost:8080

---

### 第七步：测试功能

#### 测试前端功能：
1. 打开前端页面
2. 点击"获取验证码"按钮
3. 填写表单并提交
4. 测试暗黑模式切换

#### 测试管理后台：
1. 访问：http://127.0.0.1:8000/admin
2. 使用默认账号登录：
   - 用户名：`admin`
   - 密码：`admin123`（生产环境必须修改！）
3. 测试留言管理、数据导出、统计面板等功能

---

## ⚠️ 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| **验证码加载失败** | CORS 配置不支持 file:// 协议 | 确保后端 `.env` 中 `DEBUG=True` |
| **导出 CSV 失败** | Token 认证方式错误 | v3.0 使用 Bearer Token，不是 URL 参数 |
| **PowerShell 命令报错** | 使用了 `&&` 分隔符 | 改用分号 `;` 或 `python -c` 方式 |
| **数据库连接失败** | 数据库文件未创建 | 首次启动会自动创建 `contacts.db` |
| **端口被占用** | 8000 端口被其他程序占用 | 修改端口：`port=8001` |
| **依赖安装失败** | Python 版本过低 | 确保 Python >= 3.8 |

### 前端运行方式对比

| 方式 | 命令 | CORS 配置 | 推荐场景 |
|------|------|-----------|----------|
| **PyCharm Live Preview** | 右键 Open in Browser | 自动添加 localhost:63342 | 开发调试 ✅ |
| **直接双击打开** | 双击 index.html | 自动添加 file:// | 快速测试 |
| **HTTP 服务器** | `python -m http.server 8080` | 自动添加 localhost:8080 | 生产测试 ✅ |
| **生产部署** | Docker / Railway | 配置 ALLOWED_ORIGINS | 正式环境 ✅ |

---

## 🎯 API 接口文档（v3.0）

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **API 文档**: http://localhost:8000/docs

### 公共接口（无需认证）

#### 健康检查
```http
GET /api/v1/health

Response 200:
{
  "status": "healthy",
  "version": "3.0.0",
  "database": "connected"
}
```

#### 获取验证码
```http
GET /api/v1/captcha

Response 200:
{
  "captcha_id": "uuid-string",
  "question": "8 + 3 = ?",
  "expires_in": 300
}
```

#### 提交留言
```http
POST /api/v1/contacts
Content-Type: application/json

{
  "name": "张三",
  "email": "test@example.com",
  "subject": "合作咨询",
  "message": "你好，我想和你合作...",
  "captcha_id": "验证码ID",
  "captcha_answer": "11"
}

Response 201:
{
  "id": 1,
  "name": "张三",
  "email": "test@example.com",
  "status": "unread"
}
```

#### 获取统计数据
```http
GET /api/v1/stats

Response 200:
{
  "total_contacts": 10,
  "replied_contacts": 3,
  "unread_contacts": 7,
  "new_this_week": 2
}
```

### 管理员接口（需要认证）

#### 管理员登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response 200:
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

#### 刷新 Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOi..."
}
```

#### 获取留言列表（管理员）
```http
GET /api/v1/contacts
Authorization: Bearer {access_token}
```

#### 回复留言
```http
POST /api/v1/contacts/{id}/reply
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reply": "感谢您的留言！我们会尽快与您联系。"
}
```

#### 删除留言
```http
DELETE /api/v1/contacts/{id}
Authorization: Bearer {access_token}
```

#### 导出 CSV
```http
GET /api/v1/admin/export/csv
Authorization: Bearer {access_token}
Accept: text/csv
```

#### 获取审计日志
```http
GET /api/v1/admin/audit-logs
Authorization: Bearer {access_token}
```

---

## 🔒 安全特性对比（v2.0 vs v3.0）

| 安全特性 | v2.0 | v3.0 | 改进 |
|---------|------|------|------|
| **JWT 认证** | 手写实现 | python-jose 标准库 | ✅ 防算法替换攻击 |
| **CORS 配置** | `allow_origins=["*"]` | 白名单模式 | ✅ 仅允许指定域名 |
| **密码加密** | passlib | bcrypt (12 rounds) | ✅ 更强加密 |
| **密码强度** | 无校验 | ≥8位 + 大写 + 数字 + 特殊字符 | ✅ 强密码策略 |
| **速率限制** | 无 | slowapi 中间件 | ✅ 防暴力破解 |
| **审计日志** | 无 | 完整操作记录 | ✅ 可追溯 |
| **XSS 防护** | 无 | HTML 转义 | ✅ 防脚本注入 |
| **Token 有效期** | 24小时单 Token | Access 15min + Refresh 7天 | ✅ 更安全 |
| **环境变量** | .env | pydantic-settings | ✅ 类型安全 |
| **数据库** | 同步 SQLite | 异步 SQLAlchemy | ✅ 高性能 |

---

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 后端开发语言 |
| FastAPI | >=0.104.1 | 异步 Web 框架 |
| SQLAlchemy | 2.x | 异步 ORM |
| python-jose | >=3.3.0 | JWT 认证 |
| bcrypt | >=4.1.2 | 密码加密 |
| pydantic | 2.x | 数据验证 |
| pydantic-settings | 2.x | 配置管理 |
| slowapi | >=0.1.8 | 速率限制 |
| passlib | >=1.7.4 | 密码哈希 |
| uvicorn | >=0.24.0 | ASGI 服务器 |
| aiosqlite | >=0.19.0 | 异步 SQLite |
| alembic | >=1.12.0 | 数据库迁移 |
| pytest | >=7.4.0 | 测试框架 |

### 前端

| 技术 | 用途 |
|------|------|
| HTML5 | 页面结构 |
| CSS3 | 样式、动画、暗黑模式 |
| JavaScript (ES6+) | 交互逻辑、API 调用 |

---

## ⚙️ 环境变量配置

复制 `.env.example` 为 `.env`，编辑以下配置：

```env
# 应用配置
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production

# 数据库配置（开发用 SQLite，生产用 PostgreSQL）
DATABASE_URL=sqlite+aiosqlite:///./contacts.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# 管理员账户（首次启动自动创建）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# 邮件配置（可选）
SENDER_EMAIL=your_qq_email@qq.com
SENDER_PASSWORD=your_qq_email_authorization_code
RECIPIENT_EMAIL=your_receive_email@qq.com

# CORS 白名单
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:8000
```

> **生产环境必须修改**：
> 1. `DEBUG=False`
> 2. `SECRET_KEY` 使用强随机字符串
> 3. `ADMIN_PASSWORD` 使用强密码
> 4. `ALLOWED_ORIGINS` 仅保留实际使用的域名

---

##  部署方式

### 本地开发

```bash
cd backend
pip install -r requirements.txt
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)"
```

### Docker Compose（开发环境）

```bash
docker-compose up -d
```

### Docker Compose（生产环境）

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Railway 部署

```bash
railway up --prod
```

> **注意**：`railway.yaml` 已配置指向 `backend/` 目录

### 手动构建 Docker 镜像

```bash
docker build -t portfolio-v3 ./backend
docker run -p 8000:8000 --env-file .env portfolio-v3
```

---

## 🧪 测试

### 运行所有测试

```bash
cd backend
pytest tests/ -v
```

### 运行单个测试文件

```bash
pytest tests/test_auth.py -v
pytest tests/test_contacts.py -v
pytest tests/test_security.py -v
```

### 生成测试覆盖率报告

```bash
pytest tests/ --cov=app --cov-report=html
```

---

## 📈 功能清单

| # | 功能 | 版本 | 状态 |
|---|------|------|------|
| 1 | 联系表单提交 | v1.0 | ✅ |
| 2 | 数据持久化存储 | v1.0 | ✅ |
| 3 | 邮件实时通知 | v1.0 | ✅ |
| 4 | 基础管理后台 | v1.0 | ✅ |
| 5 | API 文档（Swagger UI） | v1.0 | ✅ |
| 6 | 验证码系统 | v2.0 | ✅ |
| 7 | JWT 用户认证 | v2.0 | ✅ |
| 8 | 留言回复功能 | v2.0 | ✅ |
| 9 | CSV 数据导出 | v2.0 | ✅ |
| 10 | 访客统计分析 | v2.0 | ✅ |
| 11 | 暗黑模式 | v2.0 | ✅ |
| 12 | **6 层模块化架构** | v3.0 | ✅ 新增 |
| 13 | **JWT 双 Token 认证** | v3.0 | ✅ 新增 |
| 14 | **CORS 白名单模式** | v3.0 | ✅ 新增 |
| 15 | **速率限制中间件** | v3.0 | ✅ 新增 |
| 16 | **密码强度校验** | v3.0 | ✅ 新增 |
| 17 | **审计日志系统** | v3.0 | ✅ 新增 |
| 18 | **XSS 防护** | v3.0 | ✅ 新增 |
| 19 | **SQLAlchemy 异步 ORM** | v3.0 | ✅ 新增 |
| 20 | **Pydantic V2 数据验证** | v3.0 | ✅ 新增 |
| 21 | **自动化测试覆盖** | v3.0 | ✅ 新增 |
| 22 | **Docker Compose 多环境** | v3.0 | ✅ 新增 |

---

##  更新日志

### v3.0（2026-05-25）

**架构重构**
- ✨ 从单体架构重构为 6 层模块化架构
- ✨ 引入依赖注入模式
- ✨ 使用 SQLAlchemy 异步 ORM 替代原始 SQL
- ✨ 使用 Pydantic V2 数据验证

**安全加固**
- 🔒 JWT 认证从手写实现升级到 python-jose 标准库
- 🔒 实现 JWT 双 Token 机制（Access + Refresh）
- 🔒 CORS 从 `*` 改为白名单模式
- 🔒 密码加密升级为 bcrypt（12 rounds）
- 🔒 新增密码强度校验（≥8位 + 大写 + 数字 + 特殊字符）
- 🔒 新增速率限制中间件（登录 5次/分、留言 10次/分、验证码 20次/分）
- 🔒 新增 XSS 防护（HTML 转义）
- 🔒 新增审计日志系统（所有管理员操作可追溯）

**部署改进**
- 🚢 修复 railway.yaml 指向 backend 目录
- 🚢 新增 Docker Compose 多环境配置
- 🚢 新增数据库迁移（Alembic）

**文档完善**
- 📖 更新 README.md 为 v3.0 完整文档
-  新增 DEPLOYMENT.md 部署指南
- 📖 新增 TEST_REPORT.md 测试报告

### v2.0（2026-05-24）

- ✨ 新增验证码系统
- ✨ 新增 JWT 用户认证
- ✨ 新增留言回复功能
- ✨ 新增 CSV 数据导出
- ✨ 新增访客统计面板
- ✨ 新增暗黑模式
- ✨ 新增多平台部署配置

### v1.0（初始版本）

- 完整的个人作品集前端页面
- FastAPI 联系表单后端
- SQLite 数据存储
- SMTP 邮件通知
- 基础管理后台

---

## 📸 项目截图

> 运行项目后可在浏览器中查看效果：
> - **前端页面**：直接打开 `index.html`
> - **管理后台**：访问 http://localhost:8000/admin
> - **API 文档**：访问 http://localhost:8000/docs

---

## 📜 许可证

本项目采用 MIT 开源许可证 - 详见 [LICENSE](./LICENSE) 文件。

---

## 💻 作者

c123-ux - 全栈开发工程师

**仓库地址**：
- v2.0：https://github.com/c123-ux/FastAPI-Portfolio-Website
- v3.0：https://github.com/c123-ux/FastAPI-Portfolio-Website3.0
