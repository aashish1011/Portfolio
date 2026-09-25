import os
import json
import smtplib
import re
import secrets
import hmac
from html import escape
from email.utils import parseaddr
from email.message import EmailMessage
from flask import Flask, redirect, render_template, request, session
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
RECIPIENT = "thakuraashik27@gmail.com"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
UPLOAD_DIR = "/tmp/uploads"
CONTENT_FILE = os.path.join(app.root_path, "content.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEFAULT_CONTENT = {
    "skills": [
        {"title": "Data analysis", "description": "Finding the signal in the noise and making insights actionable.", "image": ""},
        {"title": "Python", "description": "Building clean, reliable workflows for data and automation.", "image": ""},
        {"title": "SQL", "description": "Querying, shaping, and understanding the story in databases.", "image": ""},
        {"title": "NumPy + Pandas", "description": "Exploring, cleaning, and transforming data with confidence.", "image": ""},
        {"title": "Web development", "description": "Crafting responsive digital experiences that feel considered.", "image": ""},
        {"title": "Always learning", "description": "Growing a toolkit that keeps pace with better questions.", "image": ""},
    ],
    "projects": [
        {"title": "[PROJECT NAME]", "description": "[PROJECT DESCRIPTION]", "label": "01 · PROJECT", "image": "", "link": ""},
        {"title": "[PROJECT NAME]", "description": "[PROJECT DESCRIPTION]", "label": "02 · PROJECT", "image": "", "link": ""},
        {"title": "[PROJECT NAME]", "description": "[PROJECT DESCRIPTION]", "label": "03 · PROJECT", "image": "", "link": ""},
    ]
}

def get_content():
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE) as file:
            return json.load(file)
    return DEFAULT_CONTENT

def save_content(content):
    try:
        with open(CONTENT_FILE, "w") as file:
            json.dump(content, file, indent=2)
    except OSError:
        pass

@app.get("/")
def home():
    session["contact_csrf"] = secrets.token_urlsafe(32)
    content = get_content()
    page = render_template("index.html", content=content)
    skill_strip = "".join(f'<span>{escape(item.get("title", "Capability"))}</span><span class="dot">✳</span>' for item in content.get("skills", []))
    if skill_strip:
        page = re.sub(r'<div class="strip-inner">.*?</div>', f'<div class="strip-inner">{skill_strip}{skill_strip}</div>', page, count=1, flags=re.S)
    page = page.replace('href="mailto:thakuraashik27@gmail.com">✉ Gmail', 'href="https://mail.google.com/mail/?view=cm&fs=1&to=thakuraashik27@gmail.com" target="_blank" rel="noreferrer">✉ Gmail')
    assistant = '<style>.ai-hello{position:fixed;right:24px;bottom:24px;z-index:18;display:flex;align-items:center;gap:11px;background:#101114;color:#fff;border:1px solid #34363d;padding:10px 14px 10px 10px;font:11px "DM Mono",monospace;box-shadow:0 14px 35px #10111433;animation:aiIn .4s ease,aiOut .5s ease 4.5s forwards}.ai-robot{width:28px;height:24px;border:2px solid #d7ff5f;border-radius:8px;position:relative}.ai-robot:before{content:"••";position:absolute;left:6px;top:-3px;color:#d7ff5f;font-size:17px;letter-spacing:3px}.ai-robot:after{content:"";position:absolute;width:5px;height:5px;background:#d7ff5f;border-radius:50%;top:-7px;left:10px}.ai-hello span{color:#a8a9b0}@keyframes aiIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}@keyframes aiOut{to{opacity:0;transform:translateY(8px);visibility:hidden}}@media(max-width:600px){.ai-hello{right:16px;bottom:16px}}</style><div class="ai-hello"><i class="ai-robot"></i><span>Hello — I’m Aashish’s AI assistant.</span></div>'
    walker = '<style>.walkbot{position:fixed;left:0;bottom:24px;z-index:19;width:74px;height:112px;animation:walkAcross 8s linear forwards;pointer-events:none}.walkbot .antenna{position:absolute;left:35px;top:0;width:2px;height:10px;background:#101114}.walkbot .antenna:after{content:"";position:absolute;top:-4px;left:-3px;width:8px;height:8px;border-radius:50%;background:#d7ff5f}.walkbot .head{position:absolute;top:10px;left:16px;width:44px;height:34px;border:3px solid #101114;border-radius:10px;background:#d7ff5f}.walkbot .head:before{content:"••";position:absolute;left:9px;top:1px;font:bold 20px Arial;letter-spacing:7px;color:#101114}.walkbot .body{position:absolute;top:48px;left:20px;width:36px;height:36px;border:3px solid #101114;border-radius:8px;background:#fff}.walkbot .arm{position:absolute;top:52px;width:8px;height:27px;border:3px solid #101114;border-radius:8px;background:#d7ff5f;transform-origin:top center}.walkbot .arm.left{left:10px}.walkbot .arm.right{right:10px;animation:wave .75s ease-in-out .9s 2 alternate}.walkbot .leg{position:absolute;top:82px;width:10px;height:27px;border:3px solid #101114;border-radius:8px;background:#d7ff5f;transform-origin:top center}.walkbot .leg.left{left:23px;animation:step .4s ease-in-out infinite alternate}.walkbot .leg.right{left:43px;animation:step .4s ease-in-out .2s infinite alternate}@keyframes walkAcross{0%{transform:translateX(-100px)}12%{transform:translateX(8vw)}72%{transform:translateX(68vw)}100%{transform:translateX(115vw);opacity:0}}@keyframes step{to{transform:rotate(18deg) translateY(2px)}}@keyframes wave{to{transform:rotate(-35deg)}}@media(max-width:600px){.walkbot{bottom:16px;transform:scale(.82);transform-origin:bottom left}}</style><div class="walkbot" aria-hidden="true"><i class="antenna"></i><i class="head"></i><i class="body"></i><i class="arm left"></i><i class="arm right"></i><i class="leg left"></i><i class="leg right"></i></div>'
    walker = walker.replace("<style>", "<style>.ai-hello{display:none!important}")
    walker += '<style>.walkbot{animation:walkAcross 8s cubic-bezier(.32,.02,.25,1) forwards}.walkbot .head,.walkbot .body{animation:bodyBob .38s ease-in-out infinite alternate}.walkbot .arm.left{animation:armSwing .38s ease-in-out infinite alternate}.walkbot .arm.right{animation:helloWave .7s ease-in-out 1s 2 alternate,byeWave .7s ease-in-out 5.9s 2 alternate}.walkbot .leg.left{animation:humanStep .38s ease-in-out infinite alternate}.walkbot .leg.right{animation:humanStep .38s ease-in-out .19s infinite alternate}@keyframes bodyBob{to{transform:translateY(3px)}}@keyframes humanStep{to{transform:rotate(22deg) translateY(2px)}}@keyframes armSwing{to{transform:rotate(18deg)}}@keyframes helloWave{to{transform:rotate(-38deg)}}@keyframes byeWave{to{transform:rotate(-48deg)}}.walkbot:after{content:"HELLO";position:absolute;left:48px;top:12px;color:#686b72;font:9px "DM Mono";opacity:0;animation:helloText .9s ease .7s 2 alternate,byeText .8s ease 5.65s 2 alternate}@keyframes helloText{to{opacity:1;transform:translateY(-4px)}}@keyframes byeText{to{content:"BYE";opacity:1;transform:translateY(-4px)}}</style>'
    walker += '<style>.walkbot:after{display:none!important}</style>'
    walker += '<style>.walkbot{left:auto;right:18px;top:78px;bottom:auto;width:58px;height:88px;transform:scale(.72);transform-origin:top right;animation:robotFloat 2.4s ease-in-out infinite!important;filter:drop-shadow(0 8px 8px #10111422)}.walkbot .head{left:10px}.walkbot .body{left:14px}.walkbot .arm.left{left:4px}.walkbot .arm.right{right:4px}.walkbot .leg.left{left:17px}.walkbot .leg.right{left:37px}@keyframes robotFloat{0%,100%{transform:scale(.72) translateY(0)}50%{transform:scale(.72) translateY(5px)}}@media(max-width:600px){.walkbot{top:84px;right:12px;transform:scale(.62);animation:robotFloatMobile 2.4s ease-in-out infinite!important;z-index:30}}@keyframes robotFloatMobile{0%,100%{transform:scale(.62) translateY(0)}50%{transform:scale(.62) translateY(4px)}}</style>'
    page = page.replace("<body>", "<body>" + assistant + walker)
    page = page.replace("01 / About me", "").replace("02 / Capabilities", "").replace("03 / Selected work", "").replace("04 / Say hello", "")
    page = page.replace('<div class="scroll">SCROLL TO EXPLORE ↓</div>', '<div class="scroll">SCROLL TO EXPLORE ↓</div>')
    page = page.replace("Things I’m <em>making.</em>", "Projects")
    page = page.replace("Let’s make<br><em>something good.</em>", "Let’s connect.")
    page = page.replace('<a href="#">◉ GitHub</a>', '<a href="https://github.com/aashish-110" target="_blank" rel="noreferrer">◉ GitHub</a>')
    page = page.replace('<a href="#">in LinkedIn</a>', '<a href="https://www.linkedin.com/in/aashish-kumar-thakur-749039323/" target="_blank" rel="noreferrer">in LinkedIn</a>')
    page = page.replace('<a href="tel:9824577500">☎ +977 9824577500</a>', '<a href="https://wa.me/9779824577500" target="_blank" rel="noreferrer">◉ WhatsApp</a><a href="tel:9824577500">☎ +977 9824577500</a>')
    page = re.sub(r'(<article class="unified-card project-card">.*?</article>)', lambda match: re.sub(r'<small>.*?</small>', '', match.group(1), flags=re.S), page, flags=re.S)
    page = page.replace('<span class="arrow"><a href=', '<span class="arrow"><a class="project-demo" href=')
    page = page.replace('<span class="arrow"><a class="project-demo" href=', '<span class="arrow"><a class="project-demo" href=')
    page = page.replace('>↗</a></span>', '>View demo ↗</a></span>')
    page = page.replace('<span class="arrow">↗</span>', '<span class="arrow"><span class="project-demo disabled">Coming soon</span></span>')
    project_index = [0]
    def add_project_details(match):
        index = project_index[0]
        project_index[0] += 1
        return match.group(1) + f'<a class="project-more" href="/project/{index}">More ↗</a></article>'
    page = re.sub(r'(<article class="unified-card project-card">.*?</span>)</article>', add_project_details, page, flags=re.S)
    if request.args.get("sent") == "1":
        toast = '<style>.mail-toast{position:fixed;right:24px;bottom:24px;z-index:20;background:#101114;color:#fff;border-left:4px solid #d7ff5f;padding:16px 20px;box-shadow:0 14px 35px #10111433;font:13px Manrope,sans-serif;animation:toastIn .35s ease,toastOut .45s ease 4.2s forwards}.mail-toast strong{display:block;margin-bottom:3px}.mail-toast span{color:#a8a9b0;font-size:12px}@keyframes toastIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}@keyframes toastOut{to{opacity:0;transform:translateY(8px);visibility:hidden}}@media(max-width:600px){.mail-toast{right:16px;bottom:16px;left:16px}}</style><div class="mail-toast"><strong>Message sent successfully.</strong><span>Thanks for reaching out — I’ll get back to you soon.</span></div>'
        page = page.replace("<body>", "<body>" + toast)
    page = re.sub(r"<small>\d{2} / CAPABILITY</small>", "", page)
    page = re.sub(r"<small>\d{2} · PROJECT</small>", "", page)
    page = page.replace('<form class="contact-form" action="/contact" method="post">', '<form class="contact-form" action="/contact" method="post"><input type="hidden" name="csrf_token" value="' + session["contact_csrf"] + '">')
    page = page.replace("Curious<br><em>by nature.</em><br>Built to solve.", "Building with<br><em>data &amp; purpose.</em><br>Open to work.")
    page = page.replace("I’m Aashish Kumar Thakur — a data-minded developer blending analytical thinking with thoughtful digital experiences.", "I’m Aashish Kumar Thakur, a BSc. AI student focused on data analysis, Python, SQL, and web development — currently open to internships, collaborations, and entry-level opportunities.")
    page = page.replace(".unified-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}", ".unified-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}")
    page = page.replace(".unified-card .visual{position:absolute;inset:0 0 auto;height:145px;background:linear-gradient(135deg,#30333a,#181a1f);background-size:cover;background-position:center;border-bottom:1px solid var(--line)}", ".unified-card .visual{position:absolute;top:25px;left:50%;transform:translateX(-50%);width:94px;height:94px;border-radius:50%;background:linear-gradient(135deg,#777b80,#373a40);background-size:cover;background-position:center;border:6px solid #25282d;box-shadow:0 8px 20px #0005}")
    page = page.replace(".unified-card .visual:after{content:'[ ADD IMAGE ]';position:absolute;inset:0;display:grid;place-items:center;color:#777;font:11px 'DM Mono';letter-spacing:.1em}", ".unified-card .visual:after{content:'IMAGE';position:absolute;inset:0;display:grid;place-items:center;color:#aeb1b4;font:10px 'DM Mono';letter-spacing:.1em}")
    page = page.replace(".unified-card.project-card{min-height:300px;padding-top:210px", ".unified-card.project-card{min-height:300px;padding-top:178px;background:#d8d7d1;color:#101114")
    page = page.replace(".unified-card.project-card .visual{height:195px}", ".unified-card.project-card .visual{width:130px;height:130px;border-radius:50%;border:6px solid #b8b7b1;top:24px;left:50%;transform:translateX(-50%);box-shadow:0 8px 18px #10111422}")
    page = page.replace(".unified-card.project-card .visual:after{content:'[ PROJECT IMAGE ]'}", ".unified-card.project-card .visual:after{content:'[ PROJECT IMAGE ]';color:#686b72}.unified-card.project-card p{color:#34363d}.unified-card.project-card small{color:#4c5d00}.unified-card.project-card .arrow{color:#101114}")
    page = page.replace("Have a question,<br>idea, or opportunity?<br><em>Drop me a line.</em>", "Looking for a<br>motivated developer?<br><em>Let’s work together.</em>")
    page = page.replace("Made with curiosity &amp; care", "Open to internships · collaborations · opportunities")
    page = page.replace("</body>", "<style>#projects{background:#101114!important;color:#fff!important}#projects .section-head{border-color:#34363d!important}#projects .kicker{color:#aaa!important}#projects .section-title{color:#fff!important}#projects .unified-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}#projects .unified-card.project-card{background:#191b20!important;color:#fff!important;border-color:#34363d!important;min-height:420px!important;padding:190px 28px 34px!important}#projects .unified-card.project-card:hover{background:#202228!important;border-color:#d7ff5f!important}#projects .unified-card.project-card .visual{width:120px!important;height:120px!important;top:25px!important;left:50%!important;right:auto!important;inset:25px auto auto 50%!important;transform:translateX(-50%)!important;margin:0!important;border-radius:50%!important;border:6px solid #25282d!important;box-shadow:0 8px 20px #0005!important}#projects .unified-card.project-card .visual:after{color:#aeb1b4!important}#projects .unified-card.project-card h3{color:#fff!important;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden}#projects .unified-card.project-card p{color:#a8a9b0!important;min-height:0!important;max-width:100%!important;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:6;overflow:hidden}#projects .unified-card.project-card small{color:#d7ff5f!important}#projects .unified-card.project-card .arrow,#projects .unified-card.project-card .arrow a{color:#fff!important}@media(max-width:800px){#projects .unified-grid{grid-template-columns:1fr;gap:16px}#projects .unified-card.project-card{min-height:380px!important;padding-top:178px!important}}</style></body>")
    page = page.replace("</body>", "<style>.robot-greeting{position:fixed;top:88px;right:82px;z-index:29;background:#101114;color:#fff;border:1px solid #34363d;border-radius:999px;padding:9px 13px;font:11px 'DM Mono',monospace;box-shadow:0 8px 20px #10111422}.robot-greeting:after{content:'';position:absolute;right:-6px;top:13px;width:10px;height:10px;background:#101114;border-top:1px solid #34363d;border-right:1px solid #34363d;transform:rotate(45deg)}@media(max-width:600px){.robot-greeting{top:86px;right:62px;font-size:9px;padding:8px 10px}}</style><div class='robot-greeting' id='robot-greeting'>Namaste</div><script>(function(){const hour=new Date().getHours();const greeting=hour<12?'Namaste, good morning':hour<17?'Namaste, good afternoon':hour<21?'Namaste, good evening':'Namaste, good night';const el=document.getElementById('robot-greeting');if(el)el.textContent=greeting;})();</script></body>")
    page = page.replace("</body>", "<style>#skills{background:#101114}#skills .unified-card{border-radius:14px;transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .35s,box-shadow .35s;will-change:transform}#skills .unified-card:before{content:'';position:absolute;inset:0 0 auto;height:3px;background:var(--lime);transform:scaleX(0);transform-origin:left;transition:transform .35s ease}#skills .unified-card:hover{transform:translateY(-10px) rotate(-1deg);box-shadow:0 18px 35px #0005}#skills .unified-card:hover:before{transform:scaleX(1)}#projects{background:linear-gradient(145deg,#101114 0%,#171a1f 52%,#101114 100%)}#projects .project-card{border-radius:4px;transition:transform .5s cubic-bezier(.2,.8,.2,1),border-color .35s,box-shadow .5s;will-change:transform}#projects .project-card:hover{transform:translateY(-12px);box-shadow:0 24px 45px #0006}#projects .project-card .visual{transition:transform .5s cubic-bezier(.2,.8,.2,1),box-shadow .5s}#projects .project-card:hover .visual{transform:translateX(-50%) scale(1.08) rotate(4deg);box-shadow:0 0 0 8px #d7ff5f22,0 12px 26px #0008!important}#skills .unified-card,#projects .project-card{opacity:0;transform:translateY(28px)}#skills .unified-card.is-visible,#projects .project-card.is-visible{opacity:1;transform:translateY(0)}#skills .unified-card:nth-child(2),#projects .project-card:nth-child(2){transition-delay:.08s}#skills .unified-card:nth-child(3),#projects .project-card:nth-child(3){transition-delay:.16s}#skills .unified-card:nth-child(4),#projects .project-card:nth-child(4){transition-delay:.24s}#skills .unified-card:nth-child(5),#projects .project-card:nth-child(5){transition-delay:.32s}#skills .unified-card:nth-child(6),#projects .project-card:nth-child(6){transition-delay:.4s}@media(prefers-reduced-motion:reduce){#skills .unified-card,#projects .project-card{opacity:1;transform:none;transition:none}#skills .unified-card:hover,#projects .project-card:hover{transform:none}#skills .unified-card:before{transition:none}}@media(max-width:800px){#skills .unified-card:hover,#projects .project-card:hover{transform:translateY(-6px)}}</style><script>const revealItems=document.querySelectorAll('#skills .unified-card,#projects .project-card');if('IntersectionObserver' in window){const revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');revealObserver.unobserve(entry.target)}}),{threshold:.14});revealItems.forEach(item=>revealObserver.observe(item))}else{revealItems.forEach(item=>item.classList.add('is-visible'))}</script></body>")
    page = page.replace("</body>", "<script>document.querySelectorAll('.visual').forEach(visual=>{const fallback=\"url('/static/images/ai.jpg')\";const current=visual.style.backgroundImage;if(current){const probe=new Image();probe.onload=()=>{};probe.onerror=()=>{visual.style.backgroundImage=current.replace(/url\\((['\"]?)[^'\\\"]+\\1\\)/,fallback)};const match=current.match(/url\\((['\"]?)([^'\\\"]+)\\1\\)/);if(match)probe.src=match[2]}else{visual.style.backgroundImage=fallback}});</script></body>")
    page = page.replace("</body>", "<style>.hero{overflow:visible}.hero .actions{position:relative;z-index:2}.hero .scroll{left:0;bottom:28px;z-index:1}@media(max-width:800px){.hero .scroll{display:block!important;position:static!important;writing-mode:horizontal-tb!important;margin-top:28px;font:10px 'DM Mono';color:#686b72}.hero .actions{flex-wrap:wrap;gap:10px;transform:translateX(-8px)}.hero .actions .btn{white-space:nowrap}}</style></body>")
    page = page.replace("</body>", "<style>.project-demo,.project-more{display:inline-flex!important;align-items:center;gap:8px;border-radius:999px;padding:10px 14px;font:700 11px Manrope,sans-serif;letter-spacing:.02em;transition:transform .25s,background .25s;color:#101114!important;-webkit-text-fill-color:#101114!important}.project-card a.project-demo{background:#fff!important;color:#000!important;-webkit-text-fill-color:#000!important;border:1px solid #fff!important;min-width:120px;justify-content:center;text-align:center}.project-card a.project-demo:hover{background:#fff!important;color:#000!important;-webkit-text-fill-color:#000!important;border-color:#fff!important;transform:translateY(-2px)}.project-more{background:#d7ff5f!important;border:1px solid #d7ff5f!important}.project-more:hover{background:#fff!important;border-color:#fff!important;transform:translateY(-2px)}.project-demo.disabled{background:transparent!important;color:#8c9098!important;border-color:#4a4d55!important;cursor:default}.project-card{min-height:480px!important;padding-bottom:30px!important}.project-card .arrow{position:static!important;display:flex;align-items:center;margin-top:18px}.project-card .project-demo{position:static!important}.project-card .project-more{position:static!important;align-self:flex-start;margin-top:10px}.project-card .project-more:hover{color:#101114!important}@media(max-width:800px){.project-card{min-height:430px!important}}</style></body>")
    return page

# @app.get("/resume")
# def resume():
#     resume_image = next((name for name in os.listdir(UPLOAD_DIR) if name.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))), None)
#     return render_template("resume.html", resume_image=resume_image)

@app.get("/resume")
def resume():
    resume_image = None
    if os.path.exists(UPLOAD_DIR):
        resume_image = next((name for name in os.listdir(UPLOAD_DIR) if name.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))), None)
    return render_template("resume.html", resume_image=resume_image)

@app.get("/project/<int:index>")
def project_detail(index):
    projects = get_content().get("projects", [])
    if index < 0 or index >= len(projects):
        return redirect("/#projects")
    return render_template("project.html", project=projects[index])

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if ADMIN_USERNAME and ADMIN_PASSWORD and hmac.compare_digest(request.form.get("username", ""), ADMIN_USERNAME) and hmac.compare_digest(request.form.get("password", ""), ADMIN_PASSWORD):
            session["admin"] = True
            return redirect("/admin")
        return render_template("admin.html", error="Invalid admin credentials.")
    if not session.get("admin"):
        return render_template("admin.html", login=True)
    return render_template("admin.html", login=False, content=get_content())

@app.post("/admin/content/<section>/add")
def add_content(section):
    if not session.get("admin") or section not in ("skills", "projects"):
        return redirect("/admin")
    content = get_content()
    item = {"title": request.form.get("title", "").strip(), "description": request.form.get("description", "").strip(), "image": request.form.get("image", "").strip()}
    if section == "projects":
        item["label"] = request.form.get("label", "PROJECT · NEW").strip()
        item["link"] = request.form.get("link", "").strip()
    if item["title"]: content[section].append(item)
    save_content(content)
    return redirect("/admin")

@app.post("/admin/content/<section>/<int:index>/delete")
def delete_content(section, index):
    if not session.get("admin") or section not in ("skills", "projects"):
        return redirect("/admin")
    content = get_content()
    if 0 <= index < len(content[section]): content[section].pop(index)
    save_content(content)
    return redirect("/admin")

@app.post("/admin/content/<section>/<int:index>/edit")
def edit_content(section, index):
    if not session.get("admin") or section not in ("skills", "projects"):
        return redirect("/admin")
    content = get_content()
    if 0 <= index < len(content[section]):
        item = content[section][index]
        item["title"] = request.form.get("title", item.get("title", "")).strip()
        item["description"] = request.form.get("description", item.get("description", "")).strip()
        item["image"] = request.form.get("image", item.get("image", "")).strip()
        if section == "projects": item["label"] = request.form.get("label", item.get("label", "")).strip()
        if section == "projects": item["link"] = request.form.get("link", item.get("link", "")).strip()
        save_content(content)
    return redirect("/admin")

@app.post("/admin/resume-upload")
def resume_upload():
    if not session.get("admin"):
        return redirect("/admin")
    file = request.files.get("resume_image")
    if not file or not file.filename:
        return redirect("/admin")
    filename = secure_filename(file.filename)
    if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "Only PNG, JPG, JPEG, and WEBP files are allowed.", 400
    for old_file in os.listdir(UPLOAD_DIR):
        if old_file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            os.remove(os.path.join(UPLOAD_DIR, old_file))
    file.save(os.path.join(UPLOAD_DIR, filename))
    return redirect("/resume")

@app.get("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")

@app.post("/contact")
def contact():
    csrf = request.form.get("csrf_token", "")
    if not csrf or not hmac.compare_digest(csrf, session.get("contact_csrf", "")):
        return "Invalid form session. Please refresh the page and try again.", 400
    name = request.form.get("name", "").strip()
    sender = request.form.get("email", "").strip()
    subject = request.form.get("subject", "Portfolio contact").strip()
    message = request.form.get("message", "").strip()
    parsed_name, parsed_email = parseaddr(sender)
    if not name or not sender or not message or parsed_email != sender or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", sender) or any("\n" in value or "\r" in value for value in (name, sender, subject)):
        return "Please complete the required fields.", 400
    if len(name) > 120 or len(subject) > 180 or len(message) > 8000:
        return "Your message is too long.", 400
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_username or not smtp_password:
        return "Email service is not configured.", 503

    email = EmailMessage()
    email["From"] = smtp_username
    email["To"] = RECIPIENT
    email["Reply-To"] = sender
    email["Subject"] = f"Portfolio enquiry: {subject}"
    email.set_content(f"Name: {name}\nEmail: {sender}\n\n{message}")

    with smtplib.SMTP_SSL(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "465"))) as smtp:
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(email)
    session.pop("contact_csrf", None)
    return redirect("/#contact?sent=1")

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")

app=app
