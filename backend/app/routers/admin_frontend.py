"""
Portfolio Backend v3.0 - 管理后台前端（独立 SPA）
完全脱离后端渲染，使用 Fetch API 与后端通信
"""
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["管理后台"])

ADMIN_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>留言管理后台 v3.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei','Segoe UI',sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f5f5f5;transition:all .3s}
.dark{background:#1a1a2e;color:#eaeaea}
h1{color:#4361ee;border-bottom:2px solid #4361ee;padding-bottom:10px;margin-bottom:20px}
.dark h1{color:#6c63ff}
.dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px;margin:20px 0}
.card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.1);text-align:center}
.dark .card{background:#16213e;color:#eaeaea}
.card h3{font-size:2rem;color:#4361ee;margin:0}
.dark .card h3{color:#6c63ff}
.card p{margin:5px 0 0;color:#666}
.dark .card p{color:#aaa}
.actions{display:flex;gap:10px;margin:20px 0;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:5px;padding:10px 20px;border:none;border-radius:8px;cursor:pointer;font-size:.95rem;transition:opacity .2s}
.btn:hover{opacity:.85}
.btn-primary{background:#4361ee;color:white}
.btn-success{background:#06d6a0;color:white}
.btn-danger{background:#ef476f;color:white}
.btn-warning{background:#ffd166;color:#333}
.contact-card{background:white;padding:20px;margin:15px 0;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.1);border-left:4px solid #4361ee}
.dark .contact-card{background:#16213e}
.contact-card h3{margin:0 0 8px;color:#333}
.dark .contact-card h3{color:#eaeaea}
.meta{color:#999;font-size:.85em;margin-bottom:10px}
.message{background:#f9f9f9;padding:15px;border-radius:5px;line-height:1.6;margin:10px 0;white-space:pre-wrap}
.dark .message{background:#0f3460;color:#ddd}
.reply-section{margin-top:15px;padding-top:15px;border-top:1px dashed #ddd}
.dark .reply-section{border-color:#444}
.reply-box{width:100%;padding:10px;border:1px solid #ddd;border-radius:5px;margin:10px 0;font-family:inherit;resize:vertical;min-height:80px}
.dark .reply-box{background:#1a1a2e;border-color:#444;color:#eaeaea}
.login-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:1000}
.login-box{background:white;padding:40px;border-radius:10px;width:400px;max-width:90vw}
.dark .login-box{background:#16213e}
.login-box input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:5px}
.dark .login-box input{background:#1a1a2e;border-color:#444;color:#eaeaea}
.login-box button{width:100%;padding:12px;background:#4361ee;color:white;border:none;border-radius:5px;font-size:1rem;cursor:pointer;margin-top:10px}
.hidden{display:none}
.status-badge{display:inline-block;padding:3px 10px;border-radius:15px;font-size:.8em;margin-left:10px}
.status-unread{background:#fee2e2;color:#991b1b}
.status-replied{background:#d1fae5;color:#065f46}
.loading{text-align:center;padding:40px;color:#999}
.toast{position:fixed;top:20px;right:20px;padding:15px 25px;border-radius:8px;color:white;z-index:2000;animation:slideIn .3s}
.toast-success{background:#06d6a0}
.toast-error{background:#ef476f}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;margin:15px 0}
th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd}
.dark th,.dark td{border-color:#444}
th{background:#f0f0f0;font-weight:600}
.dark th{background:#0f3460}
</style>
</head>
<body>
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
<h1>📬 联系表单管理后台 v3.0</h1>
<div class="dashboard" id="statsCards"></div>
<div class="actions">
<button class="btn btn-primary" onclick="refreshData()">🔄 刷新</button>
<button class="btn btn-success" onclick="exportCSV()">📥 导出 CSV</button>
<button class="btn btn-warning" onclick="toggleTheme()">🌙 切换主题</button>
<button class="btn btn-danger" onclick="logout()">🚪 退出登录</button>
</div>
<div id="contactsList"><div class="loading">加载中...</div></div>
</div>

<script>
const API_BASE = window.location.origin;
let token = localStorage.getItem("admin_v3_token");

function api(path, opts={}){
    const headers = {"Content-Type":"application/json"};
    if(token) headers["Authorization"] = "Bearer "+token;
    return fetch(API_BASE+path, {...opts, headers}).then(r=>r.json());
}

function toast(msg, type="success"){
    const t = document.createElement("div");
    t.className = "toast toast-"+type;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(()=>t.remove(), 3000);
}

function toggleTheme(){
    document.body.classList.toggle("dark");
    localStorage.setItem("admin_theme", document.body.classList.contains("dark")?"dark":"light");
}

if(localStorage.getItem("admin_theme")==="dark") document.body.classList.add("dark");
if(token) { showPanel(); refreshData(); }

function doLogin(){
    const u=document.getElementById("loginUser").value;
    const p=document.getElementById("loginPass").value;
    fetch(API_BASE+"/api/v1/auth/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({username:u,password:p})
    }).then(r=>r.json()).then(d=>{
        if(d.access_token){
            token=d.access_token;
            localStorage.setItem("admin_v3_token",token);
            showPanel();
            refreshData();
            toast("登录成功");
        } else {
            document.getElementById("loginError").textContent=d.detail||"登录失败";
        }
    }).catch(()=>toast("网络错误","error"));
}

function showPanel(){
    document.getElementById("loginOverlay").classList.add("hidden");
    document.getElementById("adminPanel").classList.remove("hidden");
}

function logout(){
    token=null;
    localStorage.removeItem("admin_v3_token");
    document.getElementById("loginOverlay").classList.remove("hidden");
    document.getElementById("adminPanel").classList.add("hidden");
    toast("已退出登录");
}

async function refreshData(){
    document.getElementById("contactsList").innerHTML='<div class="loading">加载中...</div>';
    // 统计
    api("/api/v1/stats").then(d=>{
        if(!d.total_contacts) return;
        document.getElementById("statsCards").innerHTML=
            `<div class="card"><h3>${d.total_contacts}</h3><p>总留言</p></div>`+
            `<div class="card"><h3>${d.replied_contacts}</h3><p>已回复</p></div>`+
            `<div class="card"><h3>${d.unread_contacts}</h3><p>待回复</p></div>`+
            `<div class="card"><h3>${d.new_this_week}</h3><p>本周新增</p></div>`;
    });
    // 留言列表
    api("/api/v1/contacts").then(d=>{
        if(!d.contacts || d.contacts.length===0){
            document.getElementById("contactsList").innerHTML='<p style="text-align:center;color:#999;padding:40px">暂无留言</p>';
            return;
        }
        let html="";
        d.contacts.forEach(c=>{
            const sc = c.status==="unread"?"status-unread":"status-replied";
            const st = c.status==="unread"?"未读":"已回复";
            html+='<div class="contact-card">'+
                `<h3>${esc(c.name)} <span class="status-badge ${sc}">${st}</span></h3>`+
                `<div class="meta">📧 ${esc(c.email)} | 🕒 ${c.created_at||""}</div>`+
                (c.subject?`<div><strong>主题：</strong>${esc(c.subject)}</div>`:"")+
                `<div class="message">${esc(c.message)}</div>`;
            if(c.reply) html+=`<div class="message" style="border-left:3px solid #06d6a0"><strong>💬 回复：</strong><br>${esc(c.reply)}</div>`;
            html+=`<div class="reply-section">
                <textarea class="reply-box" id="reply-${c.id}" placeholder="输入回复内容..."></textarea>
                <div style="display:flex;gap:10px">
                    <button class="btn btn-primary" onclick="doReply(${c.id})">💬 回复</button>
                    <button class="btn btn-danger" onclick="doDelete(${c.id})">🗑️ 删除</button>
                </div>
            </div></div>`;
        });
        document.getElementById("contactsList").innerHTML=html;
    });
}

function esc(s){ const d=document.createElement("div"); d.textContent=s||""; return d.innerHTML; }

function doReply(id){
    const r=document.getElementById("reply-"+id).value;
    if(!r.trim()){ toast("请输入回复内容","error"); return; }
    api("/api/v1/contacts/"+id+"/reply",{method:"POST",body:JSON.stringify({reply:r})}).then(d=>{
        if(d.success){ toast("回复成功"); refreshData(); }
        else toast(d.message||"回复失败","error");
    });
}

function doDelete(id){
    if(!confirm("确定删除此留言？")) return;
    api("/api/v1/contacts/"+id,{method:"DELETE"}).then(d=>{
        if(d.success){ toast("删除成功"); refreshData(); }
        else toast(d.message||"删除失败","error");
    });
}

function exportCSV(){
    if(!token){ toast("请先登录","error"); return; }
    console.log("导出CSV开始，token:", token ? "已获取" : "未获取");
    // 使用 fetch 下载 CSV，保持 Bearer Token 认证
    fetch(API_BASE+"/api/v1/admin/export/csv",{
        method:"GET",
        headers:{
            "Authorization":"Bearer "+token,
            "Accept":"text/csv"
        }
    }).then(r=>{
        console.log("导出CSV响应状态:", r.status);
        if(!r.ok) {
            return r.json().then(err=>{
                throw new Error(err.detail||"导出失败");
            }).catch(e=>{
                if(e instanceof SyntaxError) throw new Error("导出失败(HTTP "+r.status+")");
                throw e;
            });
        }
        return r.blob();
    }).then(blob=>{
        console.log("导出CSV成功，blob大小:", blob.size);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "contacts_" + new Date().toISOString().slice(0,10) + ".csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        toast("导出成功");
    }).catch(e=>{
        console.error("导出CSV错误:", e);
        toast(e.message||"导出失败","error");
    });
}
</script>
</body>
</html>"""


@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def admin_panel():
    """管理后台页面"""
    return HTMLResponse(content=ADMIN_HTML)
