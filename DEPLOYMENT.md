# 🚀 部署指南

## 功能特性（v2.0）

✅ **验证码** - 防止垃圾留言  
✅ **用户登录认证** - JWT 令牌保护管理后台  
✅ **留言回复功能** - 管理员可以直接回复留言  
✅ **数据导出** - 支持 CSV 格式导出  
✅ **访客统计** - 追踪访问数据和留言统计  
✅ **暗黑模式** - 前端和管理后台都支持暗色主题  
✅ **多平台部署** - 支持 Railway、Heroku、Docker  

---

## 本地开发

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

或直接在 IDE 中创建 `.env` 文件：

```env
SECRET_KEY=your-super-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-strong-password
SENDER_EMAIL=your-email@qq.com
SENDER_PASSWORD=your-smtp-password
RECIPIENT_EMAIL=recipient@example.com
```

### 3. 启动服务

#### 方式一：使用部署脚本（推荐 Windows 用户）

```bash
deploy.bat
```

#### 方式二：直接运行

```bash
python main_backend.py
```

### 4. 访问应用

- **API 文档**: http://localhost:8000/docs
- **管理后台**: 浏览器打开 `index.html`，然后通过 API 登录访问
- **前端页面**: 直接用浏览器打开 `index.html`

---

## 部署到 Railway（推荐）

### 前置条件

1. 注册 [Railway](https://railway.app) 账号
2. 安装 Node.js 和 npm

### 步骤

#### 方法一：使用 Railway CLI

```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 初始化项目（首次使用）
railway init

# 4. 关联项目
railway link

# 5. 设置环境变量
railway variables set SECRET_KEY="your-secret-key"
railway variables set ADMIN_USERNAME="admin"
railway variables set ADMIN_PASSWORD="your-password"

# 6. 部署
railway up --prod
```

#### 方法二：手动部署

1. 在 Railway 控制台创建新項目
2. 连接 GitHub 仓库
3. 在 Railway 控制台的 "Variables" 标签页添加环境变量
4. Railway 会自动部署

### 配置 Railway 环境变量

在 Railway 控制台中设置以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `SECRET_KEY` | JWT 密钥（必须随机） | 使用命令生成：`python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_USERNAME` | 管理员用户名 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `your-strong-password` |
| `SENDER_EMAIL` | QQ 邮箱（可选） | `your-email@qq.com` |
| `SENDER_PASSWORD` | SMTP 密码（可选） | `your-smtp-code` |
| `RECIPIENT_EMAIL` | 收件人邮箱（可选） | 同 SENDER_EMAIL |

---

## 部署到 Heroku

### 步骤

```bash
# 1. 安装 Heroku CLI
# 访问 https://devcenter.heroku.com/articles/heroku-cli

# 2. 登录
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 设置 Buildpack
heroku buildpacks:set heroku/python

# 5. 设置环境变量
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set ADMIN_USERNAME="admin"
heroku config:set ADMIN_PASSWORD="your-password"

# 6. 部署
git push heroku main
```

---

## 使用 Docker 部署

### 本地运行

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 构建镜像

```bash
docker build -t portfolio-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env portfolio-backend
```

### Docker Hub 发布

```bash
# 1. 登录 Docker Hub
docker login

# 2. 标记镜像
docker tag portfolio-backend your-username/portfolio-backend:latest

# 3. 推送
docker push your-username/portfolio-backend:latest

# 4. 在其他地方拉取运行
docker pull your-username/portfolio-backend:latest
docker run -p 8000:8000 your-username/portfolio-backend:latest
```

---

## 部署到 Vercel

Vercel 主要支持 Serverless Functions，需要做少量调整：

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 部署
vercel
```

需要在项目中创建 `api/index.py` 来适配 Vercel 的 Serverless 函数。

---

## API 接口文档

部署后访问 `/docs` 查看完整的 Swagger API 文档。

### 主要接口

| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| POST | `/api/contact` | 提交联系表单 | ❌ |
| GET | `/api/captcha` | 获取验证码 | ❌ |
| POST | `/api/login` | 管理员登录 | ❌ |
| GET | `/api/contacts` | 获取所有留言 | ❌* |
| GET | `/api/contacts/{id}` | 获取单条留言详情 | ❌* |
| POST | `/api/contacts/{id}/reply` | 回复留言 | ✅ |
| DELETE | `/api/contacts/{id}` | 删除留言 | ✅ |
| GET | `/api/export/csv` | 导出 CSV | ✅ |
| GET | `/api/stats` | 获取统计数据 | ❌ |

*注意：虽然这些接口不需要认证，但在生产环境中建议添加访问限制。

### 认证方式

使用 Bearer Token：

```bash
Authorization: Bearer <your-jwt-token>
```

---

## 安全性建议

### 🔴 生产环境必须配置

1. **修改默认密码**
   ```env
   ADMIN_PASSWORD=your-very-strong-password
   ```

2. **生成安全的 SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **启用 HTTPS**
   - Railway/Heroku 自动提供 HTTPS
   - 确保前端使用 HTTPS 请求后端 API

### 🟡 强烈建议

1. **配置邮箱通知** - 方便接收新用户留言
2. **定期备份数据库** - contacts.db 文件包含所有数据
3. **限制访问频率** - 使用 Cloudflare 等 CDN 防护
4. **监控日志** - 定期检查访问日志和安全事件

### 🟢 可选增强

1. **添加 IP 黑名单** - 阻止恶意 IP
2. **实现速率限制** - 防止暴力攻击
3. **使用 PostgreSQL** - 替换 SQLite 以提高性能
4. **启用 CSRF 保护** - 额外增加一层安全防护

---

## 常见问题

### Q: 验证码不显示？
**A:** 
1. 确保后端正常运行（http://localhost:8000/docs 可以访问）
2. 检查浏览器控制台是否有错误
3. 确认 CORS 配置正确

### Q: 无法发送邮件？
**A:** 
1. 检查 `.env` 文件中的邮箱配置是否正确
2. 确保使用的是 QQ 邮箱 SMTP 服务
3. 授权码是否正确（不是登录密码）
4. 网络是否能访问 smtp.qq.com:465

### Q: 管理后台打不开？
**A:** 
1. 先通过 `/api/login` 接口登录获取 token
2. Token 会自动保存到 localStorage
3. 刷新页面即可看到管理后台

登录方法（使用浏览器控制台）：
```javascript
fetch('/api/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: 'admin', password: 'admin123'})
}).then(r => r.json()).then(d => {
    if(d.success) console.log('登录成功:', d.access_token);
});
```

### Q: 部署后数据库不持久化？
**A:** 
Railway 的文件系统在容器重启时会丢失文件。解决方案：
1. 使用 PostgreSQL 替代 SQLite
2. 定期导出数据备份
3. 使用 Railway 的 Addons 挂载存储

切换 PostgreSQL 示例：
```python
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///contacts.db")
```

### Q: 如何重置管理员密码？
**A:** 
直接修改 `.env` 文件中的 `ADMIN_PASSWORD`，然后重启服务。

### Q: CSV 导出失败？
**A:** 
确保已登录（token 在 localStorage 中），如果仍然失败，检查控制台错误信息。

---

## 性能优化建议

1. **静态资源 CDN** - 将 CSS/JS 托管到 CDN
2. **数据库索引** - 为常用查询字段添加索引
3. **缓存策略** - 使用 Redis 缓存热点数据
4. **图片优化** - 压缩图片，使用 WebP 格式
5. **Gzip 压缩** - 启用服务器压缩

---

## 监控和维护

### 定期检查

- [ ] 查看应用日志
- [ ] 检查磁盘空间
- [ ] 更新依赖包
- [ ] 备份数据库
- [ ] 审查安全事件

### 日志查看

```bash
# Railway
railway logs

# Docker
docker-compose logs -f

# Heroku
heroku logs --tail
```

---

## 技术支持

如有问题，请查看：
- API 文档: `http://your-domain.com/docs`
- 项目主页: README.md
- 许可证: LICENSE

---

## 更新日志

### v2.0 (2026-05-24)
- ✅ 添加验证码功能
- ✅ 添加 JWT 认证系统
- ✅ 添加留言回复功能
- ✅ 添加 CSV 数据导出
- ✅ 添加访客统计分析
- ✅ 添加暗黑模式
- ✅ 优化管理后台界面
- ✅ 支持多平台部署

### v1.0 (初始版本)
- 基础联系表单功能
- 邮件通知
- 简单管理后台
