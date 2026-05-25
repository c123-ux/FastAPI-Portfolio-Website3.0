"""
Portfolio Contact Form Backend v2.0
包含：验证码、JWT认证、留言回复、数据导出、访客统计、暗黑模式
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
import smtplib
import os
import sqlite3
import csv
import io
import random
import secrets
import hashlib
import json
import base64
from dotenv import load_dotenv
from passlib.context import CryptContext
from typing import Optional

load_dotenv()

app = FastAPI(title="联系表单后端 v2.0", version="2.0")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库路径
DB_PATH = "contacts.db"
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    """初始化数据库 - 创建所有必要的表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 留言表（含新功能字段）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT DEFAULT '无主题',
            message TEXT NOT NULL,
            captcha_id TEXT,
            captcha_answer TEXT,
            status TEXT DEFAULT 'unread',
            reply TEXT,
            replied_at TIMESTAMP,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 访客表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            path TEXT NOT NULL,
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建默认管理员账户
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    hashed = pwd_context.hash(admin_password)
    cursor.execute("SELECT id FROM users WHERE username=?", (admin_username,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)",
                      (admin_username, hashed))
        print(f"✅ 管理员账户已创建: {admin_username} / {admin_password}")
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# 验证码存储（生产环境建议使用 Redis）
captchas = {}

# Pydantic 模型
class ContactForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    email: EmailStr = Field(..., description="邮箱")
    subject: Optional[str] = "无主题"
    message: str = Field(..., min_length=1, max_length=5000, description="留言内容")
    captcha_id: str = Field(..., description="验证码ID")
    captcha_answer: str = Field(..., description="验证码答案")

class LoginForm(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class ReplyForm(BaseModel):
    reply: str = Field(..., min_length=1, max_length=5000, description="回复内容")

def generate_captcha():
    """生成数学运算验证码"""
    captcha_id = secrets.token_hex(16)
    a = str(random.randint(0, 9))
    b = str(random.randint(0, 9))
    op = random.choice(["+", "-"])
    
    if op == "+":
        answer = str(int(a) + int(b))
    else:
        if int(a) < int(b):
            a, b = b, a
        answer = str(int(a) - int(b))
    
    captchas[captcha_id] = {
        "answer": answer,
        "expires": datetime.now() + timedelta(minutes=5)
    }
    
    return {
        "captcha_id": captcha_id,
        "question": f"{a} {op} {b} = ?",
        "expires_in": 300
    }

def verify_token(token: str):
    """验证 JWT Token"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # 解码 header 和 payload
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '=' * (4 - len(parts[0]) % 4)))
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * (4 - len(parts[1]) % 4)))
        
        # 验证签名
        sig_input = f"{parts[0]}.{parts[1]}"
        expected_sig = base64.urlsafe_b64encode(
            hashlib.sha256((sig_input + SECRET_KEY).encode()).digest()
        ).decode().rstrip('=')
        
        if parts[2] != expected_sig:
            return None
        
        # 检查过期时间
        exp_time = payload.get('exp', 0)
        if exp_time < (datetime.now() + timedelta(minutes=5)).timestamp():
            return None
        
        return payload
    except:
        return None

def save_to_database(data: dict):
    """保存留言到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contacts (name, email, subject, message, captcha_id, captcha_answer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['email'], data.get('subject', '无主题'),
          data['message'], data.get('captcha_id'), data.get('captcha_answer')))
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return contact_id

def send_email(data: dict):
    """发送邮件通知"""
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        recipient = os.getenv("RECIPIENT_EMAIL", sender_email)
        
        if not sender_email or not sender_password:
            print("⚠️ 未配置邮箱，跳过邮件发送")
            return False
        
        subject = f"【简历网站】新留言：{data['name']}"
        body = f"""
收到新的联系表单提交：

姓名：{data['name']}
邮箱：{data['email']}
主题：{data['subject']}
内容：
{data['message']}

时间：{data.get('created_at', 'N/A')}
        """.strip()
        
        msg = f"Subject: {subject}\n\n{body}"
        
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg)
        
        print("✅ 邮件发送成功")
        return True
    except Exception as e:
        print(f"⚠️ 邮件发送失败：{e}")
        return False

# 应用启动时初始化数据库
@app.on_event("startup")
async def startup():
    """启动时执行"""
    init_db()

# ========== 前端接口（无需认证） ==========

@app.post("/api/contact")
async def submit_contact(form: ContactForm):
    """提交联系表单（带验证码验证）"""
    try:
        # 验证验证码
        captcha_data = captchas.get(form.captcha_id)
        if not captcha_data:
            raise HTTPException(status_code=400, detail="验证码已过期，请刷新重试")
        
        if datetime.now() > captcha_data["expires"]:
            del captchas[form.captcha_id]
            raise HTTPException(status_code=400, detail="验证码已过期，请刷新重试")
        
        if captcha_data["answer"] != form.captcha_answer:
            raise HTTPException(status_code=400, detail="验证码错误")
        
        # 清除已使用的验证码
        del captchas[form.captcha_id]
        
        # 保存并发送邮件
        contact_id = save_to_database(form.dict())
        send_email({**form.dict(), 'id': contact_id, 
                   'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        
        return {
            "success": True,
            "message": "提交成功！我们会尽快联系您。",
            "data": {"id": contact_id, "name": form.name, "email": form.email}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交失败：{str(e)}")

@app.get("/api/captcha")
async def get_captcha_endpoint():
    """获取验证码"""
    return generate_captcha()

@app.get("/api/contacts")
async def get_contacts(request: Request):
    """获取所有留言（记录访客）"""
    visitor_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # 记录访客
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO visitors (ip_address, user_agent, path) VALUES (?, ?, '/contacts')",
                  (visitor_ip, user_agent))
    conn.commit()
    conn.close()
    
    # 获取留言
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"success": True, "count": len(contacts), "contacts": contacts}

@app.get("/api/stats")
async def get_stats(request: Request):
    """获取统计数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM contacts")
    total_contacts = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE status='replied'")
    replied = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(DISTINCT ip_address) as unique_visitors FROM visitors WHERE visited_at >= datetime('now', '-30 days')")
    unique_visitors = cursor.fetchone()["unique_visitors"]
    
    cursor.execute("SELECT COUNT(*) as page_views FROM visitors")
    page_views = cursor.fetchone()["page_views"]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_at >= datetime('now', '-7 days')")
    new_this_week = cursor.fetchone()["total"]
    
    cursor.execute("SELECT status, COUNT(*) as count FROM contacts GROUP BY status")
    status_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "success": True,
        "stats": {
            "total_contacts": total_contacts,
            "replied_contacts": replied,
            "unread_contacts": status_stats.get("unread", 0),
            "unique_visitors_30d": unique_visitors,
            "total_page_views": page_views,
            "new_this_week": new_this_week,
        }
    }

# ========== 管理接口（需要认证） ==========

@app.post("/api/login")
async def login(form: LoginForm):
    """管理员登录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (form.username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not pwd_context.verify(form.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 生成 JWT Token
    payload = {
        "sub": user["username"],
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now().timestamp()
    }
    
    header_b64 = base64.urlsafe_b64encode(
        json.dumps({"alg": ALGORITHM, "typ": "JWT"}).encode()
    ).decode().rstrip('=')
    
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip('=')
    
    sig_input = f"{header_b64}.{payload_b64}"
    signature = base64.urlsafe_b64encode(
        hashlib.sha256((sig_input + SECRET_KEY).encode()).digest()
    ).decode().rstrip('=')
    
    token = f"{header_b64}.{payload_b64}.{signature}"
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "Bearer",
        "username": user["username"]
    }

@app.post("/api/contacts/{contact_id}/reply")
async def reply_to_contact(contact_id: int, form: ReplyForm, request: Request):
    """回复留言"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="未授权访问")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET reply = ?, replied_at = ?, status = 'replied' WHERE id = ?",
                  (form.reply, datetime.now(), contact_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if not affected:
        raise HTTPException(status_code=404, detail="留言不存在")
    
    return {"success": True, "message": "回复成功"}

@app.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: int, request: Request):
    """删除留言"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="未授权访问")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    if not deleted:
        raise HTTPException(status_code=404, detail="留言不存在")
    
    return {"success": True, "message": "删除成功"}

@app.get("/api/export/csv")
async def export_csv(request: Request):
    """导出 CSV 文件"""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)
    
    # 支持通过 query params 传递 token（用于下载）
    if not payload:
        query_params = request.query_params.get("token", "")
        if query_params:
            token = query_params
            payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="未授权访问")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, subject, message, status, reply, created_at FROM contacts ORDER BY created_at DESC")
    contacts = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "姓名", "邮箱", "主题", "留言", "状态", "回复", "时间"])
    
    for c in contacts:
        writer.writerow([c["id"], c["name"], c["email"], c["subject"],
                        c["message"], c["status"], c["reply"] or "", c["created_at"]])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

# ========== 管理后台页面 ==========

@app.get("/admin")
async def admin_panel(request: Request):
    """管理后台 HTML 页面"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM contacts")
    total_contacts = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE status='replied'")
    replied = cursor.fetchone()["total"]
    cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
    contacts = cursor.fetchall()
    conn.close()
    
    # 构建 HTML
    html_parts = []
    html_parts.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>留言管理后台</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei','Segoe UI',sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f5f5f5;transition:all .3s}
.dark{background:#1a1a2e;color:#eaeaea}
h1{color:#4361ee;border-bottom:2px solid #4361ee;padding-bottom:10px}
.dark h1{color:#6c63ff}
.dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:20px 0}
.card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.1);text-align:center}
.dark .card{background:#16213e}
.card h3{font-size:2rem;color:#4361ee;margin:0}
.dark .card h3{color:#6c63ff}
.card p{margin:5px 0 0;color:#666}
.dark .card p{color:#a0a0a0}
.contact-card{background:white;padding:20px;margin:15px 0;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.1);border-left:4px solid #4361ee}
.dark .contact-card{background:#16213e}
.contact-card h3{margin:0 0 10px 0;color:#333}
.dark .contact-card h3{color:#eaeaea}
.meta{color:#999;font-size:.85em;margin-bottom:10px}
.message{background:#f9f9f9;padding:15px;border-radius:5px;line-height:1.6;margin:10px 0}
.dark .message{background:#0f3460}
.reply-section{margin-top:15px;padding-top:15px;border-top:1px dashed #ddd}
.dark .reply-section{border-color:#444}
.reply-box{width:100%;padding:10px;border:1px solid #ddd;border-radius:5px;margin:10px 0;font-family:inherit;resize:vertical;min-height:80px}
.dark .reply-box{background:#1a1a2e;border-color:#444;color:#eaeaea}
.btn-reply{background:#4361ee;color:white;padding:8px 20px;border:none;border-radius:5px;cursor:pointer}
.btn-delete{background:#ef476f;color:white;padding:8px 20px;border:none;border-radius:5px;cursor:pointer;margin-left:10px}
.export-btn{background:#06d6a0;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer}
.theme-toggle{position:fixed;top:20px;right:20px;background:#4361ee;color:white;border:none;border-radius:50%;width:50px;height:50px;font-size:1.5rem;cursor:pointer;z-index:999}
.status-badge{display:inline-block;padding:3px 10px;border-radius:15px;font-size:.8em;margin-left:10px}
.status-unread{background:#fee2e2;color:#991b1b}
.status-replied{background:#d1fae5;color:#065f46}
.login-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:1000}
.login-box{background:white;padding:40px;border-radius:10px;width:400px;max-width:90vw}
.dark .login-box{background:#16213e}
.login-box input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:5px}
.dark .login-box input{background:#1a1a2e;border-color:#444;color:#eaeaea}
.login-box button{width:100%;padding:12px;background:#4361ee;color:white;border:none;border-radius:5px;font-size:1rem;cursor:pointer;margin-top:10px}
.hidden{display:none}
</style>
</head>
<body>
<button class="theme-toggle" onclick="toggleTheme()">🌙</button>
<div id="loginOverlay" class="login-overlay">
<div class="login-box">
<h2 style="margin-bottom:20px;color:#4361ee;text-align:center">🔐 管理员登录</h2>
<input type="text" id="loginUser" placeholder="用户名">
<input type="password" id="loginPass" placeholder="密码">
<button onclick="doLogin()">登录</button>
<p id="loginError" style="color:#ef476f;margin-top:10px;text-align:center"></p>
</div>
</div>
<div id="adminPanel" class="hidden">
<h1>📬 联系表单管理后台</h1>
<div class="dashboard">
<div class="card"><h3>''' + str(total_contacts) + '''</h3><p>总留言</p></div>
<div class="card"><h3>''' + str(replied) + '''</h3><p>已回复</p></div>
<div class="card"><h3>''' + str(total_contacts - replied) + '''</h3><p>待回复</p></div>
<div class="card"><h3 id="visitorCount">-</h3><p>30天访客</p></div>
</div>
<button class="export-btn" onclick="exportCSV()" style="margin-top:20px">📥 导出CSV</button>
<button onclick="location.reload()" style="background:#4361ee;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;margin-left:10px;margin-top:20px">🔄 刷新</button>
''')
    
    if contacts:
        for c in contacts:
            status_class = "status-unread" if c["status"] == "unread" else "status-replied"
            status_text = "未读" if c["status"] == "unread" else "已回复"
            html_parts.append(f'''
<div class="contact-card">
<h3>{c["name"]} <span class="status-badge {status_class}">{status_text}</span></h3>
<div class="meta">📧 {c["email"]} | 🕒 {c["created_at"]} | 👁️ {c.get("views", 0)} 次查看</div>
<div style="margin:10px 0"><strong>主题：</strong>{c["subject"] or "无"}</div>
<div class="message">{c["message"]}</div>''')
            
            if c["reply"]:
                html_parts.append(f'<div class="message" style="border-left:3px solid #06d6a0"><strong>💬 我的回复：</strong><br>{c["reply"]}<br><small style="color:#999">{c["replied_at"]}</small></div>')
            
            html_parts.append(f'''
<div class="reply-section">
<textarea class="reply-box" id="reply-{c["id"]}" placeholder="输入回复内容..."></textarea>
<div style="margin-top:10px">
<button class="btn-reply" onclick="replyToContact({c["id"]})">💬 回复</button>
<button class="btn-delete" onclick="deleteContact({c["id"]})">🗑️ 删除</button>
</div>
</div>
</div>''')
    else:
        html_parts.append('<p style="text-align:center;color:#999;padding:40px">暂无留言</p>')
    
    html_parts.append('''
</div>
<script>
function toggleTheme(){document.body.classList.toggle("dark");localStorage.setItem("theme",document.body.classList.contains("dark")?"dark":"light");document.querySelector(".theme-toggle").textContent=document.body.classList.contains("dark")?"☀️":"🌙"}
if(localStorage.getItem("theme")==="dark"){document.body.classList.add("dark");document.querySelector(".theme-toggle").textContent="☀️"}
function doLogin(){var u=document.getElementById("loginUser").value,p=document.getElementById("loginPass").value;fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:u,password:p})}).then(function(r){return r.json()}).then(function(d){if(d.success){localStorage.setItem("admin_token",d.access_token);document.getElementById("loginOverlay").classList.add("hidden");document.getElementById("adminPanel").classList.remove("hidden")}else{document.getElementById("loginError").textContent=d.detail}})}
if(localStorage.getItem("admin_token")){document.getElementById("loginOverlay").classList.add("hidden");document.getElementById("adminPanel").classList.remove("hidden")}
function replyToContact(id){var r=document.getElementById("reply-"+id).value;if(!r.trim()){alert("请输入回复内容");return}var t=localStorage.getItem("admin_token");if(!t){alert("请先登录");return}fetch("/api/contacts/"+id+"/reply",{method:"POST",headers:{"Content-Type":"application/json",Authorization:"Bearer "+t},body:JSON.stringify({reply:r})}).then(function(r){return r.json()}).then(function(d){if(d.success){alert("回复成功");location.reload()}else{alert(d.detail||"回复失败")}})}
function deleteContact(id){if(!confirm("确定删除此留言？"))return;var t=localStorage.getItem("admin_token");if(!t){alert("请先登录");return}fetch("/api/contacts/"+id,{method:"DELETE",headers:{Authorization:"Bearer "+t}}).then(function(r){return r.json()}).then(function(d){if(d.success){alert("删除成功");location.reload()}else{alert(d.detail||"删除失败")}})}
function exportCSV(){var t=localStorage.getItem("admin_token");if(!t){alert("请先登录");return}window.location.href="/api/export/csv?token="+t}
fetch("/api/stats").then(function(r){return r.json()}).then(function(d){if(d.stats)document.getElementById("visitorCount").textContent=d.stats.unique_visitors_30d||0});
</script>
</body>
</html>''')
    
    return HTMLResponse(content=''.join(html_parts))

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "联系表单后端 v2.0 运行中",
        "docs": "/docs",
        "admin": "/admin",
        "features": [
            "验证码系统",
            "JWT 用户认证",
            "留言回复功能",
            "CSV 数据导出",
            "访客统计分析",
            "暗黑模式支持"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Portfolio Backend v2.0 启动中...")
    print("=" * 50)
    print(f"📍 API 文档: http://localhost:8000/docs")
    print(f"📍 管理后台: http://localhost:8000/admin")
    print("=" * 50)
    uvicorn.run("main_backend_v2:app", host="0.0.0.0", port=8000, reload=True)
