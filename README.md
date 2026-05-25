# 全栈个人作品集网站 v2.0

这是一个使用 **HTML5 + CSS3 + FastAPI** 构建的全栈个人作品集网站，包含前端展示页面和后端联系表单功能。现已全面升级，集成了验证码、JWT 认证、留言管理、数据导出、访客统计、暗黑模式等完整功能。

---

## 🚀 新增功能（v2.0）

| 功能 | 状态 | 说明 |
|------|------|------|
| 🔒 **验证码系统** | ✅ 已完成 | 数学运算验证码，5分钟过期，防止垃圾留言 |
| 👤 **JWT 用户认证** | ✅ 已完成 | 安全的登录系统，24小时令牌有效期 |
| 💬 **留言回复功能** | ✅ 已完成 | 管理员可在后台直接回复用户留言 |
| 📥 **CSV 数据导出** | ✅ 已完成 | 一键导出所有留言数据，需认证 |
| 📊 **访客统计面板** | ✅ 已完成 | 实时追踪30天访客、总浏览量、新留言数 |
| 🌙 **暗黑模式** | ✅ 已完成 | 前端和管理后台都支持，记住用户偏好 |
| 🚢 **多平台部署** | ✅ 已完成 | 支持 Railway、Heroku、Docker 一键部署 |
| 📜 **开源许可证** | ✅ 已完成 | MIT 许可证 |

---

## 📁 项目结构

```
PythonProject1/
├── .env                      # 环境变量配置（SECRET_KEY/ADMIN/邮箱）
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略文件
├── index.html                # 前端主页面（含验证码+暗黑模式）
├── style.css                 # 前端样式（含暗黑模式完整样式）
├── main_backend.py           # FastAPI 后端服务 v2.0（619行）
├── requirements.txt          # Python 依赖包
├── railway.yaml              # Railway 部署配置
├── Dockerfile                # Docker 容器镜像配置
├── docker-compose.yml        # Docker Compose 配置
├── package.json              # Node.js 配置
├── deploy.bat                # Windows 一键部署脚本
├── LICENSE                   # MIT 许可证
├── DEPLOYMENT.md             # 详细部署指南
├── README.md                 # 项目说明（本文件）
├── contacts.db               # SQLite 数据库（自动生成）
└── .venv/                    # Python 虚拟环境
```

---

## 🚀 快速开始

### 方式一：使用部署脚本（推荐 Windows 用户）

```bash
deploy.bat
```

### 方式二：手动启动

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

复制 `.env.example` 为 `.env`，编辑以下配置：

```env
# JWT 密钥（生产环境请修改为随机字符串）
SECRET_KEY=your-super-secret-key-change-this-in-production

# 管理员账户配置（默认用户名密码）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# QQ 邮箱配置（可选，不配置则不发送邮件）
SENDER_EMAIL=your_qq_email@qq.com
SENDER_PASSWORD=your_qq_email_authorization_code
RECIPIENT_EMAIL=your_receive_email@qq.com
```

> **获取 QQ 邮箱授权码：**
> 1. 登录 QQ 邮箱 → 设置 → 账户
> 2. 开启 "IMAP/SMTP 服务"
> 3. 生成授权码（16位字母）

#### 3. 启动后端

```bash
python main_backend.py
```

后端将在 `http://127.0.0.1:8000` 启动（自动创建数据库和管理员账户）。

#### 4. 打开前端

在浏览器中打开 `index.html`，或在 PyCharm 中右键 → Open in Browser。

---

## 🎯 API 接口文档

### 前端接口（无需认证）

#### 获取验证码
```http
GET /api/captcha

Response 200:
{
  "captcha_id": "2d73a8fe84ec21ae...",
  "question": "8 - 3 = ?",
  "expires_in": 300
}
```

#### 提交联系表单（含验证码）
```http
POST /api/contact
Content-Type: application/json

{
  "name": "张三",
  "email": "test@example.com",
  "subject": "合作咨询",
  "message": "你好，我想和你合作...",
  "captcha_id": "验证码返回的ID",
  "captcha_answer": "验证码答案"
}

Response 200:
{
  "success": true,
  "message": "提交成功！我们会尽快联系您。",
  "data": {"id": 1, "name": "张三", "email": "test@example.com"}
}
```

#### 获取留言列表
```http
GET /api/contacts
```

#### 获取统计数据
```http
GET /api/stats

Response 200:
{
  "stats": {
    "total_contacts": 10,
    "replied_contacts": 3,
    "unread_contacts": 7,
    "unique_visitors_30d": 25,
    "total_page_views": 100,
    "new_this_week": 2
  }
}
```

### 管理接口（需要 JWT 令牌）

#### 管理员登录
```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response 200:
{
  "success": true,
  "access_token": "eyJhbGciOi...",
  "token_type": "Bearer",
  "username": "admin"
}
```

#### 回复留言
```http
POST /api/contacts/{id}/reply
Authorization: Bearer {token}
Content-Type: application/json

{
  "reply": "感谢您的留言！我们会尽快与您联系。"
}
```

#### 删除留言
```http
DELETE /api/contacts/{id}
Authorization: Bearer {token}
```

#### 导出 CSV
```http
GET /api/export/csv?token={token}
```

### 公共页面

| 路径 | 说明 |
|------|------|
| `/admin` | 完整管理后台页面（含登录/回复/删除/导出） |
| `/docs` | Swagger UI 自动生成的交互式 API 文档 |
| `/` | 后端运行状态信息 |

---

## ✨ 功能详解

### 1. 🔒 验证码系统
- **类型**：数学运算验证码（加法/减法，10以内整数）
- **安全性**：5分钟过期，提交后自动销毁
- **用户体验**：一键刷新，即时显示

### 2. 👤 JWT 用户认证
- **加密方式**：SHA-256 签名 + Base64 编码
- **令牌有效期**：24小时（可配置）
- **使用场景**：回复留言、删除留言、导出数据

### 3. 💬 留言回复功能
- 管理员可在管理后台直接回复用户留言
- 回复后自动标记状态为"已回复"
- 用户留言卡片上会显示回复内容

### 4. 📥 CSV 数据导出
- 导出字段：ID、姓名、邮箱、主题、留言、状态、回复、时间
- 文件名格式：`contacts_YYYYMMDD_HHMMSS.csv`
- 需 JWT 令牌认证

### 5. 📊 访客统计面板
- **统计指标**：总留言数、已回复数、待回复数、30天独立访客、总浏览量、本周新增
- **数据追踪**：自动记录访客 IP、User-Agent、访问路径

### 6. 🌙 暗黑模式
- **前端页面**：点击右上角按钮切换，localStorage 保存偏好
- **管理后台**：独立暗黑模式切换按钮
- **色彩方案**：深蓝背景（#1a1a2e、#16213e、#0f3460）

### 7. 🚢 多平台部署
- **Railway**：配置 `railway.yaml`，Nixpacks 自动构建
- **Docker**：`Dockerfile` + `docker-compose.yml`
- **Heroku**：标准 Python Buildpack
- **一键部署**：`deploy.bat` 脚本

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5 | - | 页面结构、语义化标签 |
| CSS3 | - | Flexbox/Grid 布局、动画、暗黑模式 |
| JavaScript | ES6+ | 表单提交、验证码交互、暗黑模式切换 |
| FastAPI | >=0.104.1 | 异步 Python Web 框架 |
| Python | 3.8+ | 后端开发语言 |
| SQLite | - | 嵌入式数据库（零配置） |
| passlib | >=1.7.4 | 密码哈希（bcrypt） |
| bcrypt | ==4.1.2 | 密码加密库 |
| python-multipart | - | 表单数据解析 |
| uvicorn | >=0.24.0 | ASGI 服务器 |
| pydantic | >=2.5.0 | 数据验证 |
| SMTP | - | 邮件通知服务 |
| JWT | 自定义实现 | 身份认证令牌 |

---

## 🔒 安全配置

### 生产环境必须配置

1. **修改默认密码**
   ```env
   ADMIN_PASSWORD=your-very-strong-password
   ```

2. **生成安全的 SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **启用 HTTPS**（Railway/Heroku 自动提供）

### 安全规范

- ❌ **不要**将 `.env` 文件提交到 Git（已在 `.gitignore` 中配置）
- ❌ **不要**使用 QQ 邮箱登录密码，必须使用授权码
- ✅ 部署到生产环境时建议使用更严格的 CORS 配置
- ✅ 建议添加 IP 黑名单和速率限制

---

## 🎯 使用场景

- 🖥️ **前端实习面试展示** - 完整全栈项目，含8大功能
- 🌐 **个人作品集网站** - 可直接部署使用
- 📚 **全栈开发学习案例** - FastAPI + JWT + SQLite 最佳实践
- 🔬 **FastAPI 入门实践** - 从基础到高级功能的完整示例

---

## ⚙️ 部署方式

| 方式 | 命令 |
|------|------|
| **Windows 一键部署** | `deploy.bat` |
| **手动启动** | `python main_backend.py` |
| **Docker Compose** | `docker-compose up -d` |
| **Docker 构建** | `docker build -t portfolio . && docker run -p 8000:8000 portfolio` |
| **Railway CLI** | `railway up --prod` |

> 详细部署文档请参阅 [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📈 功能清单

| # | 功能 | 版本 | 状态 |
|---|------|------|------|
| 1 | 联系表单提交 | v1.0 | ✅ |
| 2 | 数据持久化存储（SQLite） | v1.0 | ✅ |
| 3 | 邮件实时通知（SMTP） | v1.0 | ✅ |
| 4 | 基础管理后台 | v1.0 | ✅ |
| 5 | Pydantic 数据验证 | v1.0 | ✅ |
| 6 | CORS 跨域支持 | v1.0 | ✅ |
| 7 | API 文档（Swagger UI） | v1.0 | ✅ |
| 8 | **验证码系统** | v2.0 | ✅ 新增 |
| 9 | **JWT 用户认证** | v2.0 | ✅ 新增 |
| 10 | **留言回复功能** | v2.0 | ✅ 新增 |
| 11 | **CSV 数据导出** | v2.0 | ✅ 新增 |
| 12 | **访客统计分析** | v2.0 | ✅ 新增 |
| 13 | **暗黑模式** | v2.0 | ✅ 新增 |
| 14 | **多平台部署配置** | v2.0 | ✅ 新增 |
| 15 | **开源许可证** | v2.0 | ✅ 新增 |

---

## 📸 项目截图

> 运行项目后可在浏览器中查看效果：
> - **前端页面**：直接打开 `index.html`
> - **管理后台**：访问 http://localhost:8000/admin
> - **API 文档**：访问 http://localhost:8000/docs

---

## 📝 许可证

本项目采用 MIT 开源许可证 - 详见 [LICENSE](./LICENSE) 文件。

---

## ‍💻 作者

c - 全栈开发工程师

---

## 📋 更新日志

### v2.0（2026-05-24）

- ✨ **新增** 🔒 数学运算验证码（5分钟过期，自动销毁）
- ✨ **新增** 👤 JWT 用户认证（24小时令牌，SHA-256 签名）
- ✨ **新增** 💬 留言回复功能（管理后台直接回复）
- ✨ **新增** 📥 CSV 数据导出（带 JWT 认证保护）
- ✨ **新增** 📊 访客统计面板（30天独立访客、浏览量、趋势分析）
- ✨ **新增** 🌙 暗黑模式（前端+管理后台，localStorage 记忆偏好）
- ✨ **新增** 🚢 部署配置（Railway + Docker + Heroku）
- ✨ **新增** 📜 开源许可证（MIT）
- 🔧 **优化** 管理后台界面（数据仪表盘、暗黑模式、操作按钮）
- 🔧 **优化** 数据库结构（新增状态、回复、浏览、访客字段）
- 🔧 **优化** 错误处理和用户反馈

### v1.0（初始版本）

- 完整的个人作品集前端页面（首页/关于/技能/项目/联系）
- FastAPI 联系表单后端
- SQLite 数据存储
- SMTP 邮件通知
- 基础管理后台
